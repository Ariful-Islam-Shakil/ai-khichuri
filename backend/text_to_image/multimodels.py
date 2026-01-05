import os
import torch
from langchain_groq import ChatGroq
from diffusers import DiffusionPipeline
from dotenv import load_dotenv
from transformers import pipeline
load_dotenv()
def get_model_pipeline(device: str = "mps"):

    # "cuda" or switch to "mps" for apple devices 
    pipe = DiffusionPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", dtype=torch.bfloat16, device_map = device)
    return pipe

from langchain.messages import HumanMessage

def query_rewrite(query: str) -> str:
    """
    Takes a raw user query and rewrites it into a detailed prompt suitable
    for generating a realistic image from a text-to-image model.
    """
    # Load your Groq API key
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Initialize the Groq chat model
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.1-8b-instant",
        temperature=0.6
    )
    
    # Instruction for the LLM to rewrite the query
    prompt = f"""
            You are a professional prompt engineer for text-to-image models.
            Rewrite the user query into a concise, keyword-focused image-generation prompt.
            Use short, clear phrases separated by commas.
            Include only essential visual keywords such as subject, action, setting, lighting, style, and realism.
            Avoid storytelling, explanations, or unnecessary adjectives.
            Limit the output to 20–25 words (maximum 70 tokens).
            Output ONLY the rewritten prompt.

            User query: "{query}"
        """

    # Get the rewritten query from the model
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Extract text from the response
    rewritten_query = response.content
    
    return rewritten_query


if __name__ == "__main__":
    user_query = "a beautifull flower garden, bee, birds and so on"
    new_query = query_rewrite(user_query)
    print("Rewritten prompt:\n##############\n", new_query, "############\n\n")

    pipeline = get_model_pipeline()
    result = pipeline(new_query)

    # For Stable Diffusion / Diffusers pipelines
    image = result.images[0]

    # Save the image
    image.save("generated_image.png")

    print("Image saved as generated_image.png")

    print("\n\n#####\nGenerating by original query\n\n")
    result = pipeline(user_query)
    image = result.images[0]
    image.save("original_query_image.png")
    print("saved original query image")