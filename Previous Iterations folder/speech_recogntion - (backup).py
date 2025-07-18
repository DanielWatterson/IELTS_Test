import speech_recognition as sr

recognizer = sr.Recognizer()

def listen_to_speech():
    """
    Listens for speech and converts it to text using SpeechRecognition.
    """
    with sr.Microphone() as source:
        print("Listening for your response...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print("You said: " + text)
        return text
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that. Could you repeat?")
        return ""
    except sr.RequestError as e:
        print(f"Request failed; {e}")
        return ""
