import language_tool_python  # Import the language tool for grammar checking
from utils import clean_feedback

# Function to check grammar using language_tool_python
def check_grammar(text):
    tool = language_tool_python.LanguageTool('en-US')  # Initialize the language tool for English (US)
    matches = tool.check(text)  # Check for grammar issues in the text
    return matches

# Custom feedback function with cleaned-up results
def custom_feedback(text, question):
    """
    Generates feedback combining grammar, sentence structure, vocabulary, and context suggestions.
    """
    print(f"Analyzing text: {text}")  # Debugging line to check the text
    grammar_issues = check_grammar(text)
    print(f"Grammar issues: {grammar_issues}")  # Debugging line to check grammar issues

    # Check if grammar_issues is None or empty
    if not grammar_issues:
        grammar_feedback = ["No grammar issues detected."]
    else:
        grammar_feedback = [f"Issue: {issue.message}\nSuggestion: {', '.join(issue.replacements)}" for issue in grammar_issues]

    # Vocabulary suggestions
    vocabulary_feedback = []
    if "very" in text:
        vocabulary_feedback.append("Consider replacing 'very' with a more specific term (e.g., 'extremely').")

    # Contextual feedback
    context_feedback = []
    if "hobbies" in question.lower() and len(text.split()) < 5:
        context_feedback.append("Try expanding your hobbies with more details.")
    
    # Combine all feedback and clean it
    feedback_list = grammar_feedback + vocabulary_feedback + context_feedback
    cleaned_feedback = clean_feedback(feedback_list)
    return cleaned_feedback
