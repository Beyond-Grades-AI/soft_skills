import os
import unittest
from unittest import TestCase
from unittest.mock import patch
from cryptography.fernet import Fernet
from soft_skills.language_model.LM import decrypt, remove_numbering, activate_lm
from unittest.mock import patch
from soft_skills.language_model.LM import create_questions, read_text_file, activate_lm, remove_numbering
from soft_skills.language_model.LM import evaluate_answers, read_text_file, activate_lm
from soft_skills.language_model.PromptBuilder import create_empathy_eval_prompt, create_critical_thinking_eval_prompt


class TestDecrypt(TestCase):
    @patch('builtins.open', create=True)
    def test_decrypt_key_file_not_found(self, mock_open):
        mock_open.side_effect = FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            decrypt()

    @patch('builtins.open', create=True)
    def test_decrypt_encrypted_file_not_found(self, mock_open):
        mock_open.side_effect = [
            mock_open.return_value.__enter__.return_value,
            FileNotFoundError
        ]
        with self.assertRaises(FileNotFoundError):
            decrypt()

    @patch('builtins.open', create=True)
    def test_decrypt_success(self, mock_open):
        mock_open.side_effect = [
            mock_open.return_value.__enter__.return_value,
            mock_open.return_value.__enter__.return_value
        ]
        mock_open.return_value.__enter__.return_value.read.side_effect = [
            b'key',
            b'encrypted_key'
        ]
        mock_open.return_value.__enter__.return_value.decode.return_value = 'decrypted_key'
        self.assertEqual(decrypt(), 'decrypted_key')

    @patch('cryptography.fernet.Fernet.decrypt')
    def test_decrypt_invalid_key(self, mock_decrypt):
        mock_decrypt.side_effect = ValueError
        with self.assertRaises(ValueError):
            decrypt()


class TestActivateLM(unittest.TestCase):

    @patch('openai.chat.completions.create')
    def test_successful_response(self, mock_create):
        mock_create.return_value = "Mocked response"
        prompt = "Test prompt"
        response = activate_lm(prompt)
        self.assertEqual(response, "Mocked response")

    @patch('openai.chat.completions.create')
    def test_exception_handling(self, mock_create):
        mock_create.side_effect = Exception("Test exception")
        prompt = "Test prompt"
        response = activate_lm(prompt)
        self.assertIsNone(response)


class TestRemoveNumbering(unittest.TestCase):

    def test_remove_numbering_with_numbering(self):
        questions = ["1. What is your name?", "2. How old are you?"]
        expected_output = ["What is your name?", "How old are you?"]
        
        self.assertEqual(remove_numbering(questions), expected_output)

    def test_remove_numbering_without_numbering(self):
        questions = ["What is your name?", "How old are you?"]
        expected_output = ["What is your name?", "How old are you?"]
        
        self.assertEqual(remove_numbering(questions), expected_output)


class TestCreateQuestions(unittest.TestCase):
    @patch('LM.read_text_file')
    def test_create_questions_with_ml(self, mock_read_file):
        mock_read_file.return_value = "Mocked empathy points"
        topic = "היסטוריה"
        soft_skill = "אמפתיה"
        result = create_questions(topic, soft_skill, use_ml=True)
        points = read_text_file("EmpathyPoints.txt")
        expected_output = remove_numbering([question.strip() for question in points.split('\n') if question.strip()])
        self.assertEqual(result, expected_output)

    @patch('LM.read_text_file')
    def test_create_questions_without_ml(self, mock_read_file):
        mock_read_file.return_value = "Mocked questions"
        topic = "ספרות"
        soft_skill = "חשיבה ביקורתית"
        result = create_questions(topic, soft_skill, use_ml=False)
        expected_output = ["Mocked questions"]
        self.assertEqual(result, expected_output)

    @patch('LM.activate_lm')
    @patch('LM.read_text_file')
    def test_create_questions_with_error(self, mock_read_file, mock_activate_lm):
        mock_read_file.return_value = "Mocked empathy points"
        mock_activate_lm.return_value = None
        topic = "היסטוריה"
        soft_skill = "אמפתיה"
        result = create_questions(topic, soft_skill, use_ml=True)
        self.assertEqual(result, ["Error occurred. Try again later"])


class TestEvaluateAnswers(unittest.TestCase):
    @patch('LM.read_text_file')
    @patch('LM.activate_lm')
    def test_empathy(self, mock_activate_lm, mock_read_text_file):
        mock_read_text_file.return_value = "points"
        mock_activate_lm.return_value = {"choices": [{"message": {"content": "evaluation"}}]}
        result = evaluate_answers("answer", "question", "אמפתיה")
        mock_read_text_file.assert_called_once_with("EmpathyPointsEval.txt")
        mock_activate_lm.assert_called_once_with("points")
        self.assertEqual(result, "evaluation")

    @patch('LM.read_text_file')
    @patch('LM.activate_lm')
    def test_critical_thinking(self, mock_activate_lm, mock_read_text_file):
        mock_read_text_file.return_value = "points"
        mock_activate_lm.return_value = {"choices": [{"message": {"content": "evaluation"}}]}
        result = evaluate_answers("answer", "question", "חשיבה ביקורתית")
        mock_read_text_file.assert_called_once_with("CriticalThinkingPointsEval.txt")
        mock_activate_lm.assert_called_once_with("points")
        self.assertEqual(result, "evaluation")

    @patch('LM.read_text_file')
    @patch('LM.activate_lm')
    def test_no_evaluation(self, mock_activate_lm, mock_read_text_file):
        mock_read_text_file.return_value = "points"
        mock_activate_lm.return_value = None
        result = evaluate_answers("answer", "question", "אמפתיה")
        mock_read_text_file.assert_called_once_with("EmpathyPointsEval.txt")
        mock_activate_lm.assert_called_once_with("points")
        self.assertEqual(result, "")


class TestEvaluateAnswers(unittest.TestCase):

    @patch('your_module.read_text_file', return_value="EmpathyPointsEval.txt")
    @patch('your_module.create_empathy_eval_prompt', return_value="empathy_prompt")
    @patch('your_module.activate_lm', return_value="empathy_response")
    def test_empathy_evaluation(self, mock_read_text_file, mock_create_empathy_eval_prompt, mock_activate_lm):
        result = evaluate_answers("answer", "question", "אמפתיה")
        self.assertEqual(result, "empathy_response")

    @patch('your_module.read_text_file', return_value="CriticalThinkingPointsEval.txt")
    @patch('your_module.create_critical_thinking_eval_prompt', return_value="critical_prompt")
    @patch('your_module.activate_lm', return_value="critical_response")
    def test_critical_thinking_evaluation(self, mock_read_text_file, mock_create_critical_thinking_eval_prompt, mock_activate_lm):
        result = evaluate_answers("answer", "question", "חשיבה ביקורתית")
        self.assertEqual(result, "critical_response")

    @patch('your_module.activate_lm', return_value=None)
    def test_no_response(self, mock_activate_lm):
        result = evaluate_answers("answer", "question", "אמפתיה")
        self.assertEqual(result, None)


if __name__ == '__main__':
    unittest.main()