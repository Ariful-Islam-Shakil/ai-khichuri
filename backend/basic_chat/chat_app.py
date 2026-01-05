import streamlit as st
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from backend.basic_chat.history_management import (
    get_mongodb_collection,
    create_user,
    save_message_to_conversation,
    get_chat_titles,
    get_conversation_history,
    update_title,
    create_new_chat,
)
from backend.basic_chat.chat_model import get_chat_model


def get_current_chat_title(user_name, conversation_id, collection):
    doc = collection.find_one(
        {
            "user_name": user_name,
            "conversations.conversation_id": conversation_id
        },
        {"conversations.$": 1}
    )
    if doc and "conversations" in doc:
        return doc["conversations"][0].get("title", "")
    return ""


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
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro"
        ],
        "huggingface": [
            "mistralai/Mistral-7B-Instruct-v0.2",
            "meta-llama/Llama-2-7b-chat-hf",
            "tiiuae/falcon-7b-instruct"
        ]
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        provider = st.selectbox("Provider", list(provider_models.keys()))

    with col2:
        model_name = st.selectbox("Model", provider_models[provider])

    with col3:
        temperature = st.slider("Temperature", 0.0, 1.0, 0.3)

    # -------------------------------
    # API Key
    # -------------------------------
    api_key = st.text_input(f"{provider.upper()} API Key", type="password")

    if not api_key:
        st.warning("Please enter API key to continue")
        return

    # -------------------------------
    # Conversation Setup
    # -------------------------------
    if "conversation_id" not in st.session_state:
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

    # -------------------------------
    # Sidebar – Chat List
    # -------------------------------
    with st.sidebar:
        st.header("💬 Chats")

        if st.button("➕ New Chat"):
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
            if st.button(
                chat["title"] or "Untitled Chat",
                key=chat["conversation_id"]
            ):
                st.session_state.conversation_id = chat["conversation_id"]
                st.session_state.messages = get_conversation_history(
                    user_name=st.session_state.user_name,
                    conversation_id=chat["conversation_id"],
                    collection=collection
                )
                st.rerun()

    # -------------------------------
    # Chat Title Edit
    # -------------------------------
    current_title = get_current_chat_title(
        st.session_state.user_name,
        st.session_state.conversation_id,
        collection
    )

    new_title = st.text_input(
        "✏️ Chat Title",
        value=current_title,
        placeholder="Rename this chat"
    )

    if st.button("Update Title"):
        if new_title.strip():
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
