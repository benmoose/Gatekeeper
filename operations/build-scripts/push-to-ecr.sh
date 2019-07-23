#!/bin/bash

set -e

: ${CIRCLE_BRANCH:?}
: ${GATEKEEPER_ECR_REPOSITORY:?}

function pushImage () {
    [[ ! $# -eq 4 ]] && exit 1

    IMAGE_NAME=$1
    DOCKERFILE_PATH=$2
    BUILD_CONTEXT=$3
    shift 3

    GIT_HASH=$(git rev-list HEAD | head -n 1 | cut -c 1-11)
    GIT_TAG=""${CIRCLE_BRANCH}"."${IMAGE_NAME}"."${GIT_HASH}""
    LATEST_TAG=""${CIRCLE_BRANCH}"."${IMAGE_NAME}".latest"

    echo -n "Building "${IMAGE_NAME}" image... "
    IMAGE_ID=$(docker build -qt ""${ECR_REPOSITORY}":"${GIT_TAG}"" -f ${DOCKERFILE_PATH} ${BUILD_CONTEXT})
    echo "Done"

    echo -n "Tagging image... "
    docker tag ${IMAGE_ID} ""${ECR_REPOSITORY}":"${LATEST_TAG}""
    echo "Done"

    echo -n "Pushing image to ECR... "
    docker push ""${ECR_REPOSITORY}":"${GIT_TAG}""
    docker push ""${ECR_REPOSITORY}":"${LATEST_TAG}""
    echo "Done"
}

pushd $(dirname "$0") && cd ..  # Run from project root

$(aws ecr get-login --no-include-email --region eu-west-1)

pushImage "server" "operations/backend/Dockerfile" "."
pushImage "nginx" "operations/nginx/Dockerfile" "operations/nginx"

popd
