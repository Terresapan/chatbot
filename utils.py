import os

# Function to save feedback to a file
def save_feedback(feedback_text):
    feedback_dir = "feedback"
    feedback_file_path = os.path.join(feedback_dir, "feedback.txt")

    # Ensure feedback directory exists
    os.makedirs(feedback_dir, exist_ok=True)

    # Save feedback to the file
    try:
        with open(feedback_file_path, "a") as file:
            file.write(feedback_text + "\n")
    except Exception as e:
        raise IOError(f"Error saving feedback: {str(e)}")