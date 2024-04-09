import openai
import time
from DataManager import read_text_file, save_text_to_file
from soft_skills.language_model.PromptBuilder import *


def activate_lm(prompt):
    openai.api_key = ""
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
        points = read_text_file("../language_model/prompt_files/EmpathyPoints.txt")
    elif soft_skill == "חשיבה ביקורתית":
        points = read_text_file("../language_model/prompt_files/CriticalThinkingPoints.txt")
    questions_prompt = create_questions_prompt(topic, points, num_questions)
    if use_ml:
        response = activate_lm(questions_prompt)
        if response is not None:
            return response.choices[0].message.content
        return "Error occurred.Try again later"
    else:
        return f"questions_prompt: \n {questions_prompt}"


def evaluate_answers(questions_list, answers_list, soft_skill):
    eval_list = []
    if soft_skill == "אמפתיה":
        points = read_text_file("../language_model/prompt_files/EmpathyPointsEval.txt")
        for answer_number, (question, answer) in enumerate(zip(questions_list, answers_list)):
            prompt = create_empathy_eval_prompt(question, answer, points)
            response = activate_lm(prompt)
            if response is not None:
                eval_list.append(f"{answer_number}) {response.choices[0].message.content}")
            time.sleep(20)  # sleep for 20 seconds before evaluating next answer

    elif soft_skill == "חשיבה ביקורתית":
        points = read_text_file("../language_model/prompt_files/CriticalThinkingPointsEval.txt")
        for answer_number, question, answer in enumerate(questions_list, answers_list):
            prompt = create_critical_thinking_eval_prompt(question, answer, points)
            response = activate_lm(prompt)
            if response is not None:
                eval_list.append(f"{answer_number}) {response.choices[0].message.content}")
            time.sleep(20)  # sleep for 20 seconds before evaluating next answer

    return eval_list


# studying_material_path = '/Users/kseniadrokov/Desktop/IndustrialRevolution.txt'
# empathy_points_path = '/Users/kseniadrokov/Desktop/EmpathyPoints.txt'
#
# studying_material = read_text_file(studying_material_path)
# empathy_points = read_text_file(empathy_points_path)

# print(response.choices[0].message.content)

# Specify the path where you want to save the text file
# file_path = '/Users/kseniadrokov/Desktop/questions.txt'
# Save the text to the file
# save_text_to_file(response.choices[0].message.content, file_path)
