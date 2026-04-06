---
name: dify-search
description: |
  Поиск картин в галерее через Dify AI pipeline.
  Мультимодальный поиск (текст + изображение) с CLIP embeddings,
  умный рефайнер запросов, Jina реранкинг.
  Используй для: поиска картин по описанию, визуальному сходству,
  тестирования поисковых алгоритмов, анализа релевантности.
triggers:
  - поиск картин
  - search paintings
  - dify pipeline
  - тест поиска
---

# dify-search

AI-powered artwork search pipeline using Dify workflow with multimodal search capabilities.

## What This Application Does

This is a **multimodal artwork search system** that combines:
- 🔍 **Query refinement** - GPT refines user queries for better search
- 🎨 **CLIP image embeddings** - Visual similarity search
- 📝 **Text embeddings** - Semantic text search
- 🎯 **Jina reranking** - Multimodal reranking for better results
- 💎 **Rich metadata** - Author, price, dimensions, visual descriptions

**Pipeline flow:**
1. User query → GPT query refiner (optional)
2. Generate embeddings (CLIP + text)
3. Vector search in Qdrant
4. Jina multimodal reranking (optional)
5. Format results as markdown with images

## Quick Start for Claude Code

When this skill is invoked with a search query, execute:

```bash
cd ~/.claude/skills/dify-search && venv/bin/python scripts/search.py "USER_QUERY"
```

**⚠️ CRITICAL - Default Parameters:**
```python
use_refiner=True
clip_model="clip-large"
search_mode="image"
jina_reranking="multimodal"
relevance_treshold=0.5
limit=20  # CRITICAL: Changing this drastically alters reranking results!
clip_fallback_treshold=0.0
```

**Important:**
- Always use `venv/bin/python` (not system python)
- Quote the query to preserve spaces
- **DO NOT change default parameters without explicit user request**
- **Especially `limit` - it critically affects reranking quality!**
- Don't switch to `clip-base` unless you have evidence it performs better for your query

**Example:**
```bash
cd ~/.claude/skills/dify-search && venv/bin/python scripts/search.py "девушки в шляпах Андрея Елецкого"
```

**Output includes:**
- Refined query (GPT-processed English version)
- Top N results with images, similarity scores, metadata
- Performance metrics (elapsed time, tokens, steps)

**Available CLI options:**
```bash
# All options (use defaults unless user explicitly requests changes!)
venv/bin/python scripts/search.py "query" \
  --clip-model clip-large \      # clip-large or clip-base
  --search-mode image \           # image, text, both, none
  --jina-reranking multimodal \   # multimodal, text, none
  --limit 20 \                    # CRITICAL: affects reranking!
  --relevance-threshold 0.5 \     # 0-1 threshold
  --no-refiner \                  # disable GPT refiner
  --verbose                       # show debug info
```

**For Claude Code - Error Prevention Rules:**

1. **NEVER change parameters without explicit user request**
   - Especially `--limit` - it drastically changes results!
   - Use defaults unless user asks for specific values

2. **When comparing models:**
   - Use identical parameters for both models
   - Only change `--clip-model` between runs
   - Use comparison script: `venv/bin/python scripts/compare_models.py`

3. **🚨 ALWAYS DOWNLOAD AND VIEW IMAGES WHEN COMPARING MODELS! 🚨**
   - **NEVER compare models by scores alone!**
   - Download top 3-5 images from each model using WebFetch/Read tools
   - Visually assess which images actually match the query
   - Scores are misleading - a model with lower scores may have better results!
   - See "Comparing CLIP Models" section for detailed methodology

4. **When user asks to compare:**
   - Ask if they want specific parameters or use defaults
   - If unsure - use defaults!
   - **MANDATORY: Download and view images before making conclusions**

## Config

API credentials stored in `config/.env`:
```bash
DIFY_BASE_URL=https://your-dify-instance.com
DIFY_API_TOKEN=app-your-token-here
```

**Note:** Actual credentials are in `config/.env` file (not committed to git).

See `config/README.md` for setup instructions.

## API Connection

### Endpoint
```
POST {DIFY_BASE_URL}/v1/workflows/run
```

