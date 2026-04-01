# API Examples

## Successful Response Example

Request:
```bash
curl -X POST "${DIFY_BASE_URL}/v1/workflows/run" \
  -H "Authorization: Bearer ${DIFY_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "query": "закат на море",
      "use_refiner": true,
      "clip_model": "clip-large",
      "search_mode": "image",
      "jina_reranking": "multimodal",
      "relevance_treshold": 0.5,
      "limit": 20,
      "clip_fallback_treshold": 0.0
    },
    "response_mode": "blocking",
    "user": "test-user"
  }'
```

Response structure:
```json
{
  "task_id": "67a1dc6f-bea1-4683-8eba-36c548f46d6b",
  "workflow_run_id": "ecc80144-f3a0-4606-be67-e9691cc2c965",
  "data": {
    "id": "ecc80144-f3a0-4606-be67-e9691cc2c965",
    "workflow_id": "bb1824dc-8fdf-4cd8-bc33-429e5de92847",
    "status": "succeeded",
    "outputs": {
      "english_clip_query": "sunset over the sea",
      "error_1": "jina_success",
      "output": "### 🎨 Найдено 20 подходящих картин\n...",
      "error": ""
    },
    "error": null,
    "elapsed_time": 11.719622,
    "total_tokens": 5015,
    "total_steps": 11,
    "created_at": 1775013116,
    "finished_at": 1775013128
  }
}
```

## Parameters Configuration

Get available parameters:
```bash
curl -H "Authorization: Bearer ${DIFY_API_TOKEN}" \
  "${DIFY_BASE_URL}/v1/parameters"
```

Response:
```json
{
  "user_input_form": [
    {
      "text-input": {
        "variable": "query",
        "label": "Запрос",
        "type": "text-input",
        "required": true
      }
    },
    {
      "checkbox": {
        "variable": "use_refiner",
        "label": "Использовать рефайнер",
        "type": "checkbox",
        "default": true,
        "required": true
      }
    },
    {
      "select": {
        "variable": "clip_model",
        "label": "Модель CLIP",
        "type": "select",
        "options": ["clip-base", "clip-large"],
        "default": "clip-large",
        "required": true
      }
    },
    {
      "select": {
        "variable": "search_mode",
        "label": "Тип векторного поиска",
        "type": "select",
        "options": ["none", "image", "text", "both"],
        "default": "image",
        "required": true
      }
    },
    {
      "select": {
        "variable": "jina_reranking",
        "label": "Тип реранкера",
        "type": "select",
        "options": ["none", "text", "multimodal"],
        "default": "multimodal",
        "required": true
      }
    },
    {
      "number": {
        "variable": "relevance_treshold",
        "label": "Порог релевантности реранкера",
        "type": "number",
        "default": "0.5",
        "required": true
      }
    },
    {
      "number": {
        "variable": "limit",
        "label": "Кол-во результатов для вывода",
        "type": "number",
        "default": "20",
        "required": true
      }
    },
    {
      "number": {
        "variable": "clip_fallback_treshold",
        "label": "Порог CLIP fallback (откл. реранкинг)",
        "type": "number",
        "default": "0",
        "required": true
      }
    }
  ]
}
```

## Common Use Cases

### Visual Search
```json
{
  "inputs": {
    "query": "закат на море",
    "search_mode": "image",
    "jina_reranking": "multimodal"
  }
}
```

### Semantic Search
```json
{
  "inputs": {
    "query": "меланхолия и одиночество",
    "search_mode": "text",
    "jina_reranking": "text"
  }
}
```

### Hybrid Search
```json
{
  "inputs": {
    "query": "портрет женщины в красном платье",
    "search_mode": "both",
    "jina_reranking": "multimodal",
    "relevance_treshold": 0.6
  }
}
```

### Fast Search (No Reranking)
```json
{
  "inputs": {
    "query": "mountain landscape",
    "clip_model": "clip-base",
    "jina_reranking": "none",
    "use_refiner": false
  }
}
```
