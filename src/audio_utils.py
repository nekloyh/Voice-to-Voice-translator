import wave
import json
from vosk import Model, KaldiRecognizer

def speech_to_text(audio_path, lang='en'):
    model_paths = {
        'en': 'models\\vosk-model-en-us-0.22',
        'vn': 'models\\vosk-model-vn-0.4'
    }
    
    model = Model(model_paths[lang])
    wf = wave.open(audio_path, 'rb')
    rec = KaldiRecognizer(model, wf.getframerate())
    
    result_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result_text += res.get("text", "") + " "
    
    return result_text.strip()