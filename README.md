# fdu-utils
FDU Utils

## Setup

### Environment Setup

1. Create a virtual environment with uv:
```bash
uv venv
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Install Claude Code.

5. Add the WhatsApp MCP server:
```bash
# Add the WhatsApp MCP server
claude mcp add whatsapp -- whatsapp-mcp

# List existing MCP servers - Validate that the server is running
claude mcp list
```

6. Start the Claude Code:
```bash
claude
```
