#!/usr/bin/env python3
"""
WizFlow CLI - Main entry point for the automation tool
"""

import argparse
import sys
import os
import json
import getpass
from pathlib import Path
from typing import Optional

from .core.llm_interface import LLMInterface
from .core.workflow_builder import WorkflowBuilder
from .core.code_generator import CodeGenerator
from .executors.workflow_executor import WorkflowExecutor
from .core.config import Config
from .core.credentials import CredentialManager
from .interactive_builder import InteractiveWorkflowBuilder
from .logger import setup_logger, get_logger


class WizFlowCLI:
    """Main CLI application class"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = Config()
        self.llm = LLMInterface(self.config)
        self.builder = WorkflowBuilder(self.llm)
        self.generator = CodeGenerator()
        self.executor = WorkflowExecutor()
        self.credentials = CredentialManager()
        self.workflows_dir = Path("workflows")
        self.workflows_dir.mkdir(exist_ok=True)
    
    def interactive_workflow(self):
        """Starts an interactive session to build a workflow."""
        builder = InteractiveWorkflowBuilder()
        workflow_json = builder.build()

        if not workflow_json or not workflow_json.get('name') or not workflow_json.get('actions'):
            self.logger.warning("\nWorkflow creation cancelled or incomplete. Exiting.")
            return

        self.logger.info("\n✅ Workflow created successfully!")

        output_name = workflow_json.get('name', 'interactive_workflow').lower().replace(' ', '_')

        # Generate Python code
        python_code = self.generator.generate_code(workflow_json)

        # Save files
        json_path = self.workflows_dir / f"{output_name}.json"
        py_path = self.workflows_dir / f"{output_name}.py"

        with open(json_path, 'w') as f:
            json.dump(workflow_json, f, indent=2)

        with open(py_path, 'w') as f:
            f.write(python_code)

        self.logger.info(f"✅ JSON Workflow Created: {json_path}")
        self.logger.info(f"✅ Python Code Generated: {py_path}")

        # Ask if user wants to run immediately
        response = input("→ Run now? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            self.run_workflow(output_name)

    def generate_workflow(self, description: str, output_name: Optional[str] = None) -> tuple[str, str]:
        """Generate workflow from natural language description"""
        self.logger.info(f"🧠 Analyzing: {description}")
        
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
        
        self.logger.info(f"✅ JSON Workflow Created: {json_path}")
        self.logger.info(f"✅ Python Code Generated: {py_path}")
        
        return str(json_path), str(py_path)
    
    def list_workflows(self):
        """List all saved workflows"""
        workflows = list(self.workflows_dir.glob("*.json"))
        if not workflows:
            self.logger.warning("📭 No workflows found")
            return
        
        self.logger.info("📋 Available Workflows:")
        for workflow in workflows:
            with open(workflow) as f:
                data = json.load(f)
            name = data.get('name', workflow.stem)
            description = data.get('description', 'No description')
            self.logger.info(f"  • {workflow.stem}: {name} - {description}")
    
    def run_workflow(self, workflow_name: str):
        """Run a saved workflow"""
        py_path = self.workflows_dir / f"{workflow_name}.py"
        json_path = self.workflows_dir / f"{workflow_name}.json"

        if not py_path.exists() or not json_path.exists():
            self.logger.error(f"❌ Workflow '{workflow_name}' not found.")
            self.logger.info("Run 'wizflow list' to see available workflows.")
            return
        
        self.logger.info(f"🚀 Running {workflow_name}...")

        # Dependency check before running
        with open(json_path, 'r') as f:
            workflow_data = json.load(f)

        requirements = workflow_data.get("requirements")
        if requirements:
            self.logger.info("🔬 Checking dependencies...")
            missing_packages = self._check_for_missing_packages(requirements)
            if missing_packages:
                self.logger.warning(f"⚠️  This workflow requires the following packages: {', '.join(missing_packages)}")
                response = input("→ Install them now? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    install_result = self.executor.install_dependencies(missing_packages)
                    if not install_result['success']:
                        self.logger.error("❌ Failed to install the following dependencies:")
                        for failed_package in install_result['failed']:
                            self.logger.error(f"  - {failed_package}")
                        return
                else:
                    self.logger.info("Skipping installation. The workflow may fail.")

        result = self.executor.execute_workflow(str(py_path))
        
        if result["success"]:
            self.logger.info("✅ Workflow completed successfully")
            if result["output"]:
                self.logger.info(f"📤 Output: {result['output']}")
        else:
            self.logger.error(f"❌ Workflow '{workflow_name}' failed to execute.")
            self.logger.error("Error details:")
            self.logger.error(result['error'])
            self.logger.info("Try running with the --verbose flag for more detailed output.")
    
    def export_workflow(self, workflow_name: str):
        """Export workflow files to current directory"""
        json_path = self.workflows_dir / f"{workflow_name}.json"
        py_path = self.workflows_dir / f"{workflow_name}.py"
        
        if not json_path.exists():
            self.logger.error(f"❌ Workflow '{workflow_name}' not found")
            return
        
        # Copy to current directory
        import shutil
        shutil.copy2(json_path, f"{workflow_name}.json")
        shutil.copy2(py_path, f"{workflow_name}.py")
        
        self.logger.info(f"📦 Exported {workflow_name}.json and {workflow_name}.py to current directory")

    def _check_for_missing_packages(self, packages: list) -> list:
        """Check if any of the required packages are not installed."""
        import importlib
        missing = []
        # Mapping from package name to import name
        package_to_import_map = {
            "beautifulsoup4": "bs4",
        }

        for package in packages:
            import_name = package_to_import_map.get(package, package)
            try:
                importlib.import_module(import_name)
            except ImportError:
                missing.append(package)
        return missing

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="WizFlow - AI-powered automation workflow generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wizflow generate "When I get an email from boss, summarize and send to WhatsApp"
  wizflow list
  wizflow run my_workflow
  wizflow export my_workflow
  wizflow config openai_key your_openai_api_key
  wizflow credentials set smtp_user my_username
"""
    )

    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output for debugging.')

    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a new workflow from a natural language description")
    generate_parser.add_argument("description", help="Natural language description of the workflow")
    generate_parser.add_argument("--name", "-n", help="Custom name for the workflow")

    # Interactive command
    subparsers.add_parser("interactive", help="Create a new workflow interactively")

    # List command
    subparsers.add_parser("list", aliases=["ls"], help="List all saved workflows")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a saved workflow")
    run_parser.add_argument("workflow_name", help="Name of the workflow to run")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export a workflow to the current directory")
    export_parser.add_argument("workflow_name", help="Name of the workflow to export")

    # Config command
    config_parser = subparsers.add_parser("config", help="Set a configuration value")
    config_parser.add_argument("key", help="Configuration key")
    config_parser.add_argument("value", help="Configuration value")

    # Credentials command
    credentials_parser = subparsers.add_parser("credentials", help="Manage credentials securely")
    cred_subparsers = credentials_parser.add_subparsers(dest="cred_action", help="Credential actions", required=True)
    
    # credentials add
    cred_add_parser = cred_subparsers.add_parser("add", help="Add a new credential")
    cred_add_parser.add_argument("service", help="The service name (e.g., openai)")
    cred_add_parser.add_argument("username", help="The username or key name for the service (e.g., api_key)")

    # credentials get
    cred_get_parser = cred_subparsers.add_parser("get", help="Get a stored credential's value")
    cred_get_parser.add_argument("service", help="The service name")
    cred_get_parser.add_argument("username", help="The username or key name")

    # credentials delete
    cred_delete_parser = cred_subparsers.add_parser("delete", help="Delete a stored credential")
    cred_delete_parser.add_argument("service", help="The service name")
    cred_delete_parser.add_argument("username", help="The username or key name")

    args = parser.parse_args()
    
    logger = setup_logger(args.verbose)

    cli = WizFlowCLI()
    
    try:
        if args.command == "generate":
            json_path, py_path = cli.generate_workflow(args.description, args.name)

            response = input("→ Run now? (y/N): ").strip().lower()
            if response in ["y", "yes"]:
                workflow_name = Path(py_path).stem
                cli.run_workflow(workflow_name)

        elif args.command == "interactive":
            cli.interactive_workflow()

        elif args.command in ["list", "ls"]:
            cli.list_workflows()

        elif args.command == "run":
            cli.run_workflow(args.workflow_name)

        elif args.command == "export":
            cli.export_workflow(args.workflow_name)

        elif args.command == "config":
            cli.config.set(args.key, args.value)
            logger.info(f"✅ Set {args.key} configuration")

        elif args.command == "credentials":
            if args.cred_action == "add":
                password = getpass.getpass(f"Enter password for '{args.username}' on service '{args.service}': ")
                cli.credentials.save_credential(args.service, args.username, password)

            elif args.cred_action == "get":
                password = cli.credentials.get_credential(args.service, args.username)
                if password:
                    logger.info(f"🔑 Credential for '{args.username}' on service '{args.service}' found.")
                    # For security, we don't display the password.
                    # We could show the first few chars or just confirm existence.
                    print("Value exists (hidden for security).")
                else:
                    logger.warning(f"🤷 No credential found for '{args.username}' on service '{args.service}'.")

            elif args.cred_action == "delete":
                # Ask for confirmation before deleting
                confirm = input(f"Are you sure you want to delete the credential for '{args.username}' on service '{args.service}'? (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    cli.credentials.delete_credential(args.service, args.username)
                else:
                    logger.info("Deletion cancelled.")

    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
