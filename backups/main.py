import os
import tkinter as tk
from ielts_test import get_ielts_questions, calculate_ielts_score
import speech_recognition as sr
from speech_recognition_custom import listen_to_speech  # Assuming this exists
from fpdf import FPDF
import language_tool_python
from datetime import datetime
from grammar_check import check_grammar  # Assuming this function exists

# Initialize the root window
window = tk.Tk()
window.title("IELTS Speaking Practice Tool")
window.geometry("600x600")  # Set a more spacious window size

# Initialize the recognizer
recognizer = sr.Recognizer()

# Global variables
question_index = 0
responses = []
feedback = []
test_mode = False  # Tracks whether it's Test Mode or Practice Mode
user_name = ""
user_id = ""
speech_mode = tk.BooleanVar(value=True)  # Track whether speech input is selected (default is True)
is_listening = False  # Tracks if the system is listening for speech
timer_label = None  # For countdown timer during speech mode
speech_response = ""  # Variable to store the current speech input

# Clean feedback for better display
def clean_feedback(feedback_list):
    cleaned_feedback = []
    for feedback_item in feedback_list:
        cleaned_item = feedback_item.strip().replace("\n", " ").replace("  ", " ")
        if cleaned_item:
            cleaned_feedback.append(cleaned_item)
    return cleaned_feedback

# Custom feedback function with cleaned-up results
def custom_feedback(text, question):
    # Grammar feedback
    grammar_issues = check_grammar(text)

    if not grammar_issues:
        grammar_feedback = ["No grammar issues detected."]
        band_score = "Band 9 (Excellent)"
    else:
        grammar_feedback = [f"Issue: {issue.message}\nSuggestion: {', '.join(issue.replacements)}" for issue in grammar_issues]
        band_score = calculate_ielts_score(grammar_issues)

    # Vocabulary feedback
    vocabulary_feedback = []
    if "very" in text:
        vocabulary_feedback.append("Consider replacing 'very' with a more specific term (e.g., 'extremely').")

    # Contextual feedback
    context_feedback = []
    if "hobbies" in question.lower() and len(text.split()) < 5:
        context_feedback.append("Try expanding your hobbies with more details.")
    
    # Combined feedback
    feedback_list = grammar_feedback + vocabulary_feedback + context_feedback
    cleaned_feedback = clean_feedback(feedback_list)

    # Include the calculated IELTS band score
    cleaned_feedback.append(f"IELTS Band Score: {band_score}")

    return cleaned_feedback


# Save responses and feedback to PDF with properly formatted text
def save_responses_to_pdf():
    global user_name, user_id
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{user_name}_IELTS_{timestamp}.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def clean_text(text):
        return text.encode("ascii", "replace").decode("ascii")

    pdf.cell(200, 10, txt="IELTS Speaking Test Responses and Feedback", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"User ID: {clean_text(user_id)}", ln=True)
    pdf.cell(200, 10, txt=f"Name: {clean_text(user_name)}", ln=True)
    pdf.ln(5)

    for i, (response, fb) in enumerate(zip(responses, feedback)):
        pdf.cell(200, 10, txt=f"Question {i + 1}: {clean_text(questions[i])}", ln=True)
        pdf.multi_cell(0, 10, txt=f"Response: {clean_text(response)}\n")
        pdf.multi_cell(0, 10, txt=f"Feedback: {clean_text('; '.join(fb))}\n")
        pdf.ln(5)

    if not os.path.exists("results"):
        os.makedirs("results")
    filepath = os.path.join("results", filename)
    pdf.output(filepath)
    feedback_label.config(text=f"Results saved to {filepath}")
    return filepath

