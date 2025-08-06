import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import openai
import base64

# Setup OpenAI API
openai.api_key = st.secrets["OPENAI_API_KEY"]

def extract_text_and_images(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text_content = ""
    image_text = ""

    for page_num, page in enumerate(doc):
        text_content += page.get_text()

        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            ocr_result = pytesseract.image_to_string(image)
            image_text += f"\n[Page {page_num+1} Image {img_index+1}]:\n{ocr_result}"

    return text_content + "\n" + image_text

def ask_chatgpt(query, context):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial analyst assistant that understands text and OCR content from PDFs, including charts, graphs, and numbers."},
            {"role": "user", "content": f"PDF Content:\n{context}\n\nNow answer this: {query}"}
        ],
        temperature=0.2,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

# UI
st.title("📊 Financial PDF Analyst (ChatGPT-powered)")
uploaded_file = st.file_uploader("Upload a PDF report (text & graphs)", type="pdf")

if uploaded_file:
    st.success("✅ File uploaded successfully!")

    if st.button("📥 Extract & Analyze"):
        with st.spinner("Extracting text + images from PDF..."):
            extracted_content = extract_text_and_images(uploaded_file)

        st.text_area("📄 Extracted Content (text + images)", extracted_content[:3000], height=300)

        question = st.text_input("Ask a question based on this PDF:")

        if question:
            with st.spinner("Asking ChatGPT..."):
                answer = ask_chatgpt(question, extracted_content)
            st.markdown(f"**Answer:** {answer}")
