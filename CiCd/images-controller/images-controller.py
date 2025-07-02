import os
import sys
import json
import base64
import logging
import shutil
from shutil import rmtree
import subprocess
import yaml
import boto3
from botocore.config import Config
import docker
from git import Repo

# Enable BuildKit globally for Docker builds
os.environ["DOCKER_BUILDKIT"] = "1"

# Logger configuration
logger = logging.getLogger("ecr_deployer")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def load_config():
    with open('configuration.yaml', 'r') as file:
        return yaml.safe_load(file)

def copy_and_overwrite(src, dst):
    if not os.path.isdir(src):
        logger.error(f"Copy directory {src} does not exist")
        return False
    logger.info(f"Copying and overwriting files from {src} to {dst}")
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    return True

def docker_logout(registry):
    try:
        subprocess.run(["docker", "logout", registry], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"Logged out from Docker registry: {registry}")
    except Exception as e:
        logger.warning(f"Failed to logout from Docker registry {registry}: {e}")

def image_exists_in_ecr(ecr_client, repository_name, image_tag):
    """Check if image tag exists in ECR with pagination handling"""
    image_ids = []
    next_token = None
    
    while True:
        if next_token:
            response = ecr_client.list_images(
                repositoryName=repository_name,
                filter={'tagStatus': 'TAGGED'},
                nextToken=next_token
            )
        else:
            response = ecr_client.list_images(
                repositoryName=repository_name,
                filter={'tagStatus': 'TAGGED'}
            )
        
        image_ids.extend(response.get('imageIds', []))
        next_token = response.get('nextToken')
        if not next_token:
            break

    existing_tags = [img['imageTag'] for img in image_ids if 'imageTag' in img]
    return image_tag in existing_tags

def process_service(service_config, config):
    service_name = service_config["name"]
    logger.info(f"Processing service: {service_name}")
    
    # Construct full local path
    local_path = os.path.join(config["global"]["repositoriesPath"], service_config["local_path"].lstrip('./'))
    repo_url = service_config["repo_url"]
    branch = service_config["branch"]
    environment = service_config["environment"]
    tag = service_config["tag"]
    copy_dir = service_config.get("copy_dir")

    # ECR repository name construction
    ECR_REPOSITORY_NAME = f"{environment}/{service_name}"
    IMAGE_TAG = tag

    try:
        # Initialize AWS clients
        ecr_client = boto3.client('ecr', config=Config(region_name=config["global"]["awsRegion"]))
        
        # Create or verify ECR repository
        try:
            ecr_client.create_repository(
                repositoryName=ECR_REPOSITORY_NAME,
                imageTagMutability=config["ecr"]["tagsMutability"],
                imageScanningConfiguration={'scanOnPush': True}
            )
            logger.info(f"Created ECR repository: {ECR_REPOSITORY_NAME}")
        except ecr_client.exceptions.RepositoryAlreadyExistsException:
            logger.info(f"ECR repository exists: {ECR_REPOSITORY_NAME}")

        # Get repository URI
        repo_data = ecr_client.describe_repositories(
            repositoryNames=[ECR_REPOSITORY_NAME]
        )
        repository_url = repo_data['repositories'][0]['repositoryUri']
        registry = repository_url.split('/')[0]

        # Check if image already exists (including 'latest')
        if image_exists_in_ecr(ecr_client, ECR_REPOSITORY_NAME, IMAGE_TAG):
            logger.info(f"Image {ECR_REPOSITORY_NAME}:{IMAGE_TAG} already exists. Skipping build/push.")
            return True

        # Git operations
        use_cloning = config["global"]["repositoriesPath"] in ("./", ".")
        repo = None
        if use_cloning:
            try:
                if os.path.exists(local_path):
                    repo = Repo(local_path)
                    repo.git.checkout(branch)
                    repo.remotes.origin.pull()
                    logger.info(f"Updated repository: {local_path}")
                else:
                    repo = Repo.clone_from(repo_url, local_path, branch=branch)
                    logger.info(f"Cloned repository: {local_path}")
            except Exception as e:
                logger.error(f"Git operations failed: {str(e)}")
                return False

        # Copy additional files if specified
        if copy_dir:
            try:
                copy_and_overwrite(copy_dir, local_path)
                logger.info(f"Copied files from {copy_dir} to {local_path}")
            except Exception as e:
                logger.error(f"File copy failed: {str(e)}")
                return False

        # Docker operations
        docker_client = docker.from_env()
        
        # ECR logout (to clear any stale token)
        docker_logout(registry)

        # ECR login
        auth = ecr_client.get_authorization_token()
        username, password = base64.b64decode(auth['authorizationData'][0]['authorizationToken']).decode().split(':')
        docker_client.login(
            username=username,
            password=password,
            registry=auth['authorizationData'][0]['proxyEndpoint']
        )
        logger.info(f"Logged in to Docker ECR registry: {registry}")

        # Build image
        image, _ = docker_client.images.build(
            path=local_path,
            tag=f"{repository_url}:{IMAGE_TAG}",
            rm=True
        )
        logger.info(f"Built image: {repository_url}:{IMAGE_TAG}")

        # Push image
        push_log = docker_client.images.push(f"{repository_url}:{IMAGE_TAG}")
        logger.info(f"Push result: {push_log}")

        # Cleanup cloned repo if we cloned it
        if use_cloning and os.path.exists(local_path):
            rmtree(local_path)
            logger.info(f"Cleaned up repository: {local_path}")

        return True

    except Exception as e:
        logger.error(f"Failed processing {service_name}: {str(e)}")
        return False

def main():
    config = load_config()
    results = []
    for service in config["services"]:
        success = process_service(service, config)
        results.append({
            "service": service["name"],
            "success": success
        })

    # Generate report
    logger.info("\n=== Processing Summary ===")
    for result in results:
        status = "SUCCESS" if result["success"] else "FAILED"
        logger.info(f"{result['service']}: {status}")

    if not all(r["success"] for r in results):
        exit(1)

if __name__ == "__main__":
    main()
