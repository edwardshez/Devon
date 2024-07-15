import subprocess

from devon_agent.config import Config


class GitVersioning:
    def __init__(self, project_path, config : Config):
        self.project_path = project_path
        self.config = config

    def check_git_installation(self):
        if self.config.versioning_type == "none":
            return True
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            return True
        except FileNotFoundError:
            return False

    def initialize_git(self):
        if self.config.versioning_type == "none":
            return
        if not self.check_git_installation():
            print("Git is not installed. Attempting to install...")
            # self.install_git()
            raise Exception("Git is not installed")

        # Check if the current directory is already a Git repository
        try:
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.project_path,
                check=True,
                capture_output=True,
                text=True,
            )
            print(
                "This directory is already a Git repository. Skipping initialization."
            )
            return
        except subprocess.CalledProcessError:
            # If the command fails, it means this is not a Git repository
            subprocess.run(["git", "init"], cwd=self.project_path, check=True)
            print("Git repository initialized successfully.")

    def get_branch(self):
        if self.config.versioning_type == "none":
            return "none"

        result = subprocess.run(
            ["git", "branch", "--show-current"],
        cwd=self.project_path,
        capture_output=True,
        text=True,
        check=True,
        )
        return result.stdout


    def commit_all_files(self, message="Initial commit"):
        if self.config.versioning_type == "none":
            return True, "none"
        res =subprocess.run(["git", "add", "."], cwd=self.project_path)
        if res.returncode != 0:
            print("git add failed")
            # print(res.stdout if res.stdout else "" + res.stderr if res.stderr else "")
            return False, res.stdout if res.stdout else "" + res.stderr if res.stderr else ""
        res = subprocess.run(
            ["git", "commit", "-m", message], cwd=self.project_path
        )

        # return  commit hash

        if res.returncode != 0:
            print("git commit failed")
            # if "nothing to commit, working tree clean" in res.stderr:
            #     return True, "nothing to commit, working tree clean"
            # print(res.stdout if res.stdout else "" + res.stderr if res.stderr else "")
            return False,  res.stdout if res.stdout else "" + res.stderr if res.stderr else ""
        
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.project_path, capture_output=True, text=True, check=True)
        return True, res.stdout.strip()
    
    def initial_commit(self):
        if self.config.versioning_type == "none":
            return True, "none"
        # check if previous commit is "initial commit"
        res = subprocess.run(["git", "log", "-1", "--pretty=%B"], cwd=self.project_path, capture_output=True, text=True, check=True)
        if  res.stdout.strip() == "initial commit":
            # return commit hash
            res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.project_path, capture_output=True, text=True, check=True)
            return True, res.stdout.strip()
        
        res =subprocess.run(["git", "add", "."], cwd=self.project_path)
        if res.returncode != 0:
            print("git add failed")
            # print(res.stdout if res.stdout else "" + res.stderr if res.stderr else "")
            return False, res.stdout if res.stdout else "" + res.stderr if res.stderr else ""
        
        res = subprocess.run(
            ["git", "commit", "-m", "initial commit", "--allow-empty"], cwd=self.project_path
        )

        if res.returncode != 0:
            print("git commit failed")
            # if "nothing to commit, working tree clean" in res.stderr:
            #     return True, "nothing to commit, working tree clean"
            # print(res.stdout if res.stdout else "" + res.stderr if res.stderr else "")
            return False,  res.stdout if res.stdout else "" + res.stderr if res.stderr else ""
        
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.project_path, capture_output=True, text=True, check=True)
        return True, res.stdout.strip()
        


    def commit_changes(self, message):
        if self.config.versioning_type == "none":
            return True, "none"
        subprocess.run(
            ["git", "commit", "-am", message], cwd=self.project_path, check=True
        )

    def get_diff_patch(self,commit_hash_src, commit_hash_dst):
        if self.config.versioning_type == "none":
            return "none"
        res = subprocess.run(["git", "diff", commit_hash_src, commit_hash_dst], cwd=self.project_path, capture_output=True, text=True, check=True)
        return res.stdout
    
    def apply_patch(self,patch):
        if self.config.versioning_type == "none":
            return True, "none"
        res = subprocess.run(["git", "apply", patch], cwd=self.project_path, capture_output=True, text=True, check=True)
        return res.returncode == 0, res.stdout if res.stdout else "" + res.stderr if res.stderr else ""

    def list_commits(self):
        if self.config.versioning_type == "none":
            return "none"
        result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=self.project_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def revert_to_commit(self, commit_hash):
        if self.config.versioning_type == "none":
            return
        subprocess.run(
            ["git", "checkout", commit_hash], cwd=self.project_path, check=True
        )

    def create_branch(self, branch_name):
        if self.config.versioning_type == "none":
            return
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=self.project_path, check=True)

    def switch_branch(self, branch_name):
        if self.config.versioning_type == "none":
            return
        subprocess.run(
            ["git", "checkout", branch_name], cwd=self.project_path, check=True
        )

    def merge_branch(self, branch_name):
        if self.config.versioning_type == "none":
            return
        subprocess.run(["git", "merge", branch_name], cwd=self.project_path, check=True)

    def check_branch_exists(self, branch_name):
        if self.config.versioning_type == "none":
            return True
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--verify", branch_name],
                cwd=self.project_path,
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def create_if_not_exists_and_checkout_branch(self, branch_name):
        if self.config.versioning_type == "none":
            return
        print(self.get_branch(),branch_name)
        if self.get_branch().strip() == branch_name:
            print("Branch already exists")
            return
        print('im here', self.check_branch_exists(branch_name))
        if not self.check_branch_exists(branch_name):
            self.create_branch(branch_name)
        try:
            old_branch = self.get_branch()
            self.checkout_branch(branch_name)
            self.merge_branch(old_branch)
            print(f"Created and checked out new branch: {branch_name}")
        except Exception as e:
            print(f"Error checking out branch: {branch_name}")
            raise e

    def delete_branch(self, branch_name):
        if self.config.versioning_type == "none":
            return
        subprocess.run(["git", "branch", "-d", branch_name], cwd=self.project_path, check=True)

    def get_branch_name(self):
        if self.config.versioning_type == "none":
            return "none"
        return "devon_agent"
    
    def checkout_branch(self, branch_name):
        if self.config.versioning_type == "none":
            return
        subprocess.run(["git", "checkout", branch_name], cwd=self.project_path, check=True)
        self.current_branch = branch_name
        

