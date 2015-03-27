#!/bin/zsh
analysis_dir=${SUSY_DM_ANALYSIS_DIR?"need to set the analysis directory"}
ntmaker_argv=$argv
argv=()
source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
localSetupROOT --quiet --rootVersion 5.34.18-x86_64-slc6-gcc4.7 
source "$analysis_dir/prod/RootCore/scripts/setup.sh"
echo `which NtMaker`
echo "executing NtMaker $ntmaker_argv"
eval "NtMaker $ntmaker_argv"
