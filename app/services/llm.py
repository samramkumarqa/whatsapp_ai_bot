from langchain_community.llms import Ollama

# 🔧 Toggle this to enable / disable LLM globally
LLM_ENABLED = False   # ⛔ Disable during order flow (recommended)

def get_llm_response(prompt: str) -> str | None:
    """
    Returns LLM response only if enabled.
    Prevents interference with business rules & order flow.
    """
    if not LLM_ENABLED:
        return None

    llm = Ollama(
        model="phi3:mini",
        temperature=0.2
    )

    try:
        response = llm.invoke(prompt)
        return response
    except Exception as e:
        print("❌ LLM error:", e)
        return None
