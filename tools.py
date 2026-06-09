"""
Tools with Strands Agent
========================
Tools = Python functions that agent can call to DO things.

Agent automatically decides:
  - which tool to use
  - when to use it
  - what arguments to pass
"""

from strands import Agent
from strands.tools import tool
from datetime import datetime
import json


# ─────────────────────────────────────────────
# TOOL 1: Get Weather
# ─────────────────────────────────────────────

@tool
def get_weather(city: str) -> str:
    """
    Get current weather for a city.
    In real app → call actual weather API like OpenWeatherMap.
    Here we simulate it.

    Args:
        city: Name of the city
    """
    # Simulated weather data
    weather_data = {
        "chennai":   "32°C, Humid, Partly Cloudy",
        "mumbai":    "30°C, Humid, Cloudy",
        "delhi":     "28°C, Dry, Sunny",
        "bangalore": "24°C, Pleasant, Light Rain",
        "kolkata":   "33°C, Humid, Sunny",
    }

    city_lower = city.lower()
    if city_lower in weather_data:
        return f"Weather in {city}: {weather_data[city_lower]}"
    else:
        return f"Weather in {city}: 25°C, Clear Sky"  # default


# ─────────────────────────────────────────────
# TOOL 2: Calculator
# ─────────────────────────────────────────────

@tool
def calculate(expression: str) -> str:
    """
    Perform a math calculation.
    Safely evaluates a mathematical expression.

    Args:
        expression: Math expression like "2 + 2" or "10 * 5 / 2"
    """
    try:
        # eval() runs math expression safely
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


# ─────────────────────────────────────────────
# TOOL 3: Save Note
# ─────────────────────────────────────────────

@tool
def save_note(title: str, content: str) -> str:
    """
    Save a note to a local JSON file.
    Notes persist across sessions.

    Args:
        title:   Short title for the note
        content: The note content
    """
    # Load existing notes
    try:
        with open("notes.json", "r") as f:
            notes = json.load(f)
    except FileNotFoundError:
        notes = []

    # Add new note with timestamp
    note = {
        "id":        len(notes) + 1,
        "title":     title,
        "content":   content,
        "saved_at":  datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    notes.append(note)

    # Save back to file
    with open("notes.json", "w") as f:
        json.dump(notes, f, indent=2)

    return f"✅ Note saved: '{title}'"


# ─────────────────────────────────────────────
# TOOL 4: Get All Notes
# ─────────────────────────────────────────────

@tool
def get_notes() -> str:
    """
    Retrieve all saved notes.
    Returns all notes stored in notes.json
    """
    try:
        with open("notes.json", "r") as f:
            notes = json.load(f)

        if not notes:
            return "No notes saved yet."

        # Format notes nicely
        result = f"📚 You have {len(notes)} note(s):\n\n"
        for note in notes:
            result += f"[{note['id']}] {note['title']}\n"
            result += f"     {note['content']}\n"
            result += f"     Saved: {note['saved_at']}\n\n"
        return result

    except FileNotFoundError:
        return "No notes saved yet."


# ─────────────────────────────────────────────
# TOOL 5: Get Current Time
# ─────────────────────────────────────────────

@tool
def get_current_time() -> str:
    """
    Get the current date and time.
    Useful when user asks about time or date.
    """
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


# ─────────────────────────────────────────────
# SETUP AGENT WITH ALL TOOLS
# ─────────────────────────────────────────────

agent = Agent(
    system_prompt="""You are a helpful assistant with access to tools.
Use tools whenever needed to give accurate answers.
Don't guess — use tools for weather, calculations, time, and notes.""",

    tools=[
        get_weather,
        calculate,
        save_note,
        get_notes,
        get_current_time,
    ]
)


# ─────────────────────────────────────────────
# MAIN CONVERSATION LOOP
# ─────────────────────────────────────────────

print("=== Agent with Tools ===")
print("Tools available: weather, calculator, notes, time")
print("Type 'exit' to quit")
print("=" * 40)

while True:
    user_input = input("\nYou: ").strip()

    if not user_input:
        continue

    if user_input.lower() in ("exit", "quit"):
        print("Bye!")
        break

    response = agent(user_input)
    print(f"\nAgent: {response}")