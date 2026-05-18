#! /home/macbuse/miniconda3/bin/python3.11
import os
import json
import urllib.parse
import time
import re
import base64
import asyncio
import requests
from bs4 import BeautifulSoup
import edge_tts

# Configuration file paths
INPUT_FILE = "input_phrases.md"
OUTPUT_FILE = "mandarin_flashcards.json"
AUDIO_DIR = "audio"

os.makedirs(AUDIO_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def load_existing_json(filepath):
    """Loads existing master flashcard data to prevent overwriting or re-downloading."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {filepath} was corrupted. Starting fresh.")
            return []
    return []

def parse_input_text(filepath):
    """Reads the raw text file and parses the fields into a list of dictionaries."""
    parsed_items = []
    if not os.path.exists(filepath):
        print(f"Error: Source file '{filepath}' not found. Please create it first.")
        return parsed_items

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): # Skip empty lines or comments
                continue
            
            parts = line.split("|")
            if len(parts) == 4:
                parsed_items.append({
                    "hanzi": parts[0].strip(),
                    "pinyin": parts[1].strip(),
                    "english": parts[2].strip(),
                    "category": parts[3].strip()
                })
    return parsed_items

def fetch_forvo_mp3(clean_hanzi):
    """Attempts to scrape human native audio from Forvo."""
    encoded_query = urllib.parse.quote(clean_hanzi)
    search_url = f"https://forvo.com/search/{encoded_query}/zh/"

    try:
        response = requests.get(search_url, headers=headers, timeout=5)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        play_element = soup.find(class_="play")
        if not play_element:
            return None

        onclick_attr = play_element.get('onclick', '')
        matches = re.findall(r"'(.*?)'", onclick_attr)
        
        if len(matches) >= 2:
            b64_path = matches[1]
            decoded_path = base64.b64decode(b64_path).decode('utf-8')
            mp3_url = f"https://audio00.forvo.com/mp3/{decoded_path}"
            
            audio_response = requests.get(mp3_url, headers=headers, timeout=5)
            if audio_response.status_code == 200:
                filepath = os.path.join(AUDIO_DIR, f"{clean_hanzi}.mp3")
                with open(filepath, "wb") as f:
                    f.write(audio_response.content)
                return filepath
    except Exception:
        pass
    return None

async def fetch_fallback_tts(clean_hanzi):
    """Fallback: Generates high-quality neural TTS using MS Edge."""
    filepath = os.path.join(AUDIO_DIR, f"{clean_hanzi}.mp3")
    voice = "zh-CN-YunxiNeural" 
    try:
        communicate = edge_tts.Communicate(clean_hanzi, voice)
        await communicate.save(filepath)
        return filepath
    except Exception as e:
        print(f"Fallback failed for '{clean_hanzi}': {e}")
        return None

async def main():
    # Load what we already have processed
    master_deck = load_existing_json(OUTPUT_FILE)
    existing_hanzi = {item["hanzi"] for item in master_deck}
    
    # Load new targets from text file
    incoming_phrases = parse_input_text(INPUT_FILE)
    
    new_additions_count = 0

    for item in incoming_phrases:
        hanzi = item["hanzi"]
        
        # Skip if this phrase already exists in the master JSON database
        if hanzi in existing_hanzi:
            continue
            
        clean_hanzi = "".join([c for c in hanzi if c not in "？。！,?!"])
        print(f"Processing new entry: {hanzi}")
        
        # Try Forvo, then Fallback
        audio_path = fetch_forvo_mp3(clean_hanzi)
        if audio_path:
            print(f" -> Sourced: Forvo (Human)")
        else:
            print(f" -> Forvo missing. Generating Neural TTS...")
            audio_path = await fetch_fallback_tts(clean_hanzi)
            if audio_path:
                print(f" -> Sourced: Neural TTS")

        item["audio_src"] = audio_path if audio_path else ""
        
        # Append directly to our active database list in memory
        master_deck.append(item)
        existing_hanzi.add(hanzi)
        new_additions_count += 1
        
        print("-" * 40)
        time.sleep(1.0) # Rate limit safety

    # Save the updated master array back to the JSON file
    if new_additions_count > 0:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(master_deck, f, ensure_ascii=False, indent=2)
        print(f"\nSuccess! Added {new_additions_count} new entries to {OUTPUT_FILE}")
    else:
        print("\nNo new phrases found. Database is completely up to date.")

if __name__ == "__main__":
    asyncio.run(main())
