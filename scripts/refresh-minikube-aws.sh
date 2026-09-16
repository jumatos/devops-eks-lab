#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON="$PROJECT_ROOT/.venv-py311/bin/python"

if [[ ! -x "$PYTHON" ]]; then
    echo "No se encontró Python en .venv-py311."
    exit 1
fi

export AWS_PROFILE=devops-lab
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1

if ! aws sts get-caller-identity --profile "$AWS_PROFILE" >/dev/null; then
    echo "Verifica tu sesión con:"
    echo "aws sso login --profile $AWS_PROFILE"
    exit 1
fi

kubectl --context=minikube get namespace task-api >/dev/null

"$PYTHON" - <<'PY'
import json
import subprocess
import boto3

role_arn = subprocess.check_output(
    [
        "terraform", "-chdir=infra/dynamodb",
        "output", "-raw", "local_api_role_arn",
    ],
    text=True,
).strip()

session = boto3.Session(
    profile_name="devops-lab",
    region_name="us-east-1",
)

with session.client("sts") as sts:
    credentials = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="minikube-task-api",
        DurationSeconds=3600,
    )["Credentials"]

secret = {
    "apiVersion": "v1",
    "kind": "Secret",
    "metadata": {
        "name": "task-api-aws",
        "namespace": "task-api",
    },
    "type": "Opaque",
    "stringData": {
        "AWS_ACCESS_KEY_ID": credentials["AccessKeyId"],
        "AWS_SECRET_ACCESS_KEY": credentials["SecretAccessKey"],
        "AWS_SESSION_TOKEN": credentials["SessionToken"],
    },
}

result = subprocess.run(
    [
        "kubectl", "--context=minikube", "apply",
        "--server-side",
        "--field-manager=local-aws-session",
        "-f", "-",
    ],
    input=json.dumps(secret),
    text=True,
    capture_output=True,
)

if result.returncode:
    raise SystemExit(
        "No se pudo actualizar el Secret. "
        "Se omitió la salida para no mostrar credenciales."
    )

print("Secret task-api-aws actualizado.")
print("Credenciales válidas hasta:", credentials["Expiration"].isoformat())
PY

DEPLOYMENT="$(kubectl --context=minikube -n task-api \
    get deployment task-api --ignore-not-found -o name)"

if [[ -n "$DEPLOYMENT" ]]; then
    kubectl --context=minikube -n task-api \
        rollout restart deployment/task-api

    kubectl --context=minikube -n task-api \
        rollout status deployment/task-api --timeout=180s
else
    echo "Credenciales preparadas. Falta instalar el chart."
fi
