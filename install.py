#!/usr/bin/env python3
"""Interactive bootstrapper for the HRK storefront and admin panel.

Why this design:
- Keep onboarding in a single audited script with zero third-party dependencies.
- Prefer explicit prompts and defaults to minimise operator error.
- Fail gracefully with structured logs so provisioning can be automated.
"""

# Commit to intelligence. Push innovation. Pull results.

import argparse
from datetime import datetime, timezone
import getpass
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def log_event(level: str, message: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Emit structured logs to stdout."""
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        "meta": meta or {},
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


class Installer:
    def __init__(self, root: Path, args: argparse.Namespace) -> None:
        self.root = root
        self.args = args
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.actions: List[str] = []
        self.env_defaults = self._load_existing_env()

    # region public API
    def run(self) -> int:
        log_event("info", "installer_start", {"root": str(self.root)})
        config = self.collect_configuration()
        env_written = self.write_env(config)
        if env_written:
            self.actions.append(".env updated")
        self.provision_directories(config)
        self.bootstrap_admin_user(config)
        self.report()
        return 0 if not self.errors else 1

    # endregion

    # region configuration
    def collect_configuration(self) -> Dict[str, str]:
        log_event("info", "collect_configuration_start", {})
        defaults = {
            "HRK_ENVIRONMENT": self.env_defaults.get("HRK_ENVIRONMENT", "production"),
            "HRK_BASE_URL": self.env_defaults.get("HRK_BASE_URL", "http://localhost:4173"),
            "HRK_DATA_DIR": self.env_defaults.get("HRK_DATA_DIR", "data"),
            "HRK_UPLOADS_DIR": self.env_defaults.get("HRK_UPLOADS_DIR", "uploads"),
            "HRK_UPLOAD_IMAGES_DIR": self.env_defaults.get("HRK_UPLOAD_IMAGES_DIR", "uploads/images"),
            "HRK_UPLOAD_THUMBS_DIR": self.env_defaults.get("HRK_UPLOAD_THUMBS_DIR", "uploads/images/thumbs"),
            "HRK_UPLOAD_IMAGES_PUBLIC": self.env_defaults.get("HRK_UPLOAD_IMAGES_PUBLIC", "/uploads/images"),
            "HRK_UPLOAD_THUMBS_PUBLIC": self.env_defaults.get("HRK_UPLOAD_THUMBS_PUBLIC", "/uploads/images/thumbs"),
            "HRK_LOGS_DIR": self.env_defaults.get("HRK_LOGS_DIR", "logs"),
            "HRK_ADMIN_LOG": self.env_defaults.get("HRK_ADMIN_LOG", "logs/admin.log"),
        }

        config = {}
        config["HRK_ENVIRONMENT"] = self.ask_choice(
            "Ympäristö", ["production", "staging", "development"], defaults["HRK_ENVIRONMENT"],
        )
        config["HRK_BASE_URL"] = self.ask_string(
            "Sivuston perus-URL (https://example.com)", defaults["HRK_BASE_URL"], allow_empty=False
        )
        config["HRK_DATA_DIR"] = self.ask_path("Data-kansio", defaults["HRK_DATA_DIR"])
        config["HRK_UPLOADS_DIR"] = self.ask_path("Uploads-kansio", defaults["HRK_UPLOADS_DIR"])
        config["HRK_UPLOAD_IMAGES_DIR"] = self.ask_path(
            "Tuotekuvien kansio", defaults["HRK_UPLOAD_IMAGES_DIR"],
        )
        config["HRK_UPLOAD_THUMBS_DIR"] = self.ask_path(
            "Thumbnail-kansio", defaults["HRK_UPLOAD_THUMBS_DIR"]
        )
        config["HRK_UPLOAD_IMAGES_PUBLIC"] = self.ask_string(
            "Tuotekuvien julkinen polku", defaults["HRK_UPLOAD_IMAGES_PUBLIC"], allow_empty=False
        )
        config["HRK_UPLOAD_THUMBS_PUBLIC"] = self.ask_string(
            "Thumbnailien julkinen polku", defaults["HRK_UPLOAD_THUMBS_PUBLIC"], allow_empty=False
        )
        config["HRK_LOGS_DIR"] = self.ask_path("Logikansio", defaults["HRK_LOGS_DIR"])
        config["HRK_ADMIN_LOG"] = self.ask_path("Admin-logi", defaults["HRK_ADMIN_LOG"], expect_file=True)
        log_event("info", "collect_configuration_complete", {"config": config})
        return config

    # endregion

    # region env persistence
    def write_env(self, config: Dict[str, str]) -> bool:
        env_path = self.root / ".env"
        lines = [f"{key}={self.format_env_value(value)}" for key, value in sorted(config.items())]
        content = "\n".join(lines) + "\n"
        try:
            if env_path.exists():
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
                backup = env_path.with_suffix(env_path.suffix + f".bak-{timestamp}")
                backup.write_text(env_path.read_text(encoding="utf-8"), encoding="utf-8")
                self.actions.append(f".env varmuuskopioitu -> {backup.name}")
            env_path.write_text(content, encoding="utf-8")
            log_event("info", "env_written", {"path": str(env_path)})
            return True
        except Exception as exc:  # noqa: BLE001
            self.errors.append(f".env kirjoitus epäonnistui: {exc}")
            log_event("error", "env_write_failed", {"error": str(exc)})
            return False

    @staticmethod
    def format_env_value(value: str) -> str:
        if any(ch.isspace() for ch in value.strip()) or "#" in value or "=" in value:
            escaped = value.replace("\n", " ").strip()
            return f'"{escaped}"'
        return value.strip()

    def _load_existing_env(self) -> Dict[str, str]:
        env_path = self.root / ".env"
        if not env_path.exists():
            return {}
        result: Dict[str, str] = {}
        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            value = value.strip().strip("'\"")
            result[key.strip()] = value
        return result

    # endregion

    # region provisioning
    def provision_directories(self, config: Dict[str, str]) -> None:
        targets = {
            "data": self.resolve_path(config["HRK_DATA_DIR"]),
            "uploads": self.resolve_path(config["HRK_UPLOADS_DIR"]),
            "images": self.resolve_path(config["HRK_UPLOAD_IMAGES_DIR"]),
            "thumbs": self.resolve_path(config["HRK_UPLOAD_THUMBS_DIR"]),
            "logs": self.resolve_path(config["HRK_LOGS_DIR"]),
        }
        for label, path in targets.items():
            self.ensure_directory(label, path)

        admin_log = self.resolve_path(config["HRK_ADMIN_LOG"])
        try:
            if not admin_log.exists():
                admin_log.touch(exist_ok=True)
            self.actions.append(f"{admin_log} varmistettu")
        except Exception as exc:  # noqa: BLE001
            self.errors.append(f"Admin-logia ei voitu luoda ({admin_log}): {exc}")
            log_event("error", "admin_log_failed", {"error": str(exc), "path": str(admin_log)})

    def ensure_directory(self, label: str, path: Path) -> None:
        try:
            path.mkdir(parents=True, exist_ok=True)
            try:
                os.chmod(path, 0o750)
            except PermissionError:
                self.warnings.append(f"chmod epäonnistui {path}")
            self.actions.append(f"{label}-kansio varmistettu -> {path}")
        except Exception as exc:  # noqa: BLE001
            self.errors.append(f"Kansiota {path} ei voitu luoda: {exc}")
            log_event("error", "directory_failed", {"error": str(exc), "path": str(path)})

    # endregion

    # region admin user
    def bootstrap_admin_user(self, config: Dict[str, str]) -> None:
        if self.args.skip_admin:
            log_event("info", "skip_admin_user", {})
            return

        data_dir = self.resolve_path(config["HRK_DATA_DIR"])
        users_file = data_dir / "users.json"
        existing_users = self.load_json(users_file)

        default_username = self.args.admin_username or "admin"
        username = self.ask_string("Admin-käyttäjänimi", default_username, allow_empty=False)

        target = next((user for user in existing_users if user.get("username") == username), None)
        if target and not self.confirm(
            f"Käyttäjä {username} on jo olemassa. Päivitetäänkö salasana?", default=True
        ):
            log_event("info", "admin_user_skipped", {"username": username})
            return

        password = self.obtain_password()
        if password is None:
            self.warnings.append("Salasanaa ei asetettu – käytä admin-paneelia luodaksesi tunnuksen.")
            return

        password_hash = self.hash_password(password)
        if not password_hash:
            self.errors.append("Salasanaa ei voitu hashoida. PHP CLI vaaditaan.")
            return

        user_payload = {
            "id": target.get("id") if target else f"u-{secrets.token_hex(4)}",
            "username": username,
            "passwordhash": password_hash,
            "role": target.get("role", "admin") if target else "admin",
            "created_at": target.get("created_at", datetime.now(timezone.utc).isoformat()),
        }

        if target:
            for index, user in enumerate(existing_users):
                if user.get("username") == username:
                    existing_users[index] = user_payload
                    break
        else:
            existing_users.append(user_payload)

        if self.write_json(users_file, existing_users):
            action = "päivitetty" if target else "luotu"
            self.actions.append(f"Admin-käyttäjä {action}: {username}")
            log_event("info", "admin_user_written", {"username": username, "action": action})
        else:
            self.errors.append("Admin-käyttäjää ei voitu kirjoittaa JSONiin.")

    def obtain_password(self) -> Optional[str]:
        if self.args.admin_password:
            pwd = self.args.admin_password.strip()
            if len(pwd) < 12:
                self.errors.append("Komentoriviltä annettu salasana on liian lyhyt (min 12 merkkiä).")
                return None
            return pwd

        if self.args.defaults:
            self.warnings.append("Oletusajossa salasanaa ei asetettu.")
            return None

        for _ in range(3):
            try:
                first = getpass.getpass("Salasana (min 12 merkkiä): ")
                second = getpass.getpass("Toista salasana: ")
            except (EOFError, KeyboardInterrupt):
                self.warnings.append("Salasanan syöttö keskeytettiin.")
                return None

            if len(first) < 12:
                print("Salasanan tulee olla vähintään 12 merkkiä.")
                continue
            if first != second:
                print("Salasanat eivät täsmää.")
                continue
            return first
        self.errors.append("Salasanan asetus epäonnistui (liian monta yritystä).")
        return None

    def hash_password(self, password: str) -> Optional[str]:
        php_path = self.args.php or self.env_defaults.get("PHP_PATH") or self.detect_php()
        if not php_path:
            self.warnings.append("PHP CLI ei löytynyt polusta. Jätä salasana tyhjäksi ja luo käyttäjä myöhemmin.")
            return None

        command = [php_path, "-r", "echo password_hash(getenv('HRK_INSTALL_PASSWORD'), PASSWORD_DEFAULT);"]
        env = os.environ.copy()
        env["HRK_INSTALL_PASSWORD"] = password
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False, env=env)  # noqa: S603
        except Exception as exc:  # noqa: BLE001
            self.errors.append(f"PHP CLI -kutsu epäonnistui: {exc}")
            return None
        finally:
            env["HRK_INSTALL_PASSWORD"] = ""

        if result.returncode != 0:
            self.errors.append(f"PHP CLI palautti virheen: {result.stderr.strip()}")
            return None

        hashed = result.stdout.strip()
        if not hashed:
            self.errors.append("PHP CLI ei palauttanut hashia.")
            return None
        return hashed

    def load_json(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw) if raw.strip() else []
            if isinstance(data, list):
                return data
        except Exception as exc:  # noqa: BLE001
            self.errors.append(f"JSONin luku epäonnistui ({path}): {exc}")
        return []

    def write_json(self, path: Path, payload: List[Dict[str, Any]]) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = path.with_suffix(path.suffix + ".tmp")
            tmp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            tmp_path.replace(path)
            return True
        except Exception as exc:  # noqa: BLE001
            self.errors.append(f"JSONin kirjoitus epäonnistui ({path}): {exc}")
            log_event("error", "json_write_failed", {"path": str(path), "error": str(exc)})
            return False

    # endregion

    # region helpers
    def ask_choice(self, prompt: str, options: List[str], default: str) -> str:
        if self.args.defaults:
            return default
        prompt_line = f"{prompt} {options} [{default}]: "
        while True:
            try:
                answer = input(prompt_line).strip()
            except (EOFError, KeyboardInterrupt):
                log_event("warning", "choice_prompt_interrupted", {"prompt": prompt})
                return default
            if answer == "":
                return default
            if answer in options:
                return answer
            print(f"Valitse jokin vaihtoehdoista: {options}")

    def ask_string(self, prompt: str, default: str, allow_empty: bool) -> str:
        if self.args.defaults and default:
            return default
        prompt_line = f"{prompt} [{default}]: "
        while True:
            try:
                answer = input(prompt_line).strip()
            except (EOFError, KeyboardInterrupt):
                log_event("warning", "string_prompt_interrupted", {"prompt": prompt})
                return default
            if answer == "":
                if default != "" or allow_empty:
                    return default
                print("Arvo ei voi olla tyhjä.")
                continue
            return answer

    def ask_path(self, prompt: str, default: str, expect_file: bool = False) -> str:
        value = self.ask_string(prompt, default, allow_empty=False)
        if expect_file:
            return value
        return value.rstrip("/")

    def confirm(self, prompt: str, default: bool = True) -> bool:
        if self.args.defaults:
            return default
        suffix = "[Y/n]" if default else "[y/N]"
        while True:
            try:
                answer = input(f"{prompt} {suffix} ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                log_event("warning", "confirm_prompt_interrupted", {"prompt": prompt})
                return default
            if answer == "":
                return default
            if answer in {"y", "yes", "k", "kyllä"}:
                return True
            if answer in {"n", "no", "e", "ei"}:
                return False
            print("Vastaa kyllä tai ei.")

    def resolve_path(self, value: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = self.root / value
        return path.resolve()

    def detect_php(self) -> Optional[str]:
        from shutil import which

        return which("php")

    def report(self) -> None:
        summary = {
            "actions": self.actions,
            "warnings": self.warnings,
            "errors": self.errors,
        }
        log_event("info", "installer_summary", summary)
        if self.errors:
            print("\nAsennus päättyi virheisiin. Tarkista yllä olevat lokit.")
        else:
            print("\nAsennus valmis. Voit kirjautua admin-paneeliin heti.")
        if self.warnings:
            print("Varoitukset:")
            for warning in self.warnings:
                print(f" - {warning}")

    # endregion


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HRK installer")
    parser.add_argument("--defaults", action="store_true", help="Käytä oletuksia ilman vuorovaikutusta")
    parser.add_argument("--skip-admin", action="store_true", help="Älä luo tai päivitä admin-käyttäjää")
    parser.add_argument("--admin-username", help="Pakota admin-käyttäjänimi")
    parser.add_argument("--admin-password", help="Pakota admin-salasana (min 12 merkkiä)")
    parser.add_argument("--php", help="Polku PHP CLI:hin")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent
    installer = Installer(root, args)
    try:
        return installer.run()
    except Exception as exc:  # noqa: BLE001
        log_event("critical", "installer_crash", {"error": str(exc)})
        print("Odottamaton virhe:", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
