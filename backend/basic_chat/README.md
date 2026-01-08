# Basic Chat Module 🥣

A comprehensive chat application module built with Streamlit and LangChain, featuring multi-provider LLM support, persistent conversation history, and user management.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Module Components](#-module-components)
- [API Reference](#-api-reference)

## ✨ Features

### 🤖 Multi-Provider LLM Support
- **Groq**: Fast inference with models like `llama-3.1-8b-instant`, `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`
- **Google Gemini**: Access to `gemini-2.5-flash`, `gemini-1.5-pro`, `gemini-1.0-pro`
- **HuggingFace**: Support for various open-source models including `openai/gpt-oss-20b`, `meta-llama/Llama-2-7b-chat-hf`, `tiiuae/falcon-7b-instruct`

### 💾 Persistent Conversation Management
- **MongoDB Atlas Integration**: All conversations are stored in MongoDB for persistence
- **Multi-User Support**: Each user has their own isolated conversation history
- **Conversation Organization**: Create, view, rename, and delete individual chats
- **Message History**: Full conversation history with system, user, and assistant messages

### 🎨 User Interface Features
- **Streamlit-based UI**: Clean, modern chat interface
- **Real-time Chat**: Interactive chat experience with message streaming
- **Sidebar Navigation**: Easy access to all conversations
- **Chat Title Management**: Rename conversations for better organization
- **Active Chat Highlighting**: Visual indication of the currently active conversation
- **Model Configuration**: Adjustable temperature and model selection

### 🔧 Advanced Capabilities
- **System Prompt Customization**: Configure assistant behavior per conversation
- **Message Type Conversion**: Seamless conversion between LangChain message objects and MongoDB documents
- **User Session Management**: Persistent login sessions
- **Conversation Deletion**: Delete individual or all conversations

## 🏗️ Architecture

The module consists of four main components:

```
basic_chat/
├── chat_app.py              # Streamlit UI and main application logic
├── chat_model.py            # LLM provider abstraction layer
├── history_management.py    # MongoDB operations and conversation management
└── basic_chat_pipeline.py   # Pipeline orchestration (placeholder)
```

### Data Flow

```
User Input → Streamlit UI → Chat Model → LLM Provider → Response
                ↓                                          ↓
         MongoDB Storage ←──────────────────────────────────
```

## 📦 Installation

### Prerequisites

- Python 3.8+
- MongoDB Atlas account
- API keys for desired LLM providers

### Dependencies

```bash
pip install streamlit
pip install langchain
pip install langchain-groq
pip install langchain-google-genai
pip install langchain-huggingface
pip install pymongo
pip install python-dotenv
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/

# LLM Provider API Keys
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
HF_TOKEN=your_huggingface_token_here
```

### MongoDB Setup

The module automatically creates the following structure in MongoDB:

```json
{
  "user_name": "string",
  "created_at": "datetime",
  "conversations": [
    {
      "conversation_id": "string",
      "title": "string",
      "created_at": "datetime",
      "messages": [
        {
          "role": "system|user|assistant",
          "content": "string"
        }
      ]
    }
  ]
}
```

## 🚀 Usage

### Running the Application

```python
from backend.basic_chat.chat_app import chat_interface
import streamlit as st

chat_interface(st)
```

Or run directly:

```bash
streamlit run backend/basic_chat/chat_app.py
```

### Basic Workflow

1. **Login/Create User**: Enter a username in the sidebar
2. **Create New Chat**: Click "➕ New Chat" button
3. **Select Model**: Choose provider and model from the configuration panel
4. **Start Chatting**: Type messages in the chat input
5. **Manage Conversations**: Switch between chats, rename, or delete them

## 🧩 Module Components

### 1. `chat_app.py`

Main Streamlit application providing the user interface.

**Key Features:**
- User authentication and session management
- Chat interface with message display
- Sidebar with conversation list
- Model and provider selection
- Chat title editing
- Conversation deletion

### 2. `chat_model.py`

LLM provider abstraction layer.

**Functions:**

#### `get_chat_model(provider, api_key, model_name, temperature)`
Returns a configured chat model instance.

**Parameters:**
- `provider` (str): One of "groq", "gemini", or "huggingface"
- `api_key` (str): API key for the provider
- `model_name` (str): Specific model identifier
- `temperature` (float): Sampling temperature (0.0-1.0)

**Returns:** LangChain chat model instance

#### `get_response_from_model(model, conversation)`
Invokes the model and appends the response to the conversation.

**Parameters:**
- `model`: LangChain chat model instance
- `conversation` (List): List of message dictionaries

**Returns:** Tuple of (updated_conversation, response_content)

### 3. `history_management.py`

MongoDB operations and conversation management.

**Core Functions:**

#### User Management

- **`create_user(user_name, collection)`**: Create a new user document
  - Returns: `bool` - True if created, False if already exists

#### Conversation Management

- **`create_new_chat(user_name, collection, title, system_prompt)`**: Create a new conversation
  - Returns: `str` - conversation_id

- **`get_chat_titles(user_name, collection)`**: Get all conversation titles for a user
  - Returns: `List[Dict]` - List of {conversation_id, title}

- **`get_conversation_history(user_name, conversation_id, collection)`**: Retrieve full conversation
  - Returns: `List` - List of LangChain message objects

- **`delete_conversation(user_name, conversation_id, collection)`**: Delete a specific conversation
  - Returns: `bool` - True if deleted successfully

- **`delete_all_conversations(user_name, collection)`**: Delete all user conversations
  - Returns: `bool` - True if deleted successfully

#### Message Management

- **`save_message_to_conversation(user_name, conversation_id, messages, collection)`**: Save messages
  - Returns: `bool` - True if saved successfully

- **`update_title(user_name, conversation_id, title, collection)`**: Update conversation title
  - Returns: `bool` - True if updated successfully

- **`update_system_prompt(user_name, conversation_id, system_prompt, collection)`**: Update system prompt
  - Returns: `bool` - True if updated successfully

#### Utility Functions

- **`get_mongodb_collection(database, collection_name)`**: Connect to MongoDB
  - Returns: `Collection` - MongoDB collection object

- **`convert_conversation_to_dict(conversation)`**: Convert LangChain messages to dictionaries
  - Returns: `List[Dict]` - Serializable message list

- **`convert_dict_to_conversation(messages_dict)`**: Convert dictionaries to LangChain messages
  - Returns: `List` - LangChain message objects

- **`get_current_chat_title(user_name, conversation_id, collection)`**: Get title of specific chat
  - Returns: `str` - Chat title

## 📚 API Reference

### MongoDB Schema

#### User Document
```python
{
    "user_name": str,           # Unique username
    "created_at": datetime,     # User creation timestamp
    "conversations": [...]      # List of conversation objects
}
```

#### Conversation Object
```python
{
    "conversation_id": str,     # Unique 32-character hex ID
    "title": str,               # Conversation title
    "created_at": datetime,     # Conversation creation timestamp
    "messages": [...]           # List of message objects
}
```

#### Message Object
```python
{
    "role": str,                # "system", "user", or "assistant"
    "content": str              # Message content
}
```

### LangChain Message Types

- **`SystemMessage`**: System-level instructions for the AI
- **`HumanMessage`**: User input messages
- **`AIMessage`**: Assistant responses

## 🔒 Security Considerations

- API keys are loaded from environment variables, never hardcoded
- MongoDB connection uses secure connection strings
- User sessions are managed through Streamlit's session state
- No sensitive data is logged or exposed in the UI

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Verify `MONGODB_URI` is correctly set in `.env`
   - Check network connectivity and firewall settings
   - Ensure MongoDB Atlas IP whitelist includes your IP

2. **API Key Errors**
   - Confirm API keys are valid and active
   - Check that the correct environment variable is set
   - Verify API key has necessary permissions

3. **Model Not Found**
   - Ensure model name is spelled correctly
   - Check that the model is available for your API tier
   - Try a different model from the same provider

## 📝 Example Usage

```python
from backend.basic_chat.history_management import (
    get_mongodb_collection,
    create_user,
    create_new_chat,
    save_message_to_conversation
)
from backend.basic_chat.chat_model import get_chat_model
from langchain.messages import HumanMessage, AIMessage

# Setup
collection = get_mongodb_collection()
user_name = "john_doe"

# Create user
create_user(user_name, collection)

# Create conversation
conv_id = create_new_chat(
    user_name=user_name,
    collection=collection,
    title="My First Chat",
    system_prompt="You are a helpful assistant."
)

# Get model
model = get_chat_model(
    provider="groq",
    api_key="your_api_key",
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)

# Chat
messages = [HumanMessage(content="Hello!")]
response = model.invoke(messages)
messages.append(AIMessage(content=response.content))

# Save
save_message_to_conversation(user_name, conv_id, messages, collection)
```

## 🤝 Contributing

When extending this module:

1. Follow the existing code structure
2. Add appropriate error handling
3. Update this README with new features
4. Test with all supported LLM providers
5. Ensure MongoDB operations are atomic

## 📄 License

This module is part of the AI Khichuri project.

---

**Built with ❤️ using Streamlit, LangChain, and MongoDB**
