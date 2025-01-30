def get_referred_tables(user_prompt: str, table_names: list) -> list:
    # Constructing the prompt with a system message and user input
    system_message = "You are an assistant capable of understanding SQL-related queries. You will be provided with a list of table names and descriptions. Your task is to determine all the tables referenced in the user's input based on the descriptions."

    # Constructing the user prompt for the LLM
    table_descriptions = "\n".join([f"{table}: {get_table_description(table)}" for table in table_names])
    prompt = f"{system_message}\n\nTable Descriptions:\n{table_descriptions}\n\nUser Query: {user_prompt}\n\nWhich tables are being referred to?"

    # Call to OpenAI API (ensure you have configured your OpenAI API key correctly)
    response = openai.Completion.create(
        model="text-davinci-003",  # Or use any model that suits your needs
        prompt=prompt,
        max_tokens=150,
        temperature=0.5
    )

    # Extract the table names from the response (Assuming the LLM will return a list of table names in the response)
    referred_tables = response.choices[0].text.strip().split(',')
    
    # Clean up the list (strip any leading/trailing spaces)
    referred_tables = [table.strip() for table in referred_tables]
    
    # Filter out any invalid or non-existent table names
    valid_tables = [table for table in referred_tables if table in table_names]
    
    return valid_tables