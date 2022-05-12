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

mod_path = os.path.dirname(os.path.abspath(__file__))
core_mod_path = os.path.join(mod_path, "..", "ackrep_core")
sys.path.insert(0, core_mod_path)
from ackrep_core import core


rendered_template_list = []


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("settingsfile", help=".yml-file for settings")
    argparser.add_argument("-nd", "--no-docker", help="omit docker comands", action="store_true")

    args = argparser.parse_args()

    with open(args.settingsfile) as f:
        settings = yaml.load(f, Loader=yaml.FullLoader)

    # ------------------------------------------------------------------------------------------------------------------
    print("find and render templates")
    res = find_and_render_templates(settings)
    rendered_template_list.extend(res)

    local_deployment_files_base_dir = du.get_dir_of_this_file()
    general_base_dir = os.path.split(local_deployment_files_base_dir)[0]

    remote = settings["type"] == "remote"
    local = not remote

    c = du.StateConnection(settings["url"], user=settings["user"], target=settings["type"])

    # ------------------------------------------------------------------------------------------------------------------
    c.cprint("stop running services (this might fail in the first run)", target_spec="both")

    # we do not use os.path.join here because the target platform is unix but the host platform should be flexible
    if local:
        # use path-separation for local OS
        path_sep = os.path.sep
    else:
        # remote OS is unix. -> use slash
        path_sep = "/"

    target_deployment_path = f"{settings['target_path']}{path_sep}ackrep_deployment"
    # 1/0

    c.chdir(target_deployment_path)
    c.run(f"docker-compose stop ackrep-django", target_spec="both", printonly=args.no_docker)

    # ------------------------------------------------------------------------------------------------------------------
    c.cprint("upload all deployment files", target_spec="remote")
    source_path = general_base_dir+os.path.sep
    c.rsync_upload(source_path, settings["target_path"], target_spec="remote", printonly=False)

    # ------------------------------------------------------------------------------------------------------------------
    c.cprint("rebuild and restart the services", target_spec="both")
    target_deployment_path = f"{settings['target_path']}/ackrep_deployment"
    c.chdir(target_deployment_path)

    if remote:
        # rebuild the ackrep-container (not the reverse proxy)
        c.run(f"docker-compose build ackrep-django", target_spec="remote", printonly=args.no_docker)
        c.run(f"docker-compose up -d ackrep-django", target_spec="remote", printonly=args.no_docker)
        # c.run(f"docker-compose up -d --build", target_spec="remote", printonly=args.no_docker)
    else:
        c.run(f"docker-compose up -d --build ackrep-django", target_spec="local", printonly=args.no_docker)


def find_and_render_templates(settings_dict):
    """
    Assume that the settings_dict specifies different key-value-pairs for different target files.
    Each target files is specified by a `template`.
    """

    # create a dict like {"template1.conf": {"value1": "abc", "value2": 10}, ...}
    template_settings_mapping = dict()

    for value in settings_dict.values():
        if not isinstance(value, dict):
            continue

        template = value.get("template")

        # load settings for this template
        ts_settings = value.get("settings")
        if template is not None:
            assert isinstance(ts_settings, dict)
            template_settings_mapping[template] = ts_settings

    # now render these templates
    results = []
    base_path = mod_path

    # make the rendering time available in the template-render-result
    date_string = f'{time.strftime("%Y-%m-%d %H:%M:%S")} ({core.settings.TIME_ZONE})'

    for template, settings in template_settings_mapping.items():
        context = dict(settings=settings, date_string=date_string)
        res = core.render_template(template, context=context, special_str=".template", base_path=base_path)
        results.append(res)

    return results


if __name__ == "__main__":
    main()
