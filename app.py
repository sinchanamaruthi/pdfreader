import streamlit as st
import fitz  # PyMuPDF
import base64
import openai
import tempfile

# Load API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="PDF Chat with GPT-4o", layout="wide")
st.title("📄 Chat with Your PDF (Images Included)")

uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
user_question = st.text_input("Ask a question about the PDF 👇")

if uploaded_file and user_question:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    doc = fitz.open(tmp_path)
    images = []

    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        b64_img = base64.b64encode(img_bytes).decode("utf-8")
        images.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64_img}"
            }
        })

    st.info("🧠 Sending to GPT-4o... Please wait ⏳")

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that reads PDFs containing both text and images."},
                {"role": "user", "content": f"My question: {user_question}"},
                *images
            ],
            temperature=0.3
        )
        answer = response.choices[0].message.content
        st.success("✅ GPT's Answer:")
        st.write(answer)

    except Exception as e:
        st.error(f"❌ GPT error: {e}")