### Headers
```
Authorization: Bearer {DIFY_API_TOKEN}
Content-Type: application/json
```

### Request Format
```json
{
  "inputs": {
    "query": "...",
    "use_refiner": true,
    "clip_model": "clip-large",
    "search_mode": "image",
    "jina_reranking": "multimodal",
    "relevance_treshold": 0.5,
    "limit": 20,
    "clip_fallback_treshold": 0.0
  },
  "response_mode": "blocking",
  "user": "user-id"
}
```

## Input Fields

### 1. `query` (string, required)
**Поисковый запрос пользователя**

- Может быть на русском или английском
- Описывает что искать: "закат на море", "портрет женщины", "зимний пейзаж"
- Если `use_refiner=true`, GPT улучшит запрос для CLIP

**Examples:**
- "закат на море" → GPT refines to "sunset over the sea"
- "картина с цветами" → "painting with flowers"
- "абстракция синего цвета" → "blue abstract art"

### 2. `use_refiner` (boolean, default: true)
**Использовать GPT для улучшения запроса**

- `true` - запрос проходит через GPT для оптимизации под CLIP
- `false` - используется оригинальный запрос

**When to use:**
- ✅ Use `true` for natural language queries
- ❌ Use `false` if you already have optimized CLIP prompts

### 3. `clip_model` (select, default: "clip-large")
**Модель CLIP для image embeddings**

Options:
- `"clip-base"` - openai/clip-vit-base-patch32 (literal matching, good for concrete visuals)
- `"clip-large"` - openai/clip-vit-large-patch14 (better semantic understanding, handles abstract concepts)

**When to use:**
- **Use `clip-large` by default** - better at abstract/artistic queries, deeper understanding
- Use `clip-base` only if clip-large gives poor results on very literal visual queries
- ⚠️ **Don't compare models by scores alone!** See "Comparing CLIP Models" section for proper methodology

**Examples:**
- `clip-large` wins: "игра света и тени" (understands chiaroscuro as technique)
- `clip-base` wins: "зеленый пейзаж" (literal color-based search)
- Both equal: "закат над водой" (concrete visual)

### 4. `search_mode` (select, default: "image")
**Тип векторного поиска**

Options:
- `"none"` - No vector search (only if you want text-only without embeddings)
- `"image"` - Search by CLIP image embeddings (visual similarity)
- `"text"` - Search by text embeddings (semantic meaning)
- `"both"` - Hybrid search (combines image + text vectors)

**When to use:**
- `"image"` - Visual queries ("sunset", "portrait", colors/composition)
- `"text"` - Semantic queries (mood, genre, objects mentioned in descriptions)
- `"both"` - Complex queries that need both visual and semantic matching
- `"none"` - Only for debugging/special cases

### 5. `jina_reranking` (select, default: "multimodal")
**Тип реранкинга результатов**

Options:
- `"none"` - No reranking (use raw vector similarity scores)
- `"text"` - Text-based reranking only
- `"multimodal"` - Jina multimodal reranking (considers both image and text)

**When to use:**
- `"multimodal"` - Best quality (recommended for production)
- `"text"` - When you only care about semantic relevance
- `"none"` - For debugging or when you trust vector scores

**Impact on results:**
- Reranking can significantly change result order
- Filters results by `relevance_treshold`
- Check `output.error_1` field to see if reranking succeeded

### 6. `relevance_treshold` (number, default: 0.5)
**Порог релевантности для реранкера (0-1)**

- Only applies when `jina_reranking != "none"`
- Results with reranking score < threshold are filtered out
- Higher threshold = fewer but more relevant results

**Recommended values:**
- `0.3-0.4` - Permissive (more results, some less relevant)
- `0.5` - Balanced (default)
- `0.6-0.7` - Strict (fewer results, high quality)

### 7. `limit` (number, default: 20)
**Количество результатов для вывода**

- How many artworks to return
- Vector search fetches more candidates, reranker filters to this limit
- Max recommended: 50 (for performance)

### 8. `clip_fallback_treshold` (number, default: 0.0)
**Порог CLIP fallback - отключает реранкинг если все CLIP scores ниже порога**

