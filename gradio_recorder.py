from datetime import date
import gradio as gr
from transformers import pipeline
import numpy as np
import os

from calendar_dates import get_all_events
from meeting_manager import write_to_database
from summarize_to_doc import meeting_minutes, save_as_docx

transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

def record_meeting(audio, meeting):
    sr, y = audio
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))
    
    audio_text = transcriber({"sampling_rate": sr, "raw": y})["text"]
    minutes = meeting_minutes(audio_text)
    audio_file_path = os.getenv("NOTES_DIR") + date.today().strftime('%Y-%m-%d-%HH') + f'{meeting}.txt'
    output_filename=os.path.basename(audio_file_path).replace("txt","docx")
    save_as_docx(minutes, os.getenv("SUMMARY_DOC_DIR") + output_filename)
    write_to_database(meeting, "output_filename")
    

with gr.Blocks() as demo:
  gr.Interface(
    fn=record_meeting,
    inputs=[gr.Audio(sources=["microphone"]), gr.Dropdown(label="Select Upcoming Meeting", choices=[event['summary'] for event in get_all_events()])],
    outputs="text",
    title="Transcribe and Associate with Meeting",
    description="Transcribe audio and select an upcoming meeting to associate with the transcription."
    # style=gr.styles.Card,
  )

if __name__ == "__main__":
    demo.launch()