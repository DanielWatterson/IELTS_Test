import os
import tkinter as tk
from grammar_check import check_grammar
from ielts_test import get_ielts_questions, calculate_ielts_score
import speech_recognition as sr
from fpdf import FPDF
import re
import nltk
from nltk import pos_tag, word_tokenize
from nltk.tokenize import sent_tokenize
import language_tool_python  # Importing LanguageTool

# Specify a custom NLTK data directory (within the project directory)
nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')

# Create the directory if it doesn't exist
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)

# Set the NLTK data path to the custom directory
nltk.data.path.append(nltk_data_dir)

# Download necessary NLTK resources to the custom directory
nltk.download('punkt', download_dir=nltk_data_dir)
nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_dir)

# Question queue and state
question_index = 0
questions = get_ielts_questions(5)  # Load 5 questions for the test
test_state = {"started": False}  # To track whether we are recording or asking the next question
responses = []  # List to store responses for PDF generation

def listen_to_speech():
    """
    Records and processes speech input using the microphone.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recording_label.config(text="Recording... Please speak now.")
        window.update()
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        recording_label.config(text="Recording complete. Processing response...")
        return text
    except sr.UnknownValueError:
        recording_label.config(text="Sorry, I couldn't understand. Please try again.")
        return ""
    except sr.RequestError as e:
        recording_label.config(text=f"Error during recording: {e}")
        return ""

def custom_grammar_checks(text):
    """
    Adds custom grammar suggestions using LanguageTool API for context-aware corrections.
    """
    feedback = []
    tool = language_tool_python.LanguageTool('en-US')

    # Check for grammar and context-aware issues using LanguageTool
    matches = tool.check(text)
    for match in matches:
        feedback.append(f"Issue: {match.message}\nSuggested Fix: {match.replacements}\n")

    return feedback

def improve_sentence_structure(text):
    """
    Suggests improvements to sentence structure.
    """
    feedback = []
    # Check for over-simplification
    if len(text.split()) < 5:  # Example check for sentence length
        feedback.append("Try to expand the sentence with more details or descriptive language.")
    return feedback

def vocabulary_suggestions(text):
    """
    Suggests improvements to vocabulary usage.
    """
    feedback = []
    if "very" in text:
        feedback.append("Consider using more specific words instead of 'very'. For example, 'extremely', 'exceptionally'.")
    return feedback

def context_aware_suggestions(text, question):
    """
    Provides context-specific suggestions based on the question and response.
    """
    feedback = []
    
    # Check for common question types and ensure answers are appropriately detailed
    if "hobbies" in question.lower() and len(text.split()) < 4:
        feedback.append("Try adding more details to your hobbies. For example, 'I enjoy fishing because it helps me relax and biking because it's a great way to stay fit.'")

    elif "work" in question.lower() and len(text.split()) < 4:
        feedback.append("Provide more details about your work experience. You could mention where you work, your responsibilities, and why you enjoy it.")

    elif "place" in question.lower() and len(text.split()) < 4:
        feedback.append("Expand on the place you visited. Mention why you liked it or what activities you enjoyed there.")

    return feedback

def generate_feedback(issues, custom_issues, structure_issues, vocabulary_issues, context_suggestions):
    """
    Combines grammar feedback and suggestions into a single response.
    """
    feedback = ""
    if issues:
        feedback += "Grammar issues found:\n\n"
        for issue in issues:
            feedback += f"Issue: {issue.context}\nSuggested Fix: {issue.replacements}\n\n"
    if custom_issues:
        feedback += "Custom Suggestions:\n\n"
        for issue in custom_issues:
            feedback += f"- {issue}\n"
    if structure_issues:
        feedback += "Sentence Structure Suggestions:\n\n"
        for issue in structure_issues:
            feedback += f"- {issue}\n"
    if vocabulary_issues:
        feedback += "Vocabulary Suggestions:\n\n"
        for issue in vocabulary_issues:
            feedback += f"- {issue}\n"
    if context_suggestions:
        feedback += "Context-specific Suggestions:\n\n"
        for suggestion in context_suggestions:
            feedback += f"- {suggestion}\n"
    if not issues and not custom_issues and not structure_issues and not vocabulary_issues and not context_suggestions:
        feedback += "No grammar issues found. Excellent work!"
    return feedback

def on_button_click():
    """
    Handles grammar checking for the user input.
    """
    entered_text = entry.get("1.0", tk.END).strip()
    if not entered_text:
        feedback_label.config(text="Please enter some text!")
        return

    if non_native_mode.get():
        entered_text = normalize_text(entered_text)

    issues = check_grammar(entered_text)
    custom_issues = custom_grammar_checks(entered_text)  # Updated custom grammar check with LanguageTool
    structure_issues = improve_sentence_structure(entered_text)
    vocabulary_issues = vocabulary_suggestions(entered_text)
    context_suggestions = context_aware_suggestions(entered_text, questions[question_index])  # Based on the current question

    feedback = generate_feedback(issues, custom_issues, structure_issues, vocabulary_issues, context_suggestions)
    
    # Only calculate score after the user has provided a response (not before)
    score = calculate_ielts_score(issues) if (issues or custom_issues or structure_issues or vocabulary_issues) else "Band 9 (Excellent)"

    feedback_label.config(text=feedback)
    score_label.config(text=f"IELTS Score: {score}")

def on_start_test():
    """
    Starts the test and displays the first question.
    """
    global question_index
    question_index = 0  # Reset the question index
    start_button.config(state=tk.DISABLED)  # Disable the Start Test button after it’s clicked
    next_button.config(state=tk.NORMAL)  # Enable the Next Question button
    question_label.config(text=f"Question {question_index + 1}: {questions[question_index]}")  # Show the first question
    score_label.config(text="")  # Hide the score label until after grammar check

def on_next_question():
    """
    Handles moving to the next question, depending on the speech-to-text mode.
    """
    global question_index

    if question_index < len(questions):
        if speech_mode.get():  # Speech-to-Text Mode
            response = listen_to_speech()
        else:  # Text Mode
            response = entry.get("1.0", tk.END).strip()

        if response:  # If a response is given
            responses.append(response)
            entry.delete("1.0", tk.END)

            # Move to the next question
            question_index += 1
            if question_index < len(questions):
                question_label.config(text=f"Question {question_index + 1}: {questions[question_index]}")
            else:
                question_label.config(text="Test complete! You may review your responses.")
                next_button.config(state=tk.DISABLED)  # Disable the button when the test is complete
                save_responses_to_pdf()
        else:
            feedback_label.config(text="Please provide a response before proceeding.")
    else:
        question_label.config(text="Test complete! You may review your responses.")

def save_responses_to_pdf():
    """
    Saves the test responses to a PDF for review.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="IELTS Speaking Test Responses", ln=True, align="C")

    for i, response in enumerate(responses, 1):
        pdf.cell(200, 10, txt=f"Question {i}: {questions[i-1]}", ln=True)
        pdf.multi_cell(0, 10, txt=f"Answer: {response}\n")

    # Save the PDF to the local directory
    pdf.output("ielts_responses.pdf")
    print("Test responses saved to 'ielts_responses.pdf'")

