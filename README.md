# 🧙‍♂️ WizFlow - AI-Powered Automation CLI Tool

Transform natural language into executable automation workflows with AI! WizFlow is a lightweight Python CLI tool that generates and runs automation scripts from simple English descriptions.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/minimax/wizflow.git
cd wizflow

# Install the package
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

### Setup API Keys (Optional)

For AI-powered workflow generation, configure your preferred LLM provider:

```bash
# OpenAI (recommended)
wizflow --config openai_key=your_openai_api_key

# Or Anthropic Claude
wizflow --config anthropic_key=your_anthropic_api_key
wizflow --config llm_provider=anthropic
```

*Note: WizFlow works without API keys using mock workflows for testing.*

## 💡 Usage Examples

### Generate Workflows

```bash
# Email automation
wizflow "When I get an email from boss, summarize and send to WhatsApp"

# Stock monitoring
wizflow "Check Apple stock price every morning and email me the results"

# Website monitoring
wizflow "Monitor example.com for new articles and email me when there are changes"

# Custom name
wizflow "Send daily weather report to my phone" --name weather_alert
```

### Manage Workflows

```bash
# List all workflows
wizflow list

# Run a specific workflow
wizflow run my_workflow

# Export workflow files
wizflow export my_workflow
```

## 🧰 How It Works

1. **Natural Language Input**: Describe your automation in plain English
2. **AI Generation**: LLM converts description to structured JSON workflow
3. **Code Generation**: Python code is automatically generated from the workflow
4. **Execution**: Run workflows immediately or save for later

### Example Output

```bash
$ wizflow "Send me an email when bitcoin price drops below $30000"

🧠 Analyzing: Send me an email when bitcoin price drops below $30000
🔄 Generating workflow structure...
🔄 Generating Python code...
✅ JSON Workflow Created: workflows/bitcoin_price_alert.json
✅ Python Code Generated: workflows/bitcoin_price_alert.py
→ Run now? (y/N): y
🚀 Running bitcoin_price_alert...
📧 Email sent to user@example.com
✅ Workflow completed successfully
```

## 📋 Supported Automation Types

### Triggers
- **Email**: Monitor incoming emails with filters
- **Schedule**: Cron-based time triggers
- **File**: Watch for file changes
- **Manual**: Run on-demand
- **Webhook**: HTTP endpoint triggers

### Actions
- **Email**: Send/receive emails via SMTP/IMAP
- **Messaging**: WhatsApp, SMS via Twilio
- **Web**: API calls, web scraping
- **Files**: Read, write, process files
- **AI**: Text summarization, analysis
- **Data**: Database queries, spreadsheet updates

## 🔧 Configuration

Configuration is stored in `~/.wizflow/config.json`:

```json
{
  "llm_provider": "openai",
  "openai_key": "your_key_here",
  "openai_model": "gpt-4",
  "anthropic_key": "your_key_here",
  "anthropic_model": "claude-3-sonnet-20240229"
}
```

### Environment Variables

You can also use environment variables:

```bash
export WIZFLOW_OPENAI_KEY=your_key
export WIZFLOW_LLM_PROVIDER=openai
```

## 📁 Project Structure

```
wizflow/
├── cli.py                 # Main CLI interface
├── core/
│   ├── config.py         # Configuration management
│   ├── llm_interface.py  # LLM provider interfaces
│   ├── workflow_builder.py # Workflow generation
│   └── code_generator.py # Python code generation
├── executors/
│   └── workflow_executor.py # Workflow execution
├── examples/             # Example workflows
├── templates/           # Code templates
└── workflows/          # Generated workflows (created at runtime)
```

## 🔒 Security & Safety

- **Sandboxed Execution**: Workflows run in isolated subprocesses
- **Timeout Protection**: Configurable execution timeouts
- **Syntax Validation**: Code validation before execution
- **Dependency Management**: Safe package installation

## 🛠️ Development

### Adding New Action Types

1. Add template to `core/code_generator.py`:
```python
'new_action': '''
# Your action implementation
def your_action(param1, param2):
    # Implementation here
    pass

your_action({param1}, {param2})
'''
```

2. Update imports in `_generate_imports()` if needed

3. Add to LLM system prompt in `llm_interface.py`

### Custom LLM Providers

Extend the `LLMProvider` class:

```python
class CustomProvider(LLMProvider):
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        # Your implementation
        return response
```

## 📦 Dependencies

### Core (Always Required)
- `requests` - HTTP operations

### LLM Providers (Choose One)
- `openai` - GPT models
- `anthropic` - Claude models

### Automation Libraries (Install as Needed)
- `beautifulsoup4` - Web scraping
- `schedule` - Task scheduling
- `twilio` - SMS/WhatsApp
- `gspread` - Google Sheets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

**"No API key found"**
- Configure your API key: `wizflow --config openai_key=your_key`
- Or use environment variables

**"Module not found"**
- Install missing dependencies: `pip install package_name`
- Or let WizFlow auto-install them

**"Workflow execution failed"**
- Check the generated Python file for syntax errors
- Validate workflow with: `wizflow validate my_workflow`

### Getting Help

- Check the examples in `wizflow/examples/`
- Review generated workflows in `workflows/` directory
- Run with `--verbose` for detailed output

## 🌟 Examples Gallery

### Business Automation
```bash
wizflow "When sales report is uploaded, analyze and send summary to team Slack"
wizflow "Monitor competitor pricing daily and alert if changes detected"
```

### Personal Productivity
```bash
wizflow "Backup my photos to cloud storage every Sunday"
wizflow "Send me weather forecast every morning at 7 AM"
```

### Development Workflows
```bash
wizflow "When GitHub issue is created, create Jira ticket and notify team"
wizflow "Monitor server health and send alerts if CPU usage exceeds 80%"
```
