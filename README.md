# Dify Search Skill

AI-powered artwork search using Dify multimodal pipeline.

## Installation

### For new agents/computers

1. **Clone or copy skill to skills directory:**
```bash
# If you have git repository
git clone <repository-url> ~/.claude/skills/dify-search

# OR copy from existing installation
cp -r /path/to/dify-search ~/.claude/skills/dify-search
```

2. **Install dependencies (optional for manual script testing):**
```bash
cd ~/.claude/skills/dify-search
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Note:** Dependencies install automatically on first script run. Manual installation is only needed for development.

3. **Done!** On first use, script will prompt for credentials.

### For Claude Code

Skill auto-loads from `~/.claude/skills/dify-search/SKILL.md`

No configuration needed - Claude will use the skill automatically when you mention artwork search tasks.

## Quick Start

**Option 1: Auto-setup (Recommended)**

Just run the script - dependencies and config setup happen automatically:
```bash
cd ~/.claude/skills/dify-search
python scripts/search.py "закат на море"
# Will auto-install dependencies and prompt for:
# - DIFY_BASE_URL (e.g., https://your-dify-instance.com)
# - DIFY_API_TOKEN (e.g., app-xxxxx)
```

Get credentials from: Dify → App Settings → API Access → API Key

**Option 2: Manual config setup**

If you prefer to set up credentials manually:
```bash
cd ~/.claude/skills/dify-search
cp config/.env.example config/.env
nano config/.env
```

Edit `.env` with your credentials:
```bash
DIFY_BASE_URL=https://your-dify-instance.com
DIFY_API_TOKEN=app-your-token-here
```

**Security note:** Never commit `.env` to git! It's already in `.gitignore`.

**For Claude Code skill usage:**

No setup needed! Just invoke:
```
/dify-search найди картины с закатом
```

Claude will handle everything automatically.

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
├── README.md             # This file (installation & usage)
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore patterns
├── config/
│   ├── .env             # Your credentials (not committed)
│   └── .env.example     # Template for .env
├── scripts/
│   ├── search.py        # Main search script with CLI parameters
│   ├── quick_compare.py # Compare CLIP models for single query
│   ├── compare_models.py # Compare models on 10 test queries
│   └── test_refiner.py  # Test GPT query refiner
├── references/
│   └── api-examples.md  # API examples and use cases
└── cache/               # Cache directory (auto-created)
```

## Scripts Overview

### search.py
**Purpose:** Main search interface with full parameter control

**When to use:**
- Regular artwork search
- Testing specific parameter combinations
- Production searches with custom settings

**User request examples:**
- "найди картины с закатом"
- "найди портреты, используй clip-base"
- "поиск абстракций, показать только 5 результатов"

### quick_compare.py
**Purpose:** Quick A/B comparison of CLIP models for ONE query

**When to use:**
- Testing which model works better for specific query
- Quick quality check before production
- Debugging model differences

**User request examples:**
- "сравни clip-large и clip-base по запросу 'лиминальное пространство'"
- "какая модель лучше для запроса 'игра света и тени'?"
- "протестируй обе CLIP модели на 'закат над морем'"

### compare_models.py
**Purpose:** Comprehensive comparison on 10 predefined test queries

**When to use:**
- Evaluating overall model performance
- Quality assurance after workflow changes
- Generating comparison reports

**User request examples:**
- "запусти полное сравнение CLIP моделей"
- "протестируй обе модели на всех тестовых запросах"
- "сделай бенчмарк clip-large vs clip-base"

### test_refiner.py
**Purpose:** Test GPT query refiner's author extraction and query processing

**When to use:**
- Debugging query refinement
- Testing author name extraction
- Evaluating GPT refiner quality

**User request examples:**
- "протестируй, как refiner обрабатывает 'закат Айвазовского'"
- "проверь извлечение автора из запроса"
- "как GPT refiner преобразует запросы с фамилиями художников?"

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

### Basic Search

Use the search script with CLI parameters:
```bash
# Basic search (uses defaults: clip-large, limit=20, multimodal reranking)
venv/bin/python scripts/search.py "закат на море"

# Verbose mode with debug info
venv/bin/python scripts/search.py "закат на море" --verbose

# With specific CLIP model
venv/bin/python scripts/search.py "закат на море" --clip-model clip-base

# Custom parameters (⚠️ changing limit affects reranking!)
venv/bin/python scripts/search.py "закат" --limit 10 --search-mode both

# See all options
venv/bin/python scripts/search.py --help
```

### CLIP Model Comparison

