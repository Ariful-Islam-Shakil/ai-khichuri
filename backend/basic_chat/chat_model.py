import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace
from langchain_huggingface.llms import HuggingFaceEndpoint
from dotenv import load_dotenv
load_dotenv()


def get_chat_model(
    provider: str = "groq",
    api_key: str = os.getenv("GROQ_API_KEY", ""),
    model_name: str="llama-3.1-8b-instant",
    temperature: float = 0.3,
):
    provider = provider.lower()

    if provider == "groq":
        return ChatGroq(
            api_key=api_key,
            model=model_name,
            temperature=temperature,
        )

    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model_name,
            temperature=temperature,
        )

    elif provider == "huggingface":
        llm = HuggingFaceEndpoint(
            repo_id=model_name,
            huggingfacehub_api_token=api_key,
            temperature=temperature,
        )
        return ChatHuggingFace(llm=llm)

    else:
        raise ValueError("Unsupported provider")
def get_response_from_model(
        model,
        conversation
        ):
    
    response = model.invoke(conversation)
    conversation.append({"role": "assistant", "content": response.content})
    return conversation, conversation[-1]["content"]