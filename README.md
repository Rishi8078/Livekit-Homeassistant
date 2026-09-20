# LiveKit AI Assistant with Home Assistant MCP Integration

A voice assistant built on LiveKit Agents that controls Home Assistant over MCP (Model Context Protocol). Speech in and out is handled by Google's Gemini Realtime model; smart-home control, weather, web search, time and system status are exposed as tools.

## Features

- **Voice Assistant**: Real-time voice interaction with Google's Gemini Realtime model
- **Smart Home Control**: Home Assistant integration via MCP
- **Wake Word Detection**: Optional, via the RealtimeSTT plugin and openWakeWord
- **Weather Information**: Current weather for any city
- **Web Search**: DuckDuckGo lookups
- **Time Management**: Local and timezone-specific time queries
- **System Monitoring**: Health and status information
- **Noise Cancellation**: Optional background noise reduction (LiveKit BVC)
- **Multi-language**: The agent is instructed to reply in the user's language

## Prerequisites

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Home Assistant instance with the MCP Server integration enabled
- LiveKit account and credentials
- Google AI API key (Gemini Realtime)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Livekit-Homeassistant
   ```

2. **Install dependencies** (creates `.venv` automatically):
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   # LiveKit
   LIVEKIT_URL=your_livekit_url
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret

   # Google AI (Gemini Realtime)
   GOOGLE_API_KEY=your_google_api_key

   # Home Assistant REST (required — the agent won't load its HA config without a token)
   HA_URL=https://your-ha-instance
   HA_TOKEN=your_long_lived_access_token

   # Home Assistant MCP (required — the agent refuses to start without these)
   HOME_ASSISTANT_MCP_URL=https://your-ha-instance/mcp_server/sse
   HOME_ASSISTANT_TOKEN=your_long_lived_access_token
   ```

## Wake Word Functionality

Wake word detection is optional and comes from the `livekit-plugins-realtimestt` plugin. If the plugin is missing or fails to configure, `agent.py` logs a warning and runs without it — the agent then responds to all speech.

Wake words are **openWakeWord model names**, not free-form phrases. Defaults: `hey_assistant`, `computer`, `friday`.

### Configuration

```env
# Enable/disable wake word detection
AGENT_ENABLE_WAKE_WORD=true

# Wake word models (comma-separated openWakeWord names)
AGENT_WAKE_WORDS=hey_assistant,computer,friday

# Wake word backend
AGENT_WAKEWORD_BACKEND=openwakeword

# Seconds of silence before wake word detection arms
AGENT_WAKE_WORD_DELAY=0.5
```

There is no sleep/active-listening timeout: once the wake word fires, the session behaves like a normal LiveKit voice session.

## Home Assistant MCP Setup

The assistant uses MCP for Home Assistant integration, which provides:
- Real-time entity state monitoring
- Service control capabilities
- Scene activation and automation control
- Color and brightness control for lights

### Setting up MCP in Home Assistant

1. **Enable the MCP Server integration** in Home Assistant
2. **Note the SSE endpoint URL** (typically `/mcp_server/sse`)
3. **Set the environment variables**:
   - `HOME_ASSISTANT_MCP_URL`: the MCP server SSE endpoint
   - `HOME_ASSISTANT_TOKEN`: your long-lived access token

The agent retries the MCP connection up to 3 times with progressive backoff and exits if it can't connect.

### Getting a Long-lived Access Token

1. In Home Assistant, go to **Settings** → **Users**
2. Click on your user profile
3. Scroll down to **Long-Lived Access Tokens**
4. Click **Create Token**
5. Give it a name (e.g., "LiveKit Assistant")
6. Copy the generated token

## Configuration

All settings come from environment variables (see `config.py`):

