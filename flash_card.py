#! /home/macbuse/miniconda3/bin/python3.11
import re
from deep_translator import GoogleTranslator
from pypinyin import pinyin, Style

def get_pinyin(hanzi_text):
    """
    Converts Hanzi into Pinyin with proper tone marks.
    Example: '健康' -> 'jiàn kāng'
    """
    # style=Style.TONE gives us standard diacritics (à, ē, mǎ)
    pinyin_list = pinyin(hanzi_text, style=Style.TONE)
    # Flatten the list of lists into a single space-separated string
    return " ".join([word[0] for word in pinyin_list])

def get_translation(hanzi_text):
    """
    Fetches the English translation from Google Translate safely.
    """
    try:
        translator = GoogleTranslator(source='zh-CN', target='en')
        return translator.translate(hanzi_text)
    except Exception as e:
        return f"Translation Error: {e}"

def generate_anki_line(hanzi_text):
    """
    Processes the raw Chinese string into a clean, tab-separated Anki row.
    Format: Hanzi \t Pinyin \t English
    """
    # Clean up any trailing whitespace or punctuation if necessary
    cleaned_text = hanzi_text.strip()
    
    pinyin_track = get_pinyin(cleaned_text)
    english_track = get_translation(cleaned_text)
    
    # Return a single tab-separated line
    return f"{cleaned_text}\t{pinyin_track}\t{english_track}"

# --- Test Execution ---
if __name__ == "__main__":
    # Simulate a list of matched strings your FSA extracted from mk_slides2.py
    extracted_vocabulary = ["健康", "身体", "明天我要去医院"]
    
    print("Generating flashcard file content...\n")
    for item in extracted_vocabulary:
        anki_row = generate_anki_line(item)
        print(anki_row)
