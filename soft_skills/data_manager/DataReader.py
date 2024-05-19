# import sqlite3
#
# # Connect to your SQLite database
# conn = sqlite3.connect('/Users/kseniadrokov/Documents/לימודים/שנה אחרונה/soft_skills/soft_skills/db.sqlite3')
#
# # Create a cursor object
# cursor = conn.cursor()
#
# # Fetch column names for the 'web_question' table
# cursor.execute("PRAGMA table_info(web_answer);")
# columns_info = cursor.fetchall()
#
# # Extract column names from the fetched information
# column_names = [info[1] for info in columns_info]
#
# # Print column names
# print("Column Names:")
# print(column_names)
#
# # Execute a query to fetch rows from the 'web_question' table
# cursor.execute("SELECT * FROM web_answer;")
# rows = cursor.fetchall()
#
# # Print the fetched rows with column names
# print("\nRows with Column Names:")
# for row in rows:
#     row_dict = dict(zip(column_names, row))
#     print(row_dict)
#
# # Close the cursor and connection
# cursor.close()
# conn.close()

import sqlite3
import pandas as pd

db_path = '../db.sqlite3'


def get_table_names():
    global db_path
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute the query to get the names of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Fetch all results from the executed query
    tables = cursor.fetchall()

    # Extract the table names from the results
    table_names = [table[0] for table in tables]

    # Close the connection
    conn.close()

    return table_names


def get_columns_names_from_table(tbl_name):
    global db_path
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({tbl_name});")
    columns_info = cursor.fetchall()

    # Extract column names from the fetched information
    column_names = [info[1] for info in columns_info]

    # Print column names
    print("Column Names:")
    print(column_names)

    # Close the connection
    conn.close()


def fetch_data_from_table(table_name):
    global db_path
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute the query to retrieve all data from the specified table
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)

    # Fetch all results from the executed query
    rows = cursor.fetchall()

    # Get the column names
    column_names = [description[0] for description in cursor.description]

    # Close the connection
    conn.close()

    return column_names, rows


def update_origin_eval(question_id, new_string):
    global db_path
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Define the update query
    query = """
    UPDATE web_answer
    SET origin_eval = ?
    WHERE question_id = ?
    """
    # Print the query and parameters for debugging
    # print("Executing SQL query:")
    # print(query)
    # print("Parameters:")
    # print((new_string, question_id))
    # print(f" question_id {question_id}")
    # Execute the update query with the provided new string and question_id
    cursor.execute(query, (new_string, question_id))

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()
    # print("Update successful.")
    # column_names, rows = fetch_data_from_table('web_answer')
    # # Print the column names and rows
    # print("Column Names:", column_names)
    # for row in rows:
    #     print(row)


# # Path to your SQLite database
# db_path = 'your_database.db'
# # The question_id you want to update
# question_id = 17160630595
# # The new string to save under the 'origin_eval' column
# new_string = "Your new string here"


def get_questions_answers_test_df():
    global db_path
    # Fetch the data from the table
    column_names, rows = fetch_data_from_table('web_answer')
    # Create a DataFrame from the fetched data
    answer_df = pd.DataFrame(rows, columns=column_names)
    # take the answer that has not been evaluated
    answer_df = answer_df[(answer_df['testbox'] == False) & (answer_df['origin_eval'] == 'Not yet evaluated')]
    # Remove '\r\n' from each text in 'answer_text' column
    answer_df['answer_text'] = answer_df['answer_text'].apply(lambda x: x.replace('\r', '').replace('\n', ''))
    # Drop rows where student_identifier is 'dyotamd2@gmail.com'
    answer_df = answer_df[answer_df['student_identifier'] != 'dyotamd2@gmail.com']
    column_names, rows = fetch_data_from_table('web_question')
    question_df = pd.DataFrame(rows, columns=column_names)
    column_names, rows = fetch_data_from_table('web_test')
    test_df = pd.DataFrame(rows, columns=column_names)
    return answer_df, question_df, test_df
# Print the DataFrame
# print(answer_df)
