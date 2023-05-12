import os
from datetime import datetime
import git
import yaml
import time


class DeploymentReportManager:
    """
    This class generates a textfile to archive useful information at deployment time, mostly the state of relevant
    git repositories.
    """
    def __init__(self, root_path: str, config):
        self.root_path = root_path
        self.config = config
        self.url = config.get("url")
        self.report_items = []
        self.get_repo_report_items(self.root_path)
        self.report_items.sort()

    def get_dirty_repos(self):
        res = [path for path, report_dict in self.report_items if report_dict["dirty"]]
        return res

    def generate_report(self, report_dir_path):

        head = f"Deployment at {self.url} ({time.strftime('%Y-%m-%d %H:%M:%S')})\n\n"

        os.makedirs(report_dir_path, exist_ok=True)
        report_path = os.path.join(report_dir_path, "deployment-report.txt")

        repo_info = dict(self.report_items)

        txt = "\n".join([head, yaml.safe_dump(repo_info)]).replace("\n./", "\n\n./")

        with open(report_path, "w") as fp:
            fp.write(txt)
        print(f"report written: {report_path}")

    def get_repo_report_items(self, start_path):

        for subdir in os.listdir(start_path):
            path = os.path.join(start_path, subdir)
            if os.path.isdir(path):
                res = self.get_repo_info(path)
                if res is None:
                    self.get_repo_report_items(path)
                else:
                    key = path.replace(self.root_path, ".")
                    self.report_items.append((key, res))

        return self.report_items

    @staticmethod
    def get_repo_info(repo_path):
        try:
            repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
                return None
        branch = repo.active_branch.name
        last_commit_hash = repo.git.rev_parse("HEAD", short=True)
        last_commit_timestamp = repo.head.commit.committed_date
        last_commit_datetime = datetime.fromtimestamp(last_commit_timestamp)
        timestamp_formatted = last_commit_datetime.strftime("%Y-%m-%d %H:%M:%S")

        status = repo.git.status()
        modified_files = status.count("modified")
        added_files = status.count("new file")
        deleted_files = status.count("deleted")
        res = {
            "branch": branch,
            "last_commit_timestamp": timestamp_formatted,
            "last_commit_hash": last_commit_hash,
            "modified_files": modified_files,
            "dirty": repo.is_dirty(),
            # "added_files": added_files,
            # "deleted_files": deleted_files,
        }

        return res
