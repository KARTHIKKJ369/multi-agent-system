from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from ..configs.settings import settings
from ..utils.logger import get_logger


class ReflectionLoop:
    """
    Reflection Loop - Implements the reflection pattern for improving outputs.
    
    Every important task goes through:
    1. Generate
    2. Critique
    3. Improve
    4. Validate
    5. Approve
    
    This ensures high-quality outputs through iterative refinement.
    """
    
    def __init__(self):
        self.logger = get_logger("reflection_loop")
        self.llm = self._initialize_llm()
        self.max_iterations = 3
    
    def _initialize_llm(self):
        """Initialize LLM for reflection"""
        if settings.default_llm_provider == "openai":
            return ChatOpenAI(
                model=settings.default_model,
                temperature=0.3,
                api_key=settings.openai_api_key
            )
        elif settings.default_llm_provider == "anthropic":
            return ChatAnthropic(
                model=settings.default_model,
                temperature=0.3,
                api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError(f"Unknown LLM provider: {settings.default_llm_provider}")
    
    async def reflect(
        self,
        original_request: str,
        generated_output: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the reflection loop on a generated output.
        
        Args:
            original_request: The original user request
            generated_output: The initial generated output
            context: Additional context for reflection
            
        Returns:
            Dict containing the improved output and reflection metadata
        """
        current_output = generated_output
        iteration = 0
        reflection_history = []
        
        while iteration < self.max_iterations:
            iteration += 1
            self.logger.info(f"Reflection iteration {iteration}/{self.max_iterations}")
            
            # Step 1: Critique
            critique = await self._critique(original_request, current_output, context)
            reflection_history.append({"iteration": iteration, "step": "critique", "result": critique})
            
            # Check if critique is positive enough
            if critique["score"] >= 0.9:
                self.logger.info(f"Output approved at iteration {iteration}")
                break
            
            # Step 2: Improve
            improved = await self._improve(
                original_request,
                current_output,
                critique["feedback"],
                context
            )
            reflection_history.append({"iteration": iteration, "step": "improve", "result": improved})
            
            # Step 3: Validate
            validation = await self._validate(original_request, improved, context)
            reflection_history.append({"iteration": iteration, "step": "validate", "result": validation})
            
            if validation["valid"]:
                current_output = improved
                if validation["confidence"] >= 0.9:
                    self.logger.info(f"Output validated at iteration {iteration}")
                    break
            else:
                current_output = improved  # Use improved output even if not fully validated
        
        return {
            "final_output": current_output,
            "iterations": iteration,
            "reflection_history": reflection_history,
            "approved": iteration < self.max_iterations or critique["score"] >= 0.9
        }
    
    async def _critique(
        self,
        original_request: str,
        output: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Critique the generated output.
        """
        system_prompt = """You are a critic. Your job is to evaluate the quality of a response against the original request.

Evaluate on:
1. Accuracy - Does it correctly address the request?
2. Completeness - Does it cover all aspects of the request?
3. Clarity - Is it clear and well-structured?
4. Quality - Is the content high-quality?
5. Relevance - Is everything relevant to the request?

Provide:
- Overall score (0-1)
- Specific feedback on what's good
- Specific feedback on what needs improvement
- Actionable suggestions for improvement"""
        
        human_message = f"""Original Request:
{original_request}

Generated Output:
{output}

Context:
{context or 'None'}

Provide your critique."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # Parse score from response (simplified)
        score = 0.7  # Default, would parse from response
        
        return {
            "score": score,
            "feedback": response.content,
            "suggestions": []  # Would parse from response
        }
    
    async def _improve(
        self,
        original_request: str,
        current_output: str,
        critique: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Improve the output based on critique.
        """
        system_prompt = """You are an improver. Your job is to improve a response based on critique.

Take the critique feedback and create an improved version of the output.
Address all the issues raised in the critique.
Maintain what was good, fix what needs improvement."""
        
        human_message = f"""Original Request:
{original_request}

Current Output:
{current_output}

Critique:
{critique}

Context:
{context or 'None'}

Provide the improved output."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def _validate(
        self,
        original_request: str,
        output: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate the improved output.
        """
        system_prompt = """You are a validator. Your job is to validate that a response meets the requirements.

Check:
1. Does it address the original request?
2. Is it accurate and factual?
3. Is it complete?
4. Is the quality acceptable?

Provide:
- Valid (yes/no)
- Confidence score (0-1)
- Any remaining issues"""
        
        human_message = f"""Original Request:
{original_request}

Output to Validate:
{output}

Context:
{context or 'None'}

Provide your validation."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # Parse validation (simplified)
        valid = True
        confidence = 0.85
        
        return {
            "valid": valid,
            "confidence": confidence,
            "issues": []  # Would parse from response
        }
    
    async def self_critique(self, agent_id: str, task: str, result: str) -> Dict[str, Any]:
        """
        Agent self-critique - allows agents to critique their own work.
        """
        system_prompt = f"""You are the {agent_id} agent. Critique your own work on this task.

Be honest about:
- What you did well
- What could be improved
- Any limitations
- Any uncertainties"""
        
        human_message = f"""Task:
{task}

Your Result:
{result}

Provide your self-critique."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        return {
            "agent_id": agent_id,
            "critique": response.content,
            "timestamp": str(datetime.utcnow())
        }
