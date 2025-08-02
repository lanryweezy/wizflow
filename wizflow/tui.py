"""
Text-based User Interface (TUI) for editing workflows.
"""

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings


class WorkflowEditor:
    """
    An interactive TUI for creating and editing WizFlow workflows.
    """
    def __init__(self, workflow_path: str):
        self.workflow_path = workflow_path
        self.workflow_data = self._load_workflow()

        # Key bindings
        kb = KeyBindings()
        @kb.add('c-q')
        def _(event):
            """Quit the application."""
            event.app.exit()

        # Main application layout
        self.app = Application(
            layout=Layout(
                HSplit([
                    Window(FormattedTextControl(f"Editing: {self.workflow_path}")),
                    Window(FormattedTextControl("Press Ctrl-Q to quit.")),
                ])
            ),
            key_bindings=kb,
            full_screen=True
        )

    def _load_workflow(self) -> dict:
        """Loads the workflow data from the given path."""
        import json
        from pathlib import Path

        path = Path(self.workflow_path)
        if not path.exists():
            return {"name": "New Workflow", "actions": []}

        with open(path, 'r') as f:
            return json.load(f)

    def run(self):
        """Run the TUI application."""
        self.app.run()
