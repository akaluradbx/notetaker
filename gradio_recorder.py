import gradio as gr
from transformers import pipeline
import numpy as np

from calendar_dates import get_all_events
from summarize_to_doc import meeting_minutes

transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

def transcribe(audio):
    sr, y = audio
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))
    
    audio_text = transcriber({"sampling_rate": sr, "raw": y})["text"]
    return meeting_minutes(audio_text)


iface = gr.Interface(
    fn=transcribe,
    inputs=[gr.Audio(sources=["microphone"]), gr.Dropdown(label="Select Upcoming Meeting", choices=[event['summary'] for event in get_all_events()])],
    outputs="text",
    title="Transcribe and Associate with Meeting",
    description="Transcribe audio and select an upcoming meeting to associate with the transcription."
    # style=gr.styles.Card,
)

iface.launch()
