import streamlit as st
import json
import os

from backend.text_to_image.multimodels import get_model_pipeline, generate_image

# ---- Metadata file path ----
METADATA_PATH = "backend/text_to_image/outputs/generated_image_metadata.json"
# output_image_dir = "/Users/mdarifulislamshakil/MyProjects/ai-khichuri/backend/text_to_image/outputs/generated_images"


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
        print("images loaded : ", len(st.session_state.images))
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
               st.session_state.images = generate_image(query, st.session_state.pipeline)

            st.success("Image generated successfully!")

    st.divider()

    # ---- Image History ----
    if st.session_state.images:
        st.subheader("🖼️ Generated Images")

        for idx, item in enumerate(reversed(st.session_state.images), start=1):
            with st.container():
                st.markdown(f"**Prompt {idx}:** {item['query']}")
                st.markdown(f"**Refined Prompt {idx}:** {item['refined_query']}")
                st.image(item["path"], width=300)  # ✅ Smaller image
                col1,col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download Image",
                        data=item["path"],
                        file_name=f"image_{idx}.png",
                        mime="image/png"
                    )
                with col2:
                    re_generate = st.button("Re-Generate", key=f"re_generate_{idx}")
                    if re_generate:
                        with st.spinner("Re-generating image..."):
                            st.session_state.images = generate_image(item["query"], st.session_state.pipeline)
                            st.rerun()
                st.divider()
    else:
        st.info("No images generated yet.")
