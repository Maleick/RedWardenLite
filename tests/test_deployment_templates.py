from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SYSTEMD_TEMPLATE = REPO_ROOT / "deploy" / "systemd" / "redwardenlite.service"
DOCKERFILE_TEMPLATE = REPO_ROOT / "deploy" / "container" / "Dockerfile"
COMPOSE_TEMPLATE = REPO_ROOT / "deploy" / "container" / "docker-compose.yml"
RUNBOOK_FILE = REPO_ROOT / "docs" / "deployment-templates.md"


def test_deployment_template_files_exist():
    assert SYSTEMD_TEMPLATE.exists()
    assert DOCKERFILE_TEMPLATE.exists()
    assert COMPOSE_TEMPLATE.exists()
    assert RUNBOOK_FILE.exists()


def test_systemd_template_contains_required_directives():
    content = SYSTEMD_TEMPLATE.read_text(encoding="utf-8")

    assert "[Unit]" in content
    assert "[Service]" in content
    assert "ExecStart=" in content
    assert "--config /etc/redwardenlite/config.yaml" in content
    assert "Restart=on-failure" in content


def test_dockerfile_template_has_expected_runtime_command():
    content = DOCKERFILE_TEMPLATE.read_text(encoding="utf-8")

    assert "FROM python:" in content
    assert "WORKDIR /opt/RedWardenLite" in content
    assert "requirements.txt" in content
    assert "CMD [\"python\", \"RedWardenLite.py\", \"--config\", \"/config/config.yaml\"]" in content


def test_compose_template_contains_config_mount_and_command():
    payload = yaml.safe_load(COMPOSE_TEMPLATE.read_text(encoding="utf-8"))

    assert "services" in payload
    assert "redwardenlite" in payload["services"]

    service = payload["services"]["redwardenlite"]
    volumes = service.get("volumes", [])

    assert any("example-config.yaml:/config/config.yaml:ro" in item for item in volumes)
    assert any("artifacts:/opt/RedWardenLite/artifacts" in item for item in volumes)
    assert service.get("command") == ["python", "RedWardenLite.py", "--config", "/config/config.yaml"]


def test_runbook_includes_smoke_and_rollback_steps():
    content = RUNBOOK_FILE.read_text(encoding="utf-8")

    assert "Upgrade-Safe Smoke Verification" in content
    assert "curl -fsS http://127.0.0.1:8080/metrics" in content
    assert "curl -i http://127.0.0.1:8080/" in content
    assert "Rollback Checklist" in content
    assert "systemctl restart redwardenlite" in content
    assert "CI Compatibility Matrix" in content
    assert "3.10" in content and "3.11" in content and "3.12" in content
