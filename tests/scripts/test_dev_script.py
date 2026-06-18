from __future__ import annotations

import os
import subprocess
from pathlib import Path


def run_dev_script(
    *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "dev.sh", *args],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )


def test_dev_script_without_arguments_prints_usage() -> None:
    result = run_dev_script()

    assert result.returncode == 0
    assert "사용법" in result.stdout
    assert "infra start" in result.stdout
    assert "app start" in result.stdout


def test_dev_script_status_lists_infra_and_app_units() -> None:
    result = run_dev_script("status")

    assert result.returncode == 0
    assert "infra" in result.stdout
    assert "postgres" in result.stdout
    assert "app" in result.stdout
    assert "api" in result.stdout
    assert "web" in result.stdout
    assert "worker" in result.stdout


def test_dev_script_rejects_unknown_command() -> None:
    result = run_dev_script("unknown")

    assert result.returncode != 0
    assert "사용법" in result.stdout


def test_dev_script_loads_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("GOODMONEYING_API_PORT=19000\nGOODMONEYING_WEB_PORT=19001\n")
    env = os.environ.copy()
    env["GOODMONEYING_ENV_FILE"] = str(env_file)

    result = run_dev_script("app", "status", env=env)

    assert result.returncode == 0
    assert "endpoint=http://127.0.0.1:19000" in result.stdout
    assert "endpoint=http://127.0.0.1:19001/" in result.stdout


def test_dev_script_shell_environment_overrides_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("GOODMONEYING_API_PORT=19000\n")
    env = os.environ.copy()
    env["GOODMONEYING_ENV_FILE"] = str(env_file)
    env["GOODMONEYING_API_PORT"] = "19100"

    result = run_dev_script("app", "status", "api", env=env)

    assert result.returncode == 0
    assert "endpoint=http://127.0.0.1:19100" in result.stdout
