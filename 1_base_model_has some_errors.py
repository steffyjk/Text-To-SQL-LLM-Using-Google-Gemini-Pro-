from dotenv import load_dotenv

load_dotenv()  # load all  the env variables

import streamlit as st
import os
import sqlite3

import google.generativeai as genai

## config our google api key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Create a function to load google gemini model and provide sql query as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content([prompt, question])
    return response.text


# Create a Function to retrive query from the sql database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()

    for row in rows:
        print("---> Data from read_sql_query", row)
    return rows


# Define Your Prompt
custom_prompt = [
    """
    You are an expert in converting Englisg question to SQL query!
    The SQL database hasa the Table PERSON_DETAILS and has the following columns - NAME, TECH, POSITION, YEARS_OF_EXPERIENCE
    \n\n For example, \nExample 1 - How many enteries of records are present?,
    the SQL command will be something like this SELECT COUNT(*) FROM PERSON_DETAILS;
    \nExample 2 - Tell me all the persons who are Software Engineer?, the SQL command will be something like
    this SELECT * FROM PERSON_DETAILS where POSITION="Sofware Engineer";
    Also the sql code should not have ``` in begining or end and sql word in the output
    """
]


# StreamLit Application

st.set_page_config(page_title="Imma Your Bro!")

st.header("Gemini Driven App To Retrive SQL Data")

question_asked = st.text_input("Input: ", key="input")

submit = st.button("Ask Me A Fucking Question Bro!")


# If submit is clicked

if submit:
    response = get_gemini_response(question=question_asked, prompt=custom_prompt)
    print(response)
    data = read_sql_query(response, os.getenv("DB_NAME"))
    st.subheader("The Response Is: ")
    for row in data:
        print("--> HEY", row)
        st.header(row)
