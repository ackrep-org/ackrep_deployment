"""
This script does the following:
- load specified config*.ini
- stop remote services
- upload all files to the server
- create `deployment_date.txt`
- restart remote services


unlock sshkey for 10 minutes
eval $(ssh-agent); ssh-add -t 10m

working command:
python deploy.py remote ../ackrep_deployment_config/config_testing2.ini
"""

from math import fabs
import sys
import os
import argparse
import yaml
import deploymentutils as du
import time
import yaml

from ipydex import IPS, activate_ips_on_exception

activate_ips_on_exception()


def check_config_consistency(args):
    """
    some values are specified in multiple locations (config.ini, docker-compose.yml).

    This function checks if the values are consistent
    """
    config = du.get_nearest_config(args.configfile)
    with open("docker-compose.yml") as fp:
        dc_dict = yaml.safe_load(fp)
    labels = dc_dict["services"]["ackrep-django"]["labels"]
    key_str = "traefik.http.routers.ackrep-django.rule"
    relevant_label = [l for l in labels if l.startswith(key_str)][0]
    #e.g.: 'traefik.http.routers.ackrep-django.rule=Host(`testing.ackrep.org`)'
    part = relevant_label.split("=")[-1]
    assert part.startswith("Host(`") and part.endswith("`)")
    dc_domain = part[6:-2]

    msg = "Domains from config file and docker-compose (traefik label) do not match. Abort"
    assert dc_domain == config.get("url"), msg


def get_args():
    du.argparser.add_argument("configfile", help="path to .ini-file for configuration")
    du.argparser.add_argument("-nd", "--no-docker", help="omit docker comands", action="store_true")
    du.argparser.add_argument("--devserver", help="run development server instead", action="store_true")

    args = du.parse_args()
    return args


def main(args):


    # limit=0 -> specify path explicitly
    config = du.get_nearest_config(args.configfile)
    run_devserver = args.devserver

    # ------------------------------------------------------------------------------------------------------------------

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


    # see README.md for the assumed directory structure
    # this is the dir where subdirs ackrep_core, ackrep_data, etc live
    target_base_path = config('target_path')

    ackrep_target_path = f"{target_base_path}/ackrep"
    target_deployment_path = f"{ackrep_target_path}/ackrep_deployment"
    target_core_path = f"{ackrep_target_path}/ackrep_core"

    c.run(f"mkdir -p {target_deployment_path}")
    c.chdir(target_deployment_path)
    # this assumes that ackrep_deployment/docker-compose.yml is already on the server
    res = c.run(f"docker ps -f name=ackrep-django -q", target_spec="both", printonly=args.no_docker)
    if len(res.stdout) > 0:
        ids = res.stdout.replace("\n", " ")
        c.run(f"docker stop {ids}", target_spec="both", printonly=args.no_docker)

    # ------------------------------------------------------------------------------------------------------------------
    # the following command assumes that all local repo-directories are in a desired state
    c.cprint("upload all deployment files", target_spec="remote")

    dirnames = ["ackrep_data", "ackrep_core", "ackrep_deployment"]
    filters = "--exclude='**/acme.json'"
    c.run(f"mkdir -p {ackrep_target_path}")
    for dirname in dirnames:

        # note: no trainling slash → upload the whole dir and keeping its name
        # thus the target path is always the same
        source_path = os.path.join(general_base_dir, dirname)
        c.rsync_upload(source_path, ackrep_target_path, filters=filters, target_spec="remote")

    c.cprint("upload all pyerk files", target_spec="remote")
    # upload all erk repos
    dirnames = ["pyerk-core", "erk-data", "pyerk-django"]

    erk_target_path = f"{target_base_path}/erk"
    c.run(f"mkdir -p {erk_target_path}")

    for dirname in dirnames:

        # note: no trainling slash → upload the whole dir and keeping its name
        # thus the target path is always the same
        source_path = os.path.join(general_base_dir, os.pardir, "erk", dirname)
        c.rsync_upload(source_path, erk_target_path, target_spec="remote")

    c.cprint("upload and rename configfile", target_spec="remote")
    c.rsync_upload(config.path, f"{ackrep_target_path}/config.ini", target_spec="remote")

    # ------------------------------------------------------------------------------------------------------------------
    c.cprint("log the deployment date to file", target_spec="both")
    c.chdir(target_core_path)


    pycmd = "import time; print(time.strftime(r'%Y-%m-%d %H:%M:%S'))"
    c.run(f'''python3 -c "{pycmd}" > deployment_date.txt''', target_spec="remote")


    # ------------------------------------------------------------------------------------------------------------------
    c.cprint("rebuild and restart the services", target_spec="both")

    c.chdir(target_deployment_path)
    c.run(f"docker-compose build ackrep-django", target_spec="remote", printonly=args.no_docker)
    if run_devserver:
        print("now run:\ndocker-compose run -p 8000:8000 ackrep-django python3 manage.py runserver 0.0.0.0:8000\nin ssh shell")
    else:
        c.run(f"docker-compose up -d ackrep-django", target_spec="remote", printonly=args.no_docker)



if __name__ == "__main__":
    args = get_args()
    check_config_consistency(args)
    # main(args)

"""
python deploy.py remote ../ackrep_deployment_config/config_testing2.ini
"""
