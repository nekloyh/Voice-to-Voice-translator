import gradio as gr
import assemblyai as aai
from translate import Translator
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import uuid
from pathlib import Path


def voice_to_voice(audio_file, input_lang, output_lang):
    """
    Transcribes audio, translate itm and convert it to speech in a specified language

    Args:
        audio_file (): _description_
        input_lang ():
        output_lang ():

    Raises:
        gr.Error: _description_
    """
    input_lang_code = LANGUAGE_CODES[input_lang]
    output_lang_code = LANGUAGE_CODES[output_lang]
        
    transcription_response = audio_transcription(audio_file, input_lang_code)
    
    if transcription_response.status == aai.TranscriptStatus.error:
        raise gr.Error(transcription_response.error)
    else:
        text = transcription_response.text
    
    translated_text = text_translation(text, input_lang_code, output_lang_code)
    
    output_audi_path = text_to_speech(translated_text, output_lang_code)
    
    return Path(output_audi_path)


def audio_transcription(audio_file, lang_code="en"):
    """Transcribe speech in audio file to text using AssemblyAI

    Args:
        audio_file (_type_): _description_
        lang_code (str): 

    Returns:
        str: Transcribed text from the audio file
    """
    aai.setting.api_key = ""
    
    transcriber = aai.Transcriber()
    transcription = transcriber.transcribe(audio_file)

    return transcription


def text_translation(text, from_lang="en", to_lang="ja"):
    """Translate English text to Japanese

    Args:
        text (str): Text to translate.
        from_lang (str): Language code of the source language.
        to_lang (str): Language code of the target language.

    Returns:
        str: translateed text in Japanese
    """
    translator = Translator(from_lang=from_lang, to_lang=to_lang)
    translator_text = translator.translate(text)
    
    return translator_text


def text_to_speech(text, lang_code="ja"):

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

LANGUAGE_CODES = {
    "English": "en",
    "Vietnamese": "vi",
    "Japanese": "ja",  
    "Chinese": "zh",
    "Filipino": "fil",
    "French": "fr",
}

input_lang = gr.Dropdown(
    label = "Input Language", 
    choices = list(LANGUAGE_CODES.keys()),
    value = "English"
)

output_lang = gr.Dropdown(
    label="Output Language", 
    choices = list(LANGUAGE_CODES.keys()) ,
    value = "Vietnamese"
)


demo = gr.Interface(
    fn = voice_to_voice,
    inputs = [audio_input, input_lang, output_lang],
    outputs = gr.Audio(label="Translated Speech"),
    live = False
)


if __name__ == "__main__":
    demo.launch()
    