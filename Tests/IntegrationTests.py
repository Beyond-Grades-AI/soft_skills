import unittest
from unittest.mock import patch, MagicMock
import os
import sqlite3
from pathlib import Path
import pandas as pd
from soft_skills.language_model import (
    create_questions_prompt, read_text_file, save_text_to_file, fetch_data_from_table, update_origin_eval,
    get_questions_answers_test_df, decrypt, activate_lm, evaluate_answers
)
from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from soft_skills.web.management.commands.check_evaluations import Command
from soft_skills.web.models import Test, Question, Student
from django.http import HttpResponse


class IntegrationTests(unittest.TestCase):

    @patch('soft_skills.language_model.PromptBuilder.create_questions_prompt')
    @patch('soft_skills.language_model.LM.activate_lm')
    def test_create_and_evaluate_empathy_questions(self, mock_activate_lm, mock_create_questions_prompt):
        # Simulate the prompt creation
        mock_create_questions_prompt.return_value = "Mocked empathy prompt"
        
        # Simulate the activation of the language model
        mock_activate_lm.return_value = {"choices": [{"message": {"content": "Mocked empathy evaluation"}}]}
        
        topic = "History"
        points = "Point 1 Point 2 Point 3"
        num_questions = 5
        
        # Create questions prompt
        prompt = create_questions_prompt(topic, points, num_questions)
        self.assertEqual(prompt, "Mocked empathy prompt")
        
        # Evaluate answers
        evaluation = activate_lm(prompt)
        self.assertEqual(evaluation, {"choices": [{"message": {"content": "Mocked empathy evaluation"}}]})
    
    @patch('soft_skills.language_model.DataManager.read_text_file')
    @patch('soft_skills.language_model.DataManager.find_file_path')
    def test_read_and_save_text_file(self, mock_find_file_path, mock_read_text_file):
        # Simulate finding the file path
        mock_find_file_path.return_value = "mocked_file.txt"
        
        # Simulate reading the file
        mock_read_text_file.return_value = "Mocked file contents"
        
        file_path = "mocked_file.txt"
        
        # Read text file
        content = read_text_file(file_path)
        self.assertEqual(content, "Mocked file contents")
        
        # Save text to file
        new_content = "New mocked file contents"
        save_text_to_file(new_content, file_path)
        
        # Verify the saving process
        with open(file_path, 'r') as file:
            self.assertEqual(file.read(), new_content)
    
    @patch('soft_skills.language_model.DataReader.find_file_path')
    @patch('sqlite3.connect')
    def test_fetch_and_update_data_in_database(self, mock_connect, mock_find_file_path):
        # Mock database connection and cursor
        mock_find_file_path.return_value = "test_db.sqlite3"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simulate fetching data from a table
        mock_cursor.description = [('column1',), ('column2',), ('column3',)]
        mock_cursor.fetchall.return_value = [('row1', 'row2', 'row3'), ('row4', 'row5', 'row6')]
        
        # Fetch data
        column_names, rows = fetch_data_from_table("test_table")
        self.assertEqual(column_names, ['column1', 'column2', 'column3'])
        self.assertEqual(rows, [('row1', 'row2', 'row3'), ('row4', 'row5', 'row6')])
        
        # Simulate updating data
        update_origin_eval(123, 'Updated origin evaluation')
        mock_cursor.execute.assert_called_once_with("UPDATE web_answer SET origin_eval = ? WHERE question_id = ?", ('Updated origin evaluation', 123))
        mock_conn.commit.assert_called_once()

    @patch('soft_skills.language_model.DataReader.get_questions_answers_test_df')
    @patch('soft_skills.language_model.LM.evaluate_answers')
    def test_get_test_data_and_evaluate(self, mock_evaluate_answers, mock_get_questions_answers_test_df):
        # Simulate getting test data
        mock_get_questions_answers_test_df.return_value = (pd.DataFrame({'answer_text': ['answer1', 'answer2']}), 
                                                           pd.DataFrame({'question_text': ['question1', 'question2']}), 
                                                           pd.DataFrame({'test_name': ['test1', 'test2']}))
        
        answer_df, question_df, test_df = get_questions_answers_test_df()
        self.assertEqual(len(answer_df), 2)
        self.assertEqual(len(question_df), 2)
        self.assertEqual(len(test_df), 2)
        
        # Simulate evaluating answers
        mock_evaluate_answers.return_value = "Mocked evaluation"
        result = evaluate_answers(answer_df.iloc[0]['answer_text'], question_df.iloc[0]['question_text'], "empathy")
        self.assertEqual(result, "Mocked evaluation")

    @patch('soft_skills.language_model.LM.decrypt')
    def test_decrypt_and_use_key(self, mock_decrypt):
        # Simulate decryption
        mock_decrypt.return_value = "decrypted_key"
        
        key = decrypt()
        self.assertEqual(key, "decrypted_key")
        
        # Simulate using the key in another function
        response = activate_lm(f"Use the key: {key}")
        self.assertIsNone(response)  # Assuming activate_lm returns None on failure

class IntegrationTestAppComponents(TestCase):

    @patch('soft_skills.web.management.commands.check_evaluations.Command.handle')
    def test_handle_function_evaluation(self, mock_handle):
        # Simulate a complete evaluation run
        Command().handle()
        mock_handle.assert_called_once()
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.test = Test.objects.create(grade='10', skill='Test Skill')
        self.question = Question.objects.create(text='Test Question', test=self.test)

    def test_login(self):
        response = self.client.post('/login/', {'username': 'testuser', 'password': '12345'})
        self.assertEqual(response.status_code, 302)  # Redirects to main screen
        self.assertRedirects(response, '/main_screen/')

    def test_create_questions(self):
        with open('test.docx', 'rb') as docx_file:
            file = SimpleUploadedFile(docx_file.name, docx_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response = self.client.post('/create_questions/', {
                'skill': 'Skill',
                'subject': 'Subject',
                'grade': 'Grade',
                'title': 'Title',
                'file': file
            })
        self.assertEqual(response.status_code, 200)
        # Check if questions are created in the database

    def test_generate_link(self):
        response = self.client.post('/generate_link/', {
            'test_id': '1',
            'subject': 'Math',
            'skill': 'Problem Solving',
            'grade': 'A',
            'test_title': 'Math Test',
            'questions[]': ['Question 1', 'Question 2']
        })
        self.assertEqual(response.status_code, 200)
        # Check the generated link in the response

    def test_display_link(self):
        response = self.client.get(reverse('display_link', args=['test_page/1', '9', 'math', 'algebra', 'Test Title']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'test_link.html')
        # Check the context data

    def test_test_page(self):
        response = self.client.get(f'/test_page/{self.test.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'test_page.html')

    def test_submit_answers(self):
        response = self.client.post('/submit_answers/', {
            'test_id': self.test.id,
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'test': 'on',
            'answer_1': 'Answer to question 1',
            'answer_2': 'Answer to question 2'
        })
        self.assertEqual(response.status_code, 200)
        # Check if answers are stored correctly

    def test_test_feedback(self):
        student = Student.objects.create(name='Student', test=self.test)
        response = self.client.post('/test_feedback/', {'test_id': self.test.id})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.context_data['students'].count(), 1)

    def test_tests_screen(self):
        self.client.session['teacher'] = 'test@example.com'
        response = self.client.get('/tests_screen/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tests_screen.html')

if __name__ == '__main__':
    unittest.main()
