"""
This script does the following:
- load specified settings
- find all templates (of config files)
- render these templates


for remote deployment

- stop remote services
- upload all files to the server
- restart remote services
"""

from math import fabs
import sys
import os
import argparse
import yaml
import deploymentutils as du
import time

from ipydex import IPS, activate_ips_on_exception

activate_ips_on_exception()


# once there was a use case for importing core during deployment ...
#mod_path = os.path.dirname(os.path.abspath(__file__))
#core_mod_path = os.path.join(mod_path, "..", "ackrep_core")
#sys.path.insert(0, core_mod_path)
#from ackrep_core import core


def main():
    du.argparser.add_argument("configfile", help="path to .ini-file for configuration")
    du.argparser.add_argument("-nd", "--no-docker", help="omit docker comands", action="store_true")

    args = du.parse_args()

    # limit=0 -> specify path explicitly
    config = du.get_nearest_config(args.configfile)

    # ------------------------------------------------------------------------------------------------------------------
    print("find and render templates")
    # obsolete?

    local_deployment_files_base_dir = du.get_dir_of_this_file()
    general_base_dir = os.path.split(local_deployment_files_base_dir)[0]

    remote_url = config("url")
    remote_user = config("user")

    if not args.target == "remote":
        msg = "local deployment is currently not supported by this script"
        raise NotImplemented(msg)

    c = du.StateConnection(remote_url, user=remote_user, target=args.target)

    # ------------------------------------------------------------------------------------------------------------------
    c.cprint("stop running services (will fail in the first deployment-run)", target_spec="both")


    # this is the dir where subdirs ackrep_core, ackrep_data, etc live
    target_base_path = config('target_path')
    target_deployment_path = f"{target_base_path}/ackrep_deployment"
    target_core_path = f"{target_base_path}/ackrep_core"

    # this assumes that ackrep_deployment/docker-compose.yml is already on the server
    c.chdir(target_deployment_path)
    c.run(f"docker-compose stop ackrep-django", target_spec="both", printonly=args.no_docker)

    # ------------------------------------------------------------------------------------------------------------------
    # the following command assumes that all local repo-directories are in a desired state
    c.cprint("upload all deployment files", target_spec="remote")

    dirnames = ["ackrep_data", "ackrep_core", "ackrep_deployment"]
    for dirname in dirnames:

        # note: no trainling slash → upload the whole dir and keeping its name
        # thus the target path is always the same
        source_path = os.path.join(general_base_dir, dirname)
        c.rsync_upload(source_path, target_base_path, target_spec="remote")

    c.cprint("upload and rename configfile", target_spec="remote")
    c.rsync_upload(config.path, f"{target_base_path}/config.ini", target_spec="remote")

    # ------------------------------------------------------------------------------------------------------------------
    c.cprint("log the deployment date to file", target_spec="both")
    c.chdir(target_core_path)


    pycmd = "import time; print(time.strftime(r'%Y-%m-%d %H:%M:%S'))"
    c.run(f'''python3 -c "{pycmd}" > deployment_date.txt''', target_spec="remote")


    # ------------------------------------------------------------------------------------------------------------------
    c.cprint("rebuild and restart the services", target_spec="both")

    c.chdir(target_deployment_path)
    c.run(f"docker-compose build ackrep-django", target_spec="remote", printonly=args.no_docker)
    c.run(f"docker-compose up -d ackrep-django", target_spec="remote", printonly=args.no_docker)



if __name__ == "__main__":
    main()

