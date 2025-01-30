import psycopg2
from psycopg2 import sql

DB_NAME = "test"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    """Creates a new PostgreSQL database."""
    conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    conn.autocommit = True
    cursor = conn.cursor()
    
    cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(DB_NAME)))
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
    
    cursor.close()
    conn.close()
    print(f"Database '{DB_NAME}' created successfully!")

def create_tables():
    """Creates three tables in the database."""
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cursor = conn.cursor()

    create_table_queries = [
        """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id),
            total_amount DECIMAL(10,2) NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10,2) NOT NULL
        )"""
    ]

    for query in create_table_queries:
        cursor.execute(query)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Tables created successfully!")

def insert_data():
    """Inserts sample data into the tables."""
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id", ("John Doe", "john@example.com"))
    user_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", ("Laptop", 1200.99))
    product_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (%s, %s)", (user_id, 1200.99))

    conn.commit()
    cursor.close()
    conn.close()
    print("Sample data inserted successfully!")

if __name__ == "__main__":
    create_database()
    create_tables()
    insert_data()
