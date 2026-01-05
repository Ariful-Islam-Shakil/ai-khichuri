from langchain.messages import HumanMessage, AIMessage, SystemMessage
import os
from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict

load_dotenv()


def get_mongodb_collection(
    database: str = "ai_khichuri",
    collection_name: str = "history"
) -> Collection:
    """
    Connect to MongoDB Atlas and return a collection object.
    """
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("MONGODB_URI not found in environment variables")

    client = MongoClient(uri)
    db = client[database]
    collection = db[collection_name]
    print("Connected to MongoDB Atlas ✅")
    return collection


def convert_conversation_to_dict(conversation: List) -> List[Dict]:
    """
    Convert LangChain message objects to MongoDB-storable dictionaries.
    """
    return [
        {
            "role": (
                "system" if isinstance(msg, SystemMessage)
                else "user" if isinstance(msg, HumanMessage)
                else "assistant"
            ),
            "content": msg.content
        }
        for msg in conversation
    ]


def convert_dict_to_conversation(messages_dict: List[Dict]) -> List:
    """
    Convert stored message dictionaries back to LangChain message objects.
    """
    conversation = []
    if not messages_dict:
        return conversation
    for msg in messages_dict:
        role = msg["role"]
        content = msg["content"]

        if role == "system":
            conversation.append(SystemMessage(content=content))
        elif role == "user":
            conversation.append(HumanMessage(content=content))
        elif role == "assistant":
            conversation.append(AIMessage(content=content))

    return conversation


def create_user(user_name: str, collection: Collection) -> bool:
    """
    Create a new user document if it does not already exist.
    Returns True if created, False if already exists.
    """
    if collection.find_one({"user_name": user_name}):
        return False

    collection.insert_one({
        "user_name": user_name,
        "created_at": datetime.utcnow(),
        "conversations": []
    })
    return True


def create_new_chat(
    user_name: str,
    collection: Collection,
    title: str = '',
    system_prompt: str = "You are a helpful assistant. Answer like a professional human being and precisely."
) -> str:
    """
    Create a new conversation for a user and return conversation_id.
    """
    if not title:
        title = f"Hello! Mr. {user_name}! How can I Help you? "
    conversation = {
        "conversation_id": os.urandom(16).hex(),
        "title": title, 
        "created_at": datetime.utcnow(),
        "messages": [
            {"role": "system", "content": system_prompt}
        ]
    }

    result = collection.update_one(
        {"user_name": user_name},
        {"$push": {"conversations": conversation}}
    )

    if result.matched_count == 0:
        raise ValueError("User not found")

    return conversation["conversation_id"]

def update_system_prompt(
    user_name: str,
    conversation_id: str,
    system_prompt: str,
    collection: Collection
) -> bool:
    """
    Update the system prompt for a conversation.
    This updates the existing system message (index 0).
    """
    result = collection.update_one(
        {
            "user_name": user_name,
            "conversations.conversation_id": conversation_id
        },
        {
            "$set": {
                "conversations.$.messages.0.content": system_prompt
            }
        }
    )

    return result.modified_count == 1


def save_message_to_conversation(
    user_name: str,
    conversation_id: str,
    messages: List,
    collection: Collection
) -> bool:
    """
    Replace the entire messages list of a conversation.
    """
    result = collection.update_one(
        {
            "user_name": user_name,
            "conversations.conversation_id": conversation_id
        },
        {
            "$set": {
                "conversations.$.messages": convert_conversation_to_dict(messages)
            }
        }
    )

    return result.modified_count == 1

def get_chat_titles(
    user_name: str,
    collection: Collection
) -> List[Dict]:
    """
    Returns a list of conversation IDs and titles for a user.
    Output format:
    [
        {"conversation_id": "...", "title": "..."},
        ...
    ]
    """
    user_doc = collection.find_one(
        {"user_name": user_name},
        {"conversations.conversation_id": 1, "conversations.title": 1}
    )

    if not user_doc or "conversations" not in user_doc:
        return []

    return [
        {
            "conversation_id": conv.get("conversation_id", ""),
            "title": conv.get("title", "")
        }
        for conv in user_doc["conversations"]
    ]
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

def update_title(
    user_name: str,
    conversation_id: str,
    title: str,
    collection: Collection
) -> bool:
    """
    Update the title of a specific conversation.
    Returns True if updated successfully.
    """
    result = collection.update_one(
        {
            "user_name": user_name,
            "conversations.conversation_id": conversation_id
        },
        {
            "$set": {"conversations.$.title": title}
        }
    )

    return result.modified_count == 1



def get_conversation_history(
    user_name: str,
    conversation_id: str,
    collection: Collection
) -> List:
    user_doc = collection.find_one(
        {
            "user_name": user_name,
            "conversations.conversation_id": conversation_id
        },
        {
            "conversations.$": 1
        }
    )

    if not user_doc or "conversations" not in user_doc:
        return []

    conversation = user_doc["conversations"][0]
    messages = conversation.get("messages", [])

    if not isinstance(messages, list):
        return []

    return convert_dict_to_conversation(messages)


def delete_conversation(
    user_name: str,
    conversation_id: str,
    collection: Collection
) -> bool:
    """
    Deletes a single conversation from a user's conversation list.
    """
    result = collection.update_one(
        {"user_name": user_name},
        {"$pull": {"conversations": {"conversation_id": conversation_id}}}
    )

    return result.modified_count == 1


def delete_all_conversations(
    user_name: str,
    collection: Collection
) -> bool:
    """
    Deletes all conversations for a user.
    """
    result = collection.update_one(
        {"user_name": user_name},
        {"$set": {"conversations": []}}
    )

    return result.modified_count == 1


# -----------------------------
# Main function for testing
# -----------------------------
def main():
    collection = get_mongodb_collection()

    user_name = "test_user"

    created = create_user(user_name, collection)
    print("User created:", created)

    conversation_id = create_new_chat(
        user_name=user_name,
        collection=collection,
        title="Test Chat",
        system_prompt="You are a helpful assistant"
    )
    print("Conversation ID:", conversation_id)

    save_message_to_conversation(
        user_name,
        conversation_id,
        {"role": "user", "content": "Hello!"},
        collection
    )

    save_message_to_conversation(
        user_name,
        conversation_id,
        {"role": "assistant", "content": "Hi! How can I help you?"},
        collection
    )

    print("Messages saved successfully ✅")

    history = get_conversation_history(
        user_name="test_user",
        conversation_id=conversation_id,
        collection=collection
    )

    print(history)

    # Delete single conversation
    # delete_conversation(user_name, conversation_id, collection)

    # Delete all conversations
    # delete_all_conversations(user_name, collection)


if __name__ == "__main__":
    main()
