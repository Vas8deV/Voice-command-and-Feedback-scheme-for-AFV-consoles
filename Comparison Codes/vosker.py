# AUDIO QUALITY
# AUDIO CODEC - PCM_S16LE 24 BIT UNCOMPRESSED
# MONO CHANNEL
# 16  KHZ SAMPLING RATE

import subprocess, sys, os, json
import time
from vosk import Model, KaldiRecognizer
import json
import fastwer
import re


SAMPLE_RATE = 16000
CHUNK_SIZE = 4000
def clean_string(text):
  
  text = re.sub(r"[^\w\d]", " ", text)
  text = re.sub(r"\s+", " ", text)
  text = text.strip().lower()
  return text

class Transcriber():
    def __init__(self, model_path):
        self.model = Model(model_path)

    def fmt(self, data):
        data = json.loads(data)
        return {
            "text": data["text"]
        }

    def transcribe(self, path):
        rec = KaldiRecognizer(self.model, SAMPLE_RATE)
        rec.SetWords(True)

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        transcription = []

        ffmpeg_command = [
                "ffmpeg",
                "-nostdin",
                "-loglevel",
                "quiet",
                "-i",
                path,
                "-ar",
                str(SAMPLE_RATE),
                "-ac",
                "1",
                "-f",
                "s16le",
                "-",
            ]

        with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE) as process:

            start_time=time.time() 
            while True:
                data = process.stdout.read(4000)
                if len(data) == 0:
                    break
                
                if rec.AcceptWaveform(data):
                    transcription.append(self.fmt(rec.Result()))

            transcription.append(self.fmt(rec.FinalResult()))
            end_time = time.time()

            time_elapsed = end_time - start_time
            print(f"Time elapsed  {time_elapsed}")

        return {
            "elapsed_time": time_elapsed,
            "transcription": transcription,
        }


model_path = r"C:\Users\batma\vocabulary\vosk_test_performance\model_in_small"
transcriber = Transcriber(model_path)
output_data=[]
i=1

# with open(r"C:\Users\batma\vocabulary\speech_dataset_vino.json", "r") as file:
with open(r"C:\Users\batma\vocabulary\wav_text_data.json", "r") as file:
    loaded_data = json.load(file)
for key, value in loaded_data.items():
    # path=f"C:/Users/batma/vocabulary/vino/{key}.wav"
    path=key
    transcription = transcriber.transcribe(path)
    duration=transcription["elapsed_time"]
    textresult = " ".join([result["text"] for result in transcription["transcription"]])
    print("Reference text: ",value)
    print("Transcribed text: ",textresult)
    out=clean_string(textresult)
    wer = fastwer.score_sent(out, value)
    cer = fastwer.score_sent(out, value, char_level=True)
    print("WER%: ", wer)
    print("CER%: ", cer)
    print()

    output_data.append({
        "filename": key,
        "reference_text": value,
        "transcribed_text": textresult,
        "transformed_text":out,
        "wer%": fastwer.score_sent(out, value),
        "cer%": fastwer.score_sent(out, value, char_level=True),
        "execution_time": duration
    })
    print(f"Processed file: {key}")  # Optional progress indicator
    print(f"file number {i}")
    i+=1

import pandas as pd
df = pd.DataFrame(output_data)
filename = r"C:\Users\batma\OneDrive\Desktop\eval_results\updated\nptel_vosk.xlsx"
df.to_excel(filename, index=False)  # Set `index=False` to avoid extra index column
print(f"Results exported to Excel file: {filename}")

