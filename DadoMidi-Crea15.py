# -*- coding: utf-8 -*-
'''
Interfaccia Grafica - tkinter
Interfaccia Midi    - Mido
Crea MIDI file type 1, Utilizza 5 channel
Crea 10 tracce: Traccia0, Basso, Piano, Voce1, Voce2 e 5 per Drum
Massimo numero di Misure = 9
Dati fissi: 4/4 (numerator=4, denominator=4)
Lunghezza nota minima = 1/8
Lunghezza nota massima= 8/8

Parametri
Tempo   = BPM
Scala   = Scelta tra alcuni tipi di scale
Key     = Scelta della nota base (tonica) (tra 0 e 11)
Accordo = per ogni misura si puo segliere il grado rispetto
		  alla nota base nei diversi accordi.
		  Gli accordi possono essere composti da 1 a 4 note
		  Per ogni nota dell'accordo si puo segliere l'ottava
		  e il grado (distanza da tonica che è 0)

Visualizza PianoRoll (muting di traccia)
Editing Pattern Lunghezza e Altezza Nota

Seglie in modo casuale pattern Ritmici e Melodici 
	da (pochi) pattern memorizzati

Prende i pattern dalla griglia e ritorna su pattern diverso
'''

from __future__ import division
import tkinter as tk
from tkinter import ttk 
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfilename # per chiedere solo il nome
import mido
from pathlib import Path # per estrarre il nome dal percorso completo
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo
# Il backends che usa è rtmidi
# occorre dichiararlo per poter compilare
import mido.backends.rtmidi  
import random # quando inizializza certi dati
import json   # per importare file json

# per editor Notepad++ percorso assoluto
# PER='C:\\......\\'
PER=''

############### LEGGE FILE ############################

# Legge nomi strumenti dal file
Strumenti = []
with open(PER + 'DME-Strumenti.txt') as inFile:
	Strumenti = [line for line in inFile]

# Legge file Help
file = PER +'DME-Help.txt'
sHelp = Path(file).read_text()

#### legge FILE SCALE 
file = PER + 'DMC-ScaleS.json'
Scala=[]
with open(file) as dati_file:
	Scala = json.load(dati_file)
# [[0, 2, 4, 5, 7, 9, 11], 'ionian']


################ FUNZIONI E PROCEDURE #################
def Help():
	pop = tk.Toplevel(z)
	pop.title("Help")
	label = tk.Label(pop, text=sHelp, justify= tk.LEFT,font=('Aerial', 12))
	label.pack(pady=10,padx=10)

def RiempiGrigliaRandom():
	global seedNumber, RitG,GraG
	RitG = [] # Ritmo Griglia
	GraG = [] # Grado Griglia
	random.seed()
	seedNumber = random.randint(0,10000)
	RiempiRandom()
	lRit,lGra = ConvStrLargo(RitG[0],GraG[0]) #### Inizializza lRit e lGra 
	RigeneraMidi()
	z.SetSeqV()

def RiempiRandom():
	global seedNumber
	random.seed(seedNumber)
	In  = random.randrange(len(PRAIn))
	Me1 = random.randrange(len(PRAMe))
	Me2 = random.randrange(len(PRAMe))
	Fi  = random.randrange(len(PRAFi))
	RitA = [PRAIn[In],PRAMe[Me1],PRAMe[Me2],PRAFi[Fi]]
	GraA=[]

	#crea e riempie di 0 ogni GraA con riferimento a RitA
	for lista in RitA: 
		GraA.append([0] * len(lista))

	#### memorizza i pattern random da mettere sulla Scelta PATTERN
	for i in range (16):
		r=int(i/4)
		c=i%4
		if r==2: # Accordi (i gradi tutti a 0)
				RitG.append(RitA[c])
				GraG.append(GraA[c])
		else: # Voce1,Voce2,Basso (monofonici) (r = 0 1 4)
			if c==0: #inizio random
				In=random.randrange(len(PRIn))
				RitG.append(PRIn[In])
				GraG.append(PGIn[In])
			elif c==1 or c==2:
				Me1=random.randrange(len(PRMe))
				RitG.append(PRMe[Me1])
				GraG.append(PGMe[Me1])
			else:
				Fi=random.randrange(len(PRFi))
				RitG.append(PRFi[Fi])
				GraG.append(PGFi[Fi])

def CalcolaPat(nlista,tipo):
	lista=aGiroAcc[nlista]
	Lista9=[]
	if tipo==0:
		Lista9=lista+lista+[0]
	elif tipo==1:
		for i in range (4):
			Lista9=Lista9+[lista[i]]+[lista[i]]
		Lista9=Lista9+[0]
	else:
		Lista9=[0,1,2,3,4,5,4,2,0]
	return Lista9

def SaveMidi():
	if NOMEFILE:
		outfile.save(PERCORSO)
		#print(PERCORSO)
		z.outT('Salvato '+ NOMEFILE)
	else:
		SaveAsMidi()

def SaveAsMidi():
	global outfile
	global NOMEFILE
	global PERCORSO
	# define options for opening or saving a file
	file_opt = options = {}
	options['defaultextension'] = '.mid'
	options['filetypes'] = [('Midi File', '.mid')]
	if NOMEFILE :
		options['initialfile'] = NOMEFILE
	else:
		options['initialfile'] = 'Dado-00'
	options['title'] = 'Salva Midi File'
	filename = asksaveasfilename(**file_opt)

	if filename:
		outfile.save(filename)
		NOMEFILE = Path(filename).stem
		PERCORSO = Path(filename).as_posix()
		#print (PERCORSO)
		z.outT('Salvato '+ NOMEFILE)
	else:
		z.outT('Non Salvato')

def ConvStrLargo(R,G): # da N elementi a 8 elementi
	i=0
	r=[]
	g=[]
	while i<len(R):
		if R[i]>1:
			r.append(R[i])
			g.append(G[i])
			for z in range(R[i]-1):
				r.append(0)
				g.append(G[i])
		else:
			r.append(R[i])
			g.append(G[i])
		i+=1
	return r,g

def TogliSuc(L):
	i=0
	while i<len(L):
		if L[i]>1:
			for t in range(i,i+L[i]):
				L[t]=0
	return L

