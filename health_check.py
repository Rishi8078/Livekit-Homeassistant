#!/usr/bin/env python3
"""
Health check script for the LiveKit AI Assistant with Home Assistant MCP integration.
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
import httpx
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self):
        self.mcp_url = os.getenv("HOME_ASSISTANT_MCP_URL")
        self.mcp_token = os.getenv("HOME_ASSISTANT_TOKEN")
        self.ha_url = os.getenv("HA_URL")
        self.ha_token = os.getenv("HA_TOKEN")
        
    async def check_mcp_connection(self) -> Dict[str, Any]:
        """Check MCP server connection"""
        if not self.mcp_url or not self.mcp_token:
            return {
                "status": "error",
                "message": "MCP environment variables not configured",
                "details": {
                    "HOME_ASSISTANT_MCP_URL": "not set" if not self.mcp_url else "set",
                    "HOME_ASSISTANT_TOKEN": "not set" if not self.mcp_token else "set"
                }
            }
        
        try:
            logger.info(f"Testing MCP connection to: {self.mcp_url}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.mcp_url,
                    headers={"Authorization": f"Bearer {self.mcp_token}"}
                )
                
                if response.status_code != 200:
                    return {
                        "status": "error",
                        "message": f"MCP server returned status {response.status_code}",
                        "details": {"status_code": response.status_code}
                    }
                
                # Read first few lines to verify SSE stream
                lines_read = 0
                async for line in response.aiter_lines():
                    if line.strip():
                        logger.info(f"MCP SSE line: {line[:100]}...")
                        lines_read += 1
                        if lines_read >= 3:  # Read first 3 lines
                            break
                
                return {
                    "status": "success",
                    "message": "MCP connection successful",
                    "details": {
                        "url": self.mcp_url,
                        "lines_received": lines_read
                    }
                }
                
        except httpx.TimeoutException:
            return {
                "status": "error",
                "message": "MCP connection timeout",
                "details": {"timeout": "30 seconds"}
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"MCP connection failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def check_ha_rest_api(self) -> Dict[str, Any]:
        """Check Home Assistant REST API (for reference)"""
        if not self.ha_url or not self.ha_token:
            return {
                "status": "warning",
                "message": "REST API environment variables not configured",
                "details": {
                    "HA_URL": "not set" if not self.ha_url else "set",
                    "HA_TOKEN": "not set" if not self.ha_token else "set"
                }
            }
        
        try:
            url = f"{self.ha_url.rstrip('/')}/api/states"
            logger.info(f"Testing REST API connection to: {url}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.ha_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    entities = response.json()
                    lights = [e for e in entities if e["entity_id"].startswith("light.")]
                    
                    return {
                        "status": "success",
                        "message": "REST API connection successful",
                        "details": {
                            "total_entities": len(entities),
                            "lights_found": len(lights)
                        }
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"REST API returned status {response.status_code}",
                        "details": {"status_code": response.status_code}
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "message": f"REST API connection failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def check_environment(self) -> Dict[str, Any]:
        """Check environment configuration"""
        required_vars = {
            "HOME_ASSISTANT_MCP_URL": self.mcp_url,
            "HOME_ASSISTANT_TOKEN": self.mcp_token,
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        if missing_vars:
            return {
                "status": "error",
                "message": f"Missing required environment variables: {', '.join(missing_vars)}",
                "details": {"missing_vars": missing_vars}
            }
        
        return {
            "status": "success",
            "message": "All required environment variables are set",
            "details": {"configured_vars": list(required_vars.keys())}
        }
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run complete health check"""
        logger.info("Starting health check...")
        
        results = {
            "timestamp": asyncio.get_event_loop().time(),
            "checks": {}
        }
        
        # Check environment
        results["checks"]["environment"] = await self.check_environment()
        
        # Check MCP connection
        results["checks"]["mcp_connection"] = await self.check_mcp_connection()
        
        # Check REST API (for reference)
        results["checks"]["rest_api"] = await self.check_ha_rest_api()
        
        # Determine overall status
        critical_errors = [
            check for check in results["checks"].values()
            if check["status"] == "error" and check.get("critical", True)
        ]
        
        if critical_errors:
            results["overall_status"] = "error"
            results["message"] = f"Health check failed with {len(critical_errors)} critical errors"
        else:
            results["overall_status"] = "success"
            results["message"] = "All critical checks passed"
        
        return results

def print_results(results: Dict[str, Any]):
    """Print health check results in a formatted way"""
    print("\n" + "="*60)
    print("LIVEKIT AI ASSISTANT - HEALTH CHECK RESULTS")
    print("="*60)
    
    print(f"\nOverall Status: {results['overall_status'].upper()}")
    print(f"Message: {results['message']}")
    
    for check_name, check_result in results["checks"].items():
        print(f"\n{check_name.upper().replace('_', ' ')}:")
        print(f"  Status: {check_result['status']}")
        print(f"  Message: {check_result['message']}")
        
        if "details" in check_result:
            print("  Details:")
            for key, value in check_result["details"].items():
                print(f"    {key}: {value}")
    
    print("\n" + "="*60)

async def main():
    """Main health check function"""
    checker = HealthChecker()
    
    try:
        results = await checker.run_health_check()
        print_results(results)
        
        # Exit with appropriate code
        if results["overall_status"] == "error":
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Health check failed with exception: {e}")
        print(f"\nHealth check failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 