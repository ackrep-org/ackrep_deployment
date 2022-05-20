import subprocess
import sys, os
import platform

uid_docker = 999
gid_docker = 999

# Change permissions so the celery worker container can create sibling container with environments
print("Changing Permissions of shared files")
if platform.system() == "Linux":
    res = subprocess.run(["id"], text=True, capture_output=True)
    uid_host = res.stdout.split("uid")[1].split("=")[1].split("(")[0]
    gid_host = res.stdout.split("gid")[1].split("=")[1].split("(")[0]
    res = subprocess.run(["sudo", "chown", f"{uid_host}:{gid_docker}", "/var/run/docker.sock"], text=True, capture_output=True)
    assert res.returncode == 0, "Could not change permissions for docker socket."
else:
    raise NotImplementedError

# run docker container
try:
    res = subprocess.run(["docker-compose", "up", "celery_worker"])
except KeyboardInterrupt:
    print("shutting down...")
    res = subprocess.run(["docker-compose", "down"])
    print("Exit.")