**Quick comparison for single query** (recommended for testing):
```bash
# Compare models for one specific query
venv/bin/python scripts/quick_compare.py "сумеречное лиминальное пространство"

# Custom query
venv/bin/python scripts/quick_compare.py "ваш запрос"
```

**Full comparison suite** (tests 10 predefined queries):
```bash
# Run all test queries through both models
venv/bin/python scripts/compare_models.py
# Saves results to comparison_results.json
```

### Testing Query Refiner

Test how GPT refiner extracts authors and processes queries:
```bash
# Test single query
venv/bin/python scripts/test_refiner.py "закат Айвазовского"

# Test multiple queries
venv/bin/python scripts/test_refiner.py "закат Айвазовского" "девушки в шляпах Андрея Елецкого"
# Saves results to test_results.json
```

### From Python

```python
from scripts.search import search_paintings

# Basic search
result = search_paintings("закат на море")

# With custom parameters
result = search_paintings(
    query="закат",
    clip_model="clip-large",
    search_mode="image",
    limit=20,
    jina_reranking="multimodal"
)
```

## Documentation

- **SKILL.md** - Complete skill documentation for Claude
- **requirements.txt** - Python dependencies list
- **references/api-examples.md** - API examples and patterns

## Development

To update the skill:
1. Edit `SKILL.md` to change Claude's knowledge
2. Edit `scripts/search.py` to add helper functions
3. Add examples to `references/api-examples.md`

Changes take effect immediately in new Claude sessions.

## Comparing CLIP Models

### CRITICAL: Visual Evaluation is Required

**Never compare CLIP models using only similarity scores!** You must visually inspect actual images to evaluate quality.

#### Why Scores Are Misleading

- **Higher score ≠ Better result**: A model can assign 0.677 to an irrelevant abstract painting while giving 0.537 to a perfect match
- **Quantity ≠ Quality**: More results doesn't mean better understanding of the query
- **Reranking can amplify errors**: Jina reranker works on top of CLIP results - garbage in, garbage out

#### Proper Comparison Methodology

1. **Run both models** on the same query set
2. **Download top 3-5 images** from each model's results
3. **Visually inspect** which images better match the query intent
4. **Consider conceptual understanding**, not just literal matching

#### Example: "сумеречное лиминальное пространство" (twilight liminal space)

**clip-base results:**
- Top result (0.677): Abstract painting with red lines ❌ - **Completely irrelevant**
- Found 8 results total
- Matched literally on "сумерки" (twilight) keyword, ignored "liminal space" concept

**clip-large results:**
- Top result (0.537): Twilight landscape with trees - Not perfect but closer
- #3 (0.517): Archway with couple - **Best match!** ✅ Archway = liminal/transitional space
- Found only 3 results, but more conceptually relevant
- **Winner on this query** - understood the abstract concept better

#### Example: "игра света и тени" (play of light and shadow)

**clip-large results:**
- Top result (0.823): "Satyr and Nymph" with dramatic chiaroscuro ✅
- Understood as artistic technique (light/shadow contrast)
- Found works with **dramatic lighting** as artistic element

**clip-base results:**
- Top result (0.819): "Walking Light" - sunlight through trees
- Literal interpretation: where there's light, there's shadow
- Found **literal shadows**, not artistic light play

**Winner: clip-large** - deeper artistic understanding

#### Using the Comparison Scripts

**For quick single-query comparison:**
```bash
cd ~/.claude/skills/dify-search
venv/bin/python scripts/quick_compare.py "your query"
```

This script:
- Compares both models on ONE specific query
- Shows side-by-side results immediately
- Faster for targeted testing
- **Still requires visual image inspection!**

**For comprehensive multi-query comparison:**
```bash
cd ~/.claude/skills/dify-search
venv/bin/python scripts/compare_models.py
```

This script:
- Tests 10 predefined queries with both models
- Saves results to `comparison_results.json`
- Prints detailed comparison report
- **But you still need to manually check images!**

#### When to Use Which Model

**Use clip-large when:**
- Query involves abstract/artistic concepts
- You need deeper semantic understanding
- Willing to trade some recall for precision
- Queries like: "игра света и тени", "драматичное освещение", conceptual searches

**Use clip-base when:**
- Query is concrete and visual
- Need faster results (slightly)
- Query has clear visual features
- Queries like: "закат над водой", "отражения в воде", "зеленый пейзаж"

**Default recommendation:** Start with **clip-large** for better semantic understanding, fall back to clip-base only if results are poor.

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
