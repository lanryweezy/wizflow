#!/usr/bin/env python3
"""
WizFlow CLI - Main entry point for the automation tool
"""

import argparse
import sys
import os
import json
from pathlib import Path
from typing import Optional

from .core.llm_interface import LLMInterface
from .core.workflow_builder import WorkflowBuilder
from .core.code_generator import CodeGenerator
from .executors.workflow_executor import WorkflowExecutor
from .core.config import Config


class WizFlowCLI:
    """Main CLI application class"""
    
    def __init__(self):
        self.config = Config()
        self.llm = LLMInterface(self.config)
        self.builder = WorkflowBuilder(self.llm)
        self.generator = CodeGenerator()
        self.executor = WorkflowExecutor()
        self.workflows_dir = Path("workflows")
        self.workflows_dir.mkdir(exist_ok=True)
    
    def generate_workflow(self, description: str, output_name: Optional[str] = None) -> tuple[str, str]:
        """Generate workflow from natural language description"""
        print(f"🧠 Analyzing: {description}")
        
        # Generate workflow JSON using LLM
        workflow_json = self.builder.build_from_description(description)
        
        # Generate workflow name if not provided
        if not output_name:
            output_name = workflow_json.get('name', 'generated_workflow').lower().replace(' ', '_')
        
        # Generate Python code
        python_code = self.generator.generate_code(workflow_json)
        
        # Save files
        json_path = self.workflows_dir / f"{output_name}.json"
        py_path = self.workflows_dir / f"{output_name}.py"
        
        with open(json_path, 'w') as f:
            json.dump(workflow_json, f, indent=2)
        
        with open(py_path, 'w') as f:
            f.write(python_code)
        
        print(f"✅ JSON Workflow Created: {json_path}")
        print(f"✅ Python Code Generated: {py_path}")
        
        return str(json_path), str(py_path)
    
    def list_workflows(self):
        """List all saved workflows"""
        workflows = list(self.workflows_dir.glob("*.json"))
        if not workflows:
            print("📭 No workflows found")
            return
        
        print("📋 Available Workflows:")
        for workflow in workflows:
            with open(workflow) as f:
                data = json.load(f)
            name = data.get('name', workflow.stem)
            description = data.get('description', 'No description')
            print(f"  • {workflow.stem}: {name} - {description}")
    
    def run_workflow(self, workflow_name: str):
        """Run a saved workflow"""
        py_path = self.workflows_dir / f"{workflow_name}.py"
        if not py_path.exists():
            print(f"❌ Workflow '{workflow_name}' not found")
            return
        
        print(f"🚀 Running {workflow_name}...")
        result = self.executor.execute_workflow(str(py_path))
        
        if result["success"]:
            print("✅ Workflow completed successfully")
            if result["output"]:
                print(f"📤 Output: {result['output']}")
        else:
            print(f"❌ Workflow failed: {result['error']}")
    
    def export_workflow(self, workflow_name: str):
        """Export workflow files to current directory"""
        json_path = self.workflows_dir / f"{workflow_name}.json"
        py_path = self.workflows_dir / f"{workflow_name}.py"
        
        if not json_path.exists():
            print(f"❌ Workflow '{workflow_name}' not found")
            return
        
        # Copy to current directory
        import shutil
        shutil.copy2(json_path, f"{workflow_name}.json")
        shutil.copy2(py_path, f"{workflow_name}.py")
        
        print(f"📦 Exported {workflow_name}.json and {workflow_name}.py to current directory")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="WizFlow - AI-powered automation workflow generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wizflow "When I get an email from boss, summarize and send to WhatsApp"
  wizflow list
  wizflow run my_workflow
  wizflow export my_workflow
        """
    )
    
    parser.add_argument('command', nargs='?', help='Natural language description or command')
    parser.add_argument('--name', '-n', help='Custom name for the workflow')
    parser.add_argument('--run', '-r', help='Run a saved workflow')
    parser.add_argument('--list', '-l', action='store_true', help='List all saved workflows')
    parser.add_argument('--export', '-e', help='Export a workflow to current directory')
    parser.add_argument('--config', '-c', help='Set configuration (e.g., --config openai_key=your_key)')
    
    args = parser.parse_args()
    
    cli = WizFlowCLI()
    
    try:
        if args.list:
            cli.list_workflows()
        elif args.run:
            cli.run_workflow(args.run)
        elif args.export:
            cli.export_workflow(args.export)
        elif args.config:
            key, value = args.config.split('=', 1)
            cli.config.set(key, value)
            print(f"✅ Set {key} configuration")
        elif args.command:
            if args.command in ['list', 'ls']:
                cli.list_workflows()
            else:
                json_path, py_path = cli.generate_workflow(args.command, args.name)
                
                # Ask if user wants to run immediately
                response = input("→ Run now? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    workflow_name = Path(py_path).stem
                    cli.run_workflow(workflow_name)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