```env
# Agent settings
AGENT_NAME=Friday
AGENT_VOICE=default          # Gemini Realtime uses its default voice
AGENT_TEMPERATURE=0.7
AGENT_MAX_RESPONSE_LENGTH=1000
AGENT_ENABLE_VIDEO=false
AGENT_ENABLE_NOISE_CANCELLATION=true

# Wake word settings
AGENT_ENABLE_WAKE_WORD=true
AGENT_WAKE_WORDS=hey_assistant,computer,friday
AGENT_WAKEWORD_BACKEND=openwakeword
AGENT_WAKE_WORD_DELAY=0.5

# Home Assistant
HA_MCP_RETRY_ATTEMPTS=3
HA_MCP_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE_PATH=logs/agent.log
```

**Note:** `AGENT_VOICE` is read into the config but not passed to the model — Gemini Realtime uses its default voice for compatibility.

## Usage

### Running the Assistant

1. **Run the health check**:
   ```bash
   uv run health_check.py
   ```

2. **Start the assistant**:
   ```bash
   uv run agent.py console      # talk to it in the terminal
   uv run agent.py dev          # dev worker, connects to LiveKit
   uv run agent.py start        # production worker
   ```

   `agent.py` uses the LiveKit CLI, so it expects one of these subcommands.

### Voice Commands

- **Smart Home Control**:
  - "Turn on the living room light"
  - "Set the bedroom light to blue"
  - "Show me all lights"
  - "Activate the movie scene"
  - "What's the temperature in the house?"

- **Information Queries**:
  - "What's the weather like in London?"
  - "Search for the latest news"
  - "What time is it in Tokyo?"
  - "How's the system doing?"

With wake word detection enabled, prefix commands with a configured wake word.

### Health Check

The health check script verifies:
- Environment variable configuration
- MCP connection to Home Assistant
- Basic system functionality

Run it before starting the assistant:
```bash
uv run health_check.py
```

## Architecture

- **Agent** (`agent.py`): session setup, MCP connection with retries, Gemini Realtime model
- **Wake Word Detection**: optional RealtimeSTT STT with an openWakeWord backend
- **MCP Integration**: Home Assistant control via `mcp.MCPServerHTTP`
- **Tools** (`tools.py`): weather, web search, time, system status
- **Prompts** (`prompts.py`): persona and interaction guidelines
- **Configuration** (`config.py`): environment-driven settings

## Troubleshooting

1. **Assistant Not Responding**:
   - If wake words are enabled, use one of the configured models (default `friday`)
   - Check the log for "RealtimeSTT plugin not available" — wake words are off in that case
   - Verify microphone permissions

2. **MCP Connection Failed**:
   - Verify `HOME_ASSISTANT_MCP_URL` is correct and reachable
   - Check that the MCP Server integration is running in Home Assistant
   - Ensure your access token is valid

3. **Voice Not Working**:
   - Verify `GOOGLE_API_KEY` is set
   - Check microphone permissions
   - Ensure LiveKit credentials are correct

4. **`ImportError: The 'mcp' package is required`**:
   - Run `uv sync` — the `livekit-agents[mcp]` extra provides it

### Logs

```bash
tail -f logs/agent.log
```

Logging goes to the file, not stdout, so the terminal stays quiet while the agent runs.

## Development

### Project Structure

```
Livekit-Homeassistant/
├── agent.py              # Main agent entry point
├── config.py             # Configuration management
├── tools.py              # Tool implementations
├── prompts.py            # Agent prompts and instructions
├── health_check.py       # Health check script
├── test.py               # Home Assistant MCP/REST connectivity probe
├── pyproject.toml        # Project metadata and dependencies
├── uv.lock               # Pinned dependency versions
├── .env                  # Secrets (gitignored)
├── LICENSE               # MIT
├── README.md             # This file
└── logs/                 # Log files (gitignored)
```

### Adding New Tools

1. Create the tool function in `tools.py`
2. Add the `@function_tool()` decorator
3. Import and register the tool in the `Assistant` tool list in `agent.py`
4. Update prompts if needed

### Testing

```bash
uv run health_check.py    # config, MCP and system checks
uv run test.py            # raw HA MCP/REST connectivity
```

## License

MIT — see [LICENSE](LICENSE).
