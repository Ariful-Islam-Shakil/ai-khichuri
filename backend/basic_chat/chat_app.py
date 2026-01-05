import streamlit as st
import os
from dotenv import load_dotenv

from langchain.messages import SystemMessage, HumanMessage, AIMessage
from backend.basic_chat.history_management import (
    get_mongodb_collection,
    create_user,
    save_message_to_conversation,
    get_chat_titles,
    get_conversation_history,
    update_title,
    create_new_chat,
    get_current_chat_title,
    delete_conversation
)
from backend.basic_chat.chat_model import get_chat_model

load_dotenv()



def chat_interface(st):
    st.set_page_config(page_title="AI Khichuri 🥣", layout="wide")
    st.title("🥣 AI Khichuri – Chat")

    # -------------------------------
    # MongoDB
    # -------------------------------
    collection = get_mongodb_collection()

    # -------------------------------
    # Sidebar – User Login
    # -------------------------------
    with st.sidebar:
        st.header("👤 User")
        user_name = st.text_input("Enter user name")

        if st.button("Login / Create"):
            if user_name:
                create_user(user_name, collection)  # safe if exists
                st.session_state.user_name = user_name
                st.success(f"Logged in as {user_name}")
                st.rerun()
            else:
                st.warning("Please enter a user name")

    if "user_name" not in st.session_state:
        st.info("👈 Login to start chatting")
        return

    # -------------------------------
    # Provider & Model Selection
    # -------------------------------
    provider_models = {
        "groq": [
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768"
        ],
        "gemini": [
            "gemini-2.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro"
        ],
        "huggingface": [
            "openai/gpt-oss-20b",
            "meta-llama/Llama-2-7b-chat-hf",
            "tiiuae/falcon-7b-instruct"
        ]
    }

    with st.expander("🤖 Model Configuration"):
        col1, col2, col3 = st.columns(3)

        with col1:
            provider = st.selectbox("Provider", list(provider_models.keys()))

        with col2:
            model_name = st.selectbox("Model", provider_models[provider])

        with col3:
            temperature = st.slider("Temperature", 0.0, 1.0, 0.3)

    # -------------------------------
    # API Key (from .env)
    # -------------------------------
    PROVIDER_KEY_MAP = {
        "groq": "GROQ_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "huggingface": "HF_TOKEN",
    }

    env_key_name = PROVIDER_KEY_MAP.get(provider)
    api_key = os.getenv(env_key_name)

    if not api_key:
        st.error(
            f"{env_key_name} not found in .env file. "
            f"Please set it before continuing."
        )
        return

    # -------------------------------
    # Conversation Setup
    # -------------------------------
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = ""
        st.session_state.messages = []

    # -------------------------------
    # Sidebar – Chat List
    # -------------------------------
    with st.sidebar:
        st.header("💬 Chats")

        if st.button("➕ New Chat", use_container_width=True):
            conv_id = create_new_chat(
                user_name=st.session_state.user_name,
                collection=collection,
                title="New Chat",
                system_prompt="You are a helpful assistant."
            )
            st.session_state.conversation_id = conv_id
            st.session_state.messages = [
                SystemMessage(content="You are a helpful assistant.")
            ]
            st.rerun()

        st.divider()

        chat_titles = get_chat_titles(
            st.session_state.user_name,
            collection
        )

        for chat in chat_titles:
            chat_id = chat["conversation_id"]
            chat_title = chat["title"] or "Untitled Chat"

            is_active = chat_id == st.session_state.conversation_id

            col1, col2 = st.columns([5, 1])

            # 🔵 Active chat highlight
            with col1:
                btn_label = f"▶ {chat_title}" if is_active else chat_title

                if st.button(
                    btn_label,
                    key=f"open_{chat_id}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.conversation_id = chat_id
                    st.session_state.messages = get_conversation_history(
                        user_name=st.session_state.user_name,
                        conversation_id=chat_id,
                        collection=collection
                    )
                    st.rerun()

            # 🗑️ Delete button
            with col2:
                if st.button("🗑️", key=f"delete_{chat_id}"):
                    delete_conversation(
                        user_name=st.session_state.user_name,
                        conversation_id=chat_id,
                        collection=collection
                    )

                    # If deleted chat was active → reset
                    if is_active:
                        st.session_state.pop("conversation_id", None)
                        st.session_state.pop("messages", None)

                    st.rerun()

    # -------------------------------
    # Chat Title Edit
    # -------------------------------
    current_title = get_current_chat_title(
        st.session_state.user_name,
        st.session_state.conversation_id,
        collection
    )
    st.session_state.current_title = current_title

    with st.expander("Edit Chat Title"):
        new_title = st.text_input(
            "✏️ Chat Title",
            value=st.session_state.current_title,
            # placeholder="Rename this chat",
            key="chat_title_input"
        )

        if st.button("Update Title", use_container_width=True):
            if new_title.strip() and new_title != current_title:
                update_title(
                    user_name=st.session_state.user_name,
                    conversation_id=st.session_state.conversation_id,
                    title=new_title.strip(),
                    collection=collection
                )
                st.success("Title updated")
                st.rerun()


    # -------------------------------
    # Display Chat History
    # -------------------------------
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(msg.content)

    # -------------------------------
    # Chat Input
    # -------------------------------
    user_input = st.chat_input("Type your message...")

    if user_input:
        human_msg = HumanMessage(content=user_input)
        st.session_state.messages.append(human_msg)

        with st.chat_message("user"):
            st.markdown(user_input)

        model = get_chat_model(
            provider=provider,
            api_key=api_key,
            model_name=model_name,
            temperature=temperature
        )

        response = model.invoke(st.session_state.messages)
        ai_msg = AIMessage(content=response.content)
        st.session_state.messages.append(ai_msg)

        with st.chat_message("assistant"):
            st.markdown(response.content)

        save_message_to_conversation(
            user_name=st.session_state.user_name,
            conversation_id=st.session_state.conversation_id,
            messages=st.session_state.messages,
            collection=collection
        )