# Tkinter GUI setup
window = tk.Tk()
window.title("IELTS Speaking Practice Tool")

# Instructions
instructions = (
    "Welcome to the IELTS Speaking Practice Tool!\n"
    "1. Click 'Start Test' to begin.\n"
    "2. Press 'Next Question' to answer the question displayed.\n"
    "3. Use 'Check Grammar' to evaluate your written or spoken response.\n"
)
instructions_label = tk.Label(window, text=instructions, font=("Arial", 12), justify="left", wraplength=400)
instructions_label.pack(pady=10)

# Question Label
question_label = tk.Label(window, text="Press Start to begin the test.", font=("Arial", 14))
question_label.pack(pady=10)

# Recording Status Label
recording_label = tk.Label(window, text="", font=("Arial", 10), fg="red")
recording_label.pack(pady=5)

# Multi-line Text Entry for manual responses
entry = tk.Text(window, height=5, width=40)
entry.pack(pady=10)

# Feedback Label
feedback_label = tk.Label(window, text="Feedback will appear here.", font=("Arial", 12))
feedback_label.pack(pady=5)

# IELTS Score Label (initialize as empty)
score_label = tk.Label(window, text="", font=("Arial", 12))
score_label.pack(pady=5)

# Buttons
start_button = tk.Button(window, text="Start Test", command=on_start_test)
start_button.pack(pady=10)

next_button = tk.Button(window, text="Next Question", command=on_next_question, state=tk.DISABLED)
next_button.pack(pady=10)

check_button = tk.Button(window, text="Check Grammar", command=on_button_click)
check_button.pack(pady=10)

# Checkbox for Speech-to-Text Mode
speech_mode = tk.BooleanVar()
speech_checkbox = tk.Checkbutton(window, text="Enable Speech-to-Text Mode", variable=speech_mode)
speech_checkbox.pack(pady=5)

# Checkbox for Non-Native Normalization Mode
non_native_mode = tk.BooleanVar()
non_native_checkbox = tk.Checkbutton(window, text="Enable Non-Native Mode (Simplify Grammar)", variable=non_native_mode)
non_native_checkbox.pack(pady=5)

# Run the Tkinter loop
window.mainloop()
