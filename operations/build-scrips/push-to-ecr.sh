#!/bin/bash

BRANCH_NAME=${CIRCLE_BRANCH}
ECR_URL=${AWS_ECR_ACCOUNT_URL}

if [[ -z "${BRANCH_NAME}" || -z "${ECR_URL}" ]]; then
    echo "CIRCLE_BRANCH and AWS_ECR_ACCOUNT_URL environment vars must be set"
    exit 1
fi

IMAGE_NAME=$1
DOCKERFILE_PATH=$2

if [[ "$#" != "2" ]]; then
    echo "Usage: push-to-ecr.sh image-name dockerfile-path"
    exit 1
fi

shift 2

REPO_NAME="travelbear/Gatekeeper"
ECR_REPO_URL=""${ECR_URL}"/"${REPO_NAME}""

GIT_TAG=""${IMAGE_NAME}"."${BRANCH_NAME}"."$(git rev-list HEAD | head -n 1)""
LATEST_TAG=""${IMAGE_NAME}"."${BRANCH_NAME}".latest"

echo -n "Building "${IMAGE_NAME}"... "
IMAGE_ID=$(docker build -qt ""${ECR_REPO_URL}":"${GIT_TAG}"" -f ${DOCKERFILE_PATH} .)
docker tag ${IMAGE_ID} ""${ECR_REPO_URL}":${LATEST_TAG}"
echo "Done"

for TAG in ${GIT_TAG} ${LATEST_TAG}
do
    docker push ""${ECR_REPO_URL}":${TAG}"
done
