#!/usr/bin/env bash

# Use "source" to apply changes to the current terminal.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    echo "Ejecuta: source scripts/init-dev.sh"
    exit 1
fi

_lab_project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)" || return 1

if [[ ! -f "$_lab_project_root/.venv-py311/bin/activate" ]]; then
    echo "No se encontró el entorno .venv-py311."
    unset _lab_project_root
    return 1
fi

cd -- "$_lab_project_root" || return 1
source "$_lab_project_root/.venv-py311/bin/activate"

export AWS_PROFILE=devops-lab
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
export ECR_REGISTRY="703671937762.dkr.ecr.us-east-1.amazonaws.com"
export ECR_REPOSITORY="$ECR_REGISTRY/devops-eks-lab-api"

unset _lab_project_root

echo "Proyecto inicializado."
echo "Perfil AWS: $AWS_PROFILE"
echo "Región AWS: $AWS_REGION"
python --version
echo "Para verificar la sesión: aws sts get-caller-identity"
echo "Si la sesión SSO expiró: aws sso login --profile devops-lab"
