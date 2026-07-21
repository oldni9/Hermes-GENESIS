from datetime import datetime
from hermes.tools.decorators import tool

@tool(name="get_current_time", description="Get the current time in ISO 8601 format.")
def get_current_time() -> str:
    return datetime.now().isoformat()