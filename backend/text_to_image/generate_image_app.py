import streamlit as st
import json
import os

from backend.text_to_image.multimodels import get_model_pipeline, generate_image

# ---- Metadata file path ----
METADATA_PATH = (
    "/Users/mdarifulislamshakil/MyProjects/ai-khichuri/"
    "backend/text_to_image/outputs/generated_image_metada.json"
)


# ---- Helper functions ----
def load_image_history():
    if os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_image_history(images):
    os.makedirs(os.path.dirname(METADATA_PATH), exist_ok=True)
    with open(METADATA_PATH, "w") as f:
        json.dump(images, f, indent=2)


# ---- Main UI ----
def generate_image_interface(st):
    st.title("🖼️ AI Image Generator")
    st.caption("Generate realistic images from text prompts")

    # ---- Session State Init (ONLY ONCE) ----
    if "images" not in st.session_state:
        st.session_state.images = load_image_history()

    if "pipeline" not in st.session_state:
        st.session_state.pipeline = get_model_pipeline()

    # ---- Input Section ----
    with st.form("image_generation_form", clear_on_submit=True):
        query = st.text_input(
            "Enter your image prompt",
            placeholder="e.g., A man riding a horse on the sea shore"
        )
        submit = st.form_submit_button("🎨 Generate Image")

    # ---- Image Generation ----
    if submit:
        if not query.strip():
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Generating image..."):
                path = generate_image(query, st.session_state.pipeline)

            new_entry = {
                "path": path,
                "query": query
            }

            # ✅ Prevent accidental duplicates
            if new_entry not in st.session_state.images:
                st.session_state.images.append(new_entry)
                save_image_history(st.session_state.images)

            st.success("Image generated successfully!")

    st.divider()

    # ---- Image History ----
    if st.session_state.images:
        st.subheader("🖼️ Generated Images")

        for idx, item in enumerate(reversed(st.session_state.images), start=1):
            with st.container():
                st.markdown(f"**Prompt {idx}:** {item['query']}")
                st.image(item["path"], width=300)  # ✅ Smaller image
                st.divider()
    else:
        st.info("No images generated yet.")
