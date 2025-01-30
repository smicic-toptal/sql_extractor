import os
import re
import psycopg2
from dotenv import load_dotenv
from openai import OpenAI
from logging_config import logger

load_dotenv()

class SQLExecuter:
    def __init__(self, db_params: dict, model_name: str = "gpt-4o") -> None:
        self.db_params = db_params
        self.conn = psycopg2.connect(**db_params)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name
        self.code_block = ""
        self.code_blocks = [r"```sql(.*?)```", r"```(.*?)```"]
        self.retry_limit = 3

    def get_table_description(self, table_name: str) -> str:
        try:
            query = f"""
            SELECT column_name, data_type, character_maximum_length, column_default, is_nullable
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE table_name = '{table_name}';
            """
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                descriptions = cursor.fetchall()
                
            if descriptions:
                formatted_description = "\n".join(
                    [f"Column: {desc[0]}, Type: {desc[1]}, Max Length: {desc[2]}, Default: {desc[3]}, Nullable: {desc[4]}"
                    for desc in descriptions]
                )
                return formatted_description
            else:
                return "No description available."
        except Exception as e:
            logger.error(f"Error fetching table description: {e}")
            return ""

    def _extract_sql_code(self, text: str, regexp: str) -> str:
        match = re.search(regexp, text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _call_llm(self, user_question: str, table_name: str, error: str = None, previous_code: str = None) -> str:
        system_message = f"""
Act as a data scientist and SQL expert. Write a SQL query to solve the given problem.
The table '{table_name}' has the following description: {self.get_table_description(table_name)}.
Ensure the query is syntactically correct for PostgreSQL.
"""

        prompt_problem = f"""
Solve the following problem:
Generate a SQL query for this request:
{user_question}

Guidelines:
1. Provide only the SQL query without any explanation.
2. The table is named '{table_name}'.
3. Ensure the query is valid for PostgreSQL.
"""
        print(system_message)
        print(prompt_problem)
        if error and previous_code:
            prompt_problem += f"\nThe previous query failed with error: {error}.\nPrevious query: {previous_code}\nTry again."

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_problem},
        ]

        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
        )

        return chat_completion.choices[0].message.content.strip()

    def execute_query(self, user_question: str, table_name: str):
        result = None
        error = None
        previous_code = None

        for attempt in range(self.retry_limit):
            generated_code = self._call_llm(user_question, table_name, error, previous_code)
            self.code_block = generated_code

            results = []
            for regexp in self.code_blocks:
                cleaned_code = self._extract_sql_code(generated_code, regexp)
                if cleaned_code:
                    results.append(cleaned_code)
            results.append(generated_code)

            if not results:
                logger.error("No valid SQL query found in the LLM response.")
                return None

            for cleaned_code in results:
                try:
                    with self.conn.cursor() as cursor:
                        cursor.execute(cleaned_code)
                        result = cursor.fetchall()
                    return self._format_response_with_llm(user_question, result)
                except Exception as e:
                    error = str(e)
                    previous_code = cleaned_code
                    logger.warning(f"Execution error: {error} when executing query {previous_code}. Trying again.")

        logger.error("Failed to execute query after multiple retries.")
        return None

    def _format_response_with_llm(self, user_question: str, result) -> str:
        """
        Uses LLM to generate a well-structured response.
        """
        prompt = f"""
The user asked the following question:
{user_question}

The SQL query result is:
{result}

Formulate a clear and concise answer in English.
"""
        messages = [
            {"role": "system", "content": "Act as a data analysis assistant."},
            {"role": "user", "content": prompt},
        ]

        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
        )

        return (chat_completion.choices[0].message.content.strip(), result, self.code_block)