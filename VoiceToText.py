import sounddevice as sd
import numpy as np

import whisper

import asyncio
import queue
import sys
import torch
import time

import os
from dotenv import load_dotenv, dotenv_values

# loading variables from .env file
load_dotenv()

#Create a file with current datetime
notes_filename=os.getenv("NOTES_DIR") +  time.strftime("%Y%m%d-%H%M%S") + ".txt"
file1 = open(notes_filename, "w")
L = ["Notes taken on : " + time.strftime("%Y%m%d-%H%M%S")+" \n"]
file1.writelines(L)
file1.close()

# SETTINGS
MODEL_TYPE="medium" #"base.en"
# the model used for transcription. https://github.com/openai/whisper#available-models-and-languages
LANGUAGE="English"
# pre-set the language to avoid autodetection
BLOCKSIZE=256000 #24678 
# this is the base chunk size the audio is split into in samples. blocksize / 16000 = chunk length in seconds. 
SILENCE_THRESHOLD=400
# should be set to the lowest sample amplitude that the speech in the audio material has
SILENCE_RATIO=100
# number of samples in one buffer that are allowed to be higher than threshold


global_ndarray = None
model = whisper.load_model(MODEL_TYPE)

async def inputstream():
	"""Generator that yields blocks of input data as NumPy arrays."""
	myqueue = asyncio.Queue()
	myloop = asyncio.get_event_loop()

	def callback(indata, frame_count, time_info, status):
		myloop.call_soon_threadsafe(myqueue.put_nowait, (indata.copy(), status))

	stream = sd.InputStream(samplerate=16000, channels=1, dtype='int16', blocksize=BLOCKSIZE, callback=callback)
	with stream:
		while True:
			indata, status = await myqueue.get()
			yield indata, status
			
		
async def myrecorder():
	global global_ndarray
	async for indata, status in inputstream():
		
		start=time.strftime("%Y%m%d-%H%M%S")
		indata_flattened = abs(indata.flatten())
				
		# discard buffers that contain mostly silence
		if(np.asarray(np.where(indata_flattened > SILENCE_THRESHOLD)).size < SILENCE_RATIO):
			continue
		
		if (global_ndarray is not None):
			global_ndarray = np.concatenate((global_ndarray, indata), dtype='int16')
		else:
			global_ndarray = indata
		# concatenate buffers if the end of the current buffer is not silent
		local_ndarray = global_ndarray.copy()
		global_ndarray = None
		indata_transformed = local_ndarray.flatten().astype(np.float32) / 32768.0
		# Convert Audio buffer to Text using whisper model
		result = model.transcribe(indata_transformed, language=LANGUAGE, fp16=torch.cuda.is_available())
		global_ndarray = None
		text=result["text"]
		# Append Converted text to end of file
		file1 = open(notes_filename, "a")  # append mode
		file1.write(text+" \n")
		file1.close()
			
		del local_ndarray
		del indata_flattened


async def main():
	print(notes_filename+'\n CTRL-C to quit')
	audio_task = asyncio.create_task(myrecorder())
	while True:
		await asyncio.sleep(1)

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		sys.exit()