import time
from celery import Celery,task

# BACKENDUSER = 'lukas'
# BACKENDHOST = 'localhost'
# BACKENDBASEPATH = '/Users/lukas/Code/atlas/recast/recast-frontend-prototype'
BACKENDUSER = 'analysis'
BACKENDHOST = 'recast-demo'
BACKENDBASEPATH = '/home/analysis/recast/recaststorage'
CELERY_RESULT_BACKEND = 'redis://{}:6379/0'.format(BACKENDHOST)

app = Celery('tasks', backend='redis://{}'.format(BACKENDHOST), broker='redis://{}'.format(BACKENDHOST))


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

red = redis.StrictRedis(host = BACKENDHOST, db = 0)
io  = emitter.Emitter({'client': red})


from datetime import datetime

def socketlog(jobguid,msg):
  io.Of('/monitor').In(str(jobguid)).Emit('room_msg',{'date':datetime.now().strftime('%Y-%m-%d %X'),'msg':msg})
  
import requests
def download_file(url,download_dir):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    download_path = '{}/{}'.format(download_dir,local_filename)
    with open(download_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return download_path    

@task
def postresults(jobguid,requestId,parameter_point,resultlister):
  workdir = 'workdirs/{}'.format(jobguid)
  resultdir = 'results/{}/{}'.format(requestId,parameter_point)
  
  if(os.path.exists(resultdir)):
    shutil.rmtree(resultdir)
    
  os.makedirs(resultdir)  

  for result,resultpath in ((r,os.path.abspath('{}/{}'.format(workdir,r))) for r in resultlister()):
    if os.path.isfile(resultpath):
      shutil.copyfile(resultpath,'{}/{}'.format(resultdir,result))
    if os.path.isdir(resultpath):
      shutil.copytree(resultpath,'{}/{}'.format(resultdir,result))

  socketlog(jobguid,'uploading resuls')

  #also copy to server
  subprocess.call('''ssh {user}@{host} "mkdir -p {base}/results/{requestId}/{point} && rm -rf {base}/results/{requestId}/{point}/dedicated"'''.format(
    user = BACKENDUSER,
    host = BACKENDHOST,
    base = BACKENDBASEPATH,
    requestId = requestId,
    point = parameter_point)
  ,shell = True)
  subprocess.call(['scp', '-r', resultdir,'{user}@{host}:{base}/results/{requestId}/{point}/dedicated'.format(
    user = BACKENDUSER,
    host = BACKENDHOST,
    base = BACKENDBASEPATH,
    requestId = requestId,
    point = parameter_point
  )])
  
  socketlog(jobguid,'done')
  return requestId

import susyhiggs.recipes as recipes

@task
def runSelection(jobguid,ntuple,samplename):
    workdir = 'workdirs/{}'.format(jobguid)
    recipes.runSelection(ntuple,samplename,workdir)
    return jobguid

@task
def plotCutflow(jobguid,ntuplefile):
    workdir = 'workdirs/{}'.format(jobguid)
    recipes.plotCutflow('{}/{}'.format(workdir,ntuplefile),workdir)
    return jobguid
  
@task
def createNtup(jobguid,samplefile,samplename):
    workdir = 'workdirs/{}'.format(jobguid)
    recipes.createNtup(samplefile,samplename,workdir)
    return jobguid

@task
def downloadWithRucio(jobguid):
    workdir = 'workdirs/{}'.format(jobguid)
    data = yaml.load(open('{}/inputs/recastinput.yaml'.format(workdir)))
    samplelist = [data['sample dataset']]
    recipes.downloadWithRucio(samplelist,workdir)
    return jobguid
    
@task
def prepare_job(jobguid,jobinfo):
  print "job info is {}".format(jobinfo)
  print "job uuid is {}".format(jobguid)
  workdir = 'workdirs/{}'.format(jobguid)

  input_url = jobinfo['run-condition'][0]['lhe-file']
  socketlog(jobguid,'downloading input files')

  filepath = download_file(input_url,workdir)

  print "downloaded file to: {}".format(filepath)
  socketlog(jobguid,'downloaded input files')


  with zipfile.ZipFile(filepath)as f:
    f.extractall('{}/inputs'.format(workdir)) 

  return jobguid

@task
def prepare_workdir(fileguid,jobguid):
  uploaddir = 'uploads/{}'.format(fileguid)
  workdir = 'workdirs/{}'.format(jobguid)
  
  os.makedirs(workdir)

  socketlog(jobguid,'prepared workdir')

  return jobguid
  

import recastapi.request
import json
import uuid

import time
  

def get_chain(request_uuid,point):
  request_info = recastapi.request.request(request_uuid)
  jobinfo = request_info['parameter-points'][point]

  jobguid = uuid.uuid1()

  analysis_queue = 'susy_queue'  

  chain = (
            prepare_workdir.subtask((request_uuid,jobguid),queue=analysis_queue) |
            prepare_job.subtask((jobinfo,),queue=analysis_queue)                 |
            downloadWithRucio.subtask(queue=analysis_queue) |
            createNtup.subtask(['./rucio_download_list.txt','new_signal'],queue = analysis_queue) |
            plotCutflow.subtask(['susyNt.root'],queue = analysis_queue) |
            runSelection.subtask(['susyNt.root','samplename'],queue = analysis_queue) |
            postresults.subtask((request_uuid,point,recipes.recastResults),queue=analysis_queue)
          )
  return (jobguid,chain)