# Function to toggle between Speech Mode and Text Input Mode
def toggle_input_mode():
    if speech_mode.get():  # If Speech Mode is enabled
        entry.config(state=tk.DISABLED)  # Disable the text box
        listen_button.config(state=tk.NORMAL)  # Enable the Listen button
        feedback_label.config(text="Speech Mode enabled. Use the Listen button to provide a response.")
    else:  # If Text Input Mode is enabled
        entry.config(state=tk.NORMAL)  # Enable the text box
        listen_button.config(state=tk.DISABLED)  # Disable the Listen button
        feedback_label.config(text="Text Input Mode enabled. Type your response in the text box.")

# Function to handle the start of the Practice Mode
def start_practice():
    global question_index, test_mode, responses, feedback
    question_index, responses, feedback = 0, [], []
    test_mode = False
    practice_button.config(state=tk.DISABLED)
    test_button.config(state=tk.NORMAL)
    next_button.config(state=tk.NORMAL)
    download_button.config(state=tk.DISABLED)

    toggle_input_mode()  # Set the input mode
    question_label.config(text=f"Practice Mode - Question {question_index + 1}: {questions[question_index]}")

# Function to handle the start of the Test Mode
def start_test():
    global question_index, test_mode, responses, feedback, is_listening, timer_label
    question_index, responses, feedback = 0, [], []
    test_mode = True
    is_listening = False
    practice_button.config(state=tk.DISABLED)
    test_button.config(state=tk.NORMAL)
    next_button.config(state=tk.NORMAL)
    download_button.config(state=tk.DISABLED)

    toggle_input_mode()  # Set the input mode
    question_label.config(text=f"Test Mode - Question {question_index + 1}: {questions[question_index]}")

# Function to start the speech recognition
def start_speech_recognition():
    global is_listening, speech_response

    # Avoid starting speech recognition if already listening
    if is_listening:
        return

    is_listening = True
    recording_label.config(text="Listening... Speak now.", fg="red")

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)

        speech_response = recognizer.recognize_google(audio)
        feedback_label.config(text=f"Speech recognized: {speech_response}")
        recording_label.config(text="Processing response...", fg="green")

    except sr.UnknownValueError:
        speech_response = "Error: Unable to understand the speech."
        feedback_label.config(text="Error: Unable to understand the speech.")
    except sr.RequestError as e:
        speech_response = f"Error with request: {e}"
        feedback_label.config(text=f"Error with request: {e}")
    except Exception as e:
        speech_response = f"Unexpected error: {e}"
        feedback_label.config(text=f"Unexpected error: {e}")

    # Reset the state and allow the user to proceed to the next question
    is_listening = False
    recording_label.config(text="Response processed. Ready for next action.", fg="green")
    next_button.config(state=tk.NORMAL)
    listen_button.config(state=tk.NORMAL)  # Allow to listen again if needed

def next_question():
    global question_index, responses, feedback, speech_response, is_listening

    # Prevent triggering next question while the system is already listening
    if is_listening:
        return

    response = ""
    if speech_mode.get():  # If in Speech Mode
        if not speech_response:
            start_speech_recognition()
            return  # Wait for speech input
        response = speech_response
    else:  # If in Text Input Mode
        response = entry.get("1.0", tk.END).strip()
        if not response:
            feedback_label.config(text="Please provide a response before moving to the next question.")
            return  # Don't proceed if the response is empty

    responses.append(response)
    entry.delete("1.0", tk.END)  # Clear the text box for the next response (if in Text Input Mode)

    fb = custom_feedback(response, questions[question_index])
    feedback.append(fb)

    if not test_mode:
        feedback_label.config(text="Feedback:\n" + "\n".join(fb))
    else:
        feedback_label.config(text="Test Mode - Proceeding to next question...")

    question_index += 1

    if question_index < len(questions):
        question_label.config(text=f"Question {question_index + 1}: {questions[question_index]}")
    else:
        question_label.config(text="Session complete!")
        next_button.config(state=tk.DISABLED)
        download_button.config(state=tk.NORMAL)