def scrivi( event, j): # aggiorna StrumeD[j]
	NoS=dizStum[j].get()		   # legge Nome strumento
	NuS = Strumenti.index(NoS)  # legge Indice strumento
	StrumeD[j]=NuS

def RigeneraMidi():
	global z
	global outfile
	global giro
	global GA
	global Iscala

	z.RigoNuovo()
	
	outfile = MidiFile(type=1)
	
	NS=notes[keyNota]+' ' + 'scala '+Scala[Iscala][1]
	Titolo = 'DadoSoft-Mido-Python '+ NS
	#outT(NS,'\n')

	BPM = z.vBPM.get() 
	if BPM==0:
		BPM=120

	S1 = Scala[Iscala][0]
	# raddoppia la scala aggiungento 12 semitoni
	S2 = S1 + [x + 12 for x in S1] # # Scala 2 ottave

	if EspOttD[0]==1:
		SV1 = S1 # Scala Voce1
	else:
		SV1 = S2

	if EspOttD[1]==1: # Scala Voce2
		SV2 = S1 
	else:
		SV2 = S2

	if EspOttD[2]==1: # Scala Accordi
		SA = S1 
	else:
		SA = S2

	if EspOttD[3]==1: # Scala Basso
		SB = S1 
	else:
		SB = S2
	
	################# CREA TRACCE ###################################

	# crea le tracce 0, Voce1, Voce2, Basso, Accordi e 5 tracce Drum
	track0  = MidiTrack()
	trackV1 = MidiTrack()
	trackV2 = MidiTrack()
	trackA  = MidiTrack()
	trackB  = MidiTrack()

	trackD1 = MidiTrack()
	trackD2 = MidiTrack()
	trackD3 = MidiTrack()
	trackD4 = MidiTrack()
	trackD5 = MidiTrack()

	# mette nomi alle tracce
	track0.name  = Titolo
	trackV1.name = Traccia[0]#'Voce1'
	trackV2.name = Traccia[1]#'Voce2'
	trackA.name  = Traccia[2]#'Accordi'
	trackB.name  = Traccia[3]#'Basso'

	# Ogni Drum ha una traccia
	trackD1.name = 'Acoustic Bass Drum'
	trackD2.name = 'Acoustic Snare'
	trackD3.name = 'Closed HiHat'
	trackD4.name = 'Open HiHat'
	trackD5.name = 'Crash Cymbal 1'

	#riempie traccia 0
	track0.append(MetaMessage('set_tempo', tempo = bpm2tempo(BPM)))
	track0.append(MetaMessage('key_signature', key=notes[keyNota]))
	track0.append(MetaMessage('time_signature', numerator=4, denominator=4))

	# chanel 
	chV1= 1
	chV2= 2
	chA = 3
	chB = 4
	chD = 9

	# Defisce il CANALE MIDI e lo STRUMENTO  per ogni traccia
	trackV1.append(Message('program_change', channel=chV1, program= StrumeD[0]))
	trackV2.append(Message('program_change', channel=chV2, program= StrumeD[1]))
	trackA.append (Message('program_change', channel=chA,  program= StrumeD[2]))
	trackB.append (Message('program_change', channel=chB,  program= StrumeD[3]))

	trackD1.append(Message('program_change', channel=chD, program= 0))#Drum
	trackD2.append(Message('program_change', channel=chD, program= 0))#Drum
	trackD3.append(Message('program_change', channel=chD, program= 0))#Drum
	trackD4.append(Message('program_change', channel=chD, program= 0))#Drum
	trackD5.append(Message('program_change', channel=chD, program= 0))#Drum

	quarto = 480 # outfile.ticks_per_beat  # DEFAULT_TICKS_PER_BEAT=480 tick s per nota da 1/4
	misura = quarto * 4
	dTott = int(quarto/2)  # lunghezza ottavo

	NGA = len(gPATT)	# Numero Giro Accordi

	#calcola lunghezza scale scelte
	LV1 =len(SV1)
	LV2 =len(SV2)
	LA =len(SA)
	LB =len(SB)

	######### RIEMPIE TRACCIA VOCE1 #######################
	dB=0
	tA=0
	for l in range(NGA): #Per ogni accordo del giro
		if PatV1[l] == -1:
			dB = dB + misura
			tA = tA + misura
		else:
			n = gPATT[l] # nota base
			Rit = RitG[0 + PatV1[l]] # seglie lista Ritmo V1
			Gra = GraG[0 + PatV1[l]] # nota
			for i in range(len(Rit)):
				# sceglie nota in sequenza su scala 
				if Rit[i]>0 :
					dur = dTott*Rit[i]
					nota = SV1[(n+Gra[i])  % LV1] + OttavaD[0]*12 + keyNota
					trackV1.append(Message('note_on', channel=chV1,note=nota, velocity=100,time=dB))
					trackV1.append(Message('note_off',channel=chV1,note=nota, velocity=0,  time=dur))
					z.PianoRoll(nota,tA,dur,0)
					dB=0
					tA+=dur
				else:
					dB+=dTott
					tA+=dTott

	######## RIEMPIE TRACCIA VOCE2 #######################
	dB=0
	tA=0
	for l in range(NGA): #Per ogni accordo del giro
		if PatV2[l] == -1: #SALTA MISURA
			dB = dB + misura
			tA = tA + misura
		else:
			n = gPATT[l] # nota base
			Rit = RitG[4 + PatV2[l]] # seglie lista Ritmo V2
			Gra = GraG[4 + PatV2[l]]
			for i in range (len(Rit)):
				# sceglie nota in sequenza su scala 
				if Rit[i]>0 :
					dur = dTott*Rit[i]
					nota = SV2[(n+Gra[i])  % LV2] + OttavaD[1]*12 + keyNota
					trackV2.append(Message('note_on', channel=chV2,note=nota, velocity=100,time=dB))
					trackV2.append(Message('note_off',channel=chV2,note=nota, velocity=0,  time=dur))
					z.PianoRoll(nota,tA,dur,1)
					dB=0
					tA+=dur
				else:
					dB+=dTott
					tA+=dTott
			
	######### RIEMPIE TRACCIA ACCORDI #######################
	dB=0
	tA=0
	for l in range(NGA): #Per ogni accordo del giro
		if PatA[l] == -1:
			dB += misura
			tA += misura
		else:
			n = gPATT[l]
			# RAC = RitA[PatA[l]] # seglie lista Ritmo Accordo
			Rit = RitG[8 + PatA[l]] # seglie lista Ritmo Acc
			Gra = GraG[8 + PatA[l]]
			#for o in Rit:
			for i in range(len(Rit)):
				# sceglie nota in sequenza su scala S
				if Rit[i]>0  :
					dur = dTott*Rit[i]
					nota1 = SA[(n+Gra[i]+DeAcGr[0]) % LA] + OttavaD[2]*12 + NoAcOt[0]*12 + keyNota
					nota2 = SA[(n+Gra[i]+DeAcGr[1]) % LA] + OttavaD[2]*12 + NoAcOt[1]*12 + keyNota
					nota3 = SA[(n+Gra[i]+DeAcGr[2]) % LA] + OttavaD[2]*12 + NoAcOt[2]*12 + keyNota
					nota4 = SA[(n+Gra[i]+DeAcGr[3]) % LA] + OttavaD[2]*12 + NoAcOt[3]*12 + keyNota

					trackA.append(Message('note_on', channel=chA,note=nota1, velocity=80, time=dB))
					if DeAcGr[1] > -1 :
						trackA.append(Message('note_on', channel=chA,note=nota2, velocity=80, time=0))
					if DeAcGr[2]> -1 :
						trackA.append(Message('note_on', channel=chA,note=nota3, velocity=80, time=0))
					if DeAcGr[3]> -1 :
						trackA.append(Message('note_on', channel=chA,note=nota4, velocity=80, time=0))
		  
					trackA.append(Message('note_off', channel=chA,note=nota1, velocity=0, time=dur))
					z.PianoRoll(nota1,tA,dur,2)
					if DeAcGr[1] > -1 :
						trackA.append(Message('note_off', channel=chA,note=nota2, velocity=0, time=0))
						z.PianoRoll(nota2,tA,dur,2)
					if DeAcGr[2] > -1 :
						trackA.append(Message('note_off', channel=chA,note=nota3, velocity=0, time=0))
						z.PianoRoll(nota3,tA,dur,2)
					if DeAcGr[3] > -1 :
						trackA.append(Message('note_off', channel=chA,note=nota4, velocity=0, time=0))
						z.PianoRoll(nota4,tA,dur,2)
					dB=0
					tA+=dur
				else:
					dB+=dTott
					tA+=dTott

	########## RIEMPIE TRACCIA BASSO #######################
	dB=0
	tA=0
	for l in range(NGA): #Per ogni accordo del giro
		if PatB[l] ==-1:
			dB += misura
			tA += misura
		else:
			n = gPATT[l] # nota base
			Rit = RitG[12 + PatB[l]] # seglie lista Ritmo Basso
			Gra=  GraG[12 + PatB[l]]
			for i in range(len(Rit)):
				# sceglie nota in sequenza su scala S
				if Rit[i]>0 :
					dur = dTott*Rit[i]
					nota1 = SB[(n+Gra[i])  % LB] + OttavaD[3]*12 + keyNota
					trackB.append(Message('note_on', channel=chB,note=nota1, velocity=127,time=dB))
					trackB.append(Message('note_off',channel=chB,note=nota1, velocity=0,  time=dur))
					z.PianoRoll(nota1,tA,dur,3)
					dB=0
					tA+=dur
				else:
					dB+=dTott
					tA+=dTott

	######### RIEMPIE TRACCE DRUM ####################### 
	dT1 = dT2 = dT3 = dT4 = dT5 = 0
	tA1 = tA2 = tA3 = tA4 = tA5 = 0
	for l in range(NGA): #Per ogni accordo del giro
		if PatD[l] == -1:
			dT1 += misura
			dT2 += misura
			dT3 += misura
			dT4 += misura
			dT5 += misura
			tA1 += misura
			tA2 += misura
			tA3 += misura
			tA4 += misura
			tA5 += misura
		else:
			i = PatD[l]
			for ot in range(8): #considera gli ottavi
				if DrumRit[i*40+ot+0] >0:
					trackD1.append(Message('note_on', channel=chD,note=NotD1, velocity=100,time=dT1))
					trackD1.append(Message('note_off',channel=chD,note=NotD1, velocity=0,  time=int(dTott)))
					z.PianoRoll(1,tA1,dTott,4)
					dT1=0
					tA1+=dTott
				else:	
					dT1+=dTott
					tA1+=dTott

				if DrumRit[i*40+ot+8] >0:
					trackD2.append(Message('note_on', channel=chD,note=NotD2, velocity=100,time=dT2))
					trackD2.append(Message('note_off',channel=chD,note=NotD2, velocity=0,  time=int(dTott)))
					z.PianoRoll(2,tA2,dTott,4)
					dT2=0
					tA2+=dTott
				else:	
					dT2+=dTott
					tA2+=dTott

				if DrumRit[i*40+ot+16] >0:
					trackD3.append(Message('note_on', channel=chD,note=NotD3, velocity=100,time=dT3))
					trackD3.append(Message('note_off',channel=chD,note=NotD3, velocity=0,  time=int(dTott)))
					z.PianoRoll(3,tA3,dTott,4)
					dT3=0
					tA3+=dTott
				else:
					dT3+=dTott
					tA3+=dTott

				if DrumRit[i*40+ot+24] >0:
					trackD4.append(Message('note_on', channel=chD,note=NotD4, velocity=100,time=dT4))
					trackD4.append(Message('note_off',channel=chD,note=NotD4, velocity=0,  time=int(dTott)))
					z.PianoRoll(4,tA4,dTott,4)
					dT4=0
					tA4+=dTott
				else:	
					dT4+=dTott
					tA4+=dTott

				if DrumRit[i*40+ot+32] >0:
					trackD5.append(Message('note_on', channel=chD,note=NotD5, velocity=100,time=dT5))
					trackD5.append(Message('note_off',channel=chD,note=NotD5, velocity=0,  time=int(dTott)))
					z.PianoRoll(5,tA5,dTott,4)
					dT5=0
					tA5+=dTott
				else:	
					dT5+=dTott
					tA5+=dTott

	outfile.tracks.append(track0)
	if MuteD[0]==0:
		outfile.tracks.append(trackV1)
	if MuteD[1]==0:
		outfile.tracks.append(trackV2)
	if MuteD[2]==0:
		outfile.tracks.append(trackA)
	if MuteD[3]==0:
		outfile.tracks.append(trackB)
	if MuteD[4]==0:
		outfile.tracks.append(trackD1)
		outfile.tracks.append(trackD2)
		outfile.tracks.append(trackD3)
		outfile.tracks.append(trackD4)
		outfile.tracks.append(trackD5)

