"""
Interactive Workflow Builder for WizFlow
Guides the user through creating a workflow step-by-step.
"""

from typing import Dict, Any, List
from wizflow.core.plugin_manager import PluginManager
from wizflow.logger import get_logger


class InteractiveWorkflowBuilder:
    """
    A class to handle the interactive creation of a workflow.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.workflow: Dict[str, Any] = {
            "name": "",
            "description": "",
            "requirements": [],
            "trigger": {},
            "actions": []
        }
        self.plugin_manager = PluginManager()

    def build(self) -> Dict[str, Any]:
        """
        Starts the interactive building process and returns the completed workflow.
        """
        self.logger.info("🧙‍♂️ Welcome to the interactive workflow builder!")
        self.logger.info("Let's create a new workflow together.")

        self._get_name_and_description()
        self._get_trigger()
        self._get_actions()

        return self.workflow

    def _get_name_and_description(self):
        """Prompts the user for the workflow's name and description."""
        self.workflow['name'] = input("▶️  What is the name of your workflow? ")
        self.workflow['description'] = input("▶️  Provide a brief description of what it does: ")

    def _get_trigger(self):
        """Guides the user through selecting and configuring a trigger."""
        self.logger.info("\n--- Trigger Setup ---")
        trigger_types = ["manual", "schedule", "email", "webhook", "file"]

        self.logger.info("Available trigger types:")
        for i, t_type in enumerate(trigger_types, 1):
            self.logger.info(f"  {i}. {t_type}")

        try:
            choice = input("▶️  Choose a trigger type (number): ")
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(trigger_types):
                trigger_type = trigger_types[choice_index]
                self.workflow['trigger']['type'] = trigger_type

                if trigger_type == 'schedule':
                    schedule = input("▶️  Enter a cron expression for the schedule (e.g., '0 9 * * *' for 9 AM daily): ")
                    self.workflow['trigger']['schedule'] = schedule
                elif trigger_type == 'email':
                    email_filter = input("▶️  Enter a filter for incoming emails (e.g., 'from:boss@example.com'): ")
                    self.workflow['trigger']['filter'] = email_filter
                elif trigger_type == 'webhook':
                    host = input("▶️  Enter the host for the webhook server (default: localhost): ") or "localhost"
                    port = input("▶️  Enter the port for the webhook server (default: 8080): ") or "8080"
                    path = input("▶️  Enter the path for the webhook (default: /): ") or "/"
                    self.workflow['trigger']['host'] = host
                    self.workflow['trigger']['port'] = int(port)
                    self.workflow['trigger']['path'] = path

                self.logger.info(f"✅ Trigger configured: {trigger_type}")
            else:
                self.logger.warning("⚠️ Invalid choice. Defaulting to 'manual' trigger.")
                self.workflow['trigger']['type'] = 'manual'
        except (ValueError, IndexError):
            self.logger.warning("⚠️ Invalid input. Defaulting to 'manual' trigger.")
            self.workflow['trigger']['type'] = 'manual'


    def _get_actions(self):
        """Guides the user through adding and configuring actions."""
        self.logger.info("\n--- Action Setup ---")
        available_plugins = self.plugin_manager.get_all_action_plugins()
        plugin_names = list(available_plugins.keys())

        # TODO: The parameter and package requirement discovery should be improved in the plugin design.
        # For now, we hardcode them for the interactive builder.
        param_map = {
            "send_email": [("to", "Recipient email"), ("subject", "Email subject"), ("message", "Email body")],
            "log_message": [("message", "Message to log"), ("level", "Log level (e.g., INFO)")],
            "send_whatsapp": [("to", "Recipient WhatsApp number"), ("message", "Message to send")],
        }
        package_map = {
            "send_email": [],
            "log_message": [],
            "send_whatsapp": ["twilio"],
            "web_scrape": ["requests", "beautifulsoup4"],
            "summarize": ["openai"], # or anthropic
        }


        while True:
            self.logger.info("\nAvailable actions:")
            for i, name in enumerate(plugin_names, 1):
                self.logger.info(f"  {i}. {name}")
            self.logger.info(f"  {len(plugin_names) + 1}. Done adding actions")

            try:
                choice = input("▶️  Choose an action to add (number): ")
                choice_index = int(choice) - 1

                if 0 <= choice_index < len(plugin_names):
                    action_name = plugin_names[choice_index]

                    self.logger.info(f"\nConfiguring '{action_name}' action:")
                    action_config = {}

                    if action_name in param_map:
                        for param_key, param_prompt in param_map[action_name]:
                            action_config[param_key] = input(f"▶️  {param_prompt}: ")
                    else:
                        self.logger.warning(f"⚠️  Interactive configuration for '{action_name}' is not fully supported yet. You may need to edit the JSON file manually.")

                    self.workflow['actions'].append({"type": action_name, "config": action_config})

                    # Add requirements
                    if action_name in package_map:
                        self.workflow['requirements'].extend(package_map[action_name])

                    self.logger.info(f"✅ Action '{action_name}' added.")

                elif choice_index == len(plugin_names):
                    if not self.workflow['actions']:
                        self.logger.warning("⚠️  You haven't added any actions.")
                        continue
                    break
                else:
                    self.logger.warning("⚠️ Invalid choice.")
            except (ValueError, IndexError):
                self.logger.warning("⚠️ Invalid input.")

        # Remove duplicate requirements
        if self.workflow['requirements']:
            self.workflow['requirements'] = sorted(list(set(self.workflow['requirements'])))
