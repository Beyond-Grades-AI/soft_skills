import unittest
from unittest.mock import patch, MagicMock
from LM import create_questions, evaluate_answers
from UI.language_model.DataManager import read_text_file
from UI.language_model.PromptBuilder import create_questions_prompt


class TestYourFunctions(unittest.TestCase):
    @patch("DataManager.read_text_file")
    def test_create_questions(self, mock_read_file):
        mock_read_file.return_value = "Mocked empathy points"
        topic = "היסטוריה"
        soft_skill = "אמפתיה"
        result = create_questions(topic, soft_skill)
        points = read_text_file("../language_model/prompt_files/EmpathyPoints.txt")
        self.assertEqual(result, f"questions_prompt: \n {create_questions_prompt(topic, points, 5)}")

    @patch("DataManager.read_text_file")
    def test_create_questions2(self, mock_read_file):
        mock_read_file.return_value = "Mocked empathy points"
        topic = "ספרות"
        soft_skill = "חשיבה ביקורתית"
        result = create_questions(topic, soft_skill)
        points = read_text_file("../language_model/prompt_files/CriticalThinkingPoints.txt")
        self.assertEqual(result, f"questions_prompt: \n {create_questions_prompt(topic, points, 5)}")

    # @patch("YourModuleName.activate_lm")
    # def test_evaluate_answers_empathy(self, mock_activate_lm):
    #     mock_response = MagicMock()
    #     mock_response.choices[0].message.content = "Mocked empathy evaluation"
    #     mock_activate_lm.return_value = mock_response
    #
    #     questions_list = ["Q1", "Q2"]
    #     answers_list = ["A1", "A2"]
    #     soft_skill = "אמפתיה"
    #     result = evaluate_answers(questions_list, answers_list, soft_skill)
    #     expected_result = ["0) Mocked empathy evaluation", "1) Mocked empathy evaluation"]
    #     self.assertEqual(result, expected_result)

    # @patch("YourModuleName.activate_lm")
    # def test_evaluate_answers_critical_thinking(self, mock_activate_lm):
    #     mock_response = MagicMock()
    #     mock_response.choices[0].message.content = "Mocked critical thinking evaluation"
    #     mock_activate_lm.return_value = mock_response
    #
    #     questions_list = ["Q1", "Q2"]
    #     answers_list = ["A1", "A2"]
    #     soft_skill = "חשיבה ביקורתית"
    #     result = evaluate_answers(questions_list, answers_list, soft_skill)
    #     expected_result = ["0) Mocked critical thinking evaluation", "1) Mocked critical thinking evaluation"]
    #     self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
