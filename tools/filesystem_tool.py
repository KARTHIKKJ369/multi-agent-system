import os
import json
from typing import Any, Dict, Optional
from pathlib import Path
from .base import BaseTool


class FilesystemTool(BaseTool):
    """Tool for filesystem operations"""
    
    def __init__(self):
        super().__init__(
            name="filesystem",
            description="Read, write, and manage files in the filesystem"
        )
    
    async def run(
        self,
        operation: str,
        path: str,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform filesystem operations.
        
        Args:
            operation: The operation to perform (read, write, list, delete)
            path: The file or directory path
            content: Content to write (for write operation)
            
        Returns:
            Dict containing operation result
        """
        await self.validate_inputs(operation=operation, path=path)
        
        try:
            if operation == "read":
                return await self._read_file(path)
            elif operation == "write":
                if content is None:
                    raise ValueError("Content required for write operation")
                return await self._write_file(path, content)
            elif operation == "list":
                return await self._list_directory(path)
            elif operation == "delete":
                return await self._delete_file(path)
            else:
                raise ValueError(f"Unknown operation: {operation}")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _read_file(self, path: str) -> Dict[str, Any]:
        """Read a file"""
        try:
            with open(path, 'r') as f:
                content = f.read()
            return {
                "success": True,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write to a file"""
        try:
            # Create parent directories if they don't exist
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w') as f:
                f.write(content)
            return {
                "success": True,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _list_directory(self, path: str) -> Dict[str, Any]:
        """List directory contents"""
        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                items.append({
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            return {
                "success": True,
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file or directory"""
        try:
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)
            return {
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read", "write", "list", "delete"],
                    "description": "The operation to perform"
                },
                "path": {
                    "type": "string",
                    "description": "The file or directory path"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write (for write operation)"
                }
            },
            "required": ["operation", "path"]
        }
