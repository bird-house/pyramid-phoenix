#!/bin/sh
#
# Cron script for log generator.
#
# Example crontab line:
# 31 2 1 * * /code/local/pyramid-phoenix/scripts/get-wps-stats_cron.sh 31 >> /gws/nopw/j04/name/management/wps/usage-logs/cron.out 2>&1
#

if [ ! -z "$1" ]
then
    args="--max-age 31"
else
    args=""
fi

odir=/gws/nopw/j04/name/management/wps/usage-logs

cd /code/local/pyramid-phoenix/scripts
source /opt/conda/etc/profile.d/conda.sh
conda activate pyramid-phoenix

[ -d $odir ] || mkdir -p $odir
datestr=$(date +%Y%m%d)

./get-wps-stats.py \
    --output-prefix $odir/$datestr \
    $args