def PlayMidi():
	global outfile
	with mido.open_output() as output:
		try:
			for message in outfile.play():
				output.send(message)
		except KeyboardInterrupt:
			output.reset()

class _GUI(tk.Tk): # Graphic User Interface
	def __init__(self):
		super().__init__()
		cx=840
		cy=600
		# Variabili usate da interfaccia grafica
		self.vScala = tk.IntVar()
		self.vNota  = tk.IntVar()
		self.vBPM   = tk.IntVar()
		self.vtMute=[]
		
		self.vtkDrum=[]
		self.title("DadoSoft - MidiCrea")
		self.resizable(False, False)
		self.tl_Mel=[]
		self.tl_Rit=[]
		self.varNS=tk.IntVar()
		self.varNSD=tk.IntVar()
		self.lsb_PAT = [] # contiene i riferimenti dei pattern (0-len(scala))
		self.ltla_PAT = []
		
		
		FComand	= tk.Frame(self, width=210,	height=198,bd=2, relief=tk.GROOVE)
		FVoci	  = tk.Frame(self, width=cx-198, height=198,bd=2, relief=tk.GROOVE) 
		FGrigSeq   = tk.Frame(self, height=198,bd=2, relief=tk.GROOVE)
	
		FAccordi   = tk.Frame(self, width=cx-198, height=200,bd=2, relief=tk.GROOVE)
		FPianoRoll = tk.Frame(self, width=cx-198, height=200,bd=2, relief=tk.GROOVE)
		FRigoSeq   = tk.Frame(self, height=200,bd=2, relief=tk.GROOVE)
	
		FComand.grid (row=0, column=0)
		FVoci.grid   (row=0, column=1)
		FGrigSeq.grid(row=0, column=2)
	
		FAccordi.grid(row=1, column=0)
		FPianoRoll.grid (row=1, column=1)
		FRigoSeq.grid(row=1, column=2)
	
		FMelo= tk.Frame(FRigoSeq,borderwidth=3, relief=tk.GROOVE)
		FDrum= tk.Frame(FRigoSeq,borderwidth=3, relief=tk.GROOVE)
	
		FMelo.grid (row=0, column=0)
		FDrum.grid (row=1, column=0)
	
		################ FComand ########################  
		YP=20
		YY=2
		
		#   Button 
		bCreaMidi = tk.Button(FComand, text="Info", command=Help)
		bCreaMidi.pack()
		bCreaMidi.place(x=2,y=YY,height=20, width=100) 
		
		bPlayMidi = tk.Button(FComand, text="Play", command=lambda:PlayMidi())
		bPlayMidi.pack()
		bPlayMidi.place(x=100+2,y=YY,height=20, width=100) 
		
		YY +=YP
		
		bSalvaMidi = tk.Button(FComand, text="Save", command=lambda:SaveMidi())
		bSalvaMidi.pack()
		bSalvaMidi.place(x=2 ,y=YY , height=20, width=100)
		
		bSalvaMidi = tk.Button(FComand, text="Save as", command=lambda:SaveAsMidi())
		bSalvaMidi.pack()
		bSalvaMidi.place(x=100+2 ,y=YY , height=20, width=100)
		YY +=YP
		#### Command2 Text OUT ####
		self.TC2 = tk.Text(FComand,height=1, width=25)
		self.TC2.pack()
		self.TC2.place(x=2 ,y=YY+1 , height=20, width=200)
		YY +=YP
		
		# PARAMETRI
		
		#  BPM
		lRM = tk.Label(FComand,text="BPM",anchor="w")
		lRM.place(x=5 ,y=YY+22 , height=20, width=40)	
		
		sBPM = tk.Scale(FComand,variable=self.vBPM ,orient=tk.HORIZONTAL, from_=60, to=240)
		sBPM.set(120)
		sBPM.place(x=40+2 ,y=YY , height=40, width=160)
		
		YY +=YP
		YY +=YP
		
		#   Scala
		sNP = tk.Scale(FComand, command=self.AggScala, variable = self.vScala ,orient=tk.HORIZONTAL, from_=0, to=len(Scala)-1)
		sNP.set(0)
		sNP.place(x=100+2 ,y=YY , height=40, width=100)
		
		lNP = tk.Label(FComand,text="Scale",anchor="w")
		lNP.pack()
		lNP.place(x=5 ,y=YY+5 , height=20, width=30)
		YY +=YP
		self.lNP1 = tk.Label(FComand,text="ionian")
		self.lNP1.pack()
		self.lNP1.place(x=2 ,y=YY , height=20, width=100)
		
		YY +=YP
		#   Nota tonica
		#Scroll oriz
		sNota = tk.Scale(FComand,command=self.AggNota, variable = self.vNota ,orient=tk.HORIZONTAL, from_=0, to=11)
		sNota.set(0)
		sNota.place(x=100+2 ,y=YY , height=40, width=100)
		# Label
		YY +=YP
		# Label
		lRM = tk.Label(FComand,text="Note",anchor="w")
		lRM.place(x=5 ,y = YY , height=20, width=30)
		
		self.lRM1 = tk.Label(FComand,text="C")
		self.lRM1.place(x=40 ,y = YY , height=20, width=30)	
		
		################ FVoci ######################## 
		
		COLORE='white'
		
		#  Intestazione Colonne FVoci
		tk.Label(FVoci, text='Track', bg=COLORE).grid(column=1, row=3,sticky = 'EW')
		tk.Label(FVoci, text='Mute', bg=COLORE).grid(column=2, row=3,sticky = 'EW')
		tk.Label(FVoci, text='Instrument',bg=COLORE).grid(column=3, row=3,sticky = 'EW')
		tk.Label(FVoci, text='Octave', bg=COLORE).grid(column=4, row=3,sticky = 'EW')
		tk.Label(FVoci, text='Exp.Oct.', bg=COLORE).grid(column=5, row=3,sticky = 'EW')
		
		tlnnb_PAT = tk.Label(FVoci, text='Chord Base Note Number',bg=COLORE,anchor="e") 
		tlnnb_PAT.grid(row=1, column=1,columnspan=5,sticky = 'EW')
		tlnac_PAT = tk.Label(FVoci, text='Name Note Base chord',bg=COLORE,anchor="e") 
		tlnac_PAT.grid(row=2, column=1,columnspan=5,sticky = 'EW')
		rows = 5
		cols = len(PatV1)
		
		pr=1  #posizione riga
		gpc=6 #posizione array di spinbox
		
		for c in range(cols): #intestazione di colonna PATTERN
			tla_PAT = tk.Label(FVoci, text=self.NotaPat(c)) #converte in nota
			tla_PAT.grid(row=pr+1, column=gpc+c)
			self.ltla_PAT.append(tla_PAT)
		
			tsb_PAT = ttk.Spinbox(FVoci,from_=0,to=6,width=5,wrap=True)  # 5 chars
			tsb_PAT.insert('end', gPATT[c]) # inserisce nota
			tsb_PAT.grid(row=pr, column=gpc+c)   # dispone e
			self.lsb_PAT.append(tsb_PAT)
			tsb_PAT.bind("<ButtonRelease-1>", lambda event, j=c: self.NotPat(j,event))

		pr=pr+2
		
		for c in range(cols): #intestazione di colonna PATTERN
			la = tk.Label(FVoci, text=str(c))
			la.grid(row=pr, column=gpc+c)
		
		pr=pr+1
		
		for r in range (5): # nomi di Tracce e CheckBox
			ttk.Label(FVoci, text=Traccia[r]).grid(column=1, row=pr+r)
			self.vtMute.append(tk.IntVar())
			c1 = tk.Checkbutton(FVoci,command=self.LeggiDati,variable=self.vtMute[r],onvalue=1, offvalue=0).grid(column=2, row=pr+r)
		
		pc=3  #posizione colonna
		
		for r in range (4): # Scelta strumenti
			CB = ttk.Combobox(FVoci, width=20, state='readonly')
			CB['values'] = tuple(Strumenti)
			CB.grid(column=pc, row=pr+r)
			CB.current(StrumeD[r])
			dizStum[r]= CB
			CB.bind("<<ComboboxSelected>>", lambda event, j=r: scrivi(event, j)) 
		
		pc+=1
		
		self.spinbox_OTT = [] # contiene i riferimenti degli spinbox OTTAVA
		for r in range(4):# drum non ha ottava
			ot = ttk.Spinbox(FVoci,command=self.LeggiDati,from_=1,to=6,width=5,wrap=True)  # 5 chars
			ot.insert('end', OttavaD[r])	# inserisce valore di partenza
			ot.grid(row=r+pr, column=pc)	# dispone e
			self.spinbox_OTT.append(ot)		  # aggiunge alla lista riga
		
		pc+=1
		
		self.spinbox_EOT = [] # spinbox Estensione OTTAVA
		for r in range(4):# drum non ha ottava
			eot = ttk.Spinbox(FVoci,command=self.LeggiDati,from_=1,to=2,width=5,wrap=True)  # 5 chars
			eot.insert('end', EspOttD[r])	# inserisce valore di partenza
			eot.grid(row=r+pr, column=pc)	# dispone e
			self.spinbox_EOT.append(eot)		  # aggiunge alla lista riga
		
		pc+=1
		
		self.spinbox_PAT = [] # spinbox Estensione PATTERN
		for r in range(rows):
			self.spinbox_row = [] # contiene i riferimenti di una riga di spinbox
			for c in range(cols):
				e = ttk.Spinbox(FVoci,command=self.LeggiDati,from_=-1,to=3,width=5,wrap=True)  # 5 chars
				e.insert('end', aSceltaPat[r][c]) # inserisce valore di partenza
				e.grid(row=r+pr, column=pc+c)   # dispone e
				self.spinbox_row.append(e)		  # aggiunge alla lista riga
			self.spinbox_PAT.append(self.spinbox_row)	# aggiunge alla lista di tutti gli spinbox
		
		#######################################################################
		### Frame Accordi
		
		self.sb_ACC = [] # contiene i riferimenti degli spinbox OTTAVA per Accordi
		self.sb_Dac = []
		intAcc=['Note','del.Oct.','del.Grade']
		
		laIntAcc =tk.Label(FAccordi, text='Chord format')
		laIntAcc.grid(row=1, column=0,columnspan=3)
		
		for c in range(3):
			laACCint =tk.Label(FAccordi, text=intAcc[c])
			laACCint.grid(row=2, column=0+c)
		
		for r in range(4):
			laACC =tk.Label(FAccordi, text= str(r))
			laACC.grid(row=3+r, column=0)
			
			aot = ttk.Spinbox(FAccordi,command=self.LeggiDati,from_=-2,to=2,width=5,wrap=True)  # 5 chars
			aot.insert('end', NoAcOt[r]) # inserisce valore di partenza
			aot.grid(row=3+r, column=1)  # dispone e
			self.sb_ACC.append(aot)      # aggiunge alla lista riga
		
			ado = ttk.Spinbox(FAccordi,command=self.LeggiDati,from_=-1,to=6,width=5,wrap=True)  # 5 chars
			ado.insert('end', DeAcGr[r])	# inserisce valore di partenza
			ado.grid(row=3+r, column=2)	 # dispone e
			self.sb_Dac.append(ado)			  # aggiunge alla lista riga

		### PIANO ROLL
		
		self.rigo = tk.Canvas(FPianoRoll, width=760, height=280)
		self.rigo.pack()
		

		############# griglia Sequenze #######################

		tk.Label(FGrigSeq, text= 'Choice of HARMONIC LAP-repetition mode').grid(row=0,column=0,columnspan=4)
		
		self.t_SB_SceGir = ttk.Spinbox(FGrigSeq,command=self.SetPatAcc,width=3,from_=0, to=4,wrap=True)
		self.t_SB_SceGir.grid(row=1,column=0)
		self.t_SB_SceGir.set(0)
		
		tk.Button(FGrigSeq,text='Create\nRandom',command=RiempiGrigliaRandom).grid(row=1, column=3,columnspan=2)
		
		self.vt_RB_SceTip=tk.IntVar()
		at_RB_SceTip=['AB','AA']
		for c in range(2):
			tk_RBD = tk.Radiobutton(FGrigSeq,command=self.SetPatAcc,text = at_RB_SceTip[c],
			variable = self.vt_RB_SceTip,value = c).grid(row=1,column=1+c)

		tk.Label(FGrigSeq, text= 'Pattern for Track').grid(row=2,column=0,columnspan=4)
		
		pref=['V1','V2','AC','BA']
		for i in range(16):
			r=int(i/4)
			c=i%4
			text=str(i)+' > '+pref[r]+'-'+str(c)
			tk_RB = tk.Radiobutton(FGrigSeq,width=10,command=self.SetSeqV, text = text,indicator = 0,
			variable = self.varNS,value = i).grid(row=r+3,column=c)
		
		for c in range(4):
			text=str(c)+' > '+'DR'+'-'+str(c)
			tk_RBD = tk.Radiobutton(FGrigSeq,width=10,command=self.SetSeqD, text = text,indicator = 0,
			variable = self.varNSD,value = c).grid(row=r+7,column=c)
		
		
		############# EDIT SEQUENZE VOCI ##############################
		
		# indice traccia attiva
		self.tkSB_PatV = ttk.Spinbox(FMelo,command=self.SetNuSeAtV,width=3,from_=0, to=16,wrap=True)
		self.tkSB_PatV.grid(row=0, column=0)
		self.tkSB_PatV.set(0)
		
		tbTrack=tk.Button(FMelo,text='Memo',command=self.DaSBaMem).grid(row=1, column=0)
		#tPlay=tk.Button(FMelo,text='Play').grid(row=2, column=0)
		
		self.RigoSeq = tk.Canvas(FMelo, width=256, height=100,bg="white",relief=tk.GROOVE)
		self.RigoSeq.grid (row=0,rowspan=6, column=1, columnspan=8)
		self.RigoSeq.update()
		
		ttk.Label(FMelo,text='Note').grid(row=6,column=0)
		ttk.Label(FMelo,text='Rhythm').grid(row=7,column=0)
		
		
		for i in range(8):
			t_SB_SeqM = ttk.Spinbox(FMelo,command=self.Plot,width=2,from_=0, to=7,wrap=True)
			t_SB_SeqM.set(lGra[i])
			t_SB_SeqM.grid (row=6,column=1+i)
			self.tl_Mel.append(t_SB_SeqM)
		
		
		for i in range(8):
			t_SB_SeqR = ttk.Spinbox(FMelo,command=self.Plot,width=2,from_=0, to=8,wrap=True)
			t_SB_SeqR.set(lRit[i])
			t_SB_SeqR.grid (row=7,column=1+i)
			self.tl_Rit.append(t_SB_SeqR)
		self.Plot()
		
		######### EDIT SEQUENZE DRUM KIT
		
		latX=26
		latY=10
		self.i_1 = tk.PhotoImage(width=latX,height=latY)
		self.i_0 = tk.PhotoImage(width=latX,height=latY)
		self.i_1.put(("yellow"),to=(0,0,latX,latY))
		self.i_0.put(("gray95"),to=(0,0,latX,latY))
		
		i=0
		
		self.tkLabDrum = tk.Label(FDrum,text='0')
		self.tkLabDrum.grid(row=0, column=0)
		tbTrackDrum = tk.Button(FDrum,text='Memo',command=self.TkDtoMem).grid(row=0, column=3,columnspan=3)
		#tPlayDrum = tk.Button(FDrum,text='Play').grid(row=0, column=5,columnspan=3)

		for r in range(5):
			rr=4-r
			tk.Label(FDrum,text=nomeDrum[r]).grid(row=2+rr, column=0)
		
		for i in range(40):
			n=i+NuSeAtD*40
			c=n % 8
			r=4-int(i/8)
			self.vtkDrum.append(tk.IntVar())
			tk.Checkbutton(FDrum, image = self.i_0, selectimage = self.i_1, onvalue=1,offvalue=0,relief='flat',bd=1, variable=self.vtkDrum[i], indicatoron=False).grid(row=r+2,column=c+1)

	def Plot(self,event=None):
		self.RigoSeq.delete("all")
		#legge dagli spinbox
		for i,N in enumerate(self.tl_Mel):
			lGra[i]= int(N.get())
			
		# corregge lunghezze eccessive
		for i,R in enumerate(self.tl_Rit):
			lRit[i]= int(R.get())
			if lRit[i]+i>8:
				lRit[i]=8-i
		
		#mette a 0 le N note successive se N attuale è > 1
		i=0
		t=0
		while i<len(lRit):# lRit sempre di 8 elementi
			if lRit[i]>1:
				for t in range(i+1,i+lRit[i]):
					if (t)<8:
						lRit[t]=0
				i=t #ultimo 0 messo
			i+=1
		# salta se il ritmo =0
		for i in range(len(lRit)): # è sempre 8
			if lRit[i]>0:
				self.PlotNota(lGra[i],lRit[i],i,1)
				i+=lRit[i]
			else:
				i+=1
	
	def SetSeqV(self):
		global NuSeAtV
		NuSeAtV=int(self.varNS.get())
		self.tkSB_PatV.set(NuSeAtV)	
		M=GraG[NuSeAtV]
		R=RitG[NuSeAtV]
		self.PlotFromGM(M,R)

	def SetSeqD(self):
		global NuSeAtD
		NuSeAtD=int(self.varNSD.get())
		self.tkLabDrum.config(text=str(NuSeAtD))
		self.ScriviDatiDK()
	
	def RiempiTk(self,r,m):
		for i in range(8):
			self.tl_Mel[i].set(m[i])
			self.tl_Rit[i].set(r[i])
	
	def DaSBaMem(self):# da tl_Rit e tl_Mel --> 
		r=[]
		m=[]
		for i in range(8):
			r.append(int(self.tl_Rit[i].get()))
			m.append(int(self.tl_Mel[i].get()))
		#mette a 0 le N note successive se attuale è N >1
		i=0
		while i<len(r):# lRit sempre di 8 elementi
			if r[i]>1:
				for t in range(i,i+r[i]-1):
					if (t+1)<8:
						r[t+1]=0
				i+=t	
			i+=1
		#compatta toglie gli zeri in eccesso
		# [2,0,0,0,4,0,0,0] -> [2,0,0,4]
		NR=[]
		NM=[]
		i=0
		while i < 8:
			if r[i]<2:
				NR.append(r[i])
				NM.append(m[i])
				i+=1
			else:
				NR.append(r[i])
				NM.append(m[i])
				i+=r[i]
		#ritono liste nella griglia
		RitG[NuSeAtV]=NR
		GraG[NuSeAtV]=NM
		RigeneraMidi()

	def PlotNota(self,nota,lung,t,lun):
		col='yellow'
		h = self.RigoSeq.winfo_height()
		w = self.RigoSeq.winfo_width()
		s=2
		x1 = s+t*(w-s*2)/8
		y1 = s+(7-nota)*((h-s*2)/8)
		lu = (w-s*2)/8*lung*0.98
		al = (h-s*2)/10
		self.RigoSeq.create_rectangle(x1, y1, x1+lu, y1+al, fill=col)

	def PlotFromGM(self,M,R):
		self.RigoSeq.delete("all")
		i=0
		t=0
		while t < 8: # è sempre 8
			if R[i]>0:
				self.PlotNota(M[i],R[i],t,1)
				t+=R[i]
			else:
				t+=1
			i+=1
		r,m = ConvStrLargo(R,M)
		self.RiempiTk(r,m)

	def SetNuSeAtV(self):
		global NuSeAtV 
		NuSeAtV=int(self.tkSB_PatV.get())

	def AggScala(self,si):
		global Iscala
		global lS1
		global Scala
		global S1
		Iscala=int(si)
		S1=Scala[Iscala][0]
		lS1 = len(S1)
		self.lNP1.config(text=Scala[Iscala][1])
		self.AggPat()

	def AggNota(self, si):
		global keyNota
		keyNota=int(si)
		self.lRM1.config(text=notes[keyNota])
		self.AggPat()
	
	def NotaPat(self, i):
		n = notes[(S1[gPATT[i]%lS1]+keyNota)%12]
		return n


	def NotPat(self, i,event=None):
		for r,var in enumerate(self.lsb_PAT):
			gPATT[r] = int(var.get())
		n = self.NotaPat(i)
		self.ltla_PAT[i].config(text=n)
		self.LeggiDati()
	
	def AggPat(self):
		for r,n in enumerate(gPATT):
			n = self.NotaPat(r)
			self.ltla_PAT[r].config(text=n)
		RigeneraMidi()

	def outT(self, testo,NL='\n'):
		self.TC2.delete('1.0', tk.END)
		t=testo+NL
		self.TC2.insert(tk.END,t )

	def RigoNuovo(self):
		#width=760
		#height=280
		self.rigo.delete("all")
		for i in range (10):
			x1=5+i*480*4/23
			self.rigo.create_line(x1,0,x1,280,fill='red')
		for i in range (8):
			y1=(128-12*i)*3-115
			self.rigo.create_line(5,y1,757,y1,fill='red')
		for i in range (9):
			x1=5+i*480*4/23+240*4/23
			self.rigo.create_text(x1, 276, text=str(i))	 

	def PianoRoll(self, nota,tA,lun,p):
		col=['yellow','azure','bisque','brown3','CadetBlue1']
		if MuteD[p]==1:
			return
		s=5
		x1=tA/23
		rigoh=250
		if p<4:
			y1=(127-nota)*3-115
		else:
			y1=rigoh-nota*6+20
		
		l=lun/23
		h=3
		self.rigo.create_rectangle(s+x1,y1,s+x1+l,y1+h, fill=col[p])

	def LeggiDati(self):
		for r, row in enumerate(self.spinbox_PAT):
			for c, var in enumerate(row):
				aSceltaPat[r][c] = int(var.get())
		for r,var in enumerate(self.spinbox_OTT):
			OttavaD[r] = int(var.get())
		for r,var in enumerate(self.spinbox_EOT):
			EspOttD[r] = int(var.get())
		for r,var in enumerate(self.vtMute):
			MuteD[r] = var.get()
		for r,var in enumerate(self.sb_ACC):
			NoAcOt[r] = int(var.get())
		for r,var in enumerate(self.sb_Dac):
			DeAcGr[r] = int(var.get())
		for r,var in enumerate(self.lsb_PAT):
			gPATT[r] = int(var.get())
		RigeneraMidi()

	def SetPatAcc(self, e=None):
		gPATT = CalcolaPat(int(self.t_SB_SceGir.get()),self.vt_RB_SceTip.get())
		for i in range(9):
			self.lsb_PAT[i].set(str(gPATT[i]))
			self.NotPat(i)
		self.LeggiDati()
		RigeneraMidi()

	def ScriviDatiDK(self):
		for i,var in enumerate(self.vtkDrum):
			var.set(DrumRit[i+40*NuSeAtD])

	def TkDtoMem(self):
		for i,var in enumerate(self.vtkDrum):
			DrumRit[i+40*NuSeAtD]=int(var.get())
		RigeneraMidi()

