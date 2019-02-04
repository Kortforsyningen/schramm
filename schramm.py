#!/usr/bin/python 
#-*- coding: latin1 -*-
#last edit: Forbedrede brugermeddelelser, simlk aug. 2011
import sys
import time
PROGRAM="Schramm v.1.1 2011-11-29"
Badtypes=["jordoverflade"]
TTYPES=["asfalt","beton","flise","gulv","terræn","klippe","perron","tag","dige","dæksel","kørebanebelægning"]
TTYPES.extend(Badtypes) #illegale ord ogsaa med her... SKAL vaere samme som kets i BADTYPES!
BADTYPES={Badtypes[0]:"terræn"} #forkerte navne og erstatninger
BADGPS=["GPS-status ukendt","GPS-egnethed ukendt"] #SKAL vaere samme som keys i BADGPS
GPSBSK=["gps-egnet","Ej umiddelbart gps-egnet","Ej gps-egnet","GPS-egnethed ukendt"]
GPSBSK.extend(BADGPS)
#BADGPS={Badgps[0]:"GPS-egnethed ukendt",Badgps[1]:} #erstatninger
GOODCOMMENTS=["RefDK.","5dnet.","10 km-net."]
GOODCOMMENTS_PREFIXES=["Rev.","RefDK.","5dnet.","10","Nyetb.","Nyetbl.","Nyetableret"]
MUST_FIND_COMMENTS=["Rev.","Nyetb.","Nyetbl.","Nyetableret"]
def Usage():
	print "Kald Schramm.py indfil"
	print "Vil outputte en retteliste: indfil_log, og en forsøgsvist rettet fil: indfil_rett"
	sys.exit()
def Log(line,logfile=None):
	#pline=line.replace(".","")+"." #lidt akavet, for at slippe for .'er midt i saetninger... betyder man skal vaere bevidst om ikke at bruge dem, brug. f.eks - eller , istedet midt i saetninger.
	pline=line #ovenstaaende for akavet!
	if logfile!=None:
		logfile.write(pline+"\n")
	print pline.decode("latin1")
def Escape():
	ud.close()
	log.close()
	print "Stopper %s." %sys.argv[0]
	sys.exit()
def JaNej(prompt):
	print prompt.decode("latin1")
	s=raw_input("j/n :")
	s=s.strip().lower()
	if s.find("exit")!=-1:
		Escape()
	if s.find("ja")!=-1 or s=="j":
		return True
	return False
def CompareThis(line):
	words=line.split()
	line=words[0]+" "
	for i in range(1,len(words)-1):
		line+=words[i]+" "
	if len(words)>1:
		line+=words[-1]
	return line.lower().replace("-"," ")
def Worddistance(w1,w2):
	d=0
	l=min(len(w1),len(w2))
	for i in range(0,l):
		if w1[i]!=w2[i]:
			d+=2     #taeller hoejere
	d+=abs(len(w1)-len(w2))
	return d
def Similarity(word1,word2): #et bud paa AI :-) Vaegtnigen skal traenes paa et godt datasaet!
	score=0
	npatterns=0
	maxlength=min(len(word1),len(word2),4)
	if len(word1)<=len(word2):
		minword=word1
		maxword=word2
	else:
		minword=word2
		maxword=word1
	lmin=len(minword)
	lmax=len(maxword)
	for i in range(1,maxlength+1):
		for j in range(0,lmin-i+1): #vaegtning, saa ender taeller mere?
			weight=6/(float(lmin)**2)*(j-lmin*0.65)**2+1
			npatterns+=weight
			end=min(lmin,j+i)
			pattern=minword[j:end]
			if maxword.find(pattern)!=-1:
				score+=weight
	return score/float(npatterns)-0.7*(lmax-lmin)/float(lmax)  #experimentel status. Vaegte skal no tilpasses...

def FindClosestWord(word,checklist):
	if word in checklist:
		return word, 0, 1
	smax=-10000
	closest=word
	for test in checklist:
		sim=Similarity(CompareThis(word),CompareThis(test)) #tjek lighed mellem lower-case udgaver.
		if sim>smax:
			closest=test
			smax=sim
	d=Worddistance(word,closest) #virkelig afstand....
	return closest, d, smax