- Advanced parameter for handling low-quality matches
- If all CLIP scores < threshold, reranking is skipped
- `0.0` = disabled (always try reranking)

**When to use:**
- Set to `0.3-0.5` if you want to skip reranking for very poor matches
- Keep at `0.0` unless you have specific needs

## Response Format

```json
{
  "task_id": "uuid",
  "workflow_run_id": "uuid",
  "data": {
    "status": "succeeded",
    "outputs": {
      "english_clip_query": "refined query for CLIP",
      "output": "markdown with results",
      "error": "",
      "error_1": ""
    },
    "elapsed_time": 11.7,
    "total_tokens": 5015,
    "total_steps": 11
  }
}
```

### Key Output Fields

#### `outputs.english_clip_query`
- The refined English query used for CLIP search
- Shows what GPT extracted from user's query

#### `outputs.output`
- Main result: markdown-formatted artwork list
- Includes:
  - Found count and search parameters
  - Each artwork: name, author, similarity score, price, dimensions, description, image URL

#### `outputs.error` / `outputs.error_1`
- Error messages if something failed
- `error_1` often shows reranking status (e.g., "jina_success" or error)

#### Performance Metrics
- `elapsed_time` - Total execution time (seconds)
- `total_tokens` - LLM tokens used
- `total_steps` - Workflow steps executed

## Interpreting Results

### Similarity Scores
Results show **similarity scores** (0-1):
- `0.95-1.0` 🎯 - Excellent match
- `0.90-0.95` 🎯 - Very good match
- `0.85-0.90` - Good match
- `0.80-0.85` - Acceptable match
- `< 0.80` - Weak match (consider adjusting query)

**Note:** Scores depend on `search_mode`:
- `"image"` mode: CLIP visual similarity
- With `jina_reranking`: Jina multimodal relevance score

### Reranking Status
Check `error_1` field:
- `"jina_success"` - Reranking worked
- Empty or error message - Reranking failed, using vector scores

### When Results Are Poor
If you get irrelevant results:
1. Check `english_clip_query` - is it what you wanted?
2. Try different `search_mode` (text vs image vs both)
3. Adjust `relevance_treshold` (lower if too few results)
4. Try `use_refiner=false` if GPT misunderstood the query
5. Check similarity scores - maybe query is too abstract

## Usage Examples

### Example 1: Basic Visual Search
```python
from scripts.search import search_paintings

results = search_paintings(
    query="закат на море",
    search_mode="image",
    limit=10
)
```

### Example 2: Semantic Text Search
```python
results = search_paintings(
    query="грустная атмосфера, осень",
    search_mode="text",
    jina_reranking="text",
    limit=5
)
```

### Example 3: Hybrid Search with Strict Filtering
```python
results = search_paintings(
    query="портрет женщины в красном",
    search_mode="both",
    jina_reranking="multimodal",
    relevance_treshold=0.7,
    limit=15
)
```

### Example 4: Fast Search Without Refiner
```python
results = search_paintings(
    query="mountain landscape",
    use_refiner=False,
    clip_model="clip-base",
    search_mode="image",
    jina_reranking="none",
    limit=20
)
```

## Philosophy

### 1. Multimodal is Better
Combining visual (CLIP) and semantic (text) search gives best results for complex queries.

### 2. Trust the Reranker
Jina multimodal reranking significantly improves result quality. Use `jina_reranking="multimodal"` by default.

### 3. Refiner Knows CLIP
GPT query refiner is trained to optimize prompts for CLIP. Trust it unless you're an expert in CLIP prompting.

### 4. Iterate on Parameters
If results are poor, don't immediately blame the model:
- Try different `search_mode`
- Adjust `relevance_treshold`
- Check what GPT refined your query to
- Experiment with `use_refiner=false`

### 5. Performance vs Quality
- `clip-large` + `multimodal reranking` = best quality (~10-15s)
- `clip-base` + `no reranking` = fast but lower quality (~2-5s)
- Choose based on your use case

## Common Patterns

