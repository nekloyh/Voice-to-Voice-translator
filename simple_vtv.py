import gradio as gr
import assemblyai as aai
from translate import Translator
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import uuid
from pathlib import Path

def voice_to_voice(audio_file):
    transcription_response = audio_transcription(audio_file)
    
    if transcription_response.status == aai.TranscriptStatus.error:
        raise gr.Error(transcription_response.error)
    else:
        text = transcription_response.text
    
    jp_translation = text_translation(text)

def audio_transcription(audio_file):
    aai.setting.api_key = ""
    
    transcriber = aai.Transcriber()
    transcription = transcriber.transcribe(audio_file)

    return transcription

def text_translation(text):
    translator_ja = Translator(from_lang="en", to_lang="ja")
    ja_text = translator_ja.translate(text)
    
    return ja_text

def text_to_speech():
    client = ElevenLabs(
        api_key = "",
    )
    
    response = client.text_to_speech.convert(
        
    )
    pass

audio_input = gr.Audio(
    sources=["microphone"],
    type="filepath"
)

demo = gr.Interface(
    fn=voice_to_voice,
    inputs=audio_input,
    outputs=[gr.Audio(label="Japanese")]
)


if __name__ == "__main__":
    demo.launch()
    