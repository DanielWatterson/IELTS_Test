def get_ielts_questions(part):
    """
    Return IELTS questions based on the test part.
    """
    if part == 1:
        return ["Can you tell me about your hometown?", "Do you work or study?"]
    elif part == 2:
        return ["Describe a memorable trip you’ve taken."]
    elif part == 3:
        return ["What makes a city worth living in?", "How can tourism impact local communities?"]
    elif part == 5:
        return [
            "Can you tell me about your hobbies?",
            "What is your favorite book or movie?",
            "Describe a memorable day in your life.",
            "What are the benefits of learning new skills?",
            "How do you usually spend your weekends?"
        ]
    return []

def calculate_ielts_score(matches):
    """
    Calculate an IELTS score based on grammar matches.
    """
    num_issues = len(matches)
    if num_issues == 0:
        return "Band 9 (Excellent)"
    elif num_issues <= 3:
        return "Band 8 (Very Good)"
    elif num_issues <= 6:
        return "Band 7 (Good)"
    elif num_issues <= 9:
        return "Band 6 (Competent)"
    else:
        return "Band 5 or below (Needs Improvement)"
