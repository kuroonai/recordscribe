#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 23:22:36 2019

@author:Naveen Kumar Vasudevan, 
        400107764,
        Doctoral Student, 
        The Xi Research Group, 
        McMaster University, 
        Hamilton, 
        Canada.
        
        naveenovan@gmail.com
        https://naveenovan.wixsite.com/kuroonai
"""
'''

Usage

This code records the audio for a given time and translates it into the language one gives.
Python recordscribe.py /home/naveen/Desktop 30

                #en-US - English, US
                #en-IN - English, India
                #en-GB - English, UK
                #vi-VN - Vietnamese, Vietnam
                #ta-IN - Tamil, India
                #es-MX - Spanish, Mexico
                
'''

import pyaudio
import wave
import os
import sys

import speech_recognition as sr
from pydub import AudioSegment
import numpy as np
from tqdm import tqdm
from fnmatch import fnmatch

from googletrans import Translator
translator = Translator()


loc = sys.argv[1]
os.chdir(loc)

chunks = 1024
form = pyaudio.paInt16
chs = 2
rt = 44100
seconds_to_record = float(sys.argv[2])

if os.name == 'posix': WAVE_OUTPUT_FILENAME = loc+"/"+"transcript.wav"
elif os.name == 'nt' : WAVE_OUTPUT_FILENAME = loc+"\\"+"transcript.wav"

pya = pyaudio.PyAudio()

stm = pya.open(format=form,
                channels=chs,
                rate=rt,
                input=True,
                frames_per_buffer=chunks)

print("*** recording ***")

frames = []

for i in range(0, int(rt / chunks * seconds_to_record)):
    data = stm.read(chunks)
    frames.append(data)

print("* done recording")

stm.stop_stream()
stm.close()
pya.terminate()

wavefile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wavefile.setnchannels(chs)
wavefile.setsampwidth(pya.get_sample_size(form))
wavefile.setframerate(rt)
wavefile.writeframes(b''.join(frames))
wavefile.close()

#loc =  '/media/sf_dive/FFOutput' #sys.argv[1]
lang = input('enter language code to anticipate (eg: "en" for English, "ta" for Tamil and "es" for Spanish ... etc\t')
cut =  float(input('Length of transcript splice in second (recommended 3-10)\t'))

#alternates = sys.argv[4].split(',')

if os.name == 'posix':
    s = '/'
    os.chdir(s.join(loc.split('/')))
    fn ="%s.srt"%input('enter substitle filename (with no space or extension)\t')

elif os.name == 'nt':
    s = '\\'
    os.chdir(s.join(loc.split('\\')))
    fn ="%s.srt"%input('enter substitle filename (with no space or extension)\t')
    
wholeaudio = AudioSegment.from_wav(loc+"/"+"transcript.wav")
wholelen = len(wholeaudio)

os.remove(fn) if os.path.exists(fn) else None
os.remove("translated.srt") if os.path.exists("translated.srt") else None

for seq,t1t,t2t in tqdm(zip(range(1,int(wholelen/(cut*1000))+1),np.arange(0, round(wholelen/cut), cut), np.arange(cut, round(wholelen/cut)+cut, cut)), total=int(wholelen/(cut*1000)), unit = "seconds" ):
    #print(t1*1000,t2*1000, t2*1000-t1*1000)
    t1 = t1t*1000
    t2 = t2t*1000
    
    if t2 > wholelen : 
    
        break
# transcribe audio file                                                         
    #AUDIO_FILE = "transcript.wav"
    #wholeaudio = AudioSegment.from_wav("transcript.wav")
    newAudio = wholeaudio[t1:t2]
    newAudio.export('temp.wav', format="wav")

    newfile = 'temp.wav'
    # use the audio file as the audio source                                        
    r = sr.Recognizer()
    
    with sr.AudioFile(newfile) as source:
        audio = r.record(source)  # read the entire audio file                  
        
        #print("\n%d\n00:00:00,%d --> 00:00:00,%d"%(seq,t1,t2),file=open("output.srt", "a"))
        try:
            
            #print(r.recognize_google(audio, language="ta-IN"),file=open("output.srt", "a"))
            if fnmatch(lang,'en*'):
                trans = r.recognize_google(audio, language=lang)
                print("\n%d\n00:00:00,%d --> 00:00:00,%d"%(seq,t1,t2),file=open(fn, "a"))
                print(trans,file=open(fn, "a"))
            else:
                trans=translator.translate(r.recognize_google(audio, language=lang)).text
                print("\n%d\n00:00:00,%d --> 00:00:00,%d"%(seq,t1,t2),file=open(fn, "a"))
                print(trans,file=open(fn, "a"))
                #en-US - English, US
                #en-IN - English, India
                #en-GB - English, UK
                #vi-VN - Vietnamese, Vietnam
                #ta-IN - Tamil, India
                #es-MX - Spanish, Mexico
        except:
            pass
