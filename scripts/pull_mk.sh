#!/bin/sh
echo Ensure GAR_R_KEY.json is present in current Dir.
echo Ask ADMIN to obtain KEY...

cat GAR_R_KEY.json | docker login -u _json_key --password-stdin https://us-east1-docker.pkg.dev

docker pull us-east1-docker.pkg.dev/webinspector-370718/docker/mapping_kit/mapping_kit-ig3:latest

docker tag us-east1-docker.pkg.dev/webinspector-370718/docker/mapping_kit/mapping_kit-ig3:latest mapping_kit-ig3:latest