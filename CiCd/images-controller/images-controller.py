import os
import sys
import logging
import shutil
from shutil import rmtree
import subprocess
import yaml
from git import Repo

# Logger configuration
logger = logging.getLogger("microk8s_deployer")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def load_config():
    with open('../../Configuration/dev/cicd.yaml', 'r') as file:
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

def docker_login_microk8s_registry(registry="localhost:32000"):
    # For MicroK8s, the registry is usually insecure and does not require login
    # But if you have authentication, perform login here
    logger.info(f"Assuming MicroK8s registry at {registry} does not require login.")

def build_and_push_image(local_path, image_tag, registry="localhost:32000"):
    full_image_tag = f"{registry}/{image_tag}"
    logger.info(f"Building Docker image: {full_image_tag}")
    try:
        subprocess.run(
            ["docker", "build", "-t", full_image_tag, local_path],
            check=True
        )
        logger.info(f"Built image: {full_image_tag}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build image {full_image_tag}: {e}")
        return False

    logger.info(f"Pushing image: {full_image_tag}")
    try:
        subprocess.run(
            ["docker", "push", full_image_tag],
            check=True
        )
        logger.info(f"Pushed image: {full_image_tag}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to push image {full_image_tag}: {e}")
        return False

def process_service(service_config, config):
    service_name = service_config["name"]
    logger.info(f"Processing service: {service_name}")

    # Construct full local path
    local_path = os.path.join(config["global"]["repositoriesPath"], service_config["local_path"].lstrip('./'))
    repo_url = service_config["repo_url"]
    branch = service_config["branch"]
    tag = service_config["tag"]
    copy_dir = service_config.get("copy_dir")
    registry = config["global"].get("microk8sRegistry", "localhost:32000")

    IMAGE_TAG = f"{service_name}:{tag}"

    try:
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

        # Build and push image to MicroK8s registry
        docker_login_microk8s_registry(registry)
        if not build_and_push_image(local_path, IMAGE_TAG, registry):
            return False

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
