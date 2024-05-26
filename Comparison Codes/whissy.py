import whisper
import time
import json
import fastwer
import re
import os

def clean_string(text):
  
  text = re.sub(r"[^\w\d]", " ", text)
  text = re.sub(r"\s+", " ", text)
  text = text.strip().lower()
  return text

model = whisper.load_model("base.en")
i=1
output_data=[]
noisedir=r"C:\Users\batma\vocabulary\AFV\Mbinsiewithvasu"
with open(r"C:\Users\batma\vocabulary\speech_dataset_vasu.json", "r") as file:
# with open(r"C:\Users\batma\vocabulary\wav_text_data.json", "r") as file:
    loaded_data = json.load(file)
for _ , value in loaded_data.items():
    max=21
    for noisewavname in os.listdir(noisedir):
        if noisewavname.endswith(".wav") and max>0:  
            noisewav_path = os.path.join(noisedir, noisewavname)
            # path=f"C:/Users/batma/vocabulary/vasu/{key}.wav"
            path=noisewav_path
            start=time.time()
            result=model.transcribe(path)
            duration=time.time()-start
            print(f"file number {i}")
            i+=1
            print("execution time: %s seconds"%(duration))
            print("Reference text: ",value)
            print("Transcribed text: ",result["text"])
            out=clean_string(result["text"])
            print("WER%: ",fastwer.score_sent(out, value))
            print("CER%: ",fastwer.score_sent(out, value, char_level=True))

            output_data.append({
                "filename": noisewavname,
                "reference_text": value,
                "transcribed_text": result["text"],
                "transformed_text": out,
                "wer%": fastwer.score_sent(out, value),
                "cer%": fastwer.score_sent(out, value, char_level=True),
                "execution_time": duration
            })

            print(f"Processed file: {noisewavname}")  # Optional progress indicator
            print()
            max=max-1
        if max==0:
            break

import pandas as pd
df = pd.DataFrame(output_data)
filename = r"C:\Users\batma\OneDrive\Desktop\eval_results\updated\noiseMbinside_whisper.xlsx"
df.to_excel(filename, index=False,)  # Set `index=False` to avoid extra index column
print(f"Results exported to Excel file: {filename}")



    
