from distutils.core import setup
import py2exe
import shutil
import os
import sys
import glob
sys.argv.append("py2exe")
#data2=["./data/MTL.ref","./data/MTL.bsk","./data/Bsk.ind","./data/dk.bmp"]
#Husk pythonw.exe.manifest!!!
#sys.path.insert(0,"ProgramFiles")
#setup(windows=['MTL2.pyw'])
excludes=["Tkconstants","Tkinter","tcl","matplotlib","pylab","javaxx"]
setup(   options = {'py2exe': {'excludes': excludes}},
windows=[{"script" : "Schramm_windows.py"}],
data_files=[("",["icon.ico"])])
#shutil.copy("C:\\Python25\\pythonw.exe.manifest","./dist/Schramm_windows.exe.manifest")
os.system("C:\\Programmer\NSIS\makensis.exe setup_schramm.nsi")
sys.exit()