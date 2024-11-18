import openai
import streamlit as st
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter

SAMBANOVA_API_KEY = "81fd70a7-9704-4a22-88ea-b250aad13ee5"
st.session_state["rag"] = True
st.session_state["collection"] = True
print(st.session_state)
chromadb.api.client.SharedSystemClient.clear_system_cache()
chroma_client = chromadb.Client()
if st.session_state["collection"]:
    collections = chroma_client.create_collection(name="my_collection3")
    st.session_state["collection"] = False


def pdftochroma(text):
    import pdfplumber
    import chromadb

    # print('called1')
    def extract_text_from_pdf(pdf_path):
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text

    # Example usage
    pdf_path = text
    text = extract_text_from_pdf(pdf_path)
    # print('text')
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=500,
        chunk_overlap=200,
    )
    listtext = text_splitter.split_text(text)

    def chromaclient(text):
        collections.add(
            documents=text,
            metadatas=[{"source": "my_source"} for i in range(1, len(text) + 1)],
            ids=["id" + str(i) for i in range(1, len(text) + 1)],
        )

    chromaclient(listtext)
def similardata(query):
    results = collections.query(query_texts=[query], n_results=10)

    ans = ""
    for i in results["documents"][0]:
        ans += i
    return ans


def generate_response(prompt):
    response = client.chat.completions.create(
        model="Meta-Llama-3.1-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        top_p=0.1,
    )
    return response.choices[0].message.content


def generate_rag_response(prompt):
    content = similardata(prompt)
    response = client.chat.completions.create(
        model="Meta-Llama-3.1-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {
                "role": "system",
                "content": f"content:{content} \nbased on the content answer the following question answer generally if required content is absent",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        top_p=0.1,
    )
    return response.choices[0].message.content


client = openai.OpenAI(
    api_key="81fd70a7-9704-4a22-88ea-b250aad13ee5",
    base_url="https://api.sambanova.ai/v1",
)

st.title("Personalized Learning Platform")
st.write("Learn dynamically with AI-generated personalized content.")

# Collect user preferences
st.sidebar.title("User Profile")
name = st.sidebar.text_input("Enter your name:")
age = st.sidebar.number_input("Age", min_value=5, max_value=100, step=1)
learning_preference = st.sidebar.selectbox(
    "Preferred Learning Style", ["Text", "Visual", "Interactive"]
)
topics = st.sidebar.multiselect(
    "Topics of Interest", ["Math", "Science", "History", "Programming", "Languages"]
)
pdf = st.file_uploader("Upload any book (optional)", type="pdf")
if pdf and st.session_state["rag"]:
    with st.spinner("Parsing Data"):
        pdftochroma(pdf)
    st.session_state["rag"] = False
if st.sidebar.button("Save Profile"):
    st.sidebar.success("Profile saved!")

# Main learning interaction
st.header("Interactive Learning")
user_query = st.text_input("What would you like to learn about today?")

if user_query:
    with st.spinner("Generating personalized content..."):
        response = (
            "This is your personalized response based on: " + user_query
        )  # Placeholder for AI response
    AI_response = generate_rag_response(user_query)

    st.write("### AI Response:")
    st.write(AI_response)

    # Add a personalized quiz or follow-up question
    st.write("### Quiz Question:")
    quiz = generate_response("generate one question for this" + user_query)
    st.write(quiz)
    user_answer = st.text_input("Your Answer:")

    if user_answer and st.button("Submit Answer"):
        with st.spinner("Evaluating your response..."):
            feedback = generate_response(
                quiz + "the answer:" + user_answer + "provide feedback and evaluate"
            )  # Placeholder for feedback
        st.write("### Feedback:")
        st.write(feedback)