### Pattern 1: Visual Similarity ("Find similar to this")
```python
search_paintings(
    query="abstract geometric shapes, colorful",
    search_mode="image",
    clip_model="clip-large",
    jina_reranking="none"  # Pure visual similarity
)
```

### Pattern 2: Semantic Search ("Find by meaning")
```python
search_paintings(
    query="одиночество, меланхолия, пустынный пейзаж",
    search_mode="text",
    jina_reranking="text"
)
```

### Pattern 3: Best Quality Search
```python
search_paintings(
    query="зимний вечер в городе",
    search_mode="both",
    clip_model="clip-large",
    jina_reranking="multimodal",
    relevance_treshold=0.6
)
```

### Pattern 4: Debug Mode
```python
search_paintings(
    query="your query",
    use_refiner=False,  # See raw query behavior
    jina_reranking="none",  # See raw vector scores
    limit=50
)
```

## Testing Strategy

When testing the pipeline:

1. **Start Simple** - Test with clear, unambiguous queries
2. **Check Refinement** - Look at `english_clip_query` to understand what GPT did
3. **Compare Modes** - Try same query with different `search_mode` values
4. **Validate Scores** - Manually check if high-scored results actually match the query
5. **Edge Cases** - Test abstract queries, multi-concept queries, negations

## Comparing CLIP Models

### 🚨 CRITICAL: Visual Evaluation is MANDATORY 🚨

**⚠️ NEVER EVER compare CLIP models using only similarity scores!**

**For Claude Code agents: This is a BLOCKING REQUIREMENT:**
1. **ALWAYS download and view images** using Read/WebFetch tools
2. **NEVER make conclusions based on scores alone**
3. **ALWAYS compare actual visual content** of top 3-5 results from each model

When evaluating which CLIP model performs better, you MUST:
1. Download and visually inspect the actual images (use Read tool or curl + Read)
2. Compare how well they match the query intent
3. Assess conceptual understanding, not just literal matching
4. Check for false positives (irrelevant results with high scores)

### Why Scores Are Misleading

Real examples from testing:

**Query: "сумеречное лиминальное пространство" (twilight liminal space)**

- `clip-base` top result: **0.677 score**
  - Image: Abstract painting with red lines on green/yellow background
  - **Completely irrelevant!** ❌ No liminal space concept at all
  - Matched literally on "сумерки" keyword, ignored "liminal space"

- `clip-large` result #3: **0.517 score** (lower!)
  - Image: Archway with couple at twilight
  - **Perfect match!** ✅ Archway = transitional/liminal space
  - Understood the abstract concept correctly

**Lesson:** Lower score found the better result! Don't trust numbers alone.

---

**Query: "мотоцикл" (motorcycle)**

- `clip-large` unique results included:
  - ❌ "Всадник" - sculpture of rider on a **HORSE** (not motorcycle!)
  - ❌ "Саксофон" - woman on a **BICYCLE** playing saxophone
  - ❌ "Велосипедист" - cyclist sculpture
  - ❌ "Русское поле" - horse riders
  - **Problem:** Understood "motorcycle" too broadly as "any vehicle with rider"

