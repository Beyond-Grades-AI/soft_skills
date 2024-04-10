from UI.language_model.DataManager import read_text_file
from UI.language_model.LM import create_questions
from UI.language_model.PromptBuilder import create_empathy_eval_prompt, create_critical_thinking_eval_prompt

if __name__ == '__main__':
    topic = read_text_file("../language_model/material_files/story.txt")
    soft_skill = "חשיבה ביקורתית"
    print(create_questions(topic, soft_skill, use_ml=True, num_questions=5))
    # question_text = "זאת השאלה"
    # answer = "זאת התשובה"
    # empathy_points = read_text_file("../language_model/prompt_files/CriticalThinkingPointsEval.txt")
    # print(create_critical_thinking_eval_prompt(question_text, answer, empathy_points))

