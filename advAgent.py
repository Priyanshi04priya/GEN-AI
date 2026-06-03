import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()
client = OpenAI()

# ── Tools ──────────────────────────────────────────────────────────────────────

def get_weather(city):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The current weather of {city} is {response.text}."
    return "Sorry, I am not able to get the weather information right now."

def run_command(command):
    result = os.system(command=command)
    return result

# ── Tool schemas ───────────────────────────────────────────────────────────────

available_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city and state, e.g., San Francisco, CA"},
                    "unit":     {"type": "string", "enum": ["Celsius", "Fahrenheit"],
                                 "description": "The temperature unit to use. Infer this from the user's location."}
                },
                "required": ["location", "unit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a system command and return its output",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The system command to run"}
                },
                "required": ["command"]
            }
        }
    }
]

# ── System prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a helpful AI assistant which solves every kind of problem of the user
in a step-by-step way and gives the final answer in a concise, to-the-point manner.

You work in start → plan → action → observe → output mode.
For a given user query and available tools, plan the step-by-step execution.
Based on planning, select a relevant tool, perform an action, wait for the observation,
then continue planning until you have the final answer.

If the user is on Windows, prefer Windows commands (e.g. "copy" instead of "cp").

Rules:
1. Output must always be valid JSON.
2. Perform ONE step at a time and wait for the next input.
3. Carefully analyse the user query before planning.
4. You have memory of the entire conversation — use it to answer follow-up questions
   without asking the user to repeat themselves.

Output format:
{
    "step":     "plan | action | observe | output",
    "content":  "string",
    "function": "string",   // only for action step
    "input":    "string"    // only for action step
}

Available tools:
- get_weather : Get the current weather of a city. Input = city name.
- run_command : Execute a shell/system command. Input = command string.

Examples:
User: What is the weather of Delhi today?
→ {"step":"plan",   "content":"User wants the current weather of Delhi."}
→ {"step":"plan",   "content":"I should call get_weather with 'Delhi'."}
→ {"step":"action", "function":"get_weather", "input":"Delhi"}
→ {"step":"observe","content":"The current weather of Delhi is 30°C with clear sky."}
→ {"step":"output", "content":"The current weather of Delhi is 30°C with a clear sky."}
"""

# ── Chat loop ──────────────────────────────────────────────────────────────────

# Persistent message history — the system prompt lives here for the whole session
messages = [{"role": "system", "content": SYSTEM_PROMPT}]

print("🤖 Hey buddy!!! [Type 'exit' or 'quit' to end the session].\n")

while True:
    # ── Get user input ─────────────────────────────────────────────────────────
    try:
        user_query = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n👋 Goodbye!")
        break

    if not user_query:
        continue
    if user_query.lower() in ("exit", "quit"):
        print("👋 Goodbye!")
        break

    # __________Append the new user message to the shared history_______________________
    messages.append({"role": "user", "content": user_query})

    #_______________________Agent reasoning loop for this query__________________________________
    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=messages
        )

        raw_content = response.choices[0].message.content
        parsed_response = json.loads(raw_content)

        #______________________Every assistant turn goes into history so the model remembers its own reasoning__________
        messages.append({"role": "assistant", "content": json.dumps(parsed_response)})

        step = parsed_response.get("step")

        # ____________________Plan: keep reasoning, no output needed ________________________
        if step == "plan":
            continue

        # ________________Action: call the requested tool ___________________________________
        elif step == "action":
            tool_name  = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            print(f"  ⚙️  [{tool_name}] → {tool_input}")

            tool_output = "Tool not found."
            if tool_name == "get_weather":
                tool_output = get_weather(tool_input)
            elif tool_name == "run_command":
                tool_output = run_command(tool_input)

            # ---------Feed the observation back as an assistant message so the model sees it------------------
            observe_msg = json.dumps({"step": "observe", "content": str(tool_output)})
            messages.append({"role": "assistant", "content": observe_msg})
            continue

        # ____________________Output: final answer for this query_____________________________________________
        elif step == "output":
            print(f"\n🤖 {parsed_response['content']}\n")
            break  # Break the inner loop; outer loop waits for the next user message

        # _______________________Fallback for unexpected step values_____________________________________________________
        else:
            print(f"⚠️  Unexpected step '{step}': {parsed_response.get('content','')}")
            break