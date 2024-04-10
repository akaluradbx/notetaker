import gradio as gr
from transformers import pipeline
import numpy as np

from summarize_to_doc import meeting_minutes

transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

def transcribe(audio):
    sr, y = audio
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))
    
    audio_text = transcriber({"sampling_rate": sr, "raw": y})["text"]
    return meeting_minutes(audio_text)


demo = gr.Interface(
    transcribe,
    gr.Audio(sources=["microphone"]),
    "text",
)

demo.launch()
