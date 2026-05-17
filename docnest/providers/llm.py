"""
LLM provider interface and implementations.

ILLMProvider          — abstract interface for language model completions
LangChainLLMProvider  — wraps any LangChain BaseChatModel (14+ providers)

get_llm_provider(provider, model, api_key) → ILLMProvider

Supported providers (lazy imports — install only what you need):

    Provider      Install                              Model example
    ──────────────────────────────────────────────────────────────────
    groq          pip install langchain-groq            llama-3.3-70b-versatile
    openai        pip install langchain-openai           gpt-4o-mini
    azure         pip install langchain-openai           gpt-4o
    anthropic     pip install langchain-anthropic        claude-3-haiku-20240307
    ollama        pip install langchain-ollama           llama3.2
    google        pip install langchain-google-genai     gemini-1.5-flash
    vertexai      pip install langchain-google-vertexai  gemini-1.5-pro
    bedrock       pip install langchain-aws              amazon.titan-text-lite-v1
    mistral       pip install langchain-mistralai        mistral-small-latest
    together      pip install langchain-together         meta-llama/Llama-3-70b
    cohere        pip install langchain-cohere           command-r-plus
    fireworks     pip install langchain-fireworks        accounts/fireworks/models/…
    nvidia        pip install langchain-nvidia-ai-endpoints  meta/llama-3.1-70b-instruct
    huggingface   pip install langchain-huggingface      HuggingFaceH4/zephyr-7b-beta
    ──────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
from abc import ABC, abstractmethod

from docnest.exceptions import IntelligenceError

# ─────────────────────────────────────────────────────────────────────────────
#  Interface
# ─────────────────────────────────────────────────────────────────────────────

class ILLMProvider(ABC):
    """Abstract interface for language model completions.

    Implement this to add a new LLM backend without changing any pipeline code.

    Example custom implementation::

        class MyLLM(ILLMProvider):
            def complete(self, prompt, system="", temperature=0.1, max_tokens=512):
                return my_api.chat(prompt)

            @property
            def provider_name(self): return "mybackend"

            @property
            def model_name(self): return "my-model-v1"
    """

    @abstractmethod
    def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.1,
        max_tokens: int = 512,
    ) -> str:
        """Generate a completion for the given prompt.

        Args:
            prompt:      User message / instruction.
            system:      System prompt (role/persona).  Empty = no system msg.
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).
            max_tokens:  Maximum tokens in the generated response.

        Returns:
            Generated text as a plain string.

        Raises:
            IntelligenceError: If the call fails (auth, network, quota, etc.)
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Canonical provider name — e.g. 'groq', 'openai', 'ollama'."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model identifier as passed to the provider."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.provider_name}/{self.model_name})"


# ─────────────────────────────────────────────────────────────────────────────
#  LangChain implementation
# ─────────────────────────────────────────────────────────────────────────────

class LangChainLLMProvider(ILLMProvider):
    """LLM completions via LangChain — one class, every cloud/local provider.

    Usage::

        llm = LangChainLLMProvider("groq", "llama-3.3-70b-versatile", api_key="gsk_...")
        answer = llm.complete("Summarise in 3 sentences.", system="You are a precise analyst.")

        # Ollama local — no api_key needed
        llm = LangChainLLMProvider("ollama", "llama3.2")
    """

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 512,
        **kwargs: object,
    ) -> None:
        self._provider = provider.lower().strip()
        self._model = model
        self._api_key = api_key
        self._default_temperature = temperature
        self._default_max_tokens = max_tokens
        self._kwargs = kwargs
        self._lc_llm: object | None = None  # lazy-loaded

    @property
    def provider_name(self) -> str:
        return self._provider

    @property
    def model_name(self) -> str:
        return self._model

    def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Call the LLM and return the response text."""
        from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore[import]

        temp   = temperature if temperature is not None else self._default_temperature
        tokens = max_tokens  if max_tokens  is not None else self._default_max_tokens

        try:
            lc = self._get_lc_llm(temp, tokens)
            messages = []
            if system:
                messages.append(SystemMessage(content=system))
            messages.append(HumanMessage(content=prompt))
            response = lc.invoke(messages)  # type: ignore[union-attr]
            return str(response.content).strip()
        except IntelligenceError:
            raise
        except Exception as exc:
            raise IntelligenceError(
                f"LLM call failed ({self._provider}/{self._model}): {exc}"
            ) from exc

    def _get_lc_llm(self, temperature: float, max_tokens: int) -> object:
        """Lazy-init the underlying LangChain chat model."""
        if self._lc_llm is not None:
            return self._lc_llm
        try:
            from docnest.llm import get_llm  # type: ignore[import]
            self._lc_llm = get_llm(
                self._provider, self._model,
                api_key=self._api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                **self._kwargs,
            )
            return self._lc_llm
        except Exception as exc:
            pkg = _provider_package(self._provider)
            raise IntelligenceError(
                f"Cannot initialise LLM provider '{self._provider}'. "
                f"Install: pip install {pkg}\n"
                f"Original error: {exc}"
            ) from exc


# ─────────────────────────────────────────────────────────────────────────────
#  Factory
# ─────────────────────────────────────────────────────────────────────────────

def get_llm_provider(
    provider: str = "groq",
    model: str = "llama-3.3-70b-versatile",
    api_key: str | None = None,
    **kwargs: object,
) -> ILLMProvider:
    """Create an ILLMProvider for the given provider and model.

    Args:
        provider: LLM provider name (groq, openai, ollama, anthropic, etc.)
        model:    Model identifier for that provider.
        api_key:  API key — optional, falls back to provider's env var.
                  Not needed for ollama or local providers.
        **kwargs: Extra kwargs forwarded to the provider constructor.

    Returns:
        ILLMProvider ready to call .complete().

    Examples::

        llm = get_llm_provider("groq", "llama-3.3-70b-versatile", api_key="gsk_...")
        llm = get_llm_provider("ollama", "llama3.2")          # local, no key
        llm = get_llm_provider("openai", "gpt-4o-mini")       # uses OPENAI_API_KEY
        llm = get_llm_provider("anthropic", "claude-3-haiku-20240307")
    """
    return LangChainLLMProvider(provider, model, api_key=api_key, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
#  Internal utility
# ─────────────────────────────────────────────────────────────────────────────

def _provider_package(provider: str) -> str:
    _PKG: dict[str, str] = {
        "groq":        "langchain-groq",
        "openai":      "langchain-openai",
        "azure":       "langchain-openai",
        "anthropic":   "langchain-anthropic",
        "ollama":      "langchain-ollama",
        "google":      "langchain-google-genai",
        "vertexai":    "langchain-google-vertexai",
        "bedrock":     "langchain-aws",
        "aws":         "langchain-aws",
        "mistral":     "langchain-mistralai",
        "together":    "langchain-together",
        "cohere":      "langchain-cohere",
        "fireworks":   "langchain-fireworks",
        "nvidia":      "langchain-nvidia-ai-endpoints",
        "huggingface": "langchain-huggingface",
        "hf":          "langchain-huggingface",
    }
    return _PKG.get(provider.lower(), f"langchain-{provider}")
