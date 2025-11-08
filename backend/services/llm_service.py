"""
LLM Service - Language Model Interface
Handles communication with Gemini or OpenAI
"""
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend.config import settings


class LLMService:
    """Service for interacting with Language Models (Gemini/OpenAI)"""

    def __init__(self, provider: str = None):
        """
        Initialize LLM service

        Args:
            provider: "gemini" or "openai" (default from settings)
        """
        self.provider = provider or settings.LLM_PROVIDER
        self.llm = self._initialize_llm()

        print(f"✅ LLM Service initialized - Using {self.provider.upper()}")

    def _initialize_llm(self):
        """Initialize the appropriate LLM based on provider"""
        if self.provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
            )
        elif self.provider == "openai":
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        Generate response from LLM

        Args:
            prompt: User prompt/query
            system_message: Optional system message for context

        Returns:
            LLM response as string
        """
        messages = []

        if system_message:
            messages.append(SystemMessage(content=system_message))

        messages.append(HumanMessage(content=prompt))

        try:
            # Log prompt size for debugging
            total_prompt_size = len(prompt) + (len(system_message) if system_message else 0)
            print(f"   📝 Prompt size: {total_prompt_size} chars (~{total_prompt_size // 4} tokens)")

            response = self.llm.invoke(messages)

            # Check if response is empty
            if not response or not response.content:
                print(f"   ⚠️ Warning: LLM returned empty response!")
                print(f"   Prompt was: {total_prompt_size} chars")
                return "Error: LLM returned empty response. The prompt may be too long or complex."

            result = response.content.strip()
            print(f"   ✅ LLM response: {len(result)} chars")

            return result

        except Exception as e:
            print(f"❌ LLM Error: {e}")
            print(f"   Error type: {type(e).__name__}")
            return f"Error generating response: {str(e)}"

    def generate_with_context(self, query: str, context: str, system_prompt: str) -> str:
        """
        Generate response with RAG context

        Args:
            query: User query
            context: Retrieved context from RAG
            system_prompt: System instructions for the LLM

        Returns:
            LLM response
        """
        full_prompt = f"""
{system_prompt}

CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUERY:
{query}

Provide a clear, accurate response based on the context and data analysis.
"""
        return self.generate(full_prompt)

    def extract_code(self, response: str) -> Optional[str]:
        """
        Extract Python code from LLM response

        Args:
            response: LLM response potentially containing code

        Returns:
            Extracted Python code or None
        """
        # Look for code blocks
        if "```python" in response:
            # Extract code between ```python and ```
            start = response.find("```python") + len("```python")
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()

        elif "```" in response:
            # Generic code block
            start = response.find("```") + 3
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()

        return None
