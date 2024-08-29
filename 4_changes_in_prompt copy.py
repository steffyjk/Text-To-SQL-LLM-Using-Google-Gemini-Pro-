from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the Google Gemini Pro API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Function to generate SQL query using Gemini Pro
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + f"\n\nUser Question: {question}")

    # Extract the SQL query by stripping out any unwanted text
    query = response.text.strip()

    # Remove any prefix like "SQL: " or similar
    if query.lower().startswith("sql:"):
        query = query[4:].strip()

    return query


# Function to retrieve data from the SQL database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows


# Function to transform messages for Gemini Pro model
def transform_to_gemini(messages_chatgpt):
    messages_gemini = []
    system_prompt = ""
    for message in messages_chatgpt:
        if message["role"] == "system":
            system_prompt = message["content"]
        elif message["role"] == "user":
            messages_gemini.append({"role": "user", "parts": [message["content"]]})
        elif message["role"] == "assistant":
            messages_gemini.append({"role": "model", "parts": [message["content"]]})
    if system_prompt:
        messages_gemini[0]["parts"].insert(0, f"*{system_prompt}*")
    return messages_gemini


# Custom prompt for SQL query generation
custom_prompt = [
    """
    You are an expert at converting English questions into SQL queries.
    The database contains a table named PERSON_DETAILS with the following columns: NAME, TECH, POSITION, and YEARS_OF_EXPERIENCE.

    Below are various examples illustrating different SQL operations:

    Example 1: How many records are in the table?
    Output: SELECT COUNT(*) FROM PERSON_DETAILS;

    Example 2: List all the people who are Software Engineers.
    Output: SELECT * FROM PERSON_DETAILS WHERE POSITION LIKE '%Software Engineer%';

    Example 3: Find all people with the name starting with 'John'.
    Output: SELECT * FROM PERSON_DETAILS WHERE NAME LIKE 'John%';

    Example 4: Show all records where the tech is not 'Python'.
    Output: SELECT * FROM PERSON_DETAILS WHERE TECH LIKE '%Python%' AND TECH IS NOT NULL;

    Example 5: Retrieve records for people who have more than 5 years of experience.
    Output: SELECT * FROM PERSON_DETAILS WHERE YEARS_OF_EXPERIENCE > 5;

    Example 6: Count the number of distinct technologies used.
    Output: SELECT COUNT(DISTINCT TECH) FROM PERSON_DETAILS;

    Example 7: Find all records where the position contains the word 'Engineer'.
    Output: SELECT * FROM PERSON_DETAILS WHERE POSITION LIKE '%Engineer%';

    Example 8: List all people sorted by their years of experience in descending order.
    Output: SELECT * FROM PERSON_DETAILS ORDER BY YEARS_OF_EXPERIENCE DESC;

    Example 9: Retrieve the name and position of people who have 'Data' in their position title and have at least 3 years of experience.
    Output: SELECT NAME, POSITION FROM PERSON_DETAILS WHERE POSITION LIKE '%Data%' AND YEARS_OF_EXPERIENCE >= 3;

    Note: Use the `LIKE` operator instead of `=` for string matching in SQL queries, unless the question specifies exact matching or synonymous terms like "exact", "precise", or "specific."
    Generate the appropriate SQL query for any English question related to this table. The output should only contain the SQL query, without any backticks or the word 'sql'.
    """
]


# Example messages to demonstrate transformation
messages_chatgpt = [
    {"role": "system", "content": "Respond only in Yoda-speak using always 10 words"},
    {"role": "user", "content": "How are you today?"},
    {"role": "assistant", "content": "Good am I, thank you. And you must be, hmm??"},
    {"role": "user", "content": "I'm the new padawan, please teach me"},
]

# Transform messages for Gemini Pro
demoMessage = transform_to_gemini([{"role": "user", "content": custom_prompt[0]}])

# Streamlit App
st.set_page_config(page_title="Gemini-Driven SQL Convertor")
st.header("Hey, ask Me Question!")

# Input question from user
question_asked = st.text_input("Enter your question:", key="input")

# Submit button
submit = st.button("Ask BROoooooo!")

# Handle submit button click
if submit:
    # Generate SQL query from Gemini Pro
    response = get_gemini_response(
        question=question_asked, prompt=demoMessage[0]["parts"][0]
    )

    # Display SQL query
    st.subheader("Generated SQL Query:")
    st.code(response, language="sql")

    # Fetch data from the database
    data = read_sql_query(response, os.getenv("DB_NAME"))

    # Display the data
    st.subheader("Query Result:")
    for row in data:
        st.write(row)
