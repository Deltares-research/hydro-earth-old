#!/bin/bash

feature_table='1TIsTsRfRDHOa4xP2wCb97KOq90gVJJkT8m5tHbPg'
hybas_id=4070056200
file_prefix='SRTM_90_Asia_'

node ../../../../ee-runner/ee-runner.js ./download_SRTM.js $feature_table $hybas_id $file_prefix

