import sqlite3

def populate_db():
    with sqlite3.connect('mcq.db') as conn:
        cursor = conn.cursor()
        
        # Insert sample MCQs for Numpy
        cursor.executemany('''
            INSERT INTO questions (module, question, option1, option2, option3, option4, correct_option)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('Numpy', 'What does NumPy stand for?', 'Numerical Python', 'Numerous Python', 'Numbers in Python', 'None of the above', 1),
            ('Numpy', 'Which of the following is the correct way to import NumPy?', 'import numpy', 'import numpy as np', 'import np', 'include numpy', 2),
            # Add more Numpy questions here
        ])

        # Insert sample MCQs for Pandas
        cursor.executemany('''
            INSERT INTO questions (module, question, option1, option2, option3, option4, correct_option)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('Pandas', 'What does Pandas stand for?', 'Panel Data', 'Panel Data Analysis', 'Python Data Analysis', 'None of the above', 1),
            ('Pandas', 'Which of the following is the correct way to import Pandas?', 'import pandas', 'import pandas as pd', 'import pd', 'include pandas', 2),
            # Add more Pandas questions here
        ])

        # Insert sample MCQs for Matplotlib
        cursor.executemany('''
            INSERT INTO questions (module, question, option1, option2, option3, option4, correct_option)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('Matplotlib', 'What is Matplotlib used for?', 'Data Analysis', 'Data Visualization', 'Data Cleaning', 'None of the above', 2),
            ('Matplotlib', 'Which of the following is the correct way to import Matplotlib?', 'import matplotlib', 'import matplotlib.pyplot as plt', 'import plt', 'include matplotlib', 2),
            # Add more Matplotlib questions here
        ])

        conn.commit()

if __name__ == '__main__':
    populate_db()
