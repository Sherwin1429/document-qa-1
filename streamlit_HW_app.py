import streamlit as st
from openai import OpenAI
import fitz


# Function to read text from an uploaded PDF file.
def read_pdf(uploaded_file):
    pdf_document = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    text = ""

    for page in pdf_document:
        text += page.get_text()

    return text


# Show title and description.
st.title("My Document Question Answering")

st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, "
    "which you can get [here](https://platform.openai.com/account/api-keys)."
)


# Ask user for their OpenAI API key.
openai_api_key = st.text_input(
    "OpenAI API Key",
    type="password"
)


# Check if an API key was entered.
if not openai_api_key:

    st.info(
        "Please add your OpenAI API key to continue.",
        icon="🗝️"
    )

else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Validate the API key immediately.
    try:
        client.models.list()
        st.success("API key is valid!")

    except Exception:
        st.error("Invalid OpenAI API key. Please try again.")
        st.stop()


    # Let the user upload only a TXT or PDF file.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .pdf)",
        type=("txt", "pdf")
    )


    # Ask the user for a question.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )


    # Continue when a document and question are provided.
    if uploaded_file and question:

        # Determine the uploaded file's extension.
        file_extension = uploaded_file.name.split('.')[-1]

        # Read TXT files normally.
        if file_extension == 'txt':
            document = uploaded_file.read().decode()

        # Read PDF files using the read_pdf function.
        elif file_extension == 'pdf':
            document = read_pdf(uploaded_file)

        # Reject unsupported file types.
        else:
            st.error("Unsupported file type.")
            st.stop()


        # Create the message that will be sent to the LLM.
        messages = [
            {
                "role": "user",
                "content": (
                    f"Here's a document: {document} "
                    f"\n\n---\n\n {question}"
                ),
            }
        ]


        # Select the model being tested.
        model_name = "gpt-5-nano"
        # Show which model is being used.
        st.info(f"Model being tested: {model_name}")


        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True,
        )


        # Stream the response to the app.
        st.write_stream(stream)