- `clip-base` filtered correctly:
  - ✅ Found unique result "Электрик" (#3, score 0.823) - man on pole with motorcycle below
  - ✅ No horses or bicycles in results
  - ✅ More precise literal understanding
  - **Winner for this concrete visual query!**

**Lesson:** CLIP-large's "better semantic understanding" can be a bug for concrete queries! Visual inspection revealed clip-base was more accurate despite having fewer results.

### ⚠️ CRITICAL: Use Identical Parameters!

**When comparing CLIP models, you MUST use IDENTICAL parameters:**

```python
# ✅ CORRECT: Same parameters, only clip_model differs
search_paintings(query="...", clip_model="clip-large", limit=20, ...)
search_paintings(query="...", clip_model="clip-base", limit=20, ...)

# ❌ WRONG: Different limit values
search_paintings(query="...", clip_model="clip-large", limit=20, ...)
search_paintings(query="...", clip_model="clip-base", limit=5, ...)  # INVALID!
```

**Why this matters:**
- `limit` drastically affects reranking behavior
- Different limits = comparing different workflows, not models
- Example: `limit=5` may skip good results that appear in top-20
- Jina reranker behaves differently with different candidate pool sizes

**Use the comparison script:**
```bash
cd ~/.claude/skills/dify-search
venv/bin/python scripts/compare_models.py  # Tests both models with identical params
```

### Comparison Methodology

**Wrong way:**
```python
# ❌ BAD: Comparing only scores
if clip_base_score > clip_large_score:
    print("clip-base is better")
```

**Right way:**
```python
# ✅ GOOD: Visual inspection required
1. Run both models on test queries
2. Download top 3-5 images from each
3. Manually evaluate which images match query intent
4. Compare conceptual vs literal understanding
```

### Model Characteristics

**clip-large (openai/clip-vit-large-patch14):**
- Better at **abstract/artistic concepts**
- Deeper semantic understanding
- Examples where it wins:
  - "игра света и тени" → Found chiaroscuro lighting technique
  - "лиминальное пространство" → Understood transitional spaces
  - Artistic/conceptual queries

**clip-base (openai/clip-vit-base-patch32):**
- Better at **literal/concrete visuals**
- More precise filtering - avoids over-generalization
- Faster (slightly)
- Examples where it wins:
  - "мотоцикл" → Found motorcycles only, filtered out horses/bicycles (clip-large included them!)
  - "закат над водой" → Sunset over water (literal)
  - "зеленый пейзаж" → Green landscape (color-based)
  - Concrete object queries where precision matters

### Using the Comparison Script

```bash
cd ~/.claude/skills/dify-search
venv/bin/python scripts/compare_models.py
```

This script:
- Tests both models on 10 predefined queries
- Saves results to `comparison_results.json`
- Shows side-by-side comparison
- **BUT you still need to manually inspect images!**

### Recommendation

**Default: Use clip-large**
- Better semantic understanding for abstract/artistic queries
- Handles conceptual queries well
- Same speed as clip-base in practice

**When to use clip-base:**
- Concrete object queries ("мотоцикл", "красная машина", etc.)
- When precision matters more than broad matching
- If clip-large includes too many false positives
- Very literal visual queries
- When you need maximum speed

**⚠️ Important:** Don't assume clip-large is always better! For concrete visual queries, clip-base often provides more precise results. **Always visually inspect images to decide!**

### Key Takeaway

**Similarity scores measure embedding distance, not human perception of relevance.**

A model that assigns high scores to wrong results is worse than one that assigns lower scores to correct results.

Always validate with your eyes, not with numbers.

## Troubleshooting

### Issue: No results returned
- Lower `relevance_treshold`
- Try `search_mode="both"` instead of specific mode
- Check if reranking failed (see `error_1`)

### Issue: Results not relevant
- Check `english_clip_query` - is refinement correct?
- Try `use_refiner=false`
- Switch between `search_mode` values
- Increase `relevance_treshold` for stricter filtering

### Issue: Too slow
- Use `clip_model="clip-base"`
- Set `jina_reranking="none"`
- Reduce `limit`

### Issue: Reranking always fails
- Check network connectivity to Jina API
- Try `jina_reranking="none"` as fallback
- Verify in logs what error is in `error_1`

## Integration Tips

### For Production
- **Always use `clip-large`** (better semantic understanding, same speed)
- Use `multimodal` reranking for best quality
- Set reasonable `limit` (10-20)
- Monitor `elapsed_time` and `total_tokens`
- Log queries and results for quality analysis
- **Don't auto-select model by query type** - clip-large handles both abstract and literal well

### For Development
- Start with `clip-large` and test if results are good
- Only try `clip-base` if clip-large fails on specific query
- Use `jina_reranking="none"` to debug vector search
- Use `limit=50` to see more candidates
- **Always visually inspect images when comparing models!**

### For Analysis
- **Never compare models by scores alone** - download and view images
- Export results with scores AND image URLs
- Compare different parameter combinations with visual validation
- Track which queries fail to find good matches
- Monitor similarity score distribution but don't trust it blindly
- Use `scripts/compare_models.py` as starting point, then manual review
