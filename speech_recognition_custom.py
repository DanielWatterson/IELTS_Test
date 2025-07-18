import speech_recognition as sr

def listen_to_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")  # Debugging statement
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for speech... Speak now.")  # Debugging statement
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Processing your speech...")  # Debugging statement
            text = recognizer.recognize_google(audio)
            print(f"Recognized Speech: {text}")  # Debugging statement
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio.")  # Debugging statement
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")  # Debugging statement
            return ""
        except Exception as e:
            print(f"An error occurred: {e}")  # Debugging statement
            return ""