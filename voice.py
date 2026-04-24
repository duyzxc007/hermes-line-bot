import os
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import uuid

# We will save static audio files in the 'static' folder
STATIC_DIR = "static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

def convert_m4a_to_wav(m4a_path: str, wav_path: str):
    """Converts LINE's m4a/aac audio to wav for SpeechRecognition."""
    try:
        audio = AudioSegment.from_file(m4a_path)
        audio.export(wav_path, format="wav")
        return True
    except Exception as e:
        print(f"Error converting audio: {e}")
        return False

def transcribe_audio(wav_path: str) -> str:
    """Uses Google's free Speech Recognition API to convert speech to text."""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            # Recognize Thai language
            text = recognizer.recognize_google(audio_data, language="th-TH")
            return text
    except sr.UnknownValueError:
        return "ขออภัย ฉันฟังที่คุณพูดไม่ออกครับ"
    except sr.RequestError as e:
        return f"ระบบแปลงเสียงมีปัญหา: {e}"
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการแปลงเสียง: {e}"

def generate_tts(text: str) -> str:
    """Converts text to speech and saves it as an MP3 file. Returns the filename."""
    filename = f"reply_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(STATIC_DIR, filename)
    
    try:
        tts = gTTS(text=text, lang="th")
        tts.save(filepath)
        return filename
    except Exception as e:
        print(f"TTS Error: {e}")
        return ""
