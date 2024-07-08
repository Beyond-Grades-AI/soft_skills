import unittest
from unittest.mock import patch, MagicMock, Mock
from unittest import TestCase
#from LM import create_questions, evaluate_answers
from soft_skills.language_model.DataManager import find_file_path, read_text_file, save_text_to_file
from soft_skills.language_model.PromptBuilder import create_questions_prompt, create_empathy_eval_prompt, create_critical_thinking_eval_prompt
from soft_skills.language_model.DataReader import find_file_path, get_table_names, get_columns_names_from_table, fetch_data_from_table, update_origin_eval, get_questions_answers_test_df
from pathlib import Path
from typing import List
import sqlite3
import pandas as pd


#class TestYourFunctions(unittest.TestCase):
#    @patch("DataManager.read_text_file")
#    def test_create_questions(self, mock_read_file):
 #       mock_read_file.return_value = "Mocked empathy points"
  #      topic = "היסטוריה"
   #     soft_skill = "אמפתיה"
    #    result = create_questions(topic, soft_skill)
     #   points = read_text_file("../language_model/prompt_files/EmpathyPoints.txt")
      #  self.assertEqual(result, f"questions_prompt: \n {create_questions_prompt(topic, points, 5)}")

   # @patch("DataManager.read_text_file")
    #def test_create_questions2(self, mock_read_file):
     #   mock_read_file.return_value = "Mocked empathy points"
      #  topic = "ספרות"
       # soft_skill = "חשיבה ביקורתית"
        #result = create_questions(topic, soft_skill)
    #    points = read_text_file("../language_model/prompt_files/CriticalThinkingPoints.txt")
     #   self.assertEqual(result, f"questions_prompt: \n {create_questions_prompt(topic, points, 5)}")

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

class TestCreateQuestionsPrompt(unittest.TestCase):

    def test_create_questions_prompt(self):
        topic = "Math"
        points = "Point 1, Point 2, Point 3"
        num_questions = 5
        expected_output = f"עבור הנושא הבא: \n{topic}\nכתוב שאלות על הנושא בצורה הבאה: \nכתוב {num_questions} שאלות\nהשאלות צריכות להיות כתובות בעברית.\nתשתמש בנקודות הבאות כדי לקבל כיוון לכתיבת השאלות:\n{points} \nהשאלות צריכות להיות מתאימות לילדים בחטיבת ביניים\nכאשר אתה בונה את השאלות תנסה לדבר ע לכמה שיותר דמויות"
        
        result = create_questions_prompt(topic, points, num_questions)
        
        self.assertEqual(result, expected_output)

class TestCreateEmpathyEvalPrompt(unittest.TestCase):

    def test_empathy_evaluation_prompt_generation(self):
        question_text = "How are you feeling today?"
        answer = "I am feeling happy."
        empathy_points = "Showed empathy towards the situation"
        
        expected_result = f"עבור השאלה הבאה:\n" \
                          f"{question_text}\n" \
                          f"יש לי את התשובה הבאה:\n" \
                          f"{answer}\n" \
                          f"תנתח את התשובה לפי הנקודות הבאות לתשובה אחת, בנוסף תתחיל את התשובה בכן אם הטקסט מראה על אמפתיה ולמה, או תתחיל את התשובה בלא אם אין אמפתיה בטקסט ולמה, אם אין מגבלת טקסט אל תוסיף את זה לתשובה, אם בתשובה הנתונה אין שאלה המעמיקה את ההבנה אל תוסיף את זה לתשובה: \n" \
                          f"{empathy_points}\n"\
                          f"התשובה צריכה להיות כתובה בפסקה אחת ולא מפורטת לפי נקודות"
        
        actual_result = create_empathy_eval_prompt(question_text, answer, empathy_points)
        
        self.assertEqual(actual_result, expected_result)

class TestCreateCriticalThinkingEvalPrompt(unittest.TestCase):

    def test_basic_case(self):
        question_text = "What is the capital of France?"
        answer = "Paris"
        critical_thinking_points = "Analyzing historical context"
        result = create_critical_thinking_eval_prompt(question_text, answer, critical_thinking_points)
        self.assertIsNotNone(result)
        
    def test_critical_thinking_answer(self):
        question_text = "What are the implications of climate change?"
        answer = "Climate change can lead to food scarcity and displacement of populations."
        critical_thinking_points = "Considering long-term effects"
        result = create_critical_thinking_eval_prompt(question_text, answer, critical_thinking_points)
        self.assertTrue("מביעה חשיבה ביקורתית" in result)
        
    def test_non_critical_thinking_answer(self):
        question_text = "What is the capital of Italy?"
        answer = "Rome"
        critical_thinking_points = "Listing facts"
        result = create_critical_thinking_eval_prompt(question_text, answer, critical_thinking_points)
        self.assertTrue("לא מבטאת חשיבה ביקורתית" in result)

