# Personal Assistant
This program with capture your audio, convert that to text in realtime.   
You will then be able to summarize the raw text into following section using Databricks DBRX LLM program
1) Abstract Summary
2) Key Points discussed during the meeting
3) Action Items
4) Highlights Sentiment during the meeting
5) Generates a sample followup email sumarizing the meeting


# Step 0 : Onetime Setup

mkdir notes
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/openai/whisper.git
pip install sounddevice numpy whisper torch python-dotenv requests python-docx 

update .env with databricks token and databricks hostname

# Step1 : Run this command to capture audio and have the audio be converted in realtime to text
python VoiceToText.py 

# Step2 : Summarize text
python summarize_to_doc.py "NOTES FILENAME"
