import requests
import pygame
import time
import os
from config import TTS_API_KEY, TTS_URL

# Initialize pygame mixer with better settings
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

def speak(text):
    """Convert text to speech and play audio"""
    if not text or not text.strip():
        print("⚠️ No text provided to speak")
        return
    
    print("🔊 Speaking:", text[:100] + "..." if len(text) > 100 else text)

    headers = {
        "Content-Type": "application/json",
        "Accept": "audio/wav"
    }

    auth = ("apikey", TTS_API_KEY)

    params = {
        "voice": "en-US_AllisonV3Voice"
    }

    payload = {
        "text": text
    }

    audio_file = None

    try:
        # Stop any currently playing audio
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            time.sleep(0.2)
        
        # Unload to release file handle
        try:
            pygame.mixer.music.unload()
        except:
            pass
        
        time.sleep(0.1)

        # Make TTS API request
        print("📡 Requesting audio from TTS API...")
        response = requests.post(
            TTS_URL,
            headers=headers,
            params=params,
            auth=auth,
            json=payload,
            stream=True,
            timeout=15
        )

        if response.status_code != 200:
            print(f"❌ TTS API Error (Status {response.status_code}):", response.text)
            return

        # Use unique filename with timestamp
        audio_file = f"response_{int(time.time() * 1000)}.wav"
        
        # Save audio file
        print(f"💾 Saving audio to {audio_file}...")
        with open(audio_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Verify file was created and has content
        if not os.path.exists(audio_file):
            print("❌ Audio file was not created")
            return
        
        file_size = os.path.getsize(audio_file)
        if file_size == 0:
            print("❌ Audio file is empty")
            return
        
        print(f"✅ Audio file saved ({file_size} bytes)")

        # Load and play audio
        print("🎵 Loading audio...")
        pygame.mixer.music.load(audio_file)
        
        print("▶️ Playing audio...")
        pygame.mixer.music.play()

        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        print("✅ Playback finished")
        
        # Unload to release file
        pygame.mixer.music.unload()
        time.sleep(0.2)
            
    except requests.Timeout:
        print("❌ TTS request timed out - check your internet connection")
    except requests.RequestException as e:
        print(f"❌ TTS Network Error: {e}")
    except pygame.error as e:
        print(f"❌ Audio Playback Error: {e}")
        print("   Check if audio file is valid WAV format")
    except Exception as e:
        print(f"❌ Unexpected Error: {type(e).__name__}: {e}")
    finally:
        # Clean up the audio file
        if audio_file and os.path.exists(audio_file):
            try:
                time.sleep(0.1)
                os.remove(audio_file)
                print(f"🗑️ Cleaned up {audio_file}")
            except PermissionError:
                print(f"⚠️ Could not delete {audio_file} (file in use)")
            except Exception as e:
                print(f"⚠️ Cleanup error: {e}")


# Test function
if __name__ == "__main__":
    print("Testing TTS...")
    speak("Hello! This is a test of the text to speech system.")
    print("Test complete!")