############################################################

####### VARIABILI GLOBALI ##################

dizStum={} # Dizionario per strumenti {indice(0..127,'nomestrumento'}

notes = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

NOMEFILE='' # solo nome senza percorso ne estensione
PERCORSO='' # percorso nome estensione

NuSeAtV=0 # Numero sequenza Attivo Griglia Voce
NuSeAtD=0 # Numero sequenza Attivo Griglia Drum

# Lunghezza del brano 9 misure (ogni accordo una misura=4/4)
gPATT=[0,1,2,3,4,5,6,2,0] # grado dell'accordo nella battuta

aGiroAcc =[[0,5,1,4],[4,0,5,1],[0,5,4,5],[5,3,5,2],[0,3,4,2],[2,5,1,4]]
pGiroAcc = 0 #(0-5)
cSceForm = 1 #(0-1)  0 = ABCD+ABCD+0 1 = AABBCCDD+0

############ ACCORI SU 9 MISURE ###################
	# LISTA SCELTA DEL PATTERN USATO NELLA MISURA
	# Numero elementi dei Pattern = numero elementi del Giro di Accordi
	# -1= Misura vuota
#dati Nota Base (-1=non suona 0=Accordo di tonica)
PatV1= [ 0, 1, 2, 1,-1,-1,-1,-1, 3] # Pattern Voce1   0-3
PatV2= [-1,-1,-1,-1, 0, 1, 2, 1, 3] # Pattern Voce2   0-3
PatA = [ 0, 1, 2, 1, 2, 1, 3, 1, 3] # Pattern Accordi 0-3
PatB = [ 0, 1, 0, 2, 0, 1, 0, 2, 3] # Pattern Basso   0-3
PatD = [ 0, 0, 1, 1, 2, 2, 1, 2, 3] # Pattern Drum    0-3

