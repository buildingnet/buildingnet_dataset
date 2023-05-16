#!/usr/bin/env bash
function gdrive_download () {
  CONFIRM=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate "https://docs.google.com/uc?export=download&id=$1" -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')
  wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$CONFIRM&id=$1" -O $2
  rm -rf /tmp/cookies.txt
}

declare -a MODELS_NAME=("MinkNet_BuildingNet_v1_normals_rgb.zip")
declare -a MODELS_ID=("1DhUAKPlrEVickIOQ37gLYoYR0VeZsSps")

for i in "${!MODELS_NAME[@]}"
do
    gdrive_download ${MODELS_ID[$i]} ${MODELS_NAME[$i]}
    unzip ${MODELS_NAME[$i]}
    rm ${MODELS_NAME[$i]}
done
