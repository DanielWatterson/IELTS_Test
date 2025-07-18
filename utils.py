# Shared utility functions
def clean_feedback(feedback_list):
    cleaned_feedback = []
    for feedback_item in feedback_list:
        cleaned_item = feedback_item.strip().replace("\n", " ").replace("  ", " ")
        if cleaned_item:
            cleaned_feedback.append(cleaned_item)
    return cleaned_feedback
