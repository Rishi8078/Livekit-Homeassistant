from dotenv import load_dotenv
import asyncio
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, mcp
from livekit.agents.llm.tool_context import StopResponse
from livekit.agents.voice.agent_activity import AgentActivity
from livekit.agents.voice.events import UserInputTranscribedEvent
from livekit.plugins import noise_cancellation, google
from google.genai import types
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import (
    get_weather, search_web, get_time_smart, get_system_status
)
from config import config

load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format=config.logging.format,
    filename=config.logging.file_path
)
logger = logging.getLogger(__name__)

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                # Try without specifying voice to use default
                temperature=config.agent.temperature,
            ),
            tools=[
                get_weather,
                search_web,
                get_time_smart,
                get_system_status,
            ],
        )

async def create_mcp_server(max_retries: int = 3) -> Optional[mcp.MCPServerHTTP]:
    """Create MCP server with retry logic and validation"""
    # Get MCP-specific environment variables
    mcp_url = os.getenv("HOME_ASSISTANT_MCP_URL")
    mcp_token = os.getenv("HOME_ASSISTANT_TOKEN")
    
    if not mcp_url or not mcp_token:
        logger.error("MCP environment variables not found (HOME_ASSISTANT_MCP_URL, HOME_ASSISTANT_TOKEN)")
        return None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to Home Assistant MCP server (attempt {attempt + 1}/{max_retries})")
            logger.info(f"MCP URL: {mcp_url}")
            
            mcp_server = mcp.MCPServerHTTP(
                url=mcp_url,
                headers={"Authorization": f"Bearer {mcp_token}"}
            )
            
            # Give MCP server more time to initialize on first attempt
            if attempt == 0:
                logger.info("Initial MCP server initialization - waiting 5 seconds...")
                await asyncio.sleep(5)
            else:
                logger.info("MCP server reconnection - waiting 3 seconds...")
                await asyncio.sleep(3)
            
            logger.info("MCP server created successfully")
            return mcp_server
            
        except Exception as e:
            logger.warning(f"MCP connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = 3 * (attempt + 1)  # Progressive backoff: 3s, 6s, 9s
                logger.info(f"Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Failed to create MCP server after {max_retries} attempts")
                return None

async def entrypoint(ctx: agents.JobContext):
    logger.info(f"Starting {config.agent.name} agent with Home Assistant MCP integration")
    
    # Create assistant
    assistant = Assistant()
    logger.info(f"[DEBUG] Using agent type: {type(assistant)} id={id(assistant)}")
    
    try:
        # Create MCP server with retry logic
        mcp_url = os.getenv("HOME_ASSISTANT_MCP_URL")
        mcp_token = os.getenv("HOME_ASSISTANT_TOKEN")
        logger.info(f"[DEBUG] MCP URL: {mcp_url}")
        logger.info(f"[DEBUG] MCP Token prefix: {mcp_token[:8] if mcp_token else 'not set'}")
        mcp_server = await create_mcp_server()
        
        if not mcp_server:
            logger.error("Failed to create MCP server. Agent cannot start without Home Assistant MCP connection.")
            raise Exception("MCP server connection failed")
        
        logger.info("Using Home Assistant MCP integration")
        session = AgentSession(mcp_servers=[mcp_server])
        
        # Configure room input options based on config
        noise_cancellation_plugin = noise_cancellation.BVC() if config.agent.enable_noise_cancellation else None
        room_options = RoomInputOptions(
            video_enabled=config.agent.enable_video,
            noise_cancellation=noise_cancellation_plugin,
        )
        
        await session.start(
            room=ctx.room,
            agent=assistant,
            room_input_options=room_options,
        )

        await ctx.connect()

        # Use MCP instructions with error handling guidance
        instructions = SESSION_INSTRUCTION + f"""

# MCP Error Handling
If you encounter "invalid slot info" errors with MCP tools:
1. Wait a moment and try the command again
2. Use GetLiveContext to refresh the connection
3. Try using more specific entity IDs instead of area names
4. If persistent, inform the user that MCP is having temporary issues

# Tool Retry Strategy
- First attempt: Try the command as requested
- If slot info error: Wait 2 seconds, then retry
- If still failing: Use GetLiveContext, then retry
- If persistent: Inform user of temporary MCP issues
"""

        await session.generate_reply(instructions=instructions)
        
    except Exception as e:
        logger.error(f"Critical error in agent session: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))