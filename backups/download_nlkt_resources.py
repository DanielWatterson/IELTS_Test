import nltk
import os

# Specify the custom NLTK data directory
nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')

# Create the directory if it doesn't exist
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)

# Set the NLTK data path to the custom directory
nltk.data.path.append(nltk_data_dir)

# Download the required resources
nltk.download('punkt', download_dir=nltk_data_dir)
nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_dir)

print("Necessary NLTK resources downloaded!")
