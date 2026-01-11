from langchain_community.llms import Ollama

def get_llm_response(prompt: str) -> str:
    llm = Ollama(
        model="phi3:mini",
        temperature=0.2
    )

    response = llm.invoke(prompt)
    return response
