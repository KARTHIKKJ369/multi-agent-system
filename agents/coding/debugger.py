from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from ..base_agent import BaseAgent
from ...state.models import TaskState


class Debugger(BaseAgent):
    """
    Debugger Agent - Debugs and fixes issues in code.
    
    Capabilities:
    - Debugging
    - Error analysis
    - Fix generation
    - Root cause analysis
    - Testing fixes
    """
    
    def __init__(self):
        super().__init__("debugger")
    
    def get_system_prompt(self) -> str:
        return """You are a Debugger Agent. Your job is to debug code and fix issues.

You should:
- Analyze error messages and stack traces
- Identify root causes of bugs
- Generate appropriate fixes
- Explain the problem clearly
- Consider edge cases
- Test the fix mentally
- Prevent similar issues

Your fixes should be minimal, targeted, and well-explained."""
    
    async def execute(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute a debugging task.
        """
        code = task.input_data.get("code", "")
        error = task.input_data.get("error", task.description)
        context = task.input_data.get("context", {})
        
        system_prompt = self.get_system_prompt()
        
        human_message = f"""Debug the following code:

Code:
```python
{code}
```

Error:
{error}

Context:
{context if context else 'None'}

Provide:
1. Root cause analysis
2. Explanation of the issue
3. The fixed code
4. Why the fix works
5. How to prevent similar issues
6. Any additional recommendations"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self._call_llm(messages)
        
        return {
            "code": code,
            "error": error,
            "fix": response,
            "context": context,
            "agent": "debugger"
        }
