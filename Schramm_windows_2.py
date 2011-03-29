#!/usr/bin/python 
#-*- coding: latin1 -*-
import wx #only windows
import sys
import time
import os
import Schramm
try:
	sys.frozen
except:
	mmdir="./"
else:
	mmdir=sys.prefix+"/"
PROGRAM="Schramm til Windows"
class MainFrame(wx.Frame): #windows only
	def __init__(self,parent,title):
		wx.Frame.__init__(self,parent,title=title)
		self.text=wx.TextCtrl(self,style=wx.TE_MULTILINE|wx.TE_READONLY)
		self.text.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.NORMAL))
		self.sizer=wx.BoxSizer()
		self.sizer.Add(self.text,1,wx.EXPAND)
		self.SetIcon(wx.Icon(mmdir+'icon.ico', wx.BITMAP_TYPE_ICO))
		filemenu=wx.Menu()
		hent=filemenu.Append(wx.ID_ANY,"Tjek en fil")
		Luk=filemenu.Append(wx.ID_ANY,"Afslut")
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&Fil")
		self.Bind(wx.EVT_MENU,self.OnClose,Luk)
		self.Bind(wx.EVT_MENU,self.OnFil,hent)
		self.SetMenuBar(menuBar) 
		self.SetSize((800,600))
		self.SetSizer(self.sizer)
		self.sizer.FitInside(self)
		sys.stdout=self
		self.Log("Velkommen til program %s." %PROGRAM)
	def OnClose(self,event):
		self.Close()
	def OnFil(self,event):
		dlg = wx.FileDialog(
		self, message=u"V\u00E6lg en beskrivelsesfil som skal tjekkes.",
		defaultDir="./",
		defaultFile="",
		wildcard="*.*",
		style=wx.OPEN)
		if dlg.ShowModal()==wx.ID_OK:
			file=dlg.GetFilename()
			dir=dlg.GetDirectory()
			filename=dir+"\\"+file
			Schramm.main([sys.argv[0],filename],False)
			self.Log(u"F\u00E6rdig med filen %s." %filename)
			self.Log("Logfil og fil med rettelser oprettet.")
		dlg.Destroy()
	def Log(self,text):
		self.text.AppendText(text+"\n")
	def write(self,text):
		self.Log(text)
class OKdialog(wx.Dialog):
	def __init__(self,parent,title,msg):
		self.OK=False
		self.cancel=False
		wx.Dialog.__init__(self,parent,title=title)
		self.SetIcon(wx.Icon(mmdir+"icon.ico", wx.BITMAP_TYPE_ICO))
		self.sizer=wx.BoxSizer(wx.VERTICAL)
		self.hsizer=wx.BoxSizer(wx.HORIZONTAL)
		self.text=wx.StaticText(self,label=msg)
		self.text.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD))
		self.sizer.Add(self.text,0,wx.ALL,15)
		self.OKbutton=wx.Button(self,label="Ja")
		self.OKbutton.Bind(wx.EVT_BUTTON,self.OnOK)
		self.cancelbutton=wx.Button(self,label="Nej")
		self.cancelbutton.Bind(wx.EVT_BUTTON,self.OnCancel)
		self.hsizer.Add(self.OKbutton,0,wx.ALL,10)
		self.hsizer.Add(self.cancelbutton,0,wx.ALL,10)
		self.sizer.Add(self.hsizer,0,wx.ALL)
		self.SetSizerAndFit(self.sizer)
		self.OKbutton.SetFocus()
	def OnCancel(self,event):
		self.cancel=True
		self.Close()
	def OnOK(self,event):
		self.OK=True
		self.Close()

			
def Log(line,log):
	global Frame
	pline=line.replace(".","")+"."
	log.write(pline+"\n")
	Frame.Log(pline.decode("latin1"))

def JaNej(prompt):
	dlg=OKdialog(None,u"Sp\u00F8rgsm\u00E5l:",prompt)
	dlg.ShowModal()
	OK=dlg.OK
	dlg.Destroy()
	return OK

def main():
	Schramm.Log=Log
	Schramm.JaNej=JaNej
	global Frame
	App=wx.App()
	Frame=MainFrame(None,PROGRAM)
	Frame.Show()
	App.MainLoop()
	sys.exit() #
if __name__=="__main__":
	main()
	