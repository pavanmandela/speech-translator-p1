from flask import Flask, request, jsonify, render_template
import speech_recognition as spr
from googletrans import Translator
from gtts import gTTS
import os
import traceback
import glob

app = Flask(__name__, static_folder='static', template_folder='templates')

# Map of supported languages
language_map = {
    'Hindi': 'hi',
    'Telugu': 'te',
    'Kannada': 'kn',
    'Tamil': 'ta',
    'Malayalam': 'ml',
    'Bengali': 'bn',
    'English': 'en'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate_speech():
    try:
        target_language = request.form.get('target_language')
        if target_language not in language_map:
            return jsonify({"error": "Invalid language selected"}), 400

        target_language_code = language_map[target_language]
        recog1 = spr.Recognizer()
        mc = spr.Microphone()

        # Capture and recognize speech
        with mc as source:
            recog1.adjust_for_ambient_noise(source, duration=0.2)
            print("Listening for speech...")
            audio = recog1.listen(source)

        try:
            recognized_text = recog1.recognize_google(audio)
        except spr.UnknownValueError:
            return jsonify({"error": "Speech was not clear, please try again."}), 400
        except spr.RequestError as e:
            return jsonify({"error": f"Speech recognition service error: {e}"}), 500

        print(f"Recognized Text: {recognized_text}")

        # Translate the recognized text
        translator = Translator()
        detected_language = translator.detect(recognized_text).lang
        translated = translator.translate(recognized_text, src=detected_language, dest=target_language_code)
        translated_text = translated.text

        # Generate audio for the translated text
        audio_file_path = f"static/outputs/translated_audio.mp3"
        speak = gTTS(text=translated_text, lang=target_language_code, slow=False)
        speak.save(audio_file_path)

        return jsonify({
            "recognized_text": recognized_text,
            "detected_language": detected_language,
            "translated_text": translated_text,
            "audio_file": f"/static/outputs/translated_audio.mp3"
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def cleanup_audio_files():
    files = glob.glob('static/outputs/*.mp3')
    for f in files:
        os.remove(f)

if __name__ == '__main__':
    if not os.path.exists('static/outputs'):
        os.makedirs('static/outputs')
    cleanup_audio_files()
    app.run(debug=True)
