# Python script to count words in a text file
import sys

# Function to count words
def count_words(file_path):
    try:
        with open(file_path, 'r') as file:
            text = file.read()
            words = text.split()
            return f'Total words: {len(words)}'
    except Exception as e:
        return f'Error reading file: {e}'

# Main functionality
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python word_count_script.py <filename>')
    else:
        file_path = sys.argv[1]
        result = count_words(file_path)
        print(result)