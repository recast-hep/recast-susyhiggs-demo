#!/bin/zsh
rucioargv=$argv
argv=()
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh
localSetupRucioClients

voms-proxy-info --exists --valid 10:00
if [ $? -eq 0 ];then
  echo "we have a valid proxy already"
else
  echo "getting proxy"
  $HOME/grid_stuff/getmyproxy.sh
fi
echo "using rucio grid proxy info is"
voms-proxy-info --all
eval "rucio $rucioargv"
