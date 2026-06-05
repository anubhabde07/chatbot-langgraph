from mcp.server.fastmcp import FastMCP
import math

mcp = FastMCP("Math Server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@mcp.tool()
def modulus(a: int, b: int) -> int:
    """Find modulus of two numbers."""
    if b == 0:
        raise ValueError("Cannot perform modulus with zero")
    return a % b


@mcp.tool()
def power(a: float, b: float) -> float:
    """Calculate power."""
    return a ** b


@mcp.tool()
def square_root(a: float) -> float:
    """Find square root."""
    if a < 0:
        raise ValueError("Cannot calculate square root of a negative number")
    return math.sqrt(a)


if __name__ == "__main__":
    mcp.run(transport="stdio")