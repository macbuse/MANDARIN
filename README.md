# AI mandarin

This is my personal project to learn mandarin. It is a work in
progress, but I have already made some using Gemini as a
tutor and using the following scripts:

- md2hanzi.py writes extracted_sentences.md
- flash_cards.py updates data.json (hanzi,pinyin,translation) and the mp3s in ./audio
- index.html probably needs to be run locally using **python -m http.server 8000**

---


So these will:
- convert hanzi to pinyin and englis
- scrape a sound for each hanzi phrase from google translate
- display in the browser with control buttons (show translation, next, exit)