class TestFindFilePath(unittest.TestCase):
    
    @patch('os.walk')
    def test_file_found(self, mock_walk):
        mock_walk.return_value = [('/path/to/dir', [], ['test_file.txt'])]
        result = find_file_path('test_file.txt', '/path/to/dir')
        self.assertEqual(result, '/path/to/dir/test_file.txt')
        
    @patch('os.walk')
    def test_file_not_found(self, mock_walk):
        mock_walk.return_value = [('/path/to/dir', [], ['another_file.txt'])]
        result = find_file_path('test_file.txt', '/path/to/dir')
        self.assertIsNone(result)



class TestReadTextFile(unittest.TestCase):
    
    @patch('soft_skills.language_model.DataManager.find_file_path')
    @patch('builtins.open')
    def test_file_found_and_read_successfully(self, mock_open, mock_find_file_path):
        mock_find_file_path.return_value = "test_file.txt"
        with patch('os.name', 'nt'):
            mock_file = MagicMock()
            mock_file.read.return_value = "Mocked file contents"
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = read_text_file("test_file.txt")
            
            self.assertEqual(result, "Mocked file contents")
    
    @patch('soft_skills.language_model.DataManager.find_file_path')
    @patch('builtins.open')
    def test_file_not_found_error_handled(self, mock_open, mock_find_file_path):
        mock_find_file_path.return_value = "non_existent_file.txt"
        mock_open.side_effect = FileNotFoundError
        
        result = read_text_file("non_existent_file.txt")
        
        self.assertIsNone(result)


class TestSaveTextToFile(unittest.TestCase):

    @patch("soft_skills.language_model.DataManager.open")
    def test_save_text_to_file_success(self, mock_open):
        file_path = "test_file.txt"
        text = "This is a test text."
        save_text_to_file(text, file_path)
        mock_open.assert_called_once_with(file_path, 'w')
        mock_open().write.assert_called_once_with(text)
    
    @patch("soft_skills.language_model.DataManager.open")
    def test_save_text_to_file_exception(self, mock_open):
        file_path = "test_file.txt"
        text = "This is a test text."
        mock_open.side_effect = Exception("File not found")
        with patch("soft_skills.language_model.DataManager.print") as mock_print:
            save_text_to_file(text, file_path)
            mock_print.assert_called_once_with(f"Error occurred while saving text to '{file_path}': File not found")


class TestFindFilePath(unittest.TestCase):

    @patch('os.walk')
    def test_file_found(self, mock_walk):
        mock_walk.return_value = [('/path/to/dir', [], ['test_file.txt'])]
        result = find_file_path('test_file.txt', '/path/to/dir')
        self.assertEqual(result, '/path/to/dir/test_file.txt')

    @patch('os.walk')
    def test_file_not_found(self, mock_walk):
        mock_walk.return_value = [('/path/to/dir', [], ['another_file.txt'])]
        result = find_file_path('test_file.txt', '/path/to/dir')
        self.assertIsNone(result)