def TjekBeskrivelse(lines,N,logfile,Stations): #linier og startlinienummer, logfil og (pointer) til Stations...
	retlines=[]
	P=lines[0].strip().replace(":","")
	alreadyfound=0
	if P in Stations:
		Log("Linie %i, punkt %s: Beskrivelse fundet tidligere!" %(N,P),logfile)
		alreadyfound=1
	else:
		Stations.append(P) #Pointer til Stations, som dermed aendres i main.
	if 2>len(P)>23:
		Log("Linie %i, punkt %s: Tvivlsomt punktnavn." %(N,P),logfile)
	founddollar=0
	foundafm=0
	foundpound=0
	foundstars=0
	foundhash=0
	lbem=0
	Nret=0
	Nwarn=0
	nospaces=0
	if lines[0].strip()[-1]!=":":
		Log("Linie %i, punkt %s: Intet ':' efter punktnavn- Retter dette." %(N,P),logfile)
		Nret+=1
		lines[0]=lines[0].strip()+":"
	for line in lines:
		if not line.isspace():
			nospaces+=1
	if nospaces==1 or (nospaces==2 and lines[-1].strip()=="@="):
		Log("Linie %i, punkt %s: Tom beskrivelse!!" %(N,P),logfile)
		return lines,alreadyfound,True
	for j in range(0,len(lines)):
		#rline=lines[j]  #som default er den rettede linie det samme som input,
		line=lines[j].strip()
		i=line.find("$")
		if i!=-1 and i!=0:
			Log("Linie %i, punkt %s: Forkert placering af $-tegn." %(N+j,P),logfile)
			Nwarn+=1
		elif i==0: # saa korrekt placering
			founddollar+=1
			splitline=line.split()
			if len(splitline)==2: #tjek med Scramm
				pass
			if len(splitline) not in [2,4]: #tjekker primaert for manglende m tegn
				Log("Linie %i, punkt %s: Forkert antal ord efter $-tegn." %(N+j,P),logfile)
				Nwarn+=1
				if len(splitline)==3:
					if line.find("m")==-1:
						try:
							float(splitline[0][1:])
						except:
							pass
						else:
							Log("Linie %i, punkt %s: Indsaetter m efter højdeangivelse." %(N+j,P),logfile)
							Nret+=1
							i =line.find(" ")
							line=line[:i]+" m "+line[i+1:]
			splitline=line.split()			
			if len(splitline) in [2,4]:
				terraenbsk=splitline[-1]
				if terraenbsk[-1]==".":
					terraenbsk=terraenbsk[0:-1] #slet sidste "."
				ord, dist, sim=FindClosestWord(terraenbsk,TTYPES)
				if BADTYPES.has_key(ord): #hvis det er en af de terraenbesk. der er kendt som klassiske fejl.
					if sim>0.45 or dist<4: #experimentielle vaerdier. Hvis OK, tilsvarende i gps-bsk.
						line=line.replace(terraenbsk,BADTYPES[ord])
						Nret+=1
						Log("Linie %i, punkt %s: Erstatter '%s' med '%s'." %(N+j,P,terraenbsk,BADTYPES[ord]),logfile)
					else:
						Log("Linie %i, punkt %s: Kunne ikke genkende terrænbeskrivelse '%s'." %(N+j,P,terraenbsk),logfile)
						Nwarn+=1
				elif 0.3<sim<0.7 or 2<dist<5:
					Log("Linie %i, punkt %s: %s\n'%s' kunne være '%s'." %(N+j,P,line,terraenbsk,ord),logfile)
					if JaNej("Mente du %s?" %(line.replace(terraenbsk,ord))):
						Nret+=1
						line=line.replace(terraenbsk,ord)
						Log("OK, erstatter '%s' med '%s'." %(terraenbsk,ord),logfile)
					else:
						Log("OK, erstatter ikke...",logfile)
						Nwarn+=1
				elif 0.7<=sim and dist!=0:
					Nret+=1
					line=line.replace(terraenbsk,ord)
					Log("Linie %i, punkt %s: Erstatter '%s' med '%s'" %(N+j,P,terraenbsk,ord),logfile)
				elif dist!=0:
					Log("Linie %i, punkt %s: Kunne ikke genkende terrænbeskrivelse '%s'." %(N+j,P,terraenbsk),logfile)
					Nwarn+=1
				if line[-1]!=".":  #indsaet . til sidst
					line+="."
					Log("Linie %i, punkt %s: Tilføjer '.' efter terrænbeskrivelse" %(N+j,P),logfile)
					Nret+=1
		
		sokkelfind=line.find("sokkel.")
		if sokkelfind!=-1:
			line=line.replace("sokkel.", "sokkelkant.")
		i=line.find("£")
		if i!=-1 and i!=0:
			Log("Linie %i, punkt %s: Forkert placering af £-tegn." %(N+j,P),logfile)
			Nwarn+=1
		elif i==0:
			gpsline=line[1:]  #ikke kodetegn med...
			if gpsline[-1]==".":
				gpsline=gpsline[0:-1] #slet sidste "." for sammenligning
			foundpound+=1
			gpsbsk, dist, sim=FindClosestWord(gpsline,GPSBSK)
			if gpsbsk in BADGPS: #erstat uanset ord-afstand...
				if dist>0:
					Log("Linie %i, punkt %s: '%s' genkendt som '%s', IKKE tilladt bsk.!" %(N+j,P,gpsline,gpsbsk),logfile)
				else:
					Log("Linie %i, punkt %s: '%s', IKKE tilladt gps-bsk.!" %(N+j,P,gpsline),logfile)
				#line="£"+BADGPS[gpsbsk]+"." # erstat som standard! Efter Logning, da line bruges her,
				#Nret+=1
				Nwarn+=1
			elif 0.3<sim<0.77:
				Log("Linie %i, punkt %s: %s." %(N+j,P,gpsline),logfile)
				if JaNej("Mente du %s?" %(gpsbsk)):
					Log("OK, erstatter '%s' med '%s'." %(gpsline,gpsbsk),logfile)
					line="£"+gpsbsk+"."
					Nret+=1
				else:
					Log("OK, erstatter ikke...",logfile)
					Nwarn+=1
			elif 0.77<=sim and dist!=0:
				Log("Linie %i, punkt %s: Erstatter '%s' med '%s'" %(N+j,P,gpsline,gpsbsk),logfile)
				line="£"+gpsbsk+"."
				Nret+=1
			elif dist!=0:
				Log("Linie %i, punkt %s: Kunne ikke genkende gps-beskrivelse." %(N+j,P),logfile)
				Nwarn+=1
			if line[-1]!=".":  #indsaet . til sidst
				line+="."
				Log("Linie %i, punkt %s: Tilføjer '.' efter gps-beskrivelse." %(N+j,P),logfile)
				Nret+=1
		i=line.find("#")
		if i!=-1 and i!=0:
			Log("Linie %i, punkt %s: Forkert placering af #-tegn." %(N+j,P),logfile)
			Nwarn+=1
		elif i==0:
			foundhash+=1
		i=line.find("<")
		if i!=-1 and i!=0:
			Log("Linie %i, punkt %s: Forkert placering af <-tegn." %(N+j,P),logfile)
			Nwarn+=1
		elif i==0:
			foundafm+=1
		i=line.find("*")
		if i!=-1 and i!=0:
			Log("Linie %i, punkt %s: Forkert placering af *-tegn." %(N+j,P),logfile)
			Nwarn+=1
		elif i==0:
			foundstars+=1
			lbem=len(line)-1
			k=line.find("rev") #aendret fra 'j', da dette indeks allerede bruges som linietaeller i bsk.
			if k!=-1:
				if line[k+3]!=".":
					line=line.replace("rev","Rev.")
					word="rev"
					rword="Rev."
				else:
					line=line.replace("rev.","Rev.")
					word="rev."
					rword="Rev." 
				Nret+=1
				Log("Linie %i, punkt %s: Erstatter '%s' med '%s' i bemærkning." %(N+j,P,word,rword),logfile)
				
			if lbem==0:
				Log("Linie %i, punkt %s: Ingen bemærkning efter *-tegn." %(N+j,P),logfile)
				Nwarn+=1
			else:
				found=False
				for word in MUST_FIND_COMMENTS:
					i=line.find(word)
					if i!=-1:
						found=True
						break
				if not found:
					Log("Linie %i, punkt %s: '%s' eller '%s' ikke fundet efter *-tegn." %(N+j,P,MUST_FIND_COMMENTS[0],MUST_FIND_COMMENTS[1]),logfile)
					Nwarn+=1
				elif len(line[i:].split())<3:
					Log("Linie %i, punkt %s: Hmmm, noget galt med bemærkningen efter *-tegn." %(N+j,P),logfile)
					Nwarn+=1
				testline=line[1:].split()
				if testline[0] not in GOODCOMMENTS_PREFIXES:
					Log("Linie %i, punkt %s: Bemærkningen efter *-tegn starter ikke ikke korrekt, eller indeholder flere net-beskrivelser." %(N+j,P),logfile)
					Nwarn+=1
				for word in GOODCOMMENTS:
					sim=Similarity(line.lower(),word.lower())
					if sim>0.25 and not(word in line):
						Log("Linie %i, punkt %s: Tilsyneladende syntaksfejl i bemærkning. Måske menes der '%s'?" %(N+j,P,word),logfile)
						Nwarn+=1
					
		retlines.append(line)
	something_wrong=False
	if Nret>0:
		Log("Punkt %s, lavede %i rettelse(r)." %(P,Nret),logfile)
		something_wrong=True
	if founddollar>1 or foundafm>1 or foundpound>1:
		Log("Linie %i, punkt %s: Noget galt fandt flere af samme kodetegn, måske to beskrivelser uden afgrænsning?" %(N,P),logfile)
		Nwarn+=1
	if foundhash==0:
		Log("Linie %i, punkt %s: Fandt ikke #-tegn." %(N,P),logfile)
		Nwarn+=1
	if founddollar==0:
		Log("Linie %i, punkt %s: Fandt ikke $-tegn." %(N,P),logfile)
		Nwarn+=1
	if foundpound==0:
		Log("Linie %i, punkt %s: Fandt ikke £-tegn." %(N,P),logfile)
		Nwarn+=1
	if foundafm==0:
		Log("Linie %i, punkt %s: Fandt ikke <-tegn." %(N,P),logfile)
	if foundstars==0:
		Log("Linie %i, punkt %s: Fandt ikke *-tegn." %(N,P),logfile)
		Nwarn+=1
	if lines[-1].strip()!="@=":
		Log("Linie %i, punkt %s: Beskrivelse ender ikke med @=." %(N,P),logfile)
		Nwarn+=1
	if Nwarn>0:
		if Nwarn==1:
			Log("Punkt %s, 1 advarsel." %P,logfile)
		else:
			Log("Punkt %s, %i advarsler." %(P,Nwarn),logfile)
		something_wrong=True
	return retlines,alreadyfound,something_wrong
