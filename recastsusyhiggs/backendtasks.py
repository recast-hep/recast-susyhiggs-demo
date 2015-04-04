import glob
import yaml

import susyhiggs.recipes as recipes

import logging
log = logging.getLogger('RECAST')

def runSelection(jobguid,ntuple,samplename):
    log.info('running selection')
    workdir = 'workdirs/{}'.format(jobguid)
    recipes.runSelection(ntuple,samplename,workdir)
    log.info('running selection done')

def plotCutflow(jobguid,ntuplefile):
    workdir = 'workdirs/{}'.format(jobguid)
    recipes.plotCutflow('{}/{}'.format(workdir,ntuplefile),workdir)
  
def createNtup(jobguid,samplefile,samplename):
    log.info('creating ntuple')
    workdir = 'workdirs/{}'.format(jobguid)
    recipes.createNtup(samplefile,samplename,workdir)
    log.info('creating ntuple done')

def downloadWithRucio(jobguid):
    workdir = 'workdirs/{}'.format(jobguid)
    yamlfileglob = glob.glob('{}/inputs/*.yaml'.format(workdir))
    assert len(yamlfileglob) == 1
    data = yaml.load(open(yamlfileglob[0]))
    samplelist = [data['sample dataset']]
    log.info('downloading samples from rucio: {}'.format(samplelist))
    recipes.downloadWithRucio(samplelist,workdir)
    log.info('rucio download done')
    
def recast(ctx):
  jobguid = ctx['jobguid']
  downloadWithRucio(jobguid)
  createNtup(jobguid,'./rucio_download_list.txt','new_signal')
  plotCutflow(jobguid,'susyNt.root')
  runSelection(jobguid,'susyNt.root','samplename')

# function returns a list of result files that will be present in the working directory
# that should be included in a recast response
def resultlist():
    return ['canvas.pdf','canvas.png','selection.log']

