"""
LLM provider factory — wraps LangChain for all intelligence and query calls.

Single entry point:  call_llm(prompt, provider, model)
Single factory:      get_llm(provider, model)   → LangChain BaseChatModel

All provider packages are lazy-imported so users only pay for what they use.
Install the provider package you need:

    Provider        Install command
    ─────────────────────────────────────────────────────────────────────
    groq            pip install langchain-groq
    openai          pip install langchain-openai
    azure           pip install langchain-openai
    anthropic       pip install langchain-anthropic
    ollama          pip install langchain-ollama
    google          pip install langchain-google-genai
    bedrock / aws   pip install langchain-aws
    mistral         pip install langchain-mistralai
    together        pip install langchain-together
    cohere          pip install langchain-cohere
    fireworks       pip install langchain-fireworks
    nvidia          pip install langchain-nvidia-ai-endpoints
    huggingface/hf  pip install langchain-huggingface
    ─────────────────────────────────────────────────────────────────────

All providers expose the same interface — swap provider+model, nothing else changes.

Phase: 3-4  |  Spec: docs/SPEC_DOCNEST_PYPI.md — Section 10
"""

from __future__ import annotations

from docnest.exceptions import IntelligenceError

# System prompt reused across all intelligence calls
_DEFAULT_SYSTEM = (
    "You are a precise document analyst. "
    "Return ONLY the requested format — no preamble, no explanation."
)


# ======================================================================
#  Public API
# ======================================================================

