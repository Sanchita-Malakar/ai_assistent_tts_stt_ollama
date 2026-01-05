import sounddevice as sd
import numpy as np
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from config import STT_API_KEY, STT_URL

authenticator = IAMAuthenticator(STT_API_KEY)
stt = SpeechToTextV1(authenticator=authenticator)
stt.set_service_url(STT_URL)

def listen_and_convert():
    print("🎤 Speak now (clearly)...")

    duration = 5
    fs = 44100

    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
    sd.wait()

    audio_bytes = audio.tobytes()

    try:
        response = stt.recognize(
            audio=audio_bytes,
            content_type="audio/l16; rate=44100; channels=1",
            # KEY CHANGES FOR INDIAN ENGLISH:
            model="en-IN_Telephony",  # Indian English model
            # Alternative models you can try:
            # model="en-IN_BroadbandModel",  # Higher quality for non-telephony
            # model="en-GB_BroadbandModel",  # British English (closer to Indian)
            
            # Additional helpful parameters:
            smart_formatting=True,  # Better formatting of numbers, dates, etc.
            speech_detector_sensitivity=0.5,  # Adjust if too sensitive/not sensitive
            background_audio_suppression=0.5,  # Reduce background noise
            inactivity_timeout=5,  # Auto-stop after 5 seconds of silence
            end_of_phrase_silence_time=0.5  # Faster phrase detection
        ).get_result()

        print("🔍 Raw STT response:", response)

        # Return None if no speech detected
        if "results" not in response or len(response["results"]) == 0:
            print("⚠️ No speech detected.")
            return None

        transcript = response["results"][0]["alternatives"][0]["transcript"].strip()
        
        
        # Return None for empty transcripts
        if not transcript:
            return None
            
        return transcript

    except Exception as e:
        print(f"❌ STT Error: {e}")
        return None
