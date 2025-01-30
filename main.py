import os
from dotenv import load_dotenv
from logging_config import logger
from sql_executer import SQLExecuter

def main():
    load_dotenv()
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', 5432),
        'dbname': os.getenv('DB_NAME', 'test_db'),
        'user': os.getenv('DB_USER', 'user'),
        'password': os.getenv('DB_PASSWORD', 'password'),
    }

    sql_executer = SQLExecuter(db_params)

    user_question = "How many users are in users table?"
    table_name = "users"

    result = sql_executer.execute_query(user_question, table_name)

    # Print the result
    if result:
        print("Generated SQL Query:", sql_executer.code_block)
        print("Formatted Response:", result[0])
        print("SQL Query Result:", result[1])
    else:
        print("Failed to execute query.")

if __name__ == "__main__":
    main()
