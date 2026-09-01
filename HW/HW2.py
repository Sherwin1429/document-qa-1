import streamlit as st
from openai import OpenAI
from google import genai
import requests
from bs4 import BeautifulSoup


# --------------------------------------------------
# Function to Read Content from a URL
# --------------------------------------------------

def read_url_content(url):
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        return soup.get_text(separator=" ", strip=True)

    except requests.RequestException as e:
        st.error(f"Error reading {url}: {e}")
        return None


# --------------------------------------------------
# Page Title
# --------------------------------------------------

st.title("Homework 2 - URL Summarizer")

st.write(
    "Enter a webpage URL below and choose your summary options "
    "from the sidebar."
)


# --------------------------------------------------
# URL Input
# --------------------------------------------------

url = st.text_input(
    "Enter a webpage URL",
    placeholder="https://example.com"
)


# --------------------------------------------------
# Sidebar - Summary Type
# --------------------------------------------------

summary_type = st.sidebar.selectbox(
    "Choose a summary type",
    [
        "Summarize the webpage in 100 words",
        "Summarize the webpage in 2 connecting paragraphs",
        "Summarize the webpage in 5 bullet points"
    ]
)


# --------------------------------------------------
# Sidebar - Output Language
# --------------------------------------------------

language = st.sidebar.selectbox(
    "Choose an output language",
    [
        "English",
        "Spanish",
        "French",
        "German",
        "Italian"
    ]
)


# --------------------------------------------------
# Sidebar - LLM Provider
# --------------------------------------------------

llm_choice = st.sidebar.selectbox(
    "Choose an LLM",
    [
        "OpenAI",
        "Gemini"
    ]
)


# --------------------------------------------------
# Sidebar - Advanced Model
# --------------------------------------------------

use_advanced_model = st.sidebar.checkbox(
    "Use advanced model"
)


# --------------------------------------------------
# Select Model
# --------------------------------------------------

if llm_choice == "OpenAI":

    if use_advanced_model:
        model_name = "gpt-5-mini"
    else:
        model_name = "gpt-5-nano"

else:

    if use_advanced_model:
         model_name = "gemini-3.5-flash"
    else:
        model_name = "gemini-3.5-flash-lite"

# Show selected model
st.sidebar.caption(f"Selected model: {model_name}")


# --------------------------------------------------
# API Keys
# --------------------------------------------------

openai_api_key = st.secrets["OPENAI_API_KEY"]
gemini_api_key = st.secrets["GEMINI_API_KEY"]


# --------------------------------------------------
# Create API Clients
# --------------------------------------------------

openai_client = OpenAI(
    api_key=openai_api_key
)

gemini_client = genai.Client(
    api_key=gemini_api_key
)


# --------------------------------------------------
# Process URL
# --------------------------------------------------

if url:

    with st.spinner("Reading webpage..."):

        webpage_content = read_url_content(url)


    if webpage_content:

        # --------------------------------------------------
        # Create Prompt
        # --------------------------------------------------

        prompt = (
            f"You are a webpage summarization assistant.\n\n"
            f"{summary_type}.\n\n"
            f"Provide the summary in {language}.\n\n"
            f"Webpage content:\n"
            f"{webpage_content}"
        )


        # --------------------------------------------------
        # Display Summary Heading
        # --------------------------------------------------

        st.subheader("Summary")


        # --------------------------------------------------
        # OpenAI
        # --------------------------------------------------

        if llm_choice == "OpenAI":

            try:

                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are a webpage summarization assistant."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

                stream = openai_client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    stream=True
                )

                st.write_stream(stream)

            except Exception as e:

                st.error(
                    f"OpenAI error: {e}"
                )


        # --------------------------------------------------
        # Gemini
        # --------------------------------------------------

        elif llm_choice == "Gemini":

            try:

                response = gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                st.write(response.text)

            except Exception as e:

                st.error(
                    f"Gemini error: {e}"
                )