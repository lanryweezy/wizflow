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

import subprocess
from .core.llm_interface import LLMInterface
from .core.workflow_builder import WorkflowBuilder
from .core.code_generator import CodeGenerator
from .executors.workflow_executor import WorkflowExecutor
from .core.config import Config
from .core.credentials import CredentialManager
from .core.plugin_manager import PLUGIN_REPOSITORY
from .tui import WorkflowEditor


class WizFlowCLI:
    """Main CLI application class"""
    
    def __init__(self):
        self.config = Config()
        self.generator = CodeGenerator()
        self.llm = LLMInterface(self.config, self.generator.plugin_manager)
        self.builder = WorkflowBuilder(self.llm)
        self.executor = WorkflowExecutor()
        self.credentials = CredentialManager()
        self.workflows_dir = Path("workflows")
        self.templates_dir = Path("templates")
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

        # Dependency check before running
        print("🔬 Analyzing dependencies...")
        analysis = self.executor.dry_run(str(py_path))
        if analysis['success'] and analysis['analysis'].get('potential_issues'):
            missing_packages = self._check_for_missing_packages(analysis['analysis']['imports'])
            if missing_packages:
                print(f"⚠️  This workflow may require the following packages: {', '.join(missing_packages)}")
                response = input("→ Install them now? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    install_result = self.executor.install_dependencies(missing_packages)
                    if not install_result['success']:
                        print(f"❌ Failed to install dependencies: {install_result['failed']}")
                        return
                else:
                    print("Skipping installation. The workflow may fail.")

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

    def _check_for_missing_packages(self, imports: list) -> list:
        """Check if any of the required packages are not installed."""
        import importlib
        missing = []
        # We only care about top-level packages that are likely to be installed via pip
        potential_packages = {'requests', 'twilio', 'beautifulsoup4', 'gspread', 'schedule'}

        for imp in imports:
            # e.g., "bs4" is the module name for "beautifulsoup4"
            if imp == 'bs4': imp = 'beautifulsoup4'

            if imp in potential_packages:
                try:
                    importlib.import_module(imp)
                except ImportError:
                    missing.append(imp)
        return missing

    def manage_credentials(self, args: list):
        """Manage user credentials"""
        if not args or len(args) < 2:
            print("❌ Invalid credentials command. Use: wizflow --credentials set <key> <value>")
            return

        action = args[0].lower()
        if action == 'set':
            if len(args) != 3:
                print("❌ Invalid 'set' command. Use: --credentials set <key> <value>")
                return
            key, value = args[1], args[2]
            self.credentials.set_credential(key, value)
            print(f"✅ Credential '{key}' set.")
        else:
            print(f"❌ Unknown credentials command: {action}")

    def manage_plugins(self, args: list):
        """Manage plugins"""
        if not args:
            print("❌ Invalid plugins command. Use: wizflow --plugins list")
            return

        action = args[0].lower()
        if action == 'list':
            self.list_plugins()
        elif action == 'install':
            if len(args) < 2:
                print("❌ Invalid 'install' command. Use: --plugins install <plugin-name>")
                return
            plugin_name = args[1]
            self.install_plugin(plugin_name)
        else:
            print(f"❌ Unknown plugins command: {action}")

    def install_plugin(self, plugin_name: str):
        """Install a plugin from the repository."""
        if plugin_name not in PLUGIN_REPOSITORY:
            print(f"❌ Plugin '{plugin_name}' not found in repository.")
            return

        plugin_url = PLUGIN_REPOSITORY[plugin_name]
        plugins_dir = Path("wizflow") / "plugins"
        target_dir = plugins_dir / plugin_name

        if target_dir.exists():
            print(f"⚠️  Plugin '{plugin_name}' is already installed.")
            return

        print(f"Installing '{plugin_name}' from {plugin_url}...")
        try:
            subprocess.run(
                ["git", "clone", plugin_url, str(target_dir)],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ Plugin '{plugin_name}' installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install plugin '{plugin_name}'.")
            print(f"   Error: {e.stderr}")
        except FileNotFoundError:
            print("❌ 'git' command not found. Please install Git and try again.")


    def list_plugins(self):
        """List all installed plugins."""
        print("🔌 Installed Plugins:")
        plugins = self.generator.plugin_manager.get_all_plugins()
        if not plugins:
            print("  No plugins found.")
            return

        for name, plugin in plugins.items():
            print(f"  • {name}")

    def manage_templates(self, args: list):
        """Handle template commands."""
        if not args:
            print("❌ Invalid templates command. Use: --templates list or --templates use <template-name>")
            return

        action = args[0].lower()
        if action == 'list':
            self.list_templates()
        elif action == 'use':
            if len(args) < 2:
                print("❌ Invalid 'use' command. Use: --templates use <template-name>")
                return
            template_name = args[1]
            self.use_template(template_name)
        else:
            print(f"❌ Unknown templates command: {action}")

    def list_templates(self):
        """List available workflow templates."""
        manifest_path = self.templates_dir / "manifest.json"
        if not manifest_path.exists():
            print("No templates found.")
            return

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        print("Available Templates:")
        for template in manifest.get('templates', []):
            print(f"  • {template['name']}: {template['description']}")

    def use_template(self, template_name: str):
        """Use a workflow template."""
        manifest_path = self.templates_dir / "manifest.json"
        if not manifest_path.exists():
            print("No templates found.")
            return

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        template_info = next((t for t in manifest.get('templates', []) if t['name'] == template_name), None)

        if not template_info:
            print(f"❌ Template '{template_name}' not found.")
            return

        template_path = self.templates_dir / f"{template_name}.json"
        if not template_path.exists():
            print(f"❌ Template file not found for '{template_name}'.")
            return

        workflow_json = json.loads(template_path.read_text())

        # Generate Python code from the template's workflow
        python_code = self.generator.generate_code(workflow_json)

        # Save files to user's workflows directory
        json_path = self.workflows_dir / f"{template_name}.json"
        py_path = self.workflows_dir / f"{template_name}.py"

        with open(json_path, 'w') as f:
            json.dump(workflow_json, f, indent=2)

        with open(py_path, 'w') as f:
            f.write(python_code)

        print(f"✅ Template '{template_name}' created in your workflows directory.")
        print(f"  - {json_path}")
        print(f"  - {py_path}")
        print(f"To run it, use: wizflow run {template_name}")


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
    parser.add_argument('--edit', help='Edit a workflow interactively')
    parser.add_argument('--list', '-l', action='store_true', help='List all saved workflows')
    parser.add_argument('--export', '-e', help='Export a workflow to current directory')
    parser.add_argument('--config', '-c', help='Set configuration (e.g., --config openai_key=your_key)')
    parser.add_argument('--credentials', nargs='+', help='Manage credentials (e.g., --credentials set smtp_user myuser)')
    parser.add_argument('--plugins', nargs='+', help='Manage plugins (e.g., --plugins list)')
    parser.add_argument('--templates', nargs='+', help='Work with workflow templates (e.g., --templates list)')
    
    args = parser.parse_args()
    
    cli = WizFlowCLI()
    
    try:
        if args.list:
            cli.list_workflows()
        elif args.run:
            cli.run_workflow(args.run)
        elif args.edit:
            workflow_path = cli.workflows_dir / f"{args.edit}.json"
            if not workflow_path.exists():
                print(f"❌ Workflow '{args.edit}' not found. Cannot edit.")
                return
            editor = WorkflowEditor(str(workflow_path))
            editor.run()
        elif args.export:
            cli.export_workflow(args.export)
        elif args.config:
            key, value = args.config.split('=', 1)
            cli.config.set(key, value)
            print(f"✅ Set {key} configuration")
        elif args.credentials:
            cli.manage_credentials(args.credentials)
        elif args.plugins:
            cli.manage_plugins(args.plugins)
        elif args.templates:
            cli.manage_templates(args.templates)
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
