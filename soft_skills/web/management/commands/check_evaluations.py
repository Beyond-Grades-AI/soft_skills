
# Function to simulate checking and evaluating answers
# myapp/management/commands/check_evaluations.py
from django.core.management.base import BaseCommand
import time
from data_manager.DataReader import get_questions_answers_test_df, update_origin_eval
from language_model.LM import evaluate_answers

class Command(BaseCommand):
    help = 'Check and evaluate answers continuously'

    def handle(self, *args, **kwargs):
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
            

# def check_and_evaluate_answers():
#     while True:
#         answer_df, question_df, test_df = get_questions_answers_test_df()
#         if not answer_df.empty:
#             for i in range(len(answer_df)):
#                 try:
#                     answer_str = answer_df['answer_text'].iloc[i]
#                     question_id = answer_df['question_id'].iloc[i]
#                     question_str = question_df[question_df['id'] == question_id]['text'].values[0]
#                     test_id = question_df[question_df['id'] == question_id]['test_id'].values[0]
#                     skill_str = test_df[test_df['id'] == test_id]['skill'].values[0]

#                     eval_str = evaluate_answers(answer_str, question_str, skill_str)

#                     update_origin_eval(f"{question_id}", eval_str)
#                 except Exception as e:
#                     print(f"Error evaluating answers: {e}")
#                     print("Sleeping for 5 minutes before retrying...")
#                     time.sleep(300)  # Sleep for 5 minutes
#                     break
#         else:
#             print("No answers to evaluate. Sleeping...")

#         # Sleep for a specified duration (e.g., 5 minutes)
#         time.sleep(300)  # 300 seconds = 5 minutes