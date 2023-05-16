#!/usr/bin/env bash

set -x
# Exit script when a command returns nonzero state
set -e

set -o pipefail

export PYTHONUNBUFFERED="True"
export OMP_NUM_THREADS=4
export CUDA_VISIBLE_DEVICES=$1
EXPERIMENT=$2
INPUT_FEAT=$3
BATCH_SIZE=$4
MAX_EPOCH=$5
TIME=$(date +"%Y-%m-%d_%H-%M-%S")

DATASET=${DATASET:-BuildingNetVoxelization0_01Dataset}
MODEL=${MODEL:-Res16UNet34C}
OPTIMIZER=${OPTIMIZER:-SGD}
LR=${LR:-1e-2}
SCHEDULER=${SCHEDULER:-CosineAnnealingLR}

OUTPATH=./outputs/$DATASET/$MODEL/${OPTIMIZER}-l$LR-b$BATCH_SIZE-$SCHEDULER-e$MAX_EPOCH-$EXPERIMENT-$INPUT_FEAT/$TIME
VERSION=$(git rev-parse HEAD)

# Save the experiment detail and dir to the common log file
mkdir -p $OUTPATH

LOG="$OUTPATH/$TIME.txt"

# put the arguments on the first line for easy resume
echo -e "
    --log_dir $OUTPATH \
    --dataset $DATASET \
    --model $MODEL \
    --train_limit_numpoints 1200000 \
    --lr $LR \
    --optimizer $OPTIMIZER \
    --batch_size $BATCH_SIZE \
    --scheduler $SCHEDULER \
    --max_epoch $MAX_EPOCH \
    --input_feat $INPUT_FEAT \
    $6" >> $LOG
echo Logging output to "$LOG"
echo $(pwd) >> $LOG
echo "Version: " $VERSION >> $LOG
echo "Git diff" >> $LOG
echo "" >> $LOG
git diff | tee -a $LOG
echo "" >> $LOG
echo -e "-------------------------------System Information----------------------------" >> $LOG
echo -e "Hostname:\t\t"`hostname` >> $LOG
echo -e "GPU(s):\t\t$CUDA_VISIBLE_DEVICES" >> $LOG
nvidia-smi | tee -a $LOG

time python -W ignore tasks/main_seg.py \
    --log_dir $OUTPATH \
    --dataset $DATASET \
    --model $MODEL \
    --train_limit_numpoints 12000000 \
    --lr $LR \
    --optimizer $OPTIMIZER \
    --batch_size $BATCH_SIZE \
    --scheduler $SCHEDULER \
    --max_epoch $MAX_EPOCH \
    --input_feat $INPUT_FEAT \
    $6 2>&1 | tee -a "$LOG"
