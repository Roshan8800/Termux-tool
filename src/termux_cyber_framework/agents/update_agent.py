import subprocess
import datetime
from termux_cyber_framework.core.use_cases.ports import LoggerPort, LogLevel, AuditLoggerPort

class UpdateAgent:
    """
    An agent responsible for checking for and applying updates to the framework
    and its tools.
    """
    def __init__(self, logger: LoggerPort, audit_logger: AuditLoggerPort):
        self.logger = logger
        self.audit_logger = audit_logger

    def _get_current_commit(self) -> str:
        """Returns the current git commit hash."""
        try:
            return subprocess.run(
                ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
            ).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"

    def check_framework_update(self) -> bool:
        """
        Checks if the local git repository is behind the remote.
        """
        self.logger.log("Checking for framework updates...", level=LogLevel.INFO)
        try:
            subprocess.run(["git", "fetch"], check=True, capture_output=True, text=True, timeout=60)
            local_hash = self._get_current_commit()
            remote_hash = subprocess.run(
                ["git", "rev-parse", "@{u}"], check=True, capture_output=True, text=True
            ).stdout.strip()

            if local_hash != remote_hash:
                self.logger.log(f"Framework update available. Local: {local_hash[:7]}, Remote: {remote_hash[:7]}", level=LogLevel.INFO)
                return True
            else:
                self.logger.log("Framework is up to date.", level=LogLevel.INFO)
                return False
        except FileNotFoundError:
            self.logger.log("`git` command not found. Cannot check for updates.", level=LogLevel.ERROR)
            return False
        except subprocess.CalledProcessError as e:
            if "no upstream configured" in e.stderr:
                self.logger.log("No upstream branch configured. Cannot check for updates.", level=LogLevel.WARNING)
            else:
                self.logger.log(f"Error checking for framework updates: {e.stderr}", level=LogLevel.ERROR)
            return False

    def _rollback_framework(self, commit_hash: str):
        """Rolls the framework back to a specific commit hash."""
        self.logger.log(f"Attempting to roll back to previous state: {commit_hash[:7]}...", level=LogLevel.WARNING)
        try:
            subprocess.run(["git", "reset", "--hard", commit_hash], check=True, capture_output=True, text=True)
            self.logger.log("Rollback successful. Please check the application state.", level=LogLevel.INFO)
        except subprocess.CalledProcessError as e:
            self.logger.log(f"CRITICAL: Rollback failed! The repository may be in an unstable state. Error: {e.stderr}", level=LogLevel.ERROR)

    def apply_framework_update(self) -> bool:
        """
        Applies updates to the framework by pulling the latest changes
        and running the install script.
        """
        self.logger.log("Applying framework update...", level=LogLevel.INFO)
        before_hash = self._get_current_commit()
        if before_hash == "unknown":
            self.logger.log("Could not get current commit hash. Cannot proceed with safe update.", level=LogLevel.ERROR)
            return False

        try:
            subprocess.run(["git", "pull"], check=True, capture_output=True, text=True, timeout=120)
            subprocess.run(["bash", "install.sh"], check=True, capture_output=True, text=True, timeout=300)

            after_hash = self._get_current_commit()
            self.logger.log("Framework update applied successfully. Please restart the framework.", level=LogLevel.INFO)
            self.audit_logger.append({
                "component": "framework", "old_version": before_hash, "new_version": after_hash,
                "status": "success", "timestamp": datetime.datetime.now().isoformat()
            })
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.log(f"Failed to apply framework update. Error: {getattr(e, 'stderr', str(e))}", level=LogLevel.ERROR)
            self._rollback_framework(before_hash)
            self.audit_logger.append({
                "component": "framework", "old_version": before_hash, "new_version": "rollback_attempted",
                "status": "failure", "error": getattr(e, 'stderr', str(e)), "timestamp": datetime.datetime.now().isoformat()
            })
            return False

    def check_tool_updates(self) -> dict:
        """
        Checks for available updates for pkg and pip packages.
        """
        self.logger.log("Checking for tool and dependency updates...", level=LogLevel.INFO)
        updates = {"pkg": False, "pip": []}
        try:
            subprocess.run(["pkg", "update"], check=True, capture_output=True, text=True, timeout=120)
            updates["pkg"] = True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.log(f"Could not check for pkg updates: {e}", level=LogLevel.WARNING)

        try:
            result = subprocess.run(
                ["pip", "list", "--outdated"], check=True, capture_output=True, text=True, timeout=120
            )
            lines = result.stdout.strip().split('\n')[2:]
            updates["pip"] = [line.split()[0] for line in lines]
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.log(f"Could not check for pip updates: {e}", level=LogLevel.WARNING)

        return updates

    def apply_tool_updates(self, pip_packages: list[str]) -> bool:
        """
        Applies updates for system packages (pkg) and specified pip packages.
        """
        self.logger.log("Applying tool and dependency updates...", level=LogLevel.INFO)
        all_successful = True

        try:
            subprocess.run(["pkg", "upgrade", "-y"], check=True, capture_output=True, text=True, timeout=600)
            self.logger.log("System packages upgraded successfully.", level=LogLevel.INFO)
            self.audit_logger.append({"component": "pkg", "status": "success", "timestamp": datetime.datetime.now().isoformat()})
        except (subprocess.CalledProcessError) as e:
            self.logger.log(f"Failed to upgrade system packages: {e.stderr}", level=LogLevel.ERROR)
            self.audit_logger.append({"component": "pkg", "status": "failure", "error": e.stderr, "timestamp": datetime.datetime.now().isoformat()})
            all_successful = False
        except FileNotFoundError:
            self.logger.log("`pkg` command not found. Cannot upgrade system packages.", level=LogLevel.ERROR)
            all_successful = False

        if pip_packages:
            try:
                subprocess.run(
                    ["pip", "install", "--upgrade", "--no-cache-dir"] + pip_packages,
                    check=True, capture_output=True, text=True, timeout=600
                )
                self.logger.log("Pip packages upgraded successfully.", level=LogLevel.INFO)
                self.audit_logger.append({"component": "pip", "updated_packages": pip_packages, "status": "success", "timestamp": datetime.datetime.now().isoformat()})
            except (subprocess.CalledProcessError) as e:
                self.logger.log(f"Failed to upgrade pip packages: {e.stderr}", level=LogLevel.ERROR)
                self.audit_logger.append({"component": "pip", "updated_packages": pip_packages, "status": "failure", "error": e.stderr, "timestamp": datetime.datetime.now().isoformat()})
                all_successful = False
            except FileNotFoundError:
                self.logger.log("`pip` command not found. Cannot upgrade pip packages.", level=LogLevel.ERROR)
                all_successful = False

        return all_successful