#creazione griglia dei pattern 
aSceltaPat=[]

#riempimnto aSceltaPat
#non copia ma fa riferimento quindi non occorre ritornare i dati ai Pat..
aSceltaPat.append(PatV1) 
aSceltaPat.append(PatV2)
aSceltaPat.append(PatA)
aSceltaPat.append(PatB)
aSceltaPat.append(PatD)

Traccia=['Voce1','Voce2','Accordi','Basso','Drum']
MuteD  =[0,0,0,0,0]   # Definisce quale Traccia è Muta [1=Muta 0=Play]
StrumeD=[58,68,0,32]  # Definisce strumento per canale/traccia
OttavaD=[5,5,3,2]     # Ottava delle tracce
EspOttD=[2,1,2,2]     # Su quante ottave si espande

keyNota=0
Iscala =0
S1 = Scala[Iscala][0] # Scala 1 ottava
lS1=len(S1)

####################### DRUM #########################

nomeDrum=['Kick','Snare','CloseHH','OpenHH','Crash']
# Definisce la nota usata nel DRUM
NotD1 = 35 #Acoustic Bass Drum
NotD2 = 38 #Acoustic Snare
NotD3 = 42 #Close HiHat
NotD4 = 46 #Open HiHat
NotD5 = 49 #Crash Cymbal 1

