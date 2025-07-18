import os
import json
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat

class AIEngine:
    def __init__(self):
        # Load environment variables
        dotenv_path = os.path.join("/opt/Hackathon/hackathon/API/API/settings", '.env')
        load_dotenv(dotenv_path)

        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")

        # Initialize the Agno Agent with OpenAIChat
        self.agent = Agent(
            model=OpenAIChat(id=self.model, api_key=self.api_key),
            description=(
                "You get the RCA for error logs and return output in a strict JSON format with RCA, solution, shell commands, and user input prompts. "
                "Use only shell commands, no comments. Use `sed` if configuration changes are needed. "
                "Ask the user for missing config paths if necessary. "
                "Final output format:\n"
                "{'rca': '...', 'solution': '...', 'commands': '...', 'user_input': '...'}"
            ),
            markdown=False
        )
        
        self.conversation_history = [] 

    def build_prompt(self, user_input: str) -> str:
        return f"""
You are an expert Linux diagnostic AI.

Given the error/log message below, perform these steps:
1. Analyze the issue and provide:
   - Root Cause Analysis (`rca`)
   - Detailed solution with examples (`solution`)
2. Generate shell commands (`commands`) to resolve the issue:
   - No explanation or comments in the commands
   - Use `sed` for file edits
3. If additional input is required from the user (e.g., configuration file paths like `postgresql.conf`, service names, etc.), include a clear question in the `user_input` field.


Return a JSON object with:
{{
  "rca": "...",
  "solution": "...",
  "commands": "cmd1\\ncmd2\\n...",
  "user_input": "Prompt to ask the user for input, or empty string"
}}

Log/Error Message:
{user_input}
"""

    def generate_prompt(self, data):
        try:
            # Handle both dict and raw string inputs
            if isinstance(data, str):
                data = eval(data)

            if isinstance(data, dict) and data.get('analysisQuery'):
                prompt_text = data.get('user_input', '') + data.get('analysisQuery')
            else:
                prompt_text = str(data)

            # Build the full instruction-based prompt
            prompt = self.build_prompt(prompt_text)

            # Run the agent and parse the output
            # raw_output = self.agent.run(prompt).content
            response = self.agent.run(prompt, memory=self.conversation_history)
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": response.content})
            raw_output = response.content
            try:
                return json.loads(raw_output)
            except:
                return eval(raw_output)
        except Exception as e:
            return {"error": str(e)}
