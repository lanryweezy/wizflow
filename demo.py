#!/usr/bin/env python3
"""
Demo script for WizFlow CLI Tool
Tests the main functionality without requiring API keys
"""

import sys
import os
from pathlib import Path

# Add the wizflow package to the path
sys.path.insert(0, str(Path(__file__).parent))

from wizflow.cli import WizFlowCLI


def demo_workflow_generation():
    """Demonstrate workflow generation"""
    print("🧙‍♂️ WizFlow Demo - Workflow Generation")
    print("=" * 50)
    
    # Create CLI instance
    cli = WizFlowCLI()
    
    # Test descriptions
    test_descriptions = [
        "When I get an email from boss, summarize and send to WhatsApp",
        "Check Apple stock price every morning and email me the results",
        "Send me a weather forecast every Friday at 5 PM"
    ]
    
    for i, description in enumerate(test_descriptions, 1):
        print(f"\n📝 Test {i}: {description}")
        print("-" * 60)
        
        try:
            json_path, py_path = cli.generate_workflow(description, f"demo_workflow_{i}")
            print(f"✅ Generated: {json_path}")
            print(f"✅ Generated: {py_path}")
            
            # Show a snippet of the generated code
            with open(py_path) as f:
                lines = f.readlines()
                print(f"\n📄 Code preview (first 10 lines):")
                for line_num, line in enumerate(lines[:10], 1):
                    print(f"  {line_num:2d}: {line.rstrip()}")
                if len(lines) > 10:
                    print(f"     ... ({len(lines) - 10} more lines)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Demo completed!")
    print(f"📁 Check the 'workflows' directory for generated files")


def demo_workflow_management():
    """Demonstrate workflow management features"""
    print("\n🛠️  WizFlow Demo - Workflow Management")
    print("=" * 50)
    
    cli = WizFlowCLI()
    
    # List workflows
    print("\n📋 Listing workflows:")
    cli.list_workflows()
    
    # Validate a workflow (if any exist)
    workflows_dir = Path("workflows")
    if workflows_dir.exists():
        py_files = list(workflows_dir.glob("*.py"))
        if py_files:
            test_file = py_files[0]
            print(f"\n🔍 Validating: {test_file.name}")
            
            result = cli.executor.validate_script(str(test_file))
            if result["valid"]:
                print("✅ Script validation passed")
            else:
                print(f"❌ Script validation failed: {result['error']}")
            
            # Dry run analysis
            print(f"\n🔬 Analyzing: {test_file.name}")
            analysis = cli.executor.dry_run(str(test_file))
            if analysis["success"]:
                print("📊 Analysis results:")
                for key, value in analysis["analysis"].items():
                    if value:
                        print(f"  • {key}: {value}")
            else:
                print(f"❌ Analysis failed: {analysis['error']}")


if __name__ == "__main__":
    print("🧙‍♂️ WizFlow CLI Tool - Complete Demo")
    print("🔧 This demo works without API keys using mock responses")
    print()
    
    try:
        # Demo workflow generation
        demo_workflow_generation()
        
        # Demo management features
        demo_workflow_management()
        
        print("\n" + "=" * 60)
        print("🎯 Next Steps:")
        print("1. Configure API keys: wizflow --config openai_key=your_key")
        print("2. Try real automation: wizflow \"your automation description\"")
        print("3. Run workflows: wizflow run workflow_name")
        print("4. Check examples in wizflow/examples/")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)
