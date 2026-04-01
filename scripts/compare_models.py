#!/usr/bin/env python3
"""
Compare CLIP models (clip-base vs clip-large) on a set of queries.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add parent dir to path to import search module
sys.path.insert(0, str(Path(__file__).parent))
from search import search_paintings


QUERIES = [
    "сочный зеленый пейзаж",
    "цветущая весна",
    "тёплый закат над водой",
    "отражения в воде",
    "шторм с драматичным освещением",
    "золотой час в снежном лесу",
    "игра света и тени",
    "ночные огни боке",
    "сумеречное лиминальное пространство",
    "солнечные блики на воде",
]


def extract_top_results(result: Dict[str, Any], top_n: int = 5) -> List[Dict]:
    """Extract top N results with scores from API response."""
    outputs = result.get("data", {}).get("outputs", {})
    output_text = outputs.get("output", "")

    # Parse markdown output to extract paintings info
    paintings = []
    lines = output_text.split('\n')

    current_painting = {}
    for line in lines:
        line = line.strip()

        # New painting starts with #### N.
        if line.startswith('#### ') and '. ' in line:
            if current_painting and 'name' in current_painting:
                paintings.append(current_painting)
            # Extract name between « and »
            if '«' in line and '»' in line:
                name = line.split('«')[1].split('»')[0]
                current_painting = {"name": name}
            else:
                current_painting = {}

        # Extract similarity score
        elif '**Сходство:**' in line or '**Similarity:**' in line:
            # Extract float from the line
            score_part = line.split('**')[-1].strip()
            # Remove emoji and extract number
            score_text = score_part.split()[0]
            try:
                current_painting["score"] = float(score_text)
            except (ValueError, IndexError):
                current_painting["score"] = 0.0

        # Extract author
        elif '**Автор:**' in line or '**Author:**' in line:
            author_text = line.split('**')[-1].strip()
            current_painting["author"] = author_text

    if current_painting and 'name' in current_painting:
        paintings.append(current_painting)

    return paintings[:top_n]


def compare_models():
    """Run all queries through both CLIP models and compare."""
    results = {
        "clip-large": {},
        "clip-base": {}
    }

    print("=" * 80)
    print("🎨 CLIP Model Comparison Test")
    print("=" * 80)
    print()
    print(f"Testing {len(QUERIES)} queries with 2 CLIP models...")
    print()

    total_tests = len(QUERIES) * 2
    current_test = 0

    # Test each query with both models
    for query_idx, query in enumerate(QUERIES, 1):
        print(f"\n{'=' * 80}")
        print(f"Query {query_idx}/{len(QUERIES)}: {query}")
        print('=' * 80)

        for model in ["clip-large", "clip-base"]:
            current_test += 1
            print(f"\n[{current_test}/{total_tests}] Testing with {model}...")

            try:
                result = search_paintings(
                    query=query,
                    clip_model=model,
                    search_mode="image",
                    jina_reranking="multimodal",
                    limit=20,
                    verbose=False
                )

                # Store result
                results[model][query] = {
                    "result": result,
                    "top_5": extract_top_results(result, top_n=5),
                    "elapsed_time": result.get("data", {}).get("elapsed_time", 0),
                    "refined_query": result.get("data", {}).get("outputs", {}).get("english_clip_query", "")
                }

                # Print brief summary
                data = result.get("data", {})
                outputs = data.get("outputs", {})
                top_results = results[model][query]["top_5"]

                print(f"✅ {model}: {data.get('elapsed_time', 0):.1f}s")
                print(f"   Refined: {outputs.get('english_clip_query', 'N/A')}")
                if top_results:
                    print(f"   Top result: {top_results[0].get('name', 'N/A')} (score: {top_results[0].get('score', 0):.3f})")

            except Exception as e:
                print(f"❌ Error with {model}: {e}")
                results[model][query] = {"error": str(e)}

    # Generate comparison report
    print("\n\n" + "=" * 80)
    print("📊 COMPARISON REPORT")
    print("=" * 80)

    for query_idx, query in enumerate(QUERIES, 1):
        print(f"\n{query_idx}. {query}")
        print("-" * 80)

        for model in ["clip-large", "clip-base"]:
            data = results[model].get(query, {})
            if "error" in data:
                print(f"\n{model}: ❌ ERROR - {data['error']}")
                continue

            top_5 = data.get("top_5", [])
            time = data.get("elapsed_time", 0)
            refined = data.get("refined_query", "")

            print(f"\n{model} ({time:.1f}s):")
            print(f"  Refined: {refined}")
            print(f"  Top 5:")
            for i, painting in enumerate(top_5, 1):
                score = painting.get('score', 0)
                name = painting.get('name', 'N/A')[:60]
                author = painting.get('author', 'N/A')
                print(f"    {i}. [{score:.3f}] {name} - {author}")

    # Performance summary
    print("\n\n" + "=" * 80)
    print("⏱️  PERFORMANCE SUMMARY")
    print("=" * 80)

    for model in ["clip-large", "clip-base"]:
        times = [
            results[model][q]["elapsed_time"]
            for q in QUERIES
            if "elapsed_time" in results[model].get(q, {})
        ]
        if times:
            avg_time = sum(times) / len(times)
            print(f"\n{model}:")
            print(f"  Average time: {avg_time:.2f}s")
            print(f"  Total time: {sum(times):.2f}s")

    # Save results to JSON
    output_file = Path(__file__).parent.parent / "comparison_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        # Simplify results for JSON (remove full API responses)
        simplified = {}
        for model in results:
            simplified[model] = {}
            for query in results[model]:
                simplified[model][query] = {
                    "top_5": results[model][query].get("top_5", []),
                    "elapsed_time": results[model][query].get("elapsed_time", 0),
                    "refined_query": results[model][query].get("refined_query", ""),
                    "error": results[model][query].get("error")
                }

        json.dump(simplified, f, ensure_ascii=False, indent=2)

    print(f"\n\n💾 Results saved to: {output_file}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    compare_models()