def call_llm(
    prompt: str,
    provider: str,
    model: str,
    api_key: str | None = None,
    system: str = _DEFAULT_SYSTEM,
    temperature: float = 0.1,
    max_tokens: int = 512,
    **kwargs: object,
) -> str:
    """Make a single LLM call through LangChain's unified interface.

    Supports every major LLM provider and cloud inference endpoint via
    LangChain's provider packages — one interface, any backend.

    Args:
        prompt:      User message content.
        provider:    Provider name — groq, openai, azure, anthropic, ollama,
                     google, bedrock, mistral, together, cohere, fireworks,
                     nvidia, huggingface.
        model:       Model identifier for that provider.
        api_key:     API key for the provider. Optional — falls back to the
                     provider's env var (GROQ_API_KEY, OPENAI_API_KEY, etc.).
                     Omit for local providers (ollama, huggingface local).
        system:      System prompt. Defaults to the DocNest analyst prompt.
        temperature: Sampling temperature (default 0.1 — precise / deterministic).
        max_tokens:  Maximum tokens in the response (default 512).
        **kwargs:    Extra kwargs forwarded to the provider constructor
                     (e.g. base_url, timeout).

    Returns:
        LLM response text (str).

    Raises:
        IntelligenceError: Provider package not installed, API key missing,
                           model not found, or network failure.

    Examples:
        # Groq (fast cloud, free tier)
        call_llm("Summarise this.", provider="groq", model="llama-3.3-70b-versatile")

        # OpenAI
        call_llm("Summarise this.", provider="openai", model="gpt-4o-mini")

        # Local Ollama
        call_llm("Summarise this.", provider="ollama", model="llama3.2")

        # Anthropic
        call_llm("Summarise this.", provider="anthropic", model="claude-3-haiku-20240307")

        # Google Gemini
        call_llm("Summarise this.", provider="google", model="gemini-1.5-flash")

        # AWS Bedrock
        call_llm("Summarise this.", provider="bedrock", model="amazon.titan-text-lite-v1")
    """
    try:
        llm = get_llm(
            provider, model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
    except IntelligenceError:
        raise
    except ImportError as exc:
        pkg = _provider_package(provider)
        raise IntelligenceError(
            f"Provider package for '{provider}' not installed.\n"
            f"  Run: pip install {pkg}\n"
            f"  Original error: {exc}"
        ) from exc

    try:
        from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore[import]
    except ImportError as exc:
        raise IntelligenceError(
            "langchain-core not installed. Run: pip install langchain-core"
        ) from exc

    messages = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(HumanMessage(content=prompt))

    try:
        result = llm.invoke(messages)
        # BaseChatModel.invoke() returns an AIMessage; .content is the text
        content = getattr(result, "content", result)
        return str(content) if not isinstance(content, str) else content
    except IntelligenceError:
        raise
    except Exception as exc:
        raise IntelligenceError(
            f"LLM call failed ({provider}/{model}): {exc}"
        ) from exc


def get_llm(
    provider: str,
    model: str,
    api_key: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 512,
    **kwargs: object,
) -> object:
    """Return a configured LangChain BaseChatModel for the given provider.

    Lazy-imports the provider package so users only install what they need.
    All returned objects implement the same .invoke() / .stream() interface.

    Args:
        provider:    Provider name (case-insensitive).
        model:       Model identifier for that provider.
        api_key:     API key. Optional — falls back to provider env var.
                     Omit for local providers (ollama, huggingface local).
        temperature: Sampling temperature.
        max_tokens:  Max tokens in the response.
        **kwargs:    Extra provider kwargs (base_url, region, timeout, etc.)

    Returns:
        A LangChain BaseChatModel instance.

    Raises:
        ImportError:       Provider package not installed.
        IntelligenceError: Unknown provider name.
    """
    p = provider.lower().strip()

    # ── Groq (fast cloud inference, free tier) ─────────────────────────────
    if p == "groq":
        import os
        if api_key:
            os.environ.setdefault("GROQ_API_KEY", api_key)
        from langchain_groq import ChatGroq  # type: ignore[import]
        return ChatGroq(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **({"api_key": api_key} if api_key else {}),
            **kwargs,
        )

    # ── OpenAI ─────────────────────────────────────────────────────────────
    if p in ("openai", "gpt"):
        from langchain_openai import ChatOpenAI  # type: ignore[import]
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **({"api_key": api_key} if api_key else {}),
            **kwargs,
        )

    # ── Azure OpenAI ────────────────────────────────────────────────────────
    if p == "azure":
        from langchain_openai import AzureChatOpenAI  # type: ignore[import]
        return AzureChatOpenAI(
            azure_deployment=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **({"api_key": api_key} if api_key else {}),
            **kwargs,
        )

    # ── Anthropic Claude ────────────────────────────────────────────────────
    if p in ("anthropic", "claude"):
        from langchain_anthropic import ChatAnthropic  # type: ignore[import]
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **({"api_key": api_key} if api_key else {}),
            **kwargs,
        )

    # ── Ollama (local, free) ────────────────────────────────────────────────
    if p == "ollama":
        from langchain_ollama import ChatOllama  # type: ignore[import]
        return ChatOllama(
            model=model,
            temperature=temperature,
            num_predict=max_tokens,
            **kwargs,
        )

    # ── Google Gemini / PaLM ────────────────────────────────────────────────
    if p in ("google", "gemini", "google_genai"):
        from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import]
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            max_output_tokens=max_tokens,
            **kwargs,
        )

    # ── Google Vertex AI ────────────────────────────────────────────────────
    if p in ("vertexai", "vertex"):
        from langchain_google_vertexai import ChatVertexAI  # type: ignore[import]
        return ChatVertexAI(
            model_name=model,
            temperature=temperature,
            max_output_tokens=max_tokens,
            **kwargs,
        )

    # ── AWS Bedrock ─────────────────────────────────────────────────────────
    if p in ("bedrock", "aws"):
        from langchain_aws import ChatBedrock  # type: ignore[import]
        return ChatBedrock(
            model_id=model,
            model_kwargs={"temperature": temperature, "max_tokens": max_tokens},
            **kwargs,
        )

    # ── Mistral AI ──────────────────────────────────────────────────────────
    if p in ("mistral", "mistralai"):
        from langchain_mistralai import ChatMistralAI  # type: ignore[import]
        return ChatMistralAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    # ── Together AI ─────────────────────────────────────────────────────────
    if p == "together":
        from langchain_together import ChatTogether  # type: ignore[import]
        return ChatTogether(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    # ── Cohere ──────────────────────────────────────────────────────────────
    if p == "cohere":
        from langchain_cohere import ChatCohere  # type: ignore[import]
        return ChatCohere(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    # ── Fireworks AI ────────────────────────────────────────────────────────
    if p == "fireworks":
        from langchain_fireworks import ChatFireworks  # type: ignore[import]
        return ChatFireworks(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    # ── NVIDIA NIM ──────────────────────────────────────────────────────────
    if p in ("nvidia", "nim"):
        from langchain_nvidia_ai_endpoints import ChatNVIDIA  # type: ignore[import]
        return ChatNVIDIA(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    # ── HuggingFace Inference Endpoints ─────────────────────────────────────
    if p in ("huggingface", "hf"):
        from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint  # type: ignore[import]
        endpoint = HuggingFaceEndpoint(repo_id=model, **kwargs)
        return ChatHuggingFace(llm=endpoint)

    raise IntelligenceError(
        f"Unknown LLM provider: '{provider}'.\n"
        "Supported: groq, openai, azure, anthropic, ollama, google, vertexai, "
        "bedrock, mistral, together, cohere, fireworks, nvidia, huggingface."
    )


# ======================================================================
#  Embeddings factory
# ======================================================================

def get_embeddings(
    provider: str,
    model: str,
    api_key: str | None = None,
    **kwargs: object,
) -> object:
    """Return a configured LangChain Embeddings instance.

    Same three-param pattern as get_llm — provider, model, api_key.
    api_key is optional: omit for local providers (huggingface, ollama)
    or when the relevant env var is already set.

    The returned object implements LangChain's Embeddings interface:
        .embed_documents(texts)  → list[list[float]]
        .embed_query(text)       → list[float]

    Args:
        provider: Provider name — huggingface, openai, azure, ollama,
                  google, vertexai, cohere, bedrock, nvidia, mistral.
        model:    Model identifier for that provider.
        api_key:  API key. Optional — falls back to provider env var.
                  Omit for huggingface (local), ollama (local), bedrock (IAM).
        **kwargs: Extra provider kwargs (base_url, region, etc.)

    Returns:
        LangChain Embeddings instance.

    Examples:
        # HuggingFace sentence-transformers — local, free, no key needed
        get_embeddings("huggingface", "all-MiniLM-L6-v2")

        # OpenAI — api_key or OPENAI_API_KEY env var
        get_embeddings("openai", "text-embedding-3-small", api_key="sk-...")

        # Ollama local — no key needed
        get_embeddings("ollama", "nomic-embed-text")

        # Google Gemini — api_key or GOOGLE_API_KEY env var
        get_embeddings("google", "models/text-embedding-004", api_key="AI...")

        # Cohere — api_key or COHERE_API_KEY env var
        get_embeddings("cohere", "embed-english-v3.0", api_key="...")
    """
    p = provider.lower().strip()

    # ── HuggingFace / sentence-transformers (local, free, no key needed) ───
    if p in ("huggingface", "hf", "sentence-transformers"):
        from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore[import]
        # api_key = HuggingFace token (only needed for private/gated models)
        extra = {"huggingfacehub_api_token": api_key} if api_key else {}
        return HuggingFaceEmbeddings(model_name=model, **extra, **kwargs)

    # ── OpenAI ──────────────────────────────────────────────────────────────
    if p == "openai":
        from langchain_openai import OpenAIEmbeddings  # type: ignore[import]
        return OpenAIEmbeddings(
            model=model,
            **({"api_key": api_key} if api_key else {}),
            **kwargs,
        )

    # ── Azure OpenAI ────────────────────────────────────────────────────────
    if p == "azure":
        from langchain_openai import AzureOpenAIEmbeddings  # type: ignore[import]
        return AzureOpenAIEmbeddings(
            azure_deployment=model,
            **({"api_key": api_key} if api_key else {}),
            **kwargs,
        )

    # ── Ollama (local, free, no key needed) ─────────────────────────────────
    if p == "ollama":
        from langchain_ollama import OllamaEmbeddings  # type: ignore[import]
        return OllamaEmbeddings(model=model, **kwargs)  # no api_key for local

    # ── Google Gemini ────────────────────────────────────────────────────────
    if p in ("google", "gemini", "google_genai"):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings  # type: ignore[import]
        return GoogleGenerativeAIEmbeddings(
            model=model,
            **({"google_api_key": api_key} if api_key else {}),
            **kwargs,
        )

    # ── Google Vertex AI (uses IAM / service account, no api_key) ───────────
    if p in ("vertexai", "vertex"):
        from langchain_google_vertexai import VertexAIEmbeddings  # type: ignore[import]
        return VertexAIEmbeddings(model_name=model, **kwargs)

    # ── Cohere ──────────────────────────────────────────────────────────────
    if p == "cohere":
        from langchain_cohere import CohereEmbeddings  # type: ignore[import]
        return CohereEmbeddings(
            model=model,
            **({"cohere_api_key": api_key} if api_key else {}),
            **kwargs,
        )

    # ── AWS Bedrock (uses IAM, no api_key) ──────────────────────────────────
    if p in ("bedrock", "aws"):
        from langchain_aws import BedrockEmbeddings  # type: ignore[import]
        return BedrockEmbeddings(model_id=model, **kwargs)

    # ── NVIDIA NIM ──────────────────────────────────────────────────────────
    if p in ("nvidia", "nim"):
        from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings  # type: ignore[import]
        return NVIDIAEmbeddings(
            model=model,
            **({"api_key": api_key} if api_key else {}),
            **kwargs,
        )

    # ── Mistral AI ──────────────────────────────────────────────────────────
    if p in ("mistral", "mistralai"):
        from langchain_mistralai import MistralAIEmbeddings  # type: ignore[import]
        return MistralAIEmbeddings(
            model=model,
            **({"api_key": api_key} if api_key else {}),
            **kwargs,
        )

    raise IntelligenceError(
        f"Unknown embeddings provider: '{provider}'.\n"
        "Supported: huggingface, openai, azure, ollama, google, vertexai, "
        "cohere, bedrock, nvidia, mistral."
    )


# ======================================================================
#  Helpers
# ======================================================================

def _provider_package(provider: str) -> str:
    """Return the pip package name for a given provider (for error messages)."""
    _MAP = {
        "groq": "langchain-groq",
        "openai": "langchain-openai",
        "gpt": "langchain-openai",
        "azure": "langchain-openai",
        "anthropic": "langchain-anthropic",
        "claude": "langchain-anthropic",
        "ollama": "langchain-ollama",
        "google": "langchain-google-genai",
        "gemini": "langchain-google-genai",
        "vertexai": "langchain-google-vertexai",
        "vertex": "langchain-google-vertexai",
        "bedrock": "langchain-aws",
        "aws": "langchain-aws",
        "mistral": "langchain-mistralai",
        "mistralai": "langchain-mistralai",
        "together": "langchain-together",
        "cohere": "langchain-cohere",
        "fireworks": "langchain-fireworks",
        "nvidia": "langchain-nvidia-ai-endpoints",
        "nim": "langchain-nvidia-ai-endpoints",
        "huggingface": "langchain-huggingface",
        "hf": "langchain-huggingface",
    }
    return _MAP.get(provider.lower(), f"langchain-{provider.lower()}")
