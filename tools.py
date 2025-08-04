import logging
import os
from dotenv import load_dotenv
# Async HTTP client for non-blocking I/O
import httpx
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from livekit.agents import function_tool, RunContext
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+
import asyncio
from functools import lru_cache

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# === Weather via Open-Meteo + Nominatim (no API key) ===

class GeoLocation(BaseModel):
    lat: float
    lon: float

class CurrentWeather(BaseModel):
    temperature: float
    windspeed: float
    winddirection: float
    weathercode: int

# Weather code mapping for better descriptions
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

@lru_cache(maxsize=100)
async def geocode(address: str) -> Optional[GeoLocation]:
    """Geocode address with caching for performance"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, params=params, headers={"User-Agent": "livekit-weather-agent"})
            r.raise_for_status()
            results = r.json()
            if not results:
                return None
            data = results[0]
            return GeoLocation(lat=float(data["lat"]), lon=float(data["lon"]))
    except Exception as e:
        logger.error(f"Geocoding error for {address}: {e}")
        return None

@function_tool()
async def get_weather(
    context: RunContext,
    city: str
) -> str:
    """
    Get the current weather for a given city using Open-Meteo and Nominatim.
    
    Args:
        city: The city name to get weather for
        
    Returns:
        Weather information including temperature, wind, and conditions
    """
    try:
        loc = await geocode(city)
        if not loc:
            return f"Could not find location: {city}. Please check the spelling or try a different city name."
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": loc.lat,
            "longitude": loc.lon,
            "current_weather": "true",
            "timezone": "auto",
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            cw = CurrentWeather.parse_obj(data["current_weather"])
            
            # Get weather description
            weather_desc = WEATHER_CODES.get(cw.weathercode, f"Unknown (code: {cw.weathercode})")
            
            return (
                f"Weather in {city}: {weather_desc}, {cw.temperature}°C, "
                f"wind {cw.windspeed} m/s at {cw.winddirection}°"
            )
    except httpx.TimeoutException:
        return f"Weather service timeout for {city}. Please try again."
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error for {city}: {e}")
        return f"Weather service error for {city}. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error getting weather for {city}: {e}")
        return f"Could not retrieve weather for {city}. Please try again."

@function_tool()
async def get_time_smart(
    context: RunContext,
    location: Optional[str] = None
) -> str:
    """
    Get current time - local time if no location specified, or time for specific location.
    
    Args:
        location: Optional timezone in IANA format (e.g., 'America/New_York', 'Europe/London') 
                 or None for local time
    
    Returns:
        Current time string for specified location or local time
    """
    try:
        if location is None:
            # Get local time
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Get timezone info
            import time
            is_dst = time.daylight and time.localtime().tm_isdst
            timezone_name = time.tzname[1 if is_dst else 0]
            
            result = f"Current local time: {formatted_time} {timezone_name}"
            
        else:
            # Get time for specific timezone
            try:
                tz = ZoneInfo(location)
                current_time = datetime.now(tz)
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
                result = f"Current time in {location}: {formatted_time}"
            except Exception as tz_error:
                logger.error(f"Invalid timezone {location}: {tz_error}")
                return f"Invalid timezone: {location}. Please use IANA format like 'America/New_York' or 'Europe/London'."
        
        logger.info(f"Time result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving time: {e}")
        if location:
            return f"Could not retrieve time for {location}. Please use IANA timezone format."
        else:
            return "Could not retrieve current local time."

@function_tool()
async def search_web(
    context: RunContext,
    query: str
) -> str:
    """
    Search the web using DuckDuckGo for current information.
    
    Args:
        query: The search query to look up
        
    Returns:
        Search results from the web
    """
    from langchain_community.tools import DuckDuckGoSearchRun
    
    try:
        # Add timeout to prevent hanging
        search_tool = DuckDuckGoSearchRun()
        
        # Run search with timeout
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, 
            lambda: search_tool.run(tool_input=query)
        )
        
        if not results or len(results.strip()) < 10:
            return f"No relevant results found for '{query}'. Please try a different search term."
        
        # Truncate very long results
        if len(results) > 1000:
            results = results[:1000] + "..."
        
        logger.info(f"Search completed for '{query}'")
        return results
        
    except Exception as e:
        logger.error(f"Error searching the web for '{query}': {e}")
        return f"Search error for '{query}'. Please try again or rephrase your query."

@function_tool()
async def get_system_status(
    context: RunContext
) -> str:
    """
    Get system status and health information.
    
    Returns:
        System status information
    """
    try:
        import psutil
        
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = (
            f"System Status: CPU {cpu_percent}%, "
            f"Memory {memory.percent}% used, "
            f"Disk {disk.percent}% used"
        )
        
        return status
        
    except ImportError:
        return "System status unavailable (psutil not installed)"
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return "System status unavailable"