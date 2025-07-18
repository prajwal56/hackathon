import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.memory import AgentMemory
from pydantic import BaseModel, Field


class DiagnosticResponse(BaseModel):
    """Structured response model for diagnostic analysis."""
    rca: str = Field(..., description="Root cause analysis of the error")
    solution: str = Field(..., description="Detailed solution with examples")
    commands: str = Field(..., description="Shell commands to resolve the issue")
    user_input: str = Field(default="", description="Additional input needed from user")
    severity: str = Field(default="medium", description="Issue severity: low/medium/high/critical")
    confidence: int = Field(default=80, description="Confidence level in diagnosis (0-100)")


class AIEngine:
    def __init__(self):
        """Initialize the Linux diagnostic AI engine with Agno framework."""
        self._load_environment()
        self._initialize_agent()
        
    def _load_environment(self):
        """Load environment variables from .env file."""
        dotenv_path = os.path.join("/opt/Hackathon/hackathon/API/API/settings", '.env')
        load_dotenv(dotenv_path)
        
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    def _initialize_agent(self):
        """Initialize the Agno agent with memory only."""
        self.agent = Agent(
            model=OpenAIChat(id=self.model, api_key=self.api_key),
            description=(
                "You are LinuxDiagnosticGPT, an expert Linux system administrator and troubleshooter with 15+ years of experience. "
                "You analyze error logs with surgical precision and provide structured solutions with shell commands. "
                "Always respond in valid JSON format with the specified structure."
            ),
            instructions=[
                "Analyze error logs systematically and provide root cause analysis",
                "Generate only executable shell commands without comments",
                "Use 'sed' for configuration file modifications when needed",
                "Request missing information from users when necessary",
                "Always return valid JSON in the specified format",
                "Prioritize system stability and security in all recommendations",
                "Use conservative approaches for production systems"
            ],
            memory=AgentMemory(
                db_url="sqlite:///diagnostic_memory.db",
                table_name="diagnostic_sessions"
            ),
            response_model=DiagnosticResponse,
            markdown=False,
            show_tool_calls=True
        )
    
    def analyze_error(self, error_data: Any) -> Dict[str, Any]:
        """
        Analyze error logs and return diagnostic information.
        
        Args:
            error_data: Error log data (string or dict)
            
        Returns:
            Dict containing RCA, solution, commands, and user input prompts
        """
        try:
            # Parse input data
            prompt_text = self._parse_input_data(error_data)
            
            # Build diagnostic prompt
            diagnostic_prompt = self._build_diagnostic_prompt(prompt_text)
            
            # Run agent analysis
            response = self.agent.run(diagnostic_prompt)
            
            # Parse and validate response
            return self._parse_response(response.content)
            
        except Exception as e:
            return {
                "error": str(e),
                "rca": "Analysis failed due to internal error",
                "solution": "Please check input format and try again",
                "commands": "",
                "user_input": "",
                "severity": "medium",
                "confidence": 0
            }
    
    def _parse_input_data(self, data: Any) -> str:
        """Parse and extract error message from input data."""
        if isinstance(data, str):
            return data
        
        if isinstance(data, dict):
            if data.get('analysisQuery'):
                return data.get('user_input', '') + data.get('analysisQuery')
            return str(data)
        
        return str(data)
    
    def _build_diagnostic_prompt(self, error_message: str) -> str:
        """Build structured prompt for error analysis with advanced prompt engineering."""
        return f"""
**DIAGNOSTIC ANALYSIS REQUEST**

**System Context:**
- Linux production environment
- Require safe, tested solutions
- Zero-downtime approach preferred

**Error/Log Message:**
{error_message}

**Analysis Requirements:**

1. **Root Cause Analysis (RCA):**
   - Identify the exact underlying cause
   - Consider system interactions and dependencies
   - Assess potential cascading effects

2. **Solution Strategy:**
   - Provide step-by-step resolution with examples
   - Include verification steps
   - Mention any prerequisites or dependencies

3. **Shell Commands:**
   - Generate production-ready, safe commands
   - Use 'sed' for configuration file modifications
   - Include backup commands where applicable
   - No comments in command strings

4. **User Input Requirements:**
   - Ask for missing critical information (config paths, service names, etc.)
   - Be specific about what information is needed

5. **Assessment:**
   - Severity level (low/medium/high/critical)
   - Confidence level in diagnosis (0-100)

**Response Format** (must be valid JSON):
{{
  "rca": "Detailed root cause analysis explaining the why behind the error",
  "solution": "Step-by-step solution with examples and verification steps",
  "commands": "command1\\ncommand2\\ncommand3",
  "user_input": "Specific question for user or empty string",
  "severity": "low/medium/high/critical",
  "confidence": 85
}}

**Safety Guidelines:**
- Never suggest commands that could cause data loss
- Always prioritize system stability
- Use non-destructive diagnostic commands first
- Warn about potential side effects in the solution field

Provide your analysis now:
"""
    
    def _parse_response(self, raw_output: str) -> Dict[str, Any]:
        """Parse and validate agent response."""
        try:
            # Try JSON parsing first
            if isinstance(raw_output, str):
                return json.loads(raw_output)
            elif isinstance(raw_output, dict):
                return raw_output
            else:
                return dict(raw_output)
        except json.JSONDecodeError:
            try:
                # Fallback to eval for Python-like strings
                return eval(raw_output)
            except:
                # Return structured error if parsing fails
                return {
                    "error": "Failed to parse agent response",
                    "rca": "Response parsing error - the AI agent returned an invalid response format",
                    "solution": "The diagnostic agent encountered a parsing error. Please try rephrasing your error message or check if it contains special characters.",
                    "commands": "",
                    "user_input": "Please try rephrasing your error message",
                    "severity": "medium",
                    "confidence": 0
                }
    
    def get_session_history(self) -> list:
        """Get conversation history from agent memory."""
        if hasattr(self.agent, 'memory') and self.agent.memory:
            return self.agent.memory.get_messages()
        return []
    
    def clear_session(self):
        """Clear current diagnostic session."""
        if hasattr(self.agent, 'memory') and self.agent.memory:
            self.agent.memory.clear()
