#!/usr/bin/env python
import click

import ROOT

@click.command()
@click.argument('filename')
@click.option('--output','-o',default='plot.pdf')
def plot(filename,output):
  """ program that plot the cutflow from the provided susyNt file """
  f = ROOT.TFile.Open(filename)
  cutflow = f.Get('rawCutFlow')
  c = ROOT.TCanvas('canvas','canvas',600,600)
  cutflow.Draw()
  c.SaveAs(output)
  
if __name__ == '__main__':
  plot()
