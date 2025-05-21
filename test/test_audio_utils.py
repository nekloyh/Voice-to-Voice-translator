import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.audio_utils import speech_to_text

text = speech_to_text("audio/What-Makes-Kurzgesagt-So-Special-.wav", lang="en")
print("Transcribed text:", text)