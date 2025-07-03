import os
import sys
import logging
import shutil
from shutil import rmtree
import subprocess
import yaml
from git import Repo
import re

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

def build_and_push_image_with_digest(local_path, image_name, registry):
    """
    Build and push a Docker image to a configurable registry, and return the digest reference.
    """
    temp_tag = f"{registry}/{image_name}:temp"
    logger.info(f"Building Docker image: {temp_tag}")
    try:
        subprocess.run(["docker", "build", "-t", temp_tag, local_path], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build image {temp_tag}: {e}")
        return None

    logger.info(f"Pushing image: {temp_tag}")
    try:
        subprocess.run(["docker", "push", temp_tag], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to push image {temp_tag}: {e}")
        return None

    logger.info(f"Retrieving digest for image: {temp_tag}")
    try:
        output = subprocess.check_output(
            ["docker", "inspect", "--format={{index .RepoDigests 0}}", temp_tag]
        ).decode().strip()
        match = re.match(r".+@(?P<digest>sha256:[a-f0-9]+)", output)
        if not match:
            logger.error(f"Could not extract digest from: {output}")
            return None
        digest = match.group("digest")
        digest_ref = f"{registry}/{image_name}@{digest}"
        logger.info(f"Image digest reference: {digest_ref}")
    except Exception as e:
        logger.error(f"Failed to get image digest: {e}")
        return None

    subprocess.run(["docker", "rmi", temp_tag], check=False)
    return digest_ref

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
        digest_ref = build_and_push_image_with_digest(local_path, IMAGE_TAG, registry)
        if not digest_ref:
            return False

        # Cleanup cloned repo if we cloned it
        if use_cloning and os.path.exists(local_path):
            rmtree(local_path)
            logger.info(f"Cleaned up repository: {local_path}")

        # Return digest reference for further use
        return digest_ref

    except Exception as e:
        logger.error(f"Failed processing {service_name}: {str(e)}")
        return False

def main():
    config = load_config()
    results = []
    for service in config["services"]:
        digest_ref = process_service(service, config)
        success = digest_ref is not False
        results.append({
            "service": service["name"],
            "success": success,
            "digest_ref": digest_ref if success else None
        })

    # Generate report
    logger.info("\n=== Processing Summary ===")
    for result in results:
        status = "SUCCESS" if result["success"] else "FAILED"
        logger.info(f"{result['service']}: {status}")
        if result["digest_ref"]:
            logger.info(f"Digest: {result['digest_ref']}")

    if not all(r["success"] for r in results):
        exit(1)

if __name__ == "__main__":
    main()
