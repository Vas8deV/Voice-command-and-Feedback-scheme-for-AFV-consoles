from transformers import pipeline
import time
import re
import json
import fastwer

def clean_string(text):
  
  text = re.sub(r"[^\w\d]", " ", text)
  text = re.sub(r"\s+", " ", text)
  text = text.strip().lower()
  return text

# with open(r"C:\Users\batma\vocabulary\speech_dataset_vino.json", "r") as file:
with open(r"C:\Users\batma\vocabulary\wav_text_data.json", "r") as file:
    loaded_data = json.load(file)
output_data=[]

transcriber = pipeline("automatic-speech-recognition", model=r"C:\Users\batma\vocabulary\hugging\wav2vec2-base-960h")
# transcriber.save_pretrained("wav2vec2-base-960h")

for key, value in loaded_data.items():
    # path=f"C:/Users/batma/vocabulary/vino/{key}.wav"
    path=key
    start=time.time()
    result=transcriber(path)
    duration=time.time()-start
    print("execution time: %s seconds"%(duration))
    print("Reference text: ",value)
    print("Transcribed text: ",result["text"])
    out=clean_string(result["text"])
    print("Transform text:", out)
    wer = fastwer.score_sent(out, value)
    cer = fastwer.score_sent(out, value, char_level=True)
    print("WER%: ", wer)
    print("CER%: ", cer)
    print()

    output_data.append({
        "filename": key,
        "reference_text": value,
        "transcribed_text": result["text"],
        "transformed_text": out,
        "wer %": fastwer.score_sent(out, value),
        "cer %": fastwer.score_sent(out, value, char_level=True),
        "execution_time": duration
    })
    print(f"Processed file: {key}")  # Optional progress indicator

import pandas as pd
df = pd.DataFrame(output_data)
filename = r"C:\Users\batma\OneDrive\Desktop\eval_results\updated\nptel_wav2vec.xlsx"
df.to_excel(filename, index=False)  # Set `index=False` to avoid extra index column
print(f"Results exported to Excel file: {filename}")    



    
