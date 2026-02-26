# Deployment Templates Runbook

## Purpose

Phase 7 provides baseline deployment templates for host service and container workflows, plus a deterministic smoke verification path after deploy/upgrade.

## Template Assets

- `deploy/systemd/redwardenlite.service`
- `deploy/container/Dockerfile`
- `deploy/container/docker-compose.yml`

## Host Workflow (systemd)

1. Create service user and directories:

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin redwardenlite || true
sudo mkdir -p /opt/RedWardenLite /etc/redwardenlite
sudo chown -R redwardenlite:redwardenlite /opt/RedWardenLite
```

2. Install project and dependencies:

```bash
cd /opt/RedWardenLite
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Install config and service unit:

```bash
sudo cp example-config.yaml /etc/redwardenlite/config.yaml
sudo cp deploy/systemd/redwardenlite.service /etc/systemd/system/redwardenlite.service
sudo systemctl daemon-reload
sudo systemctl enable --now redwardenlite
```

## Container Workflow (Docker Compose)

1. Build and start service:

```bash
cd /opt/RedWardenLite/deploy/container
docker compose up -d --build
```

2. Check service state:

```bash
docker compose ps
docker compose logs --tail=100 redwardenlite
```

## Upgrade-Safe Smoke Verification

Run after every deploy/upgrade:

1. Process health:

```bash
systemctl is-active redwardenlite
```

(or `docker compose ps` in container mode)

2. Metrics endpoint reachability:

```bash
curl -fsS http://127.0.0.1:8080/metrics | head -n 5
```

3. Representative proxy path reachability:

```bash
curl -i http://127.0.0.1:8080/
```

4. Contract regression check from repo:

```bash
. .venv/bin/activate
python -m pytest -q tests/test_observability_contracts.py tests/test_transport_runtime.py tests/test_transport_parity.py
```

## Rollback Checklist

1. Revert to previous known-good config and image/build.
2. Restart service:

```bash
sudo systemctl restart redwardenlite
```

(or `docker compose up -d` with previous image tag)

3. Re-run smoke verification commands above.
4. If failure persists, disable rollout and restore last known-good release artifacts before further changes.

## CI Compatibility Matrix

CI validates contract suites against supported CPython versions:

- 3.10
- 3.11
- 3.12

This matrix runs the same hard-fail gate sequence before the full suite on each version.
