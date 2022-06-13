#!/usr/bin/env python3
import queue
import sounddevice as sd
import vosk
import sys
import json
import requests
import time

url = '****'
control = '/device/light/control'
myobj = {'auth_key': '****',
         'id': ''}
lamps = {'children': ['3494546b6ed5'],
         'study': ['e8db84a9e51b'],
         'center': ['e8db84aa6528', 'e8db84a9e9d1'],
         'kitchen': ['c45bbe7565ee', 'c45bbe7715e2', 'c45bbe75891a']
         }

q = queue.Queue()


def callback(indata, frames, time, status):
    q.put(bytes(indata))


try:
    model = vosk.Model(lang="en-us")
    with sd.RawInputStream(samplerate=44100, blocksize=8000, device=None,
                           dtype='int16', channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, 44100)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result())['text']
                if text:
                    print(text)
                if "jack" in text:
                    for key in lamps:
                        if key in text or "everything" in text:
                            for device in lamps[key]:
                                if "on" in text:
                                    myobj['turn'] = 'on'
                                    print("SWITCHING %s - on" % device)
                                    myobj['id'] = device
                                    requests.post(url+control, data=myobj)
                                    time.sleep(1.5)
                                if "off" in text:
                                    myobj['turn'] = 'off'
                                    myobj['id'] = device
                                    print("SWITCHING %s - off" % device)
                                    requests.post(url+control, data=myobj)
                                    time.sleep(1.5)
except KeyboardInterrupt:
    sys.exit(0)
except Exception as e:
    sys.exit(type(e).__name__ + ': ' + str(e))
