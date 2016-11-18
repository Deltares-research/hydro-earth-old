#!/bin/bash
# This script runs the wtools scripts
export resolution=$1
export feature_table=$2
export hybas_id=$3
export model_dir=$4

# export resolution=0.05
# export feature_table=1GdJzOuuAFwgcBl_hM75j6DZ83S2U1u9Z2LWJ8n_L 
# export hybas_id=1050845560 
# export model_dir="wflow-`date +%F-%H_%M_%S`-1050845560"

srtm_prefix='SRTM_WTOOLS'

export SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

export SKELETON="$SCRIPTPATH/../data/wflow-templates/wflow_sbm_template"
#export TRG_MODEL="`mktemp -d --suffix=_$hybas_id --tmpdir=$SCRIPTPATH/../web-site/.results/temp/`"

export TRG_MODEL="$SCRIPTPATH/../file-server/results/$model_dir"
mkdir $TRG_MODEL

export STATICMAPS="$SKELETON/staticmaps"
export CODE="$SCRIPTPATH/../wtools/scripts"
export EERUNNER="$SCRIPTPATH/../../ee-runner"


## GET THE SRTM DEM
echo "Retrieving SRTM DEM for ft:$feature_table;basin id:$hybas_id"
# move to root folder, otherwise paths are incorrect
export CUR_DIR=`pwd`
cd $TRG_MODEL
echo "Current dir: `pwd`"
echo "Feature table: $feature_table"
echo "HydroBASIN: $hybas_id"
node ../../../../ee-runner/ee-runner.js ../../../wtools/scripts/srtm/download_SRTM.js $feature_table $hybas_id
echo "node ../../../../ee-runner/ee-runner.js ../../../wtools/scripts/srtm/download_SRTM.js $feature_table $hybas_id" > ./1

unzip ./SRTM.zip -d $TRG_MODEL
rm ./SRTM.zip

export SRTM_DEM=$TRG_MODEL/SRTM.elevation.tif
echo "SRTM DEM in $SRTM_DEM"
echo "Copying skeleton from $SKELETON to $TRG_MODEL"
rsync -av --exclude=staticmaps $SKELETON/* $TRG_MODEL

echo "Adding a placeholder for the staticmaps"
mkdir $TRG_MODEL/staticmaps

echo "Running the WTOOLS scripts"
python $CODE/create_grid.py -d $TRG_MODEL/mask -f $SRTM_DEM -c $resolution -p EPSG:4326 -s -l create_grid.log

python $CODE/static_maps.py -d $TRG_MODEL/staticmaps -s $TRG_MODEL/mask -i $STATICMAPS/static_maps.ini -V $STATICMAPS/clim -D $SRTM_DEM -L $STATICMAPS/wflow_landuse.tif -S $STATICMAPS/wflow_soil.tif -O [$STATICMAPS/FirstZoneCapacity.tif,$STATICMAPS/FirstZoneKsatVer.tif,$STATICMAPS/FirstZoneMinCapacity.tif,$STATICMAPS/InfiltCapSoil.tif,$STATICMAPS/M.tif,$STATICMAPS/thetaS.tif,$STATICMAPS/PavedFrac.tif] -C -A -r $STATICMAPS/riv_up16000.shp -c $TRG_MODEL/mask/mask.shp

echo "Zipping contents from $TRG_MODEL into wflow.zip"
cd ..
zip -r "$model_dir.zip" "$model_dir"

# just a quick check in case if something else passed as $model_dir
if [[ $model_dir == wflow-* ]];
then
  rm -Rf $model_dir
fi

exit 0
