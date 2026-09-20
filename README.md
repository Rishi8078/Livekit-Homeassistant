# LiveKit AI Assistant with Home Assistant MCP Integration

A sophisticated AI personal assistant built with LiveKit Agents that integrates with Home Assistant via MCP (Model Context Protocol). The assistant provides voice interaction, smart home control, weather information, web search, and more.

## Features

- **Voice Assistant**: Real-time voice interaction with Google's Realtime Model
- **Wake Word Detection**: Only responds when called by name (e.g., "Friday", "Hey Friday")
- **Smart Home Control**: Full Home Assistant integration via MCP
- **Weather Information**: Current weather for any city
- **Web Search**: Real-time information lookup
- **Time Management**: Local and timezone-specific time queries
- **System Monitoring**: Health and status information
- **Noise Cancellation**: Optional background noise reduction
- **Multi-language Support**: Automatic language detection and response

## Prerequisites

- Python 3.9+
- Home Assistant instance with MCP server enabled
- LiveKit account and credentials
- Google Cloud credentials for speech services

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd lievkit
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   # LiveKit Configuration
   LIVEKIT_URL=your_livekit_url
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   
   # Google Cloud Configuration
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
   
   # Home Assistant MCP Configuration
   HOME_ASSISTANT_MCP_URL=https://your-ha-instance/mcp_server/sse
   HOME_ASSISTANT_TOKEN=your_long_lived_access_token
   
   # Wake Word Configuration (Optional)
   WAKE_WORD_ENABLED=true
   WAKE_WORDS=friday,hey friday,sir friday,mr friday,good morning friday
   WAKE_WORD_TIMEOUT=30
   ```

## Wake Word Functionality

The assistant uses wake word detection to only respond when called by name:

### **Default Wake Words:**
- "Friday" - Basic wake word
- "Hey Friday" - Casual wake word
- "Sir Friday" - Formal wake word
- "Mr Friday" - Alternative formal wake word
- "Good morning Friday" - Greeting wake word

### **How It Works:**
1. **Sleep Mode**: Assistant ignores all speech until wake word is detected
2. **Active Listening**: After wake word, assistant listens for 30 seconds (configurable)
3. **Command Processing**: Commands are processed normally during active listening
4. **Auto-Sleep**: Returns to sleep mode after timeout

### **Configuration:**
```env
# Enable/disable wake word detection
WAKE_WORD_ENABLED=true

# Custom wake words (comma-separated)
WAKE_WORDS=friday,hey friday,sir friday

# How long to stay active after wake word (seconds)
WAKE_WORD_TIMEOUT=30
```

## Home Assistant MCP Setup

The assistant uses MCP (Model Context Protocol) for Home Assistant integration, which provides:
- Real-time entity state monitoring
- Complete service control capabilities
- Scene activation and automation control
- Color and brightness control for lights
- All Home Assistant features through the MCP interface

### Setting up MCP in Home Assistant

1. **Install the MCP Server add-on** in Home Assistant
2. **Configure the MCP Server** with your Home Assistant URL and token
3. **Enable the MCP Server** and note the SSE endpoint URL
4. **Set the environment variables**:
   - `HOME_ASSISTANT_MCP_URL`: The MCP server SSE endpoint
   - `HOME_ASSISTANT_TOKEN`: Your long-lived access token

### Getting a Long-lived Access Token

1. In Home Assistant, go to **Settings** → **Users**
2. Click on your user profile
3. Scroll down to **Long-Lived Access Tokens**
4. Click **Create Token**
5. Give it a name (e.g., "LiveKit Assistant")
6. Copy the generated token

## Configuration

The assistant can be configured through environment variables:

```env
# Agent settings
AGENT_NAME=Friday
AGENT_VOICE=default  # Uses default voice for Gemini 2.0 Flash Live
AGENT_TEMPERATURE=0.7
AGENT_ENABLE_VIDEO=false
AGENT_ENABLE_NOISE_CANCELLATION=true

# Wake word settings
WAKE_WORD_ENABLED=true
WAKE_WORDS=friday,hey friday,sir friday
WAKE_WORD_TIMEOUT=30

# Logging settings
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/agent.log
```

**Note:** The Gemini 2.0 Flash Live model has limited voice support. The assistant uses the default voice to ensure compatibility. Custom voice selection is not currently supported for this model.

## Usage

### Running the Assistant

1. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Run the health check**:
   ```bash
   python health_check.py
   ```

3. **Start the assistant**:
   ```bash
   python agent.py
   ```

### Voice Commands

The assistant responds to natural language commands after being awakened:

- **Wake Word Examples**:
  - "Friday, what's the weather like?"
  - "Hey Friday, turn on the living room light"
  - "Sir Friday, show me all lights"

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

### Health Check

The health check script verifies:
- Environment variable configuration
- MCP connection to Home Assistant
- Basic system functionality

Run it before starting the assistant:
```bash
python health_check.py
```

## Architecture

- **Agent**: Main assistant logic with Google Realtime Model
- **Wake Word Detection**: Text-based wake word recognition
- **MCP Integration**: Home Assistant control via Model Context Protocol
- **Tools**: Weather, web search, time, and system monitoring
- **Prompts**: Sophisticated persona and interaction guidelines
- **Configuration**: Centralized settings management

## Troubleshooting

### Common Issues

1. **Assistant Not Responding**:
   - Make sure you're using a wake word (e.g., "Friday")
   - Check that wake word detection is enabled
   - Verify microphone permissions

2. **MCP Connection Failed**:
   - Verify `HOME_ASSISTANT_MCP_URL` is correct
   - Check that the MCP server is running in Home Assistant
   - Ensure your access token has the necessary permissions

3. **Voice Not Working**:
   - Verify Google Cloud credentials are properly set
   - Check microphone permissions
   - Ensure LiveKit credentials are correct

4. **Home Assistant Control Issues**:
   - Verify entity names and IDs
   - Check Home Assistant logs for errors
   - Ensure MCP server is properly configured

### Logs

Check the logs for detailed error information:
```bash
tail -f logs/agent.log
```

## Development

### Project Structure

```
lievkit/
├── agent.py              # Main agent entry point
├── config.py             # Configuration management
├── tools.py              # Tool implementations
├── prompts.py            # Agent prompts and instructions
├── health_check.py       # Health check script
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── logs/                # Log files directory
```

### Adding New Tools

1. Create the tool function in `tools.py`
2. Add the `@function_tool()` decorator
3. Import and register the tool in `agent.py`
4. Update prompts if needed

### Testing

Run the health check to verify all components:
```bash
python health_check.py
```

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here] 