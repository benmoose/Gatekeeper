#!/bin/bash

set -e
export DOCKER_BUILDKIT=1

: ${AWS_REGION:?}
: ${CIRCLE_BRANCH:?}
: ${GATEKEEPER_ECR_REPOSITORY:?}

function pushImage () {
    [[ ! $# -eq 3 ]] && echo "Expected three arguments." && exit 1

    IMAGE_NAME=$1
    DOCKERFILE_PATH=$2
    BUILD_CONTEXT=$3
    shift 3

    GIT_HASH=$(git rev-list HEAD | head -n 1 | cut -c 1-14)
    GIT_TAG=""${GATEKEEPER_ECR_REPOSITORY}":"${CIRCLE_BRANCH}"."${IMAGE_NAME}"."${GIT_HASH}""
    LATEST_TAG=""${GATEKEEPER_ECR_REPOSITORY}":"${CIRCLE_BRANCH}"."${IMAGE_NAME}".latest"

    echo -n "Building "${IMAGE_NAME}" image... "
    IMAGE_ID=$(docker build -qt ${GIT_TAG} -f ${DOCKERFILE_PATH} ${BUILD_CONTEXT})
    echo "Done"

    echo -n ""${LATEST_TAG}" tagged... "
    docker tag ${IMAGE_ID} ${LATEST_TAG}
    echo "Done"

    echo -n "Pushing image to ECR... "
    docker push ${GIT_TAG}
    docker push ${LATEST_TAG}
    echo "Done"
}

pushd $(dirname "$0") && cd ../..  # Run from Gatekeeper dir

$(aws ecr get-login --no-include-email --region ${AWS_REGION})

pushImage "server" "operations/django/Dockerfile" "."
pushImage "nginx" "operations/nginx/Dockerfile" "operations/nginx"
pushImage "sync-keys" "operations/sync-keys/Dockerfile" "operations/sync-keys"

popd
