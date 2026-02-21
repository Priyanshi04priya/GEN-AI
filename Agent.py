import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
load_dotenv()
client = OpenAI()

#Tool formation ----> make a funtion which can be called by the agent to get the weather of a city
def get_weather(city):
    url= f"https://wttr.in/{city}?format=%C+%t" #%C is for condition and %t is for temperature
    response= requests.get(url)

    if response.status_code==200:
        return f"The current weather of {city} is {response.text}." 
    else:
        return "Sorry, I am not able to get the weather information right now."   

def run_command(command):
    result=os.system(command=command)
    return result


available_tools = {    #we can add more tools in this dictionary as we create more tools
    # openAI provides a direct template for making a tool and we can use that template to create more tools and add them in this dictionary
    #Just paste the function name in the "function" field and a brief description of the tool in the "description" field and it will be ready to use for the agent.
    "get_weather": {
        "function": get_weather,
        "description": "This tool is used to get the current weather of a city. It takes the name of the city as input and returns the current weather of that city."
    },
    "run_command": {
        "function": run_command,
        "description": "Takes a command as input to execute on system and returns output."
    }

}

systemprompt = """You are a helpful AI assistant which solves every kind of problem of user in a step by step way and give the final answer to the user in a more to the point way so that it can be more helpful for the user. Always try to give the final answer to the user in a more to the point way so that it can be more helpful for the user.  
You work on start, plan, action, observe mode.
For a given user query and available tools, plan the step by step execution, based on planning
select the relevant tool from available tools and based on the tool selection you perform an action to call the tool
wait for the observation from the tool and based on the observation you perform the next step of planning and then again select the relevant tool and perform action and wait for the observation and keep doing this until you have the final answer for the user query. Always try to give the final answer to the user in a more to the point way so that it can be more helpful for the user.
Rules:
1. output should be in json format.
2. Always perform one step at a time and wait for next input
3. carefully analyze the user query.

output format:
{{
    "step": "string",
    "content": "string",
    "function": "string", #only for action step
    "input": "string" #only for action step
}}

Available tools:
- get_weather: This tool is used to get the current weather of a city. It takes the name of the city as input and returns the current weather of that city.
- run_command: Takes a command as input to execute on system and returns output.
Examples:
user query: What is the weather of delhi today?
output: {{"step": "plan","content": "The user is interested in knowing the current weatherof Delhi."}}
output: {{"step": "plan","content": "From the available tool I should call get_weather."}}
output: {{"step": "action","function": "get_weather","input": "Delhi"}}
output: {{"step": "observe","content": "The current weather of Delhi is 30 degree celsius with clear sky."}}
output: {{"step": "output","content": "The current weather of Delhi is 30 degree celsius with clear sky."}}
"""

messages=[
    {"role": "system", "content": systemprompt},
]
user_query = input(">")
messages.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=messages
    )
    parsed_response = json.loads(response.choices[0].message.content)
    messages.append({"role": "assistant", "content": json.dumps(parsed_response)})
    if parsed_response["step"] == "plan":
        continue
    if parsed_response["step"] == "action": #In action part, we get the funtion to call and also the input i.e city name
        tool_name= parsed_response["function"]
        tool_input= parsed_response["input"]
        if tool_name in available_tools:
            tool_function= available_tools[tool_name]["function"]
            tool_output= tool_function(tool_input)
            messages.append({"role": "assistant", "content": json.dumps({"step": "observe", "content": tool_output})})
            continue
    if parsed_response["step"] == "output":
        print(f"🤖 {parsed_response['content']}")
        break