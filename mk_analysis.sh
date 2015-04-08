#!/bin/zsh

set -e

./scripts/setup_area_ntuplize.sh ../code/prod
./scripts/setup_area_analysis.sh ../code/analysis
mkdir ../celery


