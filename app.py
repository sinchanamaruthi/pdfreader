import streamlit as st
import fitz  # PyMuPDF
import openai
from PIL import Image
import io
import base64

# Load secret from Streamlit Cloud (we'll set it there later)
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="📄 GPT-4 Vision PDF Assistant")
st.title("📄 GPT-4 Vision PDF Assistant")

uploaded_file = st.file_uploader("📤 Upload a PDF file", type=["pdf"])

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    pages = []
    st.write("📸 Select pages to analyze:")

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        st.image(img, caption=f"Page {i + 1}")
        pages.append(img)

    selected_pages = st.multiselect("✅ Pick pages to send to GPT", list(range(1, len(pages)+1)), default=[1])

    question = st.text_input("🧠 What do you want to ask GPT about the selected pages?")

    if st.button("Ask GPT") and selected_pages and question:
        st.info("📡 Sending to GPT-4 Vision...")

        image_parts = []
        for pg in selected_pages:
            buffer = io.BytesIO()
            pages[pg-1].save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            image_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}",
                    "detail": "high"
                }
            })

        messages = [
            {"role": "user", "content": [
                {"type": "text", "text": question},
                *image_parts
            ]}
        ]

        try:
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1500
            )
            st.success("📌 Answer from GPT:")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"❌ GPT error: {e}")
