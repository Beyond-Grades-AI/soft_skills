def read_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
        return file_contents
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None


def save_text_to_file(text, file_path):
    try:
        with open(file_path, 'w') as file:
            file.write(text)
        print(f"Text saved to '{file_path}' successfully.")
    except Exception as e:
        print(f"Error occurred while saving text to '{file_path}': {e}")




