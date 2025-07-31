"""
Workflow Executor - Safely executes generated Python workflows
"""

import subprocess
import sys
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class WorkflowExecutor:
    """Executes Python workflow scripts safely"""
    
    def __init__(self):
        self.timeout = 300  # 5 minutes default timeout
    
    def execute_workflow(self, script_path: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute a workflow script"""
        script_path = Path(script_path)
        
        if not script_path.exists():
            return {
                "success": False,
                "error": f"Script not found: {script_path}",
                "output": "",
                "exit_code": 1
            }
        
        # Use provided timeout or default
        exec_timeout = timeout or self.timeout
        
        try:
            # Execute the script in a subprocess
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=exec_timeout,
                cwd=script_path.parent
            )
            
            return {
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else "",
                "output": result.stdout,
                "exit_code": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Workflow execution timed out after {exec_timeout} seconds",
                "output": "",
                "exit_code": 124
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "exit_code": 1
            }
    
    def validate_script(self, script_path: str) -> Dict[str, Any]:
        """Validate Python script syntax"""
        script_path = Path(script_path)
        
        if not script_path.exists():
            return {
                "valid": False,
                "error": f"Script not found: {script_path}"
            }
        
        try:
            with open(script_path) as f:
                source_code = f.read()
            
            # Compile to check syntax
            compile(source_code, str(script_path), 'exec')
            
            return {
                "valid": True,
                "error": ""
            }
        
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Syntax error: {e}"
            }
        
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {e}"
            }
    
    def dry_run(self, script_path: str) -> Dict[str, Any]:
        """Perform a dry run analysis of the workflow"""
        script_path = Path(script_path)
        
        # First validate syntax
        validation = self.validate_script(script_path)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "analysis": {}
            }
        
        try:
            with open(script_path) as f:
                source_code = f.read()
            
            # Analyze the script
            analysis = self._analyze_script(source_code)
            
            return {
                "success": True,
                "error": "",
                "analysis": analysis
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    def _analyze_script(self, source_code: str) -> Dict[str, Any]:
        """Analyze script for potential issues and requirements"""
        import ast
        import re
        
        analysis = {
            "imports": [],
            "external_calls": [],
            "file_operations": [],
            "network_calls": [],
            "potential_issues": []
        }
        
        # Parse AST
        try:
            tree = ast.parse(source_code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["imports"].append(node.module)
                
                elif isinstance(node, ast.Call):
                    if hasattr(node.func, 'attr'):
                        func_name = node.func.attr
                        
                        # Check for network calls
                        if func_name in ['get', 'post', 'put', 'delete', 'request']:
                            analysis["network_calls"].append(func_name)
                        
                        # Check for file operations
                        elif func_name in ['open', 'read', 'write']:
                            analysis["file_operations"].append(func_name)
        
        except SyntaxError:
            analysis["potential_issues"].append("Script has syntax errors")
        
        # Check for potentially missing dependencies
        risky_imports = ['requests', 'twilio', 'smtplib', 'beautifulsoup4']
        for imp in analysis["imports"]:
            if imp in risky_imports:
                analysis["potential_issues"].append(f"May require '{imp}' package")
        
        return analysis
    
    def install_dependencies(self, requirements: list) -> Dict[str, Any]:
        """Install required dependencies"""
        if not requirements:
            return {"success": True, "installed": []}
        
        installed = []
        failed = []
        
        for package in requirements:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    installed.append(package)
                else:
                    failed.append(f"{package}: {result.stderr}")
            
            except Exception as e:
                failed.append(f"{package}: {str(e)}")
        
        return {
            "success": len(failed) == 0,
            "installed": installed,
            "failed": failed
        }
