import subprocess
import os.path

def downloadWithRucio(dsids,workdir):
  for dsid in dsids:
    print "downloading dsid: {}".format(dsid)
    p = subprocess.Popen(['rucio_wrapper.sh','download',dsid],cwd = workdir)
    p.wait()
  files = ['/'.join(dsid.split(':')) for dsid in dsids]
  with open('{}/rucio_download_list.txt'.format(workdir),'w') as f:
    for file in files:
        #verify that file is present
        relpath = '{}/{}'.format(workdir,file)
        if not os.path.isfile(relpath): raise IOError
        f.write(os.path.abspath('{}/{}'.format(workdir,file)))

def createNtup(filelist,samplename,workdir):
    subprocess.call(['NtMaker_wrapper.sh','-f',filelist,'-s',samplename,'--saveTruth','--filterOff'], cwd = workdir)

def runSelection(ntuple,samplename,workdir):
    with open('{}/selection.log'.format(workdir),'w') as f:
        subprocess.call(['SusySel_wrapper.sh','-i','{}/{}'.format(workdir,ntuple),'-s',samplename],stdout = f)

def plotCutflow(ntuplefile,workdir):
  import ROOT
  file = ROOT.TFile.Open(ntuplefile)
  cutflow = file.Get('rawCutFlow')
  c = ROOT.TCanvas('canvas','canvas',600,600)
  cutflow.Draw()
  c.SaveAs('{}/canvas.pdf'.format(workdir))
  c.SaveAs('{}/canvas.png'.format(workdir))


# function returns a list of result files that will be present in the working directory
# that should be included in a recast response
def recastResults():
    return ['canvas.pdf','canvas.png','selection.log']
