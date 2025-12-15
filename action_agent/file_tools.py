"""
File Tools - File operations with code structure analysis
"""

import os
from typing import Dict, Any, Optional, List
from .logger import ActionLogger


class FileTools:
    """
    File operations with code structure analysis
    """
    
    def __init__(self, logger: Optional[ActionLogger] = None):
        """
        Initialize file tools
        
        Args:
            logger: ActionLogger instance (creates new if not provided)
        """
        self.logger = logger or ActionLogger()
    
    def read_file(self, file_path: str, analyze_structure: bool = True) -> Dict[str, Any]:
        """
        Read a file and optionally analyze its structure
        
        Args:
            file_path: Path to the file (absolute or relative)
            analyze_structure: Whether to analyze code structure (default: True)
            
        Returns:
            Dict with file content and optionally structure analysis
        """
        try:
            # Resolve path
            if not os.path.isabs(file_path):
                # Relative to current directory
                file_path = os.path.abspath(file_path)
            
            # Check if file exists
            if not os.path.exists(file_path):
                self.logger.log(
                    action_type="file_read",
                    action=f"read_file('{file_path}')",
                    result=None,
                    success=False,
                    error_message=f"File not found: {file_path}"
                )
                return {
                    "success": False,
                    "content": "",
                    "file_path": file_path,
                    "error": f"File not found: {file_path}"
                }
            
            if not os.path.isfile(file_path):
                self.logger.log(
                    action_type="file_read",
                    action=f"read_file('{file_path}')",
                    result=None,
                    success=False,
                    error_message=f"Path is not a file: {file_path}"
                )
                return {
                    "success": False,
                    "content": "",
                    "file_path": file_path,
                    "error": f"Path is not a file: {file_path}"
                }
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = {
                "success": True,
                "content": content,
                "file_path": file_path,
                "file_size": len(content)
            }
            
            # Analyze structure if requested and it's a code file
            if analyze_structure and self._is_code_file(file_path):
                structure = self._analyze_code_structure(content, file_path)
                result["structure"] = structure
            
            # Log the action
            self.logger.log(
                action_type="file_read",
                action=f"read_file('{file_path}')",
                result=f"Read {len(content)} characters",
                success=True,
                metadata={"file_size": len(content), "has_structure": "structure" in result}
            )
            
            return result
            
        except PermissionError:
            error_msg = f"Permission denied: {file_path}"
            self.logger.log(
                action_type="file_read",
                action=f"read_file('{file_path}')",
                result=None,
                success=False,
                error_message=error_msg
            )
            return {
                "success": False,
                "content": "",
                "file_path": file_path,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            self.logger.log(
                action_type="file_read",
                action=f"read_file('{file_path}')",
                result=None,
                success=False,
                error_message=error_msg
            )
            return {
                "success": False,
                "content": "",
                "file_path": file_path,
                "error": error_msg
            }
    
    def write_file(self, file_path: str, content: str, append: bool = False) -> Dict[str, Any]:
        """
        Write content to a file
        
        Args:
            file_path: Path to the file
            content: Content to write
            append: If True, append to file; if False, overwrite
            
        Returns:
            Dict with execution result
        """
        try:
            # Resolve path
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
            
            # Create directory if needed
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            # Write file
            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            action = "appended to" if append else "wrote to"
            self.logger.log(
                action_type="file_write",
                action=f"write_file('{file_path}', append={append})",
                result=f"Successfully {action} file",
                success=True,
                metadata={"content_length": len(content), "append": append}
            )
            
            return {
                "success": True,
                "file_path": file_path,
                "action": action,
                "content_length": len(content)
            }
            
        except Exception as e:
            error_msg = f"Error writing file: {str(e)}"
            self.logger.log(
                action_type="file_write",
                action=f"write_file('{file_path}')",
                result=None,
                success=False,
                error_message=error_msg
            )
            return {
                "success": False,
                "file_path": file_path,
                "error": error_msg
            }
    
    def list_files(self, directory: Optional[str] = None) -> Dict[str, Any]:
        """
        List files and directories in a directory
        
        Args:
            directory: Directory path (defaults to current directory)
            
        Returns:
            Dict with file listing
        """
        try:
            if directory is None:
                directory = os.getcwd()
            
            if not os.path.isabs(directory):
                directory = os.path.abspath(directory)
            
            if not os.path.exists(directory):
                return {
                    "success": False,
                    "files": [],
                    "directory": directory,
                    "error": f"Directory not found: {directory}"
                }
            
            if not os.path.isdir(directory):
                return {
                    "success": False,
                    "files": [],
                    "directory": directory,
                    "error": f"Path is not a directory: {directory}"
                }
            
            files = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                files.append({
                    "name": item,
                    "is_directory": os.path.isdir(item_path),
                    "is_file": os.path.isfile(item_path)
                })
            
            # Sort: directories first, then files
            files.sort(key=lambda x: (not x["is_directory"], x["name"]))
            
            self.logger.log(
                action_type="file_list",
                action=f"list_files('{directory}')",
                result=f"Found {len(files)} items",
                success=True
            )
            
            return {
                "success": True,
                "files": files,
                "directory": directory,
                "count": len(files)
            }
            
        except Exception as e:
            error_msg = f"Error listing directory: {str(e)}"
            self.logger.log(
                action_type="file_list",
                action=f"list_files('{directory}')",
                result=None,
                success=False,
                error_message=error_msg
            )
            return {
                "success": False,
                "files": [],
                "directory": directory or "current",
                "error": error_msg
            }
    
    def _is_code_file(self, file_path: str) -> bool:
        """Check if file is a code file"""
        code_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php']
        return any(file_path.endswith(ext) for ext in code_extensions)
    
    def _analyze_code_structure(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze code structure (currently supports Python)
        
        Args:
            content: File content
            file_path: File path (for determining language)
            
        Returns:
            Dict with structure analysis
        """
        if file_path.endswith('.py'):
            return self._analyze_python(content, file_path)
        
        # For other languages, return basic info
        return {
            "type": "unknown",
            "language": "unknown"
        }
    
    def _analyze_python(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Python file structure using AST
        
        Args:
            content: Python file content
            file_path: File path
            
        Returns:
            Dict with Python structure analysis
        """
        try:
            import ast
            
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            test_functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node)
                    }
                    functions.append(func_info)
                    
                    # Check if it's a test function
                    if node.name.startswith("test_"):
                        test_functions.append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node)
                    })
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Get import statement
                    try:
                        import_str = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
                        imports.append(import_str)
                    except:
                        imports.append(str(node))
            
            is_test_file = "test" in file_path.lower() or any(f["name"].startswith("test_") for f in functions)
            
            return {
                "type": "python",
                "functions": functions,
                "classes": classes,
                "imports": imports[:10],  # Limit imports
                "is_test_file": is_test_file,
                "test_functions": test_functions,
                "function_count": len(functions),
                "class_count": len(classes)
            }
            
        except SyntaxError as e:
            return {
                "type": "python",
                "error": f"Syntax error: {str(e)}",
                "line": e.lineno if hasattr(e, 'lineno') else None
            }
        except Exception as e:
            return {
                "type": "python",
                "error": f"Could not parse: {str(e)}"
            }


