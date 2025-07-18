import language_tool_python  # Import the language tool for grammar checking

# Function to check grammar using language_tool_python
def check_grammar(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    return matches  # Return a list of grammar issues