#     !pattern Drum0   !pattern Drum1     !pattern Drum2    !pattern Drum3  
baD=[[1,0,0,0,1,0,0,0],[1,0,0,0,1,0,0,0],[1,1,0,0,1,1,0,0],[0,0,0,0,0,0,0,0]] # Acoustic Bass Drum
sna=[[0,0,1,0,0,0,1,0],[0,0,0,1,0,0,0,1],[0,1,0,0,0,1,0,0],[1,1,1,0,0,0,0,0]] # snare
cHH=[[1,0,1,0,1,0,1,0],[0,1,0,1,0,1,0,1],[1,1,1,1,1,1,1,0],[0,0,0,0,0,0,0,0]] # close HH
oHH=[[0,0,0,0,0,0,0,0],[1,0,1,0,1,0,1,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]] # open HH
pia=[[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[1,0,0,0,0,0,0,0]] # crash

DrumRit=[] # Array a una dimensione che contiene i 4 Drum Pattern 
for i in range(4):
   DrumRit = DrumRit + baD[i] +sna[i] + cHH[i] + oHH[i] + pia[i]

############# VOCE1 VOCE2 BASSO #########################

# Ritmo e Grado devono avere lo stesso numero di elementi per ogni lista
# per R  (0=rest 1..8 durate in 1/8 (totale somma 8 (-1 e 0 contano 1)))
# per G  distanza da nota base (Tonica)

########## Pattern Validi per V1 V2 BA
# Pattern Iniziali
PRIn =[[0,0,0,0,4],[0,0,0,0,2,2],[0,0,0,0,1,1,1,1],[0,0,4,2],[0,1,1,1,3,1]]
PGIn =[[0,0,0,0,2],[0,0,0,0,2,4],[0,0,0,0,5,4,3,2],[0,0,2,4],[0,0,2,0,5,4]]

# Pattern Finali
PRFi =[[8],[4,0,0,0,0],[2,0,0,0,0,0,0],[1,0,0,0,0,0,0,0,0],[4,4],[1,7],[2,6],[2,2,4],[1,1,2,4],[1,1,1,1,4],[1,1,6]]
PGFi =[[0],[0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[5,0],[4,0],[4,0],[2,4,7],[2,3,4,7],[2,5,2,5,7],[4,4,0]]

# Pattern Medi
PRMe =[[4,4],[2,2,2,2],[1,1,1,1,1,1,1,1],[4,2,2],[2,2,4],[2,4,2],[1,1,2,2,2],[1,2,1,2,2],[2,1,1,4]]
PGMe =[[4,0],[0,2,4,6],[0,2,4,6,5,4,3,2],[0,2,4],[1,3,4],[2,0,4],[1,2,1,3,4],[1,0,2,0,2],[4,3,2,0]]

########## Pattern Validi per Accordi
# La formazione del'accordo dipende da DeAcGr
NoAcOt=[0,1,0,1]  # NotaAccordo[x]= NoAcOt[x] * 12 Nota Accordo Ottava
DeAcGr=[0,2,4,-1] # NotaAccordo[x]= DeAcGr[x] *12  Delta Accordo Grado

# Pattern Accordi 
PRAIn =[[1,0,1,0,1,0,2],[4,2,2],[1,2,1,2,1,1],[2,2,4],[4,1,0,1,1],[1,1,1,1,1,1,1,1]]
PRAMe =[[0,1,0,1,0,1,2],[2,2,0,1,2],[1,2,1,2,0,0],[2,2,2,2],[1,1,2,1,1,2],[1,0,1,0,1,0,1,0]]
PRAFi =[[1,0,6],[2,1,1,4],[4,4],[2,6],[8],[1,1,6]]

######## RANDOM #####################

# Griglia (Ritmo e Grado)
RitG = [] # Ritmo Griglia
GraG = [] # Grado Griglia

seedNumber = 0

if __name__ == "__main__":
	global z
	RiempiRandom()
	lRit,lGra = ConvStrLargo(RitG[0],GraG[0]) #### Inizializza lRit e lGra 
	z = _GUI()
	z.ScriviDatiDK()
	RigeneraMidi()
	z.mainloop()
