import openai
import time
from .DataManager import read_text_file, save_text_to_file
from cryptography.fernet import Fernet
from .PromptBuilder import *
from ..data_manager.DataReader import get_questions_answers_test_df, update_origin_eval


def decrypt():
    # Load the encryption key
    with open("encryption_key.key", "rb") as f:
        key = f.read()

    cipher_suite = Fernet(key)

    # Load and decrypt the API key
    with open("encrypted_api_key.txt", "rb") as f:
        encrypted_api_key = f.read()

    decrypted_api_key = cipher_suite.decrypt(encrypted_api_key).decode("utf-8")
    # print(decrypted_api_key)
    return decrypted_api_key


def activate_lm(prompt):
    openai.api_key = decrypt()
    try:
        response = openai.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo",
        )
        return response
    except Exception as e:
        print(f"An error occurred while activating the lm: {e}")
        return None


def create_questions(topic, soft_skill, use_ml=False, num_questions=5):
    if soft_skill == "אמפתיה":
        points = read_text_file("EmpathyPoints.txt")
    elif soft_skill == "חשיבה ביקורתית":
        points = read_text_file("CriticalThinkingPoints.txt")
    questions_prompt = create_questions_prompt(topic, points, num_questions)
    if use_ml:
        response = activate_lm(questions_prompt)
        if response is not None:
            return response.choices[0].message.content
        return "Error occurred.Try again later"
    else:
        return f"questions_prompt: \n {questions_prompt}"


def evaluate_answers(answer, question, soft_skill):
    eval_list = []
    if soft_skill == "אמפתיה":
        points = read_text_file("EmpathyPointsEval.txt")
        prompt = create_empathy_eval_prompt(question, answer, points)
        response = activate_lm(prompt)
        if response is not None:
            eval_list.append(f"{response.choices[0].message.content}")
        time.sleep(20)  # sleep for 20 seconds before evaluating next answer

    elif soft_skill == "חשיבה ביקורתית":
        points = read_text_file("CriticalThinkingPointsEval.txt")
        prompt = create_critical_thinking_eval_prompt(question, answer, points)
        response = activate_lm(prompt)
        if response is not None:
            eval_list.append(f"{response.choices[0].message.content}")
        time.sleep(20)  # sleep for 20 seconds before evaluating next answer

    return eval_list[0]


# Function to simulate checking and evaluating answers
def check_and_evaluate_answers():
    while True:
        answer_df, question_df, test_df = get_questions_answers_test_df()
        if not answer_df.empty:
            for i in range(len(answer_df)):
                try:
                    answer_str = answer_df['answer_text'].iloc[i]
                    question_id = answer_df['question_id'].iloc[i]
                    question_str = question_df[question_df['id'] == question_id]['text'].values[0]
                    test_id = question_df[question_df['id'] == question_id]['test_id'].values[0]
                    skill_str = test_df[test_df['id'] == test_id]['skill'].values[0]

                    eval_str = evaluate_answers(answer_str, question_str, skill_str)

                    update_origin_eval(f"{question_id}", eval_str)
                except Exception as e:
                    print(f"Error evaluating answers: {e}")
                    print("Sleeping for 5 minutes before retrying...")
                    time.sleep(300)  # Sleep for 5 minutes
                    break
        else:
            print("No answers to evaluate. Sleeping...")

        # Sleep for a specified duration (e.g., 5 minutes)
        time.sleep(300)  # 300 seconds = 5 minutes
