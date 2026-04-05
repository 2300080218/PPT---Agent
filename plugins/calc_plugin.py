import logging
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="[MATH-MCP] %(asctime)s | %(message)s")
log = logging.getLogger("math_mcp")

mcp = FastMCP(name="math-operations-mcp")

@mcp.tool()
def add_numbers(a: float, b: float) -> str:
    """Add two numbers together."""
    res = a + b
    log.info(f"add_numbers: {a} + {b} = {res}")
    return f"Result: {res}"

@mcp.tool()
def multiply_numbers(a: float, b: float) -> str:
    """Multiply two numbers."""
    res = a * b
    log.info(f"multiply_numbers: {a} * {b} = {res}")
    return f"Result: {res}"

if __name__ == "__main__":
    log.info("Starting Math MCP Server...")
    mcp.run(transport="stdio")
