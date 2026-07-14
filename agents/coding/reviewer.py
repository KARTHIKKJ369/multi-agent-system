from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from ..base_agent import BaseAgent
from ...state.models import TaskState


class Reviewer(BaseAgent):
    """
    Reviewer Agent - Reviews code for quality and best practices.
    
    Capabilities:
    - Code review
    - Quality assurance
    - Best practices verification
    - Security review
    - Performance review
    """
    
    def __init__(self):
        super().__init__("reviewer")
    
    def get_system_prompt(self) -> str:
        return """You are a Reviewer Agent. Your job is to review code for quality, best practices, and potential issues.

You should:
- Check for code quality and readability
- Verify adherence to best practices
- Identify potential bugs or issues
- Check for security vulnerabilities
- Evaluate performance considerations
- Suggest improvements
- Provide constructive feedback

Your reviews should be thorough, fair, and actionable."""
    
    async def execute(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute a code review task.
        """
        code = task.input_data.get("code", task.description)
        language = task.input_data.get("language", "python")
        review_criteria = task.input_data.get("criteria", ["quality", "security", "performance"])
        
        system_prompt = self.get_system_prompt()
        
        human_message = f"""Review the following code:

Code:
```{language}
{code}
```

Review criteria: {', '.join(review_criteria)}

Provide:
1. Overall assessment (1-10 scale)
2. Strengths
3. Issues found (with severity levels)
4. Security concerns (if any)
5. Performance considerations
6. Specific improvement suggestions
7. Whether the code is ready for production"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self._call_llm(messages)
        
        return {
            "code": code,
            "review": response,
            "language": language,
            "criteria": review_criteria,
            "agent": "reviewer"
        }
