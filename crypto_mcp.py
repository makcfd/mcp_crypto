#!/usr/bin/env python3
"""
Gemini Knowledge MCP Server
A dynamic research agent for Cursor AI powered by Gemini 1.5 Pro.
"""

import asyncio
import json
import os
from typing import Any, Sequence

from google.genai import types
from google import genai
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

# Master prompt template
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

def extract_json_from_response(text: str) -> dict:
    """Finds and parses the first valid JSON object from the model's text response."""
    try:
        # Find the start of the JSON markdown block
        json_markdown_start = text.find('```json')
        if json_markdown_start != -1:
            # Find the end of the markdown block
            json_markdown_end = text.rfind('```')
            # Extract the JSON string (adjusting for the markers)
            json_str = text[json_markdown_start + 7:json_markdown_end].strip()
        else:
            # If no markdown block is found, assume the whole text is a JSON string
            json_str = text

        return json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON Parsing Error: {e}\nRaw Response:\n{text}")
        return {"error": "Failed to parse JSON from model", "raw_response": text}

# Initialize MCP server
server = Server("crypto-knowledge-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="explain_crypto_concept",
            description="Get comprehensive explanations of cryptocurrency and quantitative finance concepts with implementation guides",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The cryptocurrency or quantitative finance concept to explain"
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="get_crypto_strategy",
            description="Get detailed trading strategies and algorithmic approaches for cryptocurrency markets",
            inputSchema={
                "type": "object",
                "properties": {
                    "strategy_type": {
                        "type": "string",
                        "description": "The type of trading strategy or algorithmic approach to explain"
                    }
                },
                "required": ["strategy_type"]
            }
        ),
        Tool(
            name="analyze_crypto_indicator",
            description="Analyze technical indicators and their implementation in cryptocurrency trading",
            inputSchema={
                "type": "object",
                "properties": {
                    "indicator": {
                        "type": "string",
                        "description": "The technical indicator to analyze and implement"
                    }
                },
                "required": ["indicator"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    
    # Configure Gemini with Google Search
    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(
        tools=[grounding_tool],
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    )
    
    try:
        if name == "explain_crypto_concept":
            topic = arguments.get("topic", "")
            if not topic:
                return [TextContent(type="text", text="Error: Topic is required")]
            
            final_prompt = MASTER_PROMPT.format(topic=topic)
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=final_prompt,
                config=config
            )
            
            structured_response = extract_json_from_response(response.text)
            
            # Format the response nicely
            formatted_response = json.dumps(structured_response, indent=2)
            return [TextContent(type="text", text=formatted_response)]
            
        elif name == "get_crypto_strategy":
            strategy_type = arguments.get("strategy_type", "")
            if not strategy_type:
                return [TextContent(type="text", text="Error: Strategy type is required")]
            
            # Modify the prompt for strategy-specific requests
            strategy_prompt = MASTER_PROMPT.format(topic=f"cryptocurrency trading strategy: {strategy_type}")
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=strategy_prompt,
                config=config
            )
            
            structured_response = extract_json_from_response(response.text)
            formatted_response = json.dumps(structured_response, indent=2)
            return [TextContent(type="text", text=formatted_response)]
            
        elif name == "analyze_crypto_indicator":
            indicator = arguments.get("indicator", "")
            if not indicator:
                return [TextContent(type="text", text="Error: Indicator is required")]
            
            # Modify the prompt for indicator-specific requests
            indicator_prompt = MASTER_PROMPT.format(topic=f"cryptocurrency technical indicator: {indicator}")
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=indicator_prompt,
                config=config
            )
            
            structured_response = extract_json_from_response(response.text)
            formatted_response = json.dumps(structured_response, indent=2)
            return [TextContent(type="text", text=formatted_response)]
            
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="gemini://crypto-knowledge",
            name="Crypto Knowledge Base",
            description="Access to comprehensive cryptocurrency and quantitative finance knowledge",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a resource."""
    if uri == "gemini://crypto-knowledge":
        return json.dumps({
            "description": "Gemini-powered cryptocurrency and quantitative finance knowledge base",
            "capabilities": [
                "Cryptocurrency concept explanations",
                "Trading strategy analysis",
                "Technical indicator implementation",
                "Quantitative finance methods",
                "Python code examples"
            ],
            "usage": "Use the available tools to get detailed explanations and implementations"
        }, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri}")

# async def main():
#     """Main entry point for the MCP server."""
#     # Validate environment
#     if not os.environ.get("GOOGLE_API_KEY"):
#         print("Error: GOOGLE_API_KEY environment variable is required")
#         return
#     async with stdio_server() as (read_stream, write_stream):
#         await server.run(
#             read_stream,
#             write_stream,
#             server.create_initialization_options()
#         )
#     # Run the server
#     async with stdio_server() as (read_stream, write_stream):
#         await server.run(
#             read_stream,
#             write_stream,
#             InitializationOptions(
#                 server_name="gemini-knowledge-server",
#                 server_version="1.0.0",
#                 capabilities=server.get_capabilities(
#                     notification_options=None,
#                     experimental_capabilities=None,
#                 )
#             )
#         )
from mcp.server.lowlevel.server import NotificationOptions   # NEW

# ...

async def main() -> None:
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable is required")
        return

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gemini-knowledge-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
