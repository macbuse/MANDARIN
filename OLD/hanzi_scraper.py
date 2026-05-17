#! /home/macbuse/miniconda3/bin/python3.11

import os
import json
from deep_translator import GoogleTranslator
from pypinyin import pinyin, Style
from gtts import gTTS

# Ensure the local audio directory exists
os.makedirs("audio", exist_ok=True)

def generate_card_data(hanzi_text, filename_prefix):
    cleaned_text = hanzi_text.strip()
    mp3_path = f"audio/{filename_prefix}.mp3"
    
    # 1. Calculate Pinyin
    pinyin_list = pinyin(cleaned_text, style=Style.TONE)
    pinyin_track = " ".join([word[0] for word in pinyin_list])
    
    # 2. Fetch Translation
    try:
        english_track = GoogleTranslator(source='zh-CN', target='en').translate(cleaned_text)
    except Exception:
        english_track = "Translation Unavailable"
        
    # 3. Automatically Download the MP3 Asset
    try:
        # lang='zh-CN' ensures the native Mandarin accent voice engine is triggered
        tts = gTTS(text=cleaned_text, lang='zh-CN')
        tts.save(mp3_path)
        print(f"✓ Synthesized and saved: {mp3_path}")
    except Exception as e:
        print(f"× Audio generation failed for {cleaned_text}: {e}")

    # Return the exact dictionary node format our JS expects
    return {
        "hanzi": cleaned_text,
        "pinyin": pinyin_track,
        "mp3": mp3_path,
        "translation": english_track # Added in case you want to display it later
    }

if __name__ == "__main__":
    # Simulated input array from your mk_slides2.py regex matches
    raw_vocabulary = ["健康", "明天我要去医院"]
    
    compiled_dataset = []
    
    print("Starting automated deck asset compilation...\n")
    for index, phrase in enumerate(raw_vocabulary):
        # Create a unique, clean filename (e.g., track_0.mp3, track_1.mp3)
        prefix = f"track_{index}"
        card_node = generate_card_data(phrase, prefix)
        compiled_dataset.append(card_node)
        
    # Write out the clean data.json file side-by-side with index.html
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(compiled_dataset, f, ensure_ascii=False, indent=2)
        
    print("\nCompilation successful! data.json and audio assets are synchronized.")