# Reset function, user info setup, and GUI components
def reset():
    global question_index, responses, feedback, user_name, user_id, is_listening, speech_response
    question_index = 0
    responses = []
    feedback = []
    user_name = ""
    user_id = ""
    is_listening = False
    speech_response = ""

    name_entry.config(state=tk.NORMAL)
    id_entry.config(state=tk.NORMAL)
    submit_button.config(state=tk.NORMAL)
    practice_button.config(state=tk.DISABLED)
    test_button.config(state=tk.DISABLED)
    next_button.config(state=tk.DISABLED)
    download_button.config(state=tk.DISABLED)

    name_entry.delete(0, tk.END)
    id_entry.delete(0, tk.END)
    feedback_label.config(text="Feedback will appear here.")
    question_label.config(text="Press a button to start.")
    entry.delete("1.0", tk.END)

    recording_label.config(text="")

def set_user_info():
    global user_name, user_id
    user_name = name_entry.get().strip()
    user_id = id_entry.get().strip()
    if user_name and user_id:
        name_entry.config(state=tk.DISABLED)
        id_entry.config(state=tk.DISABLED)
        submit_button.config(state=tk.DISABLED)
        practice_button.config(state=tk.NORMAL)
        test_button.config(state=tk.NORMAL)
        feedback_label.config(text="User info saved. You can now start Practice or Test Mode.")
    else:
        feedback_label.config(text="Please enter both Name and User ID.")

questions = get_ielts_questions(5)

# Tkinter GUI setup with improved design
tk.Label(window, text="Name:", font=("Arial", 14)).pack(pady=5)
name_entry = tk.Entry(window, font=("Arial", 12))
name_entry.pack(pady=5)

tk.Label(window, text="User ID:", font=("Arial", 14)).pack(pady=5)
id_entry = tk.Entry(window, font=("Arial", 12))
id_entry.pack(pady=5)

submit_button = tk.Button(window, text="Submit", command=set_user_info, font=("Arial", 12, "bold"))
submit_button.pack(pady=10)

instructions = (
    "Welcome to the IELTS Speaking Practice Tool!\n"
    "Choose a mode to begin:\n"
    "Practice Mode: Instant feedback after each response.\n"
    "Test Mode: Full IELTS test with feedback at the end.\n"
)
instructions_label = tk.Label(window, text=instructions, font=("Arial", 14), wraplength=400, justify="left")
instructions_label.pack(pady=10)

question_label = tk.Label(window, text="Press a button to start.", font=("Arial", 14))
question_label.pack(pady=10)

feedback_label = tk.Label(window, text="Feedback will appear here.", font=("Arial", 12), wraplength=400)
feedback_label.pack(pady=10)

# Checkbox for toggling input mode
input_mode_checkbox = tk.Checkbutton(
    window,
    text="Enable Speech Mode",
    variable=speech_mode,
    command=toggle_input_mode,
    font=("Arial", 12)
)
input_mode_checkbox.pack(pady=10)

entry = tk.Text(window, height=5, width=40, font=("Arial", 12))
entry.pack(pady=5)

practice_button = tk.Button(window, text="Start Practice Mode", command=start_practice, font=("Arial", 12, "bold"), state=tk.DISABLED)
practice_button.pack(pady=10)

test_button = tk.Button(window, text="Start Test Mode", command=start_test, font=("Arial", 12, "bold"), state=tk.DISABLED)
test_button.pack(pady=10)

listen_button = tk.Button(window, text="Listen", command=start_speech_recognition, font=("Arial", 12), state=tk.NORMAL)
listen_button.pack(pady=10)

next_button = tk.Button(window, text="Next Question", command=next_question, font=("Arial", 12), state=tk.DISABLED)
next_button.pack(pady=10)

download_button = tk.Button(window, text="Download Results", command=save_responses_to_pdf, font=("Arial", 12), state=tk.DISABLED)
download_button.pack(pady=10)

reset_button = tk.Button(window, text="Reset", command=reset, font=("Arial", 12))
reset_button.pack(pady=10)

recording_label = tk.Label(window, text="", font=("Arial", 12))
recording_label.pack(pady=10)

window.mainloop()
