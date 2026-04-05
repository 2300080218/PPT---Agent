import logging
from datetime import datetime
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="[TIME-MCP] %(asctime)s | %(message)s")
log = logging.getLogger("time_mcp")

mcp = FastMCP(name="time-utils-mcp")

@mcp.tool()
def get_current_time() -> str:
    """Get the current time in ISO format."""
    now = datetime.now().isoformat()
    log.info(f"get_current_time: {now}")
    return f"Current time is: {now}"

@mcp.tool()
def get_current_date() -> str:
    """Get the current date."""
    today = datetime.now().strftime("%Y-%m-%d")
    log.info(f"get_current_date: {today}")
    return f"Today's date is: {today}"

if __name__ == "__main__":
    log.info("Starting Time MCP Server...")
    mcp.run(transport="stdio")
