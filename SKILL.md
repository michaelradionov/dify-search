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

**Important:**
- Always use `venv/bin/python` (not system python)
- Quote the query to preserve spaces
- Default parameters: `clip-large`, `multimodal reranking`, `limit=20`

**Example:**
```bash
cd ~/.claude/skills/dify-search && venv/bin/python scripts/search.py "девушки в шляпах Андрея Елецкого"
```

**Output includes:**
- Refined query (GPT-processed English version)
- Top N results with images, similarity scores, metadata
- Performance metrics (elapsed time, tokens, steps)

**Note:** CLI currently supports only query parameter. For custom parameters (search_mode, limit, etc.), parameters must be hardcoded in the script (see Issue: CLI parameters support needed).

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
- `"clip-base"` - openai/clip-vit-base-patch32 (faster, less accurate)
- `"clip-large"` - openai/clip-vit-large-patch14 (slower, more accurate)

**When to use:**
- Use `clip-large` for production/best results
- Use `clip-base` for testing/speed

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
- Always use `clip-large` and `multimodal` reranking
- Set reasonable `limit` (10-20)
- Monitor `elapsed_time` and `total_tokens`
- Log queries and results for quality analysis

### For Development
- Use `clip-base` for faster iteration
- Start with `jina_reranking="none"` to debug vector search
- Use `limit=50` to see more candidates

### For Analysis
- Export results with scores to CSV
- Compare different parameter combinations
- Track which queries fail to find good matches
- Monitor similarity score distribution
