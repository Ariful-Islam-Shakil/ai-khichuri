import streamlit as st

from backend.basic_chat.chat_app import chat_interface
from backend.text_to_image.generate_image_app import generate_image_interface
from backend.pdf_to_text.pdf_services_app import pdf_chat_interface


def main():
    st.set_page_config(
        page_title="AI Khichuri",
        page_icon="🤖",
        layout="wide"
    )

    # -------- Sidebar --------
    with st.sidebar:
        st.markdown("## 🤖 AI Khichuri")
        st.caption("One platform, many AI tools")

        feature = st.radio(
            "Choose a feature",
            [
                "💬 Chat Assistant",
                "🖼️ Text to Image",
                # Future features here
                "📄 PDF Chat",
                # "🎥 Video Generator",
                # "🧠 Agents"
            ]
        )

        st.divider()
        st.caption("More features coming soon 🚀")

    # -------- Main Content --------
    if feature == "💬 Chat Assistant":
        chat_interface(st)

    elif feature == "🖼️ Text to Image":
        generate_image_interface(st)
    elif feature == "📄 PDF Chat":
        pdf_chat_interface(st)


if __name__ == "__main__":
    main()
