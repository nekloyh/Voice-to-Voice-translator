import gradio as gr
import assemblyai as aai
from translate import Translator
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import uuid
from pathlib import Path


def voice_to_voice(audio_file):
    """_summary_

    Args:
        audio_file (_type_): _description_

    Raises:
        gr.Error: _description_
    """
    transcription_response = audio_transcription(audio_file)
    
    if transcription_response.status == aai.TranscriptStatus.error:
        raise gr.Error(transcription_response.error)
    else:
        text = transcription_response.text
    
    ja_translation = text_translation(text)
    
    ja_audi_path = text_to_speech(ja_translation)
    
    ja_path = Path(ja_audi_path)
    
    return ja_path


def audio_transcription(audio_file):
    """Transcribe speech in audio file to text using AssemblyAI

    Args:
        audio_file (_type_): _description_

    Returns:
        str: Transcribed text from the audio file
    """
    aai.setting.api_key = ""
    
    transcriber = aai.Transcriber()
    transcription = transcriber.transcribe(audio_file)

    return transcription


def text_translation(text):
    """Translate English text to Japanese

    Args:
        text (str): given text in English

    Returns:
        str: translateed text in Japanese
    """
    translator_ja = Translator(from_lang="en", to_lang="ja")
    ja_text = translator_ja.translate(text)
    
    return ja_text


def text_to_speech(text):

    client = ElevenLabs(
        api_key = "",
    )
    
    response = client.text_to_speech.convert(
        voice_id = "",
        optimize_streaming_latency = "0",
        output_format = "mp3_22050_32",
        text = text,
        model_id = "eleven_multiligual_v2",
        voice_settings = VoiceSettings(
            stability = 0.5,
            similarity_boost = 0.8,
            style = 0.5,
            use_speaker_boost = True,
        ),
    )

    save_file_path = f"{uuid.uuid4()}.mp3"

    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
                
    print(f"{save_file_path}: A new audio file was saved successfully!")
    
    return save_file_path


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
    