# Crypto Knowledge MCP Server

A Model Context Protocol (MCP) server that provides comprehensive cryptocurrency and quantitative finance knowledge powered by Google's Gemini XX with real-time web search capabilities.

## Features

- **Comprehensive Explanations**: Get detailed explanations of crypto concepts with implementation guides
- **Trading Strategies**: Analyze various cryptocurrency trading strategies and algorithmic approaches
- **Technical Indicators**: Detailed analysis and implementation of technical indicators
- **Real-time Research**: Uses Google Search for up-to-date information
- **Python Examples**: Includes practical, well-commented code snippets
- **Implementation Guides**: Step-by-step instructions for developers

## Installation

1. **Clone or download the files**:
   - `crypto_mcp.py` - Main MCP server
   - `requirements.txt` - Python dependencies
   - `.env.example` - Environment variables template

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key
   ```

4. **Get Google API Key**:
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - Add it to your `.env` file

## Configuration for Cursor AI

### Method 1: Direct Configuration

Add this to your Cursor AI MCP configuration:

   ```json
   {
     "servers": {
       "gemini-knowledge": {
         "command": "python",
         "args": ["/path/to/your/mcp_server.py"]
       }
     }
   }
   ```

## Available Tools

### 1. `explain_crypto_concept`
Get comprehensive explanations of cryptocurrency and quantitative finance concepts.

**Parameters:**
- `topic` (string): The concept to explain

**Example:**
```
Topic: "RSI indicator"
Topic: "arbitrage trading"
Topic: "smart contract security"
```

### 2. `get_crypto_strategy`
Get detailed trading strategies and algorithmic approaches.

**Parameters:**
- `strategy_type` (string): The strategy type to analyze

**Example:**
```
Strategy: "mean reversion"
Strategy: "momentum trading"
Strategy: "pairs trading"
```

### 3. `analyze_crypto_indicator`
Analyze technical indicators and their implementation.

**Parameters:**
- `indicator` (string): The technical indicator to analyze

**Example:**
```
Indicator: "MACD"
Indicator: "Bollinger Bands"
Indicator: "Stochastic Oscillator"
```

## Response Format

All tools return structured JSON responses with:

- **name**: Official concept name
- **description**: Clear explanation and purpose
- **use_case_in_crypto**: Practical crypto applications
- **components_or_formula**: Mathematical formulas or key components
- **implementation_steps**: Step-by-step implementation guide
- **python_example**: Clean, commented Python code
- **key_considerations**: Best practices and pitfalls

## Testing the Server

You can test the server directly:

```bash
python mcp_server.py
```

The server will start and listen for MCP protocol messages via stdio.

## Usage in Cursor AI

Once configured, you can use the server in Cursor AI by:

1. **Ask for explanations**: "Can you explain how RSI works in crypto trading?"
2. **Get strategies**: "What's the best approach for momentum trading in crypto?"
3. **Analyze indicators**: "How do I implement MACD for Bitcoin analysis?"

The server will:
1. Research the topic using Google Search
2. Synthesize the information
3. Provide structured, actionable responses
4. Include practical Python implementations

## Troubleshooting

1. **API Key Issues**: Ensure your Google API key is valid and has Gemini API access
2. **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
3. **Connection Issues**: Check that Cursor AI can execute the Python script and access the environment variables
4. **Response Errors**: The server includes error handling and will return descriptive error messages

## Security Notes

- Keep your Google API key secure and never commit it to version control
- Use environment variables or secure configuration management
- Consider rate limiting for production use
- Monitor API usage to avoid unexpected charges

## Advanced Usage

The server can be extended with additional tools by:
1. Adding new tool definitions in `handle_list_tools()`
2. Implementing the logic in `handle_call_tool()`
3. Creating specialized prompts for different use cases
