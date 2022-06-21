import subprocess
import sys, os
import platform
import getpass

# get uid inside container
cmd = ["docker", "run", "ackrep_deployment_celery_worker", "id", "-u"]
res = subprocess.run(cmd, text=True, capture_output=True)
uid_docker = res.stdout.replace("\n", "")

# get uid of host
host_uid = os.getuid()
print("host uid:", host_uid)
host_name = getpass.getuser()
print("host_name:", host_name)

root_dir = os.path.dirname(os.path.abspath(__file__))

if platform.system() == "Linux":
#     uid_host = os.getuid()
#     gid_host = os.getgid()
    
    # Note: this is done via subprocess since os.chown has no recursive option

    print("Changing Permissions...")

    cmds = []
    # Change permissions so that the celery worker container can create sibling container with environments
    cmds.append(["sudo", "chown", f"{host_uid}:{uid_docker}", "/var/run/docker.sock"])
#     # Change permissions so that the env container make changes to data_repo
#     cmds.append(["sudo", "chown", "-R", f"{uid_host}:{gid_docker}", f"{root_dir}/../ackrep_data"])
#     cmds.append(["sudo", "chmod", "-R", "g+rw", f"{root_dir}/../ackrep_data"])
#     cmds.append(["sudo", "chown", "-R", f"{uid_host}:{gid_docker}", f"{root_dir}/../ackrep_data_for_unittests"])
#     cmds.append(["sudo", "chmod", "-R", "g+rw", f"{root_dir}/../ackrep_data_for_unittests"])
    for cmd in cmds:
        res = subprocess.run(
            cmd, text=True, capture_output=True
        )
        if res.returncode != 0:
            print(res.stderr)
            print(res.stdout)
        assert res.returncode == 0, f"Could not change permissions number.\n{cmd} failed."
    print("Done.")
else:
    raise NotImplementedError

# save data_repo address on host for volume mapping of env container
data_repo_host_address = os.path.join(os.path.split(root_dir)[0], "ackrep_data")
print("data repo on host:", data_repo_host_address)



# run docker containers
# subprocess needs an executable first
# extra quotation marks to cover whitespaces
cmd = f"/bin/sh -c 'DATA_REPO_HOST_ADDRESS={data_repo_host_address} HOST_UID={host_uid} HOST_NAME={host_name} docker-compose up'"
# default_env container is supposed to exit with code 1
try:
    res = subprocess.run([cmd], shell=True)
except KeyboardInterrupt:
    print("shutting down...")
    res = subprocess.run(["docker-compose", "down"])
    print("Exit.")
