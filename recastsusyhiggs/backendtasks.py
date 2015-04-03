from celery import shared_task

import subprocess
import glob
import jinja2
import yoda
import os
import shutil

import redis
import emitter
import zipfile
import yaml

import susyhiggs.recipes as recipes

from recastbackend.logging import socketlog

@shared_task
def runSelection(jobguid,ntuple,samplename):
    socketlog(jobguid,'running selection')
    workdir = 'workdirs/{}'.format(jobguid)
    recipes.runSelection(ntuple,samplename,workdir)
    socketlog(jobguid,'running selection done')
    return jobguid

@shared_task
def plotCutflow(jobguid,ntuplefile):
    workdir = 'workdirs/{}'.format(jobguid)
    recipes.plotCutflow('{}/{}'.format(workdir,ntuplefile),workdir)
    return jobguid
  
@shared_task
def createNtup(jobguid,samplefile,samplename):
    socketlog(jobguid,'creating ntuple')
    workdir = 'workdirs/{}'.format(jobguid)
    recipes.createNtup(samplefile,samplename,workdir)
    socketlog(jobguid,'creating ntuple done')
    return jobguid

@shared_task
def downloadWithRucio(jobguid):
    workdir = 'workdirs/{}'.format(jobguid)
    yamlfileglob = glob.glob('{}/inputs/*.yaml'.format(workdir))
    assert len(yamlfileglob) == 1
    data = yaml.load(open(yamlfileglob[0]))
    samplelist = [data['sample dataset']]
    socketlog(jobguid,'downloading samples from rucio: {}'.format(samplelist))
    recipes.downloadWithRucio(samplelist,workdir)
    socketlog(jobguid,'rucio download done')
    return jobguid
    
def get_chain(queuename):
  chain = (
            downloadWithRucio.subtask(queue=queuename) |
            createNtup.subtask(['./rucio_download_list.txt','new_signal'],queue = queuename) |
            plotCutflow.subtask(['susyNt.root'],queue = queuename) |
            runSelection.subtask(['susyNt.root','samplename'],queue = queuename) 
          )
  return chain

# function returns a list of result files that will be present in the working directory
# that should be included in a recast response
def resultlist():
    return ['canvas.pdf','canvas.png','selection.log']

