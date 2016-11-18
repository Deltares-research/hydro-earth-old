#!/bin/bash

export resolution=$1
export feature_table=$2
export hybas_id=$3
export model_dir=$4

export SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
export TRG_MODEL="$SCRIPTPATH/../web-site/.results/$model_dir"
mkdir $TRG_MODEL

./run_wtools.sh $resolution $feature_table $hybas_id $model_dir > "$TRG_MODEL/wtools.log"
