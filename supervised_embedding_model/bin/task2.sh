#!/bin/bash

source bin/utils.sh

task="task-2"
mkdir -p checkpoints/$task/
WITH_PREPROCESS="$1"
[ -z "$WITH_PREPROCESS" ] && WITH_PREPROCESS='False'


if [ "$WITH_PREPROCESS" == "True" ]; then
	python parse_candidates.py data/dialog-bAbI-tasks/dialog-babi-candidates.txt > data/candidates.tsv
  parse_dialogs 'dialog-babi-task2-API-refine' $task
fi

python train.py --train data/train-$task.tsv --dev data/dev-$task-500.tsv \
  --vocab data/vocab-$task.tsv --emb_dim 128 --save_dir checkpoints/$task/model
