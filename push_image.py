import os, sys
import subprocess
import argparse

from ipydex import IPS
from sympy import re

"""
run 
`python push_image.py -i <image_name> -v <x.y.z> -m "<message>"`
from the command line
"""

argparser = argparse.ArgumentParser()
argparser.add_argument("-i", "--image", help="image name", metavar="image", default="default_environment")
argparser.add_argument("-v", "--version", help="version tag", metavar="version")
argparser.add_argument("-m", "--message", help="description of version", metavar="message")

args = argparser.parse_args()

image = args.image

# assert version is specified
assert args.version is not None, "no version tag specified"
version = args.version
assert len(version.split(".")) == 3, "version tag not in the form of major.minor.fix"

# assert message is specified
assert args.message is not None, "no message specified"
message = args.message


# manipulate dockerfile to write version description
#! this assumes a lot about naming conventions
root_path = os.path.dirname(__file__)
dockerfile_path = os.path.join(root_path, "dockerfiles/ackrep_core", f"Dockerfile_{image}")
content = f'LABEL org.opencontainers.image.description "{message}"'

dockerfile = open(dockerfile_path, "r")
lines = dockerfile.readlines()
dockerfile.close()

dockerfile = open(dockerfile_path, "a")
dockerfile.write("\n" + content)
dockerfile.close()

# rebuild image to incorporate description
print("Rebuilding Image")
res = subprocess.run(["docker-compose", "build", image])
assert res.returncode == 0

# get image id
prefix = "ackrep_deployment_"
image_name = prefix + image
res = subprocess.run(["docker", "images", image_name, "-q"], text=True, capture_output=True)
assert res.returncode == 0
id = res.stdout.replace("\n", "")
assert len(id) == 12, "unable to find image id"

# publish
repo_name = "ghcr.io/ackrep-org/"

# tag image with version 
remote_name = repo_name + image + ":" + version
cmd = ["docker", "tag", id, remote_name]
res = subprocess.run(cmd)
assert res.returncode == 0
# push
print("Pushing to", remote_name)
cmd = ["docker", "image", "push", remote_name]
res = subprocess.run(cmd)
assert res.returncode == 0

# tag image with latest
remote_name = repo_name + image + ":" + "latest"
cmd = ["docker", "tag", id, remote_name]
res = subprocess.run(cmd)
assert res.returncode == 0
# push
print("Pushing to", remote_name)
cmd = ["docker", "image", "push", remote_name]
res = subprocess.run(cmd)
assert res.returncode == 0

# reset dockerfile
dockerfile = open(dockerfile_path, "w")
dockerfile.writelines(lines)
dockerfile.close()

print("\nDone")
url = "https://github.com/orgs/ackrep-org/packages/container/package/" + image
print("Check the result:", url)