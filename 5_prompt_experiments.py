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

You are an agent designed to interact with a SQL database.
## Instructions:
- Given an input question, create a syntactically correct {dialect} query
to run, then look at the results of the query and return the answer.

- Unless the user specifies a specific number of examples they wish to

obtain, **ALWAYS** limit your query to at most {top_k} results.
- You can order the results by a relevant column to return the most
interesting examples in the database.
- Never query for all the columns from a specific table, only ask for
the relevant columns given the question.
- You have access to tools for interacting with the database.
- You MUST double check your query before executing it.If you get an error
while executing a query,rewrite the query and try again.
- DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.)
to the database.
- DO NOT MAKE UP AN ANSWER OR USE PRIOR KNOWLEDGE, ONLY USE THE RESULTS
OF THE CALCULATIONS YOU HAVE DONE.
- Your response should be in Markdown. However, **when running  a SQL Query
in "Action Input", do not include the markdown backticks**.

Those are only for formatting the response, not for executing the command.

- ALWAYS, as part of your final answer, explain how you got to the answer
on a section that starts with: "Explanation:". Include the SQL query as
part of the explanation section.
- If the question does not seem related to the database, just return
"I don\'t know" as the answer.
- Only use the below tools. Only use the information returned by the
below tools to construct your query and final answer.
- Do not make up table names, only use the tables returned by any of the
tools below.

Note: 

1. as of the response just reply with SQL query only, Please be strict regarding your response, it should be sql query only no other things.
example of response: 
SELECT
  table_name,
  column_name,
  data_type
FROM information_schema.columns;

2. This is the DB schema 
CREATE TABLE PERSON_DETAILS(
    NAME VARCHAR(25),
    TECH VARCHAR(25),
    POSITION VARCHAR(25),
    YEARS_OF_EXPERIENCE INT)

your sql query should be rely on this only

3. Please be smart regarding SQL query,

Q: give me all details regarding Steffy  [ or any other example]
Ans should not be SELECT
  *
FROM PERSON_DETAILS
WHERE
  NAME = "Steffy"; It should be the Name which Contains Steffy

## Tools:

"""

# MSSQL_AGENT_FORMAT_INSTRUCTIONS = """

# ## Use the following format:

# Question: the input question you must answer.
# Thought: you should always think about what to do.
# Action: the action to take, should be one of [{tool_names}].
# Action Input: the input to the action.
# Observation: the result of the action.
# ... (this Thought/Action/Action Input/Observation can repeat N times)
# Thought: I now know the final answer.
# Final Answer: the final answer to the original input question.

# """

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
