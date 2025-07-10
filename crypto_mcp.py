#!/usr/bin/env python3
"""
Crypto Knowledge MCP Server — FastMCP Edition
Exposes three Gemini-backed crypto tools and one resource over SSE.
Run locally:     python server.py            (defaults to SSE on :8000)
In Docker:       PORT=9000 python server.py  (binds to 0.0.0.0:9000)
"""

import os, json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastmcp import FastMCP

# ------------------------------------------------------------------ #
#  0.  Environment & model client
# ------------------------------------------------------------------ #
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY is required")

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

# ------------------------------------------------------------------ #
#  1.  Prompt template & helper
# ------------------------------------------------------------------ #
MASTER_PROMPT = """
You are a world-class financial engineer and senior quantitative analyst. You have deep expertise in cryptocurrency trading, algorithmic strategies, advanced statistics, and machine learning models. 

Your task is to provide a comprehensive, implementation-focused guide for an AI software developer on the following topic: "{topic}"

You MUST follow these steps:
1.  **Internal Research:** Use your built-in Google Search tool to conduct thorough research on the topic. Find the official definition, the underlying mathematical or logical formula, common use cases in the crypto domain, and popular Python implementations.
2.  **Critical Synthesis:** Analyze the search results. Discard any promotional fluff, irrelevant information, or overly simplistic explanations. Synthesize the core, actionable knowledge.
3.  **Structured Formatting:** You MUST format your entire final answer as a single, valid JSON object. There should be NO text, explanation, or markdown outside of the ```json ... ``` block.

The JSON object must strictly follow this structure:
{{
  "name": "The full, official name of the concept.",
  "description": "A clear, concise explanation of what the concept is and its primary purpose.",
  "use_case_in_crypto": "Specific, practical applications of this concept for cryptocurrency analysis or trading, based on your research.",
  "components_or_formula": "The mathematical formula, key components, or logical steps explained clearly. This must be a string.",
  "implementation_steps": [
    "A numbered list of high-level steps for a developer to follow for implementation.",
    "Step 2...",
    "Step 3..."
  ],
  "python_example": "A clean, well-commented, and practical Python code snippet demonstrating a common implementation. The code should be self-contained where possible.",
  "key_considerations": [
      "A list of potential pitfalls, limitations, or expert best practices to be aware of during implementation.",
      "Consideration 2..."
  ]
}}

Now, begin your research and provide the structured response for the specified topic.
"""

def extract_json_from_response(text: str) -> str:
    """Return a pretty JSON string parsed from a Gemini reply."""
    try:
        start = text.find("```json")
        end   = text.rfind("```")
        json_str = text[start + 7:end].strip() if start != -1 else text
        parsed   = json.loads(json_str)
        return json.dumps(parsed, indent=2)
    except Exception:
        return json.dumps({"error": "Failed to parse JSON", "raw": text}, indent=2)

# ------------------------------------------------------------------ #
#  2.  FastMCP registration
# ------------------------------------------------------------------ #
mcp = FastMCP("crypto-knowledge-server")

def _gemini_call(prompt: str) -> str:
    """Internal helper that calls Gemini with Google Search grounding."""
    tool = types.Tool(google_search=types.GoogleSearch())
    cfg  = types.GenerateContentConfig(
        tools=[tool],
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    )
    reply = client.models.generate_content(
        model="gemini-2.5-pro", contents=prompt, config=cfg
    )
    return extract_json_from_response(reply.text)

# ---------- TOOLS -------------------------------------------------- #

@mcp.tool(
    name="explain_crypto_concept",
    description="Explain a cryptocurrency or quantitative-finance concept"  # :contentReference[oaicite:2]{index=2}
)
def explain_crypto_concept(topic: str) -> str:
    prompt = MASTER_PROMPT.format(topic=topic)
    return _gemini_call(prompt)

@mcp.tool(
    name="get_crypto_strategy",
    description="Generate a detailed algorithmic trading strategy outline"
)
def get_crypto_strategy(strategy_type: str) -> str:
    prompt = MASTER_PROMPT.format(topic=f"cryptocurrency trading strategy: {strategy_type}")
    return _gemini_call(prompt)

@mcp.tool(
    name="analyze_crypto_indicator",
    description="Analyse a technical indicator and show Python implementation"
)
def analyze_crypto_indicator(indicator: str) -> str:
    prompt = MASTER_PROMPT.format(topic=f"cryptocurrency technical indicator: {indicator}")
    return _gemini_call(prompt)

# ---------- RESOURCE ---------------------------------------------- #

@mcp.resource("gemini://crypto-knowledge")   # :contentReference[oaicite:3]{index=3}
def crypto_knowledge_base() -> str:
    """Static metadata describing this server."""
    return json.dumps({
        "description": "Gemini-powered cryptocurrency & quantitative finance knowledge base",
        "capabilities": [
            "Concept explanations",
            "Trading strategy design",
            "Indicator implementation",
            "Python snippets"
        ],
        "usage": "Invoke the tools with the relevant arguments"
    }, indent=2)

# ------------------------------------------------------------------ #
#  3.  Entry-point
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    # Expose over **SSE** so any remote MCP client can connect.  FastMCP handles
    # the Uvicorn webserver for you; override host/port with env vars if needed.
    mcp.run(
        # transport="sse",               # one-word change to go remote :contentReference[oaicite:4]{index=4}
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
log_level="debug",
        transport="http", path="/mcp",
    )
