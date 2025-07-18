import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.memory import AgentMemory
from pydantic import BaseModel, Field
import uuid

class DiagnosticResponse(BaseModel):
    """Structured response model for diagnostic analysis."""
    rca: str = Field(..., description="Root cause analysis of the error")
    solution: str = Field(..., description="Detailed solution with examples")
    commands: str = Field(..., description="Shell commands to resolve the issue")
    user_input: str = Field(default="", description="Additional input needed from user")
    severity: str = Field(default="medium", description="Issue severity: low/medium/high/critical")
    confidence: int = Field(default=80, description="Confidence level in diagnosis (0-100)")

class AIEngine:
    def __init__(self, session_id: Optional[str] = None):
        """Initialize the Linux diagnostic AI engine with Agno framework."""
        self.session_id = session_id or str(uuid.uuid4())
        self.rules_initialized = False
        self.conversation_count = 0
        self.rules_refresh_interval = 10  # Refresh rules every 10 conversations
        self._load_environment()
        self._initialize_agent()
        self._load_conversation_history()
        
    def _load_environment(self):
        """Load environment variables from .env file."""
        dotenv_path = os.path.join("/opt/Hackathon/hackathon/API/API/settings", '.env')
        load_dotenv(dotenv_path)
        
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    def _initialize_agent(self):
        """Initialize the Agno agent with persistent system instructions."""
        # Enhanced system instructions that persist
        system_instructions = [
            "You are LinuxDiagnosticGPT, an expert Linux system administrator with 15+ years of experience",
            "ALWAYS respond in valid JSON format with: rca, solution, commands, user_input, severity, confidence",
            "Generate deterministic, executable shell commands with error handling",
            "Use absolute paths, include backups before modifications, validate before applying changes",
            "Commands must be production-safe with rollback capabilities",
            "Include step-by-step verification and success confirmations",
            "Consider conversation history and build upon previous diagnoses",
            "Prioritize system stability and security in all recommendations",
            "commands shoud not have comment or explanation in the command itself, only commands should be there",
        ]
        
        self.agent = Agent(
            model=OpenAIChat(id=self.model, api_key=self.api_key),
            description=(
                "You are LinuxDiagnosticGPT, an expert Linux system administrator and troubleshooter. "
                "You provide structured diagnostic analysis with executable commands. "
                "Always maintain the diagnostic framework and respond in the required JSON format."
            ),
            instructions=system_instructions,
            memory=AgentMemory(
                db_url="sqlite:///diagnostic_memory.db",
                table_name="diagnostic_sessions"
            ),
            response_model=DiagnosticResponse,
            markdown=False,
            show_tool_calls=True
        )
    
    def _load_conversation_history(self):
        """Load existing conversation history for this session."""
        try:
            if hasattr(self.agent, 'memory') and self.agent.memory:
                messages = self.agent.memory.get_messages()
                # Count actual user queries to track conversation progress
                self.conversation_count = len([
                    msg for msg in messages 
                    if msg.get('role') == 'user' and 
                    not msg.get('content', '').startswith('DIAGNOSTIC_RULES_REFRESH')
                ])
                
                # Check if rules exist in recent context
                recent_messages = messages[-20:] if len(messages) > 20 else messages
                self.rules_initialized = any(
                    "LINUX DIAGNOSTIC EXPERT SYSTEM" in msg.get('content', '') 
                    for msg in recent_messages
                )
                
                print(f"Loaded {len(messages)} messages from session {self.session_id}")
                print(f"Conversation count: {self.conversation_count}")
                print(f"Rules in recent context: {self.rules_initialized}")
        except Exception as e:
            print(f"Warning: Could not load conversation history: {e}")
    
    def _get_diagnostic_rules(self) -> str:
        """Get the comprehensive diagnostic rules."""
        return f"""
**DIAGNOSTIC_RULES_REFRESH** - Session: {self.session_id} - Count: {self.conversation_count}

**LINUX DIAGNOSTIC EXPERT SYSTEM - ACTIVE RULES**

**CRITICAL INSTRUCTIONS - ALWAYS FOLLOW:**

**JSON OUTPUT FORMAT (MANDATORY):**
{{
    "rca": "Comprehensive root cause analysis with technical details",
    "solution": "Detailed step-by-step solution with verification points",
    "commands": "cmd1 && echo 'Step 1 complete'\\ncmd2 && echo 'Step 2 complete'",
    "user_input": "Information needed from user or empty string",
    "severity": "low|medium|high|critical",
    "confidence": 85
}}

**COMMAND GENERATION RULES:**
1. **DETERMINISTIC:** Identical inputs → Identical command sequences
2. **EXECUTABLE:** Each command must work independently in sequence
3. **SAFE:** Include validation checks before destructive operations
4. **ROLLBACK:** Always provide backup/restore procedures
5. **UNIVERSAL:** Compatible with RHEL/CentOS/Ubuntu/Debian
6. **SECURED:** Include appropriate sudo/privilege escalation

**COMMAND STRUCTURE REQUIREMENTS:**
- Use absolute paths: `/usr/bin/systemctl` not `systemctl`
- Include existence checks: `[[ -f /path/file ]] && command`
- Chain with `&&` for dependent operations
- Add timeouts for network operations: `timeout 5 command`
- Success confirmations: `&& echo 'Step N complete'`
- Error handling: `|| echo 'Step N failed'`

**SAFETY PROTOCOLS:**
- Backup before modify: `cp file file.backup.$(date +%Y%m%d_%H%M%S)`
- Validate before apply: `nginx -t && systemctl reload nginx`
- Check service status: `systemctl is-active service`
- Test network connectivity: `nc -zv host port`
- Verify permissions before privilege operations

**ANALYSIS FRAMEWORK:**
1. **ROOT CAUSE:** Identify primary failure point and dependencies
2. **SOLUTION:** Design minimal-impact resolution with rollback
3. **COMMANDS:** Phase approach - diagnose, prepare, fix, verify
4. **SAFETY:** Non-destructive where possible, with clear rollback path

**CONSISTENCY REQUIREMENTS:**
- Same error patterns → Same diagnostic approach
- Standardized command syntax and structure
- Predictable backup and recovery procedures
- Production-safe execution order

These rules remain active for all subsequent analyses in this session.
"""
    
    def _should_refresh_rules(self) -> bool:
        """Determine if rules should be refreshed based on conversation count."""
        return (
            not self.rules_initialized or 
            self.conversation_count > 0 and 
            self.conversation_count % self.rules_refresh_interval == 0
        )
    
    def _refresh_rules_if_needed(self):
        """Refresh diagnostic rules periodically to maintain context."""
        if self._should_refresh_rules():
            rules_message = self._get_diagnostic_rules()
            
            # Send rules refresh to maintain context
            self.agent.run(f"DIAGNOSTIC_RULES_REFRESH: {rules_message}")
            
            # Save rules refresh to memory with special marker
            self._save_message_to_memory("system", rules_message)
            
            self.rules_initialized = True
            print(f"Diagnostic rules refreshed for session {self.session_id} at conversation {self.conversation_count}")
    
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
            
            # Refresh rules if needed (before analysis)
            self._refresh_rules_if_needed()
            
            # Build diagnostic prompt with comprehensive context
            diagnostic_prompt = self._build_diagnostic_prompt(prompt_text)
            
            # Increment conversation count
            self.conversation_count += 1
            
            # Save user input to memory
            self._save_message_to_memory("user", f"Error Analysis #{self.conversation_count}: {prompt_text}")
            
            # Run agent analysis
            response = self.agent.run(diagnostic_prompt)
            
            # Parse and validate response
            parsed_response = self._parse_response(response.content)
            
            # Save AI response to memory
            self._save_message_to_memory("assistant", json.dumps(parsed_response, indent=2))
            
            return parsed_response
            
        except Exception as e:
            error_response = {
                "error": str(e),
                "rca": "Analysis failed due to internal error",
                "solution": "Please check input format and try again",
                "commands": "",
                "user_input": "",
                "severity": "medium",
                "confidence": 0
            }
            
            # Save error to memory
            self._save_message_to_memory("assistant", json.dumps(error_response, indent=2))
            
            return error_response
    
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
        """Build comprehensive diagnostic prompt with smart context management."""
        # Get relevant conversation context (more intelligent selection)
        conversation_context = self._get_intelligent_conversation_context()
        
        # Get recent similar errors for pattern recognition
        similar_context = self._get_similar_error_context(error_message)
        
        return f"""
**ERROR ANALYSIS REQUEST #{self.conversation_count}**

**CONVERSATION CONTEXT:**
{conversation_context}

**SIMILAR ERROR PATTERNS:**
{similar_context}

**CURRENT ERROR/LOG:**
{error_message}

**INSTRUCTIONS:**
Apply the active diagnostic rules and framework to analyze this error.
Consider the conversation history and any similar patterns.
Provide comprehensive analysis in the required JSON format.
Build upon previous diagnoses if the issue is related.
"""
    
    def _get_intelligent_conversation_context(self) -> str:
        """Get intelligently filtered conversation context."""
        try:
            history = self.get_session_history()
            if not history:
                return "No previous conversation in this session."
            
            # Filter out system messages and get relevant context
            user_assistant_messages = [
                msg for msg in history 
                if msg.get('role') in ['user', 'assistant'] and 
                not msg.get('content', '').startswith('DIAGNOSTIC_RULES_REFRESH')
            ]
            
            if not user_assistant_messages:
                return "No previous error analysis in this session."
            
            # Smart context selection: recent + important messages
            recent_messages = user_assistant_messages[-6:]  # Last 6 exchanges
            
            # Also include any critical/high severity diagnoses
            critical_messages = [
                msg for msg in user_assistant_messages[:-6]  # Exclude recent ones
                if msg.get('role') == 'assistant' and 
                '"severity": "critical"' in msg.get('content', '')
            ][-2:]  # Last 2 critical issues
            
            # Combine contexts
            context_messages = critical_messages + recent_messages
            
            context_lines = []
            for i, msg in enumerate(context_messages, 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                
                # Smart truncation - preserve JSON structure for assistant messages
                if role == 'assistant' and content.startswith('{'):
                    try:
                        json_content = json.loads(content)
                        summary = f"RCA: {json_content.get('rca', '')[:100]}... | Severity: {json_content.get('severity', 'unknown')}"
                        content = summary
                    except:
                        content = content[:200] + "..."
                elif len(content) > 200:
                    content = content[:200] + "..."
                
                context_lines.append(f"{i}. {role.upper()}: {content}")
            
            return "\n".join(context_lines)
            
        except Exception as e:
            return f"Error loading conversation context: {e}"
    
    def _get_similar_error_context(self, current_error: str) -> str:
        """Get context about similar errors from conversation history."""
        try:
            history = self.get_session_history()
            current_error_lower = current_error.lower()
            
            # Extract key error terms
            error_keywords = []
            for word in current_error_lower.split():
                if any(keyword in word for keyword in ['error', 'fail', 'denied', 'timeout', 'connection', 'permission']):
                    error_keywords.append(word)
            
            if not error_keywords:
                return "No similar error patterns found in session history."
            
            # Find messages with similar error patterns
            similar_messages = []
            for msg in history:
                if msg.get('role') == 'user':
                    content_lower = msg.get('content', '').lower()
                    if any(keyword in content_lower for keyword in error_keywords):
                        similar_messages.append(msg)
            
            if not similar_messages:
                return "No similar error patterns found in session history."
            
            # Return summary of similar patterns
            patterns = []
            for msg in similar_messages[-3:]:  # Last 3 similar errors
                content = msg.get('content', '')[:150] + "..."
                patterns.append(f"- {content}")
            
            return "Similar errors in this session:\n" + "\n".join(patterns)
            
        except Exception as e:
            return f"Error finding similar patterns: {e}"
    
    def _save_message_to_memory(self, role: str, content: str):
        """Save a message to memory with metadata."""
        try:
            if hasattr(self.agent, 'memory') and self.agent.memory:
                self.agent.memory.add_message({
                    "role": role,
                    "content": content,
                    "session_id": self.session_id,
                    "conversation_count": self.conversation_count,
                    "timestamp": json.dumps({"timestamp": "now"})
                })
        except Exception as e:
            print(f"Warning: Could not save message to memory: {e}")
    
    def _parse_response(self, raw_output: str) -> Dict[str, Any]:
        """Parse and validate agent response."""
        try:
            if isinstance(raw_output, str):
                return json.loads(raw_output)
            elif isinstance(raw_output, dict):
                return raw_output
            else:
                return dict(raw_output)
        except json.JSONDecodeError:
            try:
                return eval(raw_output)
            except:
                return {
                    "error": "Failed to parse agent response",
                    "rca": "Response parsing error - the AI agent returned an invalid response format",
                    "solution": "The diagnostic agent encountered a parsing error. Please try rephrasing your error message.",
                    "commands": "",
                    "user_input": "Please try rephrasing your error message",
                    "severity": "medium",
                    "confidence": 0
                }
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """Get conversation history from agent memory."""
        try:
            if hasattr(self.agent, 'memory') and self.agent.memory:
                return self.agent.memory.get_messages()
            return []
        except Exception as e:
            print(f"Error getting session history: {e}")
            return []
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        history = self.get_session_history()
        
        user_messages = [msg for msg in history if msg.get('role') == 'user']
        assistant_messages = [msg for msg in history if msg.get('role') == 'assistant']
        
        return {
            "session_id": self.session_id,
            "conversation_count": self.conversation_count,
            "total_messages": len(history),
            "user_queries": len(user_messages),
            "ai_responses": len(assistant_messages),
            "rules_initialized": self.rules_initialized,
            "next_rules_refresh": self.rules_refresh_interval - (self.conversation_count % self.rules_refresh_interval),
            "last_activity": history[-1].get('timestamp') if history else None
        }
    
    def clear_session(self):
        """Clear current diagnostic session."""
        try:
            if hasattr(self.agent, 'memory') and self.agent.memory:
                self.agent.memory.clear()
                print(f"Cleared session: {self.session_id}")
            
            # Reset all session state
            self.rules_initialized = False
            self.conversation_count = 0
            self.session_id = str(uuid.uuid4())
            
            print(f"New session started: {self.session_id}")
            
        except Exception as e:
            print(f"Error clearing session: {e}")
    
    def force_rules_refresh(self):
        """Force refresh of diagnostic rules."""
        self.rules_initialized = False
        self._refresh_rules_if_needed()
        print("Diagnostic rules forcefully refreshed")
    
    def set_rules_refresh_interval(self, interval: int):
        """Set how often rules should be refreshed."""
        self.rules_refresh_interval = max(1, interval)
        print(f"Rules refresh interval set to {self.rules_refresh_interval} conversations")
