import os
import tkinter as tk
from grammar_check import check_grammar
from ielts_test import get_ielts_questions, calculate_ielts_score
import speech_recognition as sr
from fpdf import FPDF
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import language_tool_python

# Specify a custom NLTK data directory (within the project directory)
nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)
nltk.data.path.append(nltk_data_dir)
nltk.download('punkt', download_dir=nltk_data_dir)

# Global variables for test state
question_index = 0
responses = []
feedback = []
test_mode = False  # Tracks whether it's Test Mode or Practice Mode

# Initialize the recognizer
recognizer = sr.Recognizer()

def listen_to_speech():
    """
    Records and processes speech input using the microphone.
    """
    with sr.Microphone() as source:
        recording_label.config(text="Recording... Please speak now.")
        window.update()
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        recording_label.config(text="Recording complete.")
        return text
    except sr.UnknownValueError:
        recording_label.config(text="Sorry, I couldn't understand. Please try again.")
        return ""
    except sr.RequestError as e:
        recording_label.config(text=f"Error during recording: {e}")
        return ""

def custom_feedback(text, question):
    """
    Generates feedback combining grammar, sentence structure, vocabulary, and context suggestions.
    """
    tool = language_tool_python.LanguageTool('en-US')
    grammar_issues = tool.check(text)
    grammar_feedback = [f"Issue: {issue.message}\nSuggestion: {issue.replacements}" for issue in grammar_issues]

    # Vocabulary suggestions
    vocabulary_feedback = []
    if "very" in text:
        vocabulary_feedback.append("Consider replacing 'very' with a more specific term (e.g., 'extremely').")

    # Contextual feedback
    context_feedback = []
    if "hobbies" in question.lower() and len(text.split()) < 5:
        context_feedback.append("Try expanding your hobbies with more details.")
    
    feedback_list = grammar_feedback + vocabulary_feedback + context_feedback
    return feedback_list

def save_responses_to_pdf():
    """
    Saves the responses and feedback to a PDF.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="IELTS Speaking Test Responses and Feedback", ln=True, align="C")
    pdf.ln(10)
    
    for i, (response, fb) in enumerate(zip(responses, feedback)):
        pdf.cell(200, 10, txt=f"Question {i + 1}: {questions[i]}", ln=True)
        pdf.multi_cell(0, 10, txt=f"Response: {response}\n")
        pdf.multi_cell(0, 10, txt=f"Feedback: {'; '.join(fb)}\n")
        pdf.ln(5)

    pdf.output("ielts_responses_feedback.pdf")

def start_practice():
    """
    Starts Practice Mode where feedback is provided immediately for each response.
    """
    global question_index, test_mode, responses, feedback
    question_index, responses, feedback = 0, [], []
    test_mode = False
    practice_button.config(state=tk.DISABLED)
    test_button.config(state=tk.NORMAL)
    next_button.config(state=tk.NORMAL)
    question_label.config(text=f"Practice Mode - Question {question_index + 1}: {questions[question_index]}")

def start_test():
    """
    Starts Test Mode where feedback is provided at the end of the session.
    """
    global question_index, test_mode, responses, feedback
    question_index, responses, feedback = 0, [], []
    test_mode = True
    test_button.config(state=tk.DISABLED)
    practice_button.config(state=tk.NORMAL)
    next_button.config(state=tk.NORMAL)
    question_label.config(text=f"Test Mode - Part 1: {questions[question_index]}")

def next_question():
    """
    Moves to the next question and handles response recording or typing.
    """
    global question_index, responses, feedback

    if question_index < len(questions):
        response = listen_to_speech() if speech_mode.get() else entry.get("1.0", tk.END).strip()
        if not response:
            feedback_label.config(text="Please provide a response.")
            return

        responses.append(response)
        entry.delete("1.0", tk.END)

        # Generate feedback for Practice Mode
        if not test_mode:
            fb = custom_feedback(response, questions[question_index])
            feedback.append(fb)
            feedback_label.config(text="Feedback:\n" + "\n".join(fb))

        question_index += 1
        if question_index < len(questions):
            question_label.config(text=f"Question {question_index + 1}: {questions[question_index]}")
        else:
            question_label.config(text="Session complete! Saving results...")
            next_button.config(state=tk.DISABLED)
            save_responses_to_pdf()
    else:
        question_label.config(text="All questions completed.")

# Load IELTS questions
questions = get_ielts_questions(5)

# Tkinter GUI
window = tk.Tk()
window.title("IELTS Speaking Practice Tool")

# Instructions
instructions = (
    "Welcome to the IELTS Speaking Practice Tool!\n"
    "Choose a mode to begin:\n"
    "Practice Mode: Instant feedback after each response.\n"
    "Test Mode: Full IELTS test with feedback at the end.\n"
)
instructions_label = tk.Label(window, text=instructions, font=("Arial", 12), wraplength=400, justify="left")
instructions_label.pack(pady=10)

# Question display
question_label = tk.Label(window, text="Press a button to start.", font=("Arial", 14))
question_label.pack(pady=10)

# Feedback label
feedback_label = tk.Label(window, text="Feedback will appear here.", font=("Arial", 12), wraplength=400)
feedback_label.pack(pady=10)

# Recording status
recording_label = tk.Label(window, text="", font=("Arial", 10), fg="red")
recording_label.pack(pady=5)

# Text entry
entry = tk.Text(window, height=5, width=50)
entry.pack(pady=10)

# Buttons
practice_button = tk.Button(window, text="Start Practice Mode", command=start_practice)
practice_button.pack(pady=5)

test_button = tk.Button(window, text="Start Test Mode", command=start_test)
test_button.pack(pady=5)

next_button = tk.Button(window, text="Next Question", command=next_question, state=tk.DISABLED)
next_button.pack(pady=10)

# Checkbox for speech-to-text
speech_mode = tk.BooleanVar()
speech_checkbox = tk.Checkbutton(window, text="Enable Speech-to-Text Mode", variable=speech_mode)
speech_checkbox.pack(pady=5)

# Run the app
window.mainloop()
