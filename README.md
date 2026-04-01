# Dify Search Skill

AI-powered artwork search using Dify multimodal pipeline.

## Quick Start

1. **Setup configuration:**
```bash
cd ~/.claude/skills/dify-search
cp config/.env.example config/.env
# Edit config/.env with your credentials
```

2. **Setup virtual environment (for using scripts):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests
```

3. **Test the skill:**
```bash
source venv/bin/activate
python scripts/search.py "закат на море"
```

## What This Skill Provides

When you invoke this skill, Claude will have access to:
- 📚 Complete API documentation
- 🔧 All parameter meanings and best practices
- 🎯 Interpretation guidelines for results
- 💡 Common patterns and troubleshooting tips
- 🐍 Helper scripts for testing

## Files Structure

```
dify-search/
├── SKILL.md              # Main skill documentation (read by Claude)
├── README.md             # This file
├── .gitignore           # Git ignore patterns
├── config/
│   ├── .env             # Your credentials (not committed)
│   ├── .env.example     # Template for .env
│   └── README.md        # Setup instructions
├── scripts/
│   └── search.py        # Helper script for searches
├── references/
│   └── api-examples.md  # API examples and use cases
└── cache/               # Cache directory (auto-created)
```

## Usage in Claude Code

Just mention what you want to search:
```
"найди картины с закатом на море"
```

Claude will automatically:
1. Load skill knowledge from SKILL.md
2. Use appropriate parameters for your query
3. Call the Dify API
4. Interpret and present results

## Manual Testing

Use the helper script directly (make sure venv is activated):
```bash
source venv/bin/activate

# Basic search
python scripts/search.py "your query"

# Verbose mode
python scripts/search.py "your query" --verbose

# From Python
python
>>> from scripts.search import search_paintings
>>> result = search_paintings("закат на море", limit=5)
```

## Documentation

- **SKILL.md** - Complete skill documentation for Claude
- **config/README.md** - Configuration setup
- **references/api-examples.md** - API examples and patterns

## Development

To update the skill:
1. Edit `SKILL.md` to change Claude's knowledge
2. Edit `scripts/search.py` to add helper functions
3. Add examples to `references/api-examples.md`

Changes take effect immediately in new Claude sessions.

## Troubleshooting

**"Config file not found"**
- Copy `config/.env.example` to `config/.env`
- Fill in your Dify credentials

**"API Error: 401 Unauthorized"**
- Check `DIFY_API_TOKEN` in `config/.env`
- Verify token is valid in Dify dashboard

**"No results returned"**
- Try lowering `relevance_treshold`
- Check if query is too specific
- Try different `search_mode` values

See SKILL.md → Troubleshooting for more details.