class TestGetTableNames(unittest.TestCase):
    @patch('language_model.DataReader.find_file_path')
    def test_no_tables(self, mock_find_file_path):
        mock_find_file_path.return_value = Path('db.sqlite3')
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER)")
        cursor.close()
        conn.close()
        self.assertEqual(get_table_names(), [])

    @patch('language_model.DataReader.find_file_path')
    def test_one_table(self, mock_find_file_path):
        mock_find_file_path.return_value = Path('db.sqlite3')
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test_table1 (id INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS test_table2 (id INTEGER)")
        cursor.close()
        conn.close()
        self.assertEqual(get_table_names(), ['test_table1', 'test_table2'])

    @patch('language_model.DataReader.find_file_path')
    def test_no_db_file(self, mock_find_file_path):
        mock_find_file_path.return_value = None
        self.assertEqual(get_table_names(), [])


class TestGetColumnsNamesFromTable(unittest.TestCase):

    @patch('soft_skills.language_model.DataReader.find_file_path')
    @patch('sqlite3.connect')
    def test_fetch_column_names(self, mock_connect, mock_find_file_path):
        mock_find_file_path.return_value = 'test_db.sqlite3'
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = [(0, 'id', 'INTEGER', 0, None, 1)]
        
        # Call the function
        get_columns_names_from_table('test_table')
        
        # Assert the expected output
        expected_column_names = ['id']
        self.assertEqual(mock_cursor.execute.call_args[0][0], "PRAGMA table_info(test_table);")
        self.assertEqual(mock_cursor.fetchall.call_count, 1)
        self.assertEqual(mock_cursor.close.call_count, 1)


class TestFetchDataFromTable(TestCase):
    @patch('soft_skills.language_model.DataReader.find_file_path')
    @patch('sqlite3.connect')
    def test_fetch_data_from_table(self, mock_connect, mock_find_file_path):
        # Mock the return values of the functions
        mock_find_file_path.return_value = 'db.sqlite3'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Define the expected data
        expected_column_names = ['column1', 'column2', 'column3']
        expected_rows = [('row1', 'row2', 'row3'), ('row4', 'row5', 'row6')]

        # Set the return values of the cursor
        mock_cursor.description = [(name,) for name in expected_column_names]
        mock_cursor.fetchall.return_value = expected_rows

        # Call the function
        column_names, rows = fetch_data_from_table('table_name')

        # Assert the results
        self.assertEqual(column_names, expected_column_names)
        self.assertEqual(rows, expected_rows)

        # Assert that the functions were called with the correct arguments
        mock_find_file_path.assert_called_once_with('db.sqlite3')
        mock_connect.assert_called_once_with('db.sqlite3')
        mock_cursor.execute.assert_called_once_with('SELECT * FROM table_name')
        mock_cursor.fetchall.assert_called_once()

    @patch('soft_skills.language_model.DataReader.find_file_path')
    @patch('sqlite3.connect')
    def test_fetch_data_from_table_empty_table(self, mock_connect, mock_find_file_path):
        # Mock the return values of the functions
        mock_find_file_path.return_value = 'db.sqlite3'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Set the return values of the cursor
        mock_cursor.description = []
        mock_cursor.fetchall.return_value = []

        # Call the function
        column_names, rows = fetch_data_from_table('table_name')

        # Assert the results
        self.assertEqual(column_names, [])
        self.assertEqual(rows, [])

        # Assert that the functions were called with the correct arguments
        mock_find_file_path.assert_called_once_with('db.sqlite3')
        mock_connect.assert_called_once_with('db.sqlite3')
        mock_cursor.execute.assert_called_once_with('SELECT * FROM table_name')
        mock_cursor.fetchall.assert_called_once()


class TestUpdateOriginEval(unittest.TestCase):

    @patch('DataReader.find_file_path', return_value='test_db.sqlite3')
    def test_update_origin_eval_success(self, mock_find_file_path):
        # Mock the sqlite3 connection and cursor
        mock_cursor = Mock()
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor

        # Mock the execute and commit methods
        mock_cursor.fetchall.return_value = [('origin_eval', 'question_id')]
        mock_cursor.description = [('origin_eval'), ('question_id')]

        with patch('sqlite3.connect', return_value=mock_conn):
            update_origin_eval(123, 'New origin evaluation')

        # Assert that the update query was executed
        mock_cursor.execute.assert_called_once_with("UPDATE web_answer SET origin_eval = ? WHERE question_id = ?", ('New origin evaluation', 123))
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('DataReader.find_file_path', return_value='test_db.sqlite3')
    def test_update_origin_eval_empty_string(self, mock_find_file_path):
        # Mock the sqlite3 connection and cursor
        mock_cursor = Mock()
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor

        with patch('sqlite3.connect', return_value=mock_conn):
            update_origin_eval(456, '')

        # Assert that the update query was executed with an empty string
        mock_cursor.execute.assert_called_once_with("UPDATE web_answer SET origin_eval = ? WHERE question_id = ?", ('', 456))
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()



def test_get_questions_answers_test_df():
    # Test if the function returns three DataFrames
    answer_df, question_df, test_df = get_questions_answers_test_df()
    assert isinstance(answer_df, pd.DataFrame)
    assert isinstance(question_df, pd.DataFrame)
    assert isinstance(test_df, pd.DataFrame)

    # Test if the answer_df DataFrame has the correct columns
    expected_columns = ['id', 'question_id', 'student_identifier', 'answer_text', 'testbox', 'origin_eval']
    assert set(answer_df.columns) == set(expected_columns)

    # Test if the answer_df DataFrame has the correct number of rows
    assert len(answer_df) > 0

    # Test if the question_df DataFrame has the correct columns
    expected_columns = ['id', 'question_id', 'question_text', 'question_type', 'question_weight', 'question_weight_type']
    assert set(question_df.columns) == set(expected_columns)

    # Test if the question_df DataFrame has the correct number of rows
    assert len(question_df) > 0

    # Test if the test_df DataFrame has the correct columns
    expected_columns = ['id', 'test_id', 'test_name', 'test_type', 'test_weight', 'test_weight_type']
    assert set(test_df.columns) == set(expected_columns)

    # Test if the test_df DataFrame has the correct number of rows
    assert len(test_df) > 0


if __name__ == "__main__":
    unittest.main()
