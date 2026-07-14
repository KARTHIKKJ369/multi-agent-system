import subprocess
import tempfile
import os
from typing import Any, Dict, Optional
from .base import BaseTool


class PythonTool(BaseTool):
    """Tool for executing Python code safely"""
    
    def __init__(self):
        super().__init__(
            name="python",
            description="Execute Python code and return the output"
        )
    
    async def run(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute Python code.
        
        Args:
            code: The Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict containing execution result
        """
        await self.validate_inputs(code=code, timeout=timeout)
        
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute the code
                result = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            finally:
                # Clean up the temporary file
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Maximum execution time in seconds",
                    "default": 30
                }
            },
            "required": ["code"]
        }