def main(args,exit=True):
	if len(args)<2:
		Usage()
	indfil=args[1]
	logfil=indfil+"_log"
	retfil=indfil+"_rett"
	try:
		ind=open(indfil,"r")
	except:
		print "Indfil kunne ikke findes!"
		Usage()
	Stations=[]
	Ndoubles=0
	log=open(logfil,"w")
	ud=open(retfil,"w")
	Bsk=[] #til beskrivelser...
	Lines=ind.readlines()
	ind.close()
	bsk=[]
	foundpoint=False #til at skippe tomme linier mellem punktbeskrivelser.
	bsknospace=0 #til at taelle ikke tomme linier
	Log("Kører program %s, %s." %(PROGRAM,time.asctime()),log)
	for i in range(0,len(Lines)):
		line=Lines[i]
		if (not foundpoint) and not line.isspace():
			foundpoint=True
			
		if foundpoint:
			if bsknospace==1 and (not line.isspace()) and line.strip()[-1]==":": #Til tomme beskrivelser...
				Bsk.append(bsk)
				bsk=[]
				bsknospace=0   #vi har fundet et punkt... 
				
			bsk.append(line)
			if not line.isspace():
				bsknospace+=1
		if line.find("@=")!=-1: 
			Bsk.append(bsk)
			bsk=[]
			foundpoint=False
			bsknospace=0
	Log("Fandt %i punktbeskrivelser i %s." %(len(Bsk),indfil),log)
	if bsknospace>0:
		Log("Der er muligvis en beskrivelse i sidst i filen, som ikke er afsluttet med '@='!",log)
		Log("Tilføjer denne beskrivelse!",log)
		Bsk.append(bsk)
	Log("%s" %("*"*65),log)
	linenumber=0
	last_wrong=0
	for bsk in Bsk:
		retlines,alreadyfound,something_wrong=TjekBeskrivelse(bsk,linenumber+1,log,Stations) #Stations aendres i Tjeb. bsk.
		if something_wrong:
			Log("%i linier frem fra sidste beskrivelse med fejl/rettelser." %(linenumber-last_wrong),log)
			last_wrong=linenumber+len(bsk)
			Log("%s" %("*"*65),log)
		Ndoubles+=alreadyfound #hvis stationen var beskrevet i forvejen!
		linenumber+=len(bsk)
		for line in retlines:
			ud.write(line+"\n")
	if Ndoubles>0:
		Log("Fandt %i dobbeltbeskrivelse(r)." %Ndoubles,log)
	ud.close()
	log.close()
	if exit:
		sys.exit()

if __name__=="__main__":
	main(sys.argv)