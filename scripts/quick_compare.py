#!/usr/bin/env python3
"""Quick comparison of CLIP models for a single query."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from search import search_paintings
import json


def compare_single_query(query: str):
    """Compare clip-base vs clip-large for a single query."""

    print("=" * 80)
    print(f"🎨 Comparing CLIP models for query: {query}")
    print("=" * 80)
    print()

    results = {}

    for model in ["clip-large", "clip-base"]:
        print(f"\n{'=' * 80}")
        print(f"Testing with {model}...")
        print('=' * 80)

        result = search_paintings(
            query=query,
            clip_model=model,
            search_mode="image",
            jina_reranking="multimodal",
            limit=5,
            verbose=False
        )

        results[model] = result

        # Print output
        data = result.get("data", {})
        outputs = data.get("outputs", {})

        print(f"\n🇬🇧 Refined query: {outputs.get('english_clip_query', 'N/A')}")
        print(f"⏱️  Time: {data.get('elapsed_time', 0):.2f}s")
        print()
        print(outputs.get('output', 'No output'))
        print()

    # Side-by-side comparison
    print("\n\n" + "=" * 80)
    print("📊 SIDE-BY-SIDE COMPARISON")
    print("=" * 80)

    for model in ["clip-large", "clip-base"]:
        data = results[model].get("data", {})
        print(f"\n{model.upper()}: {data.get('elapsed_time', 0):.2f}s")
        print("-" * 80)

        outputs = data.get("outputs", {})
        output_text = outputs.get("output", "")

        # Extract paintings
        paintings = []
        lines = output_text.split('\n')
        current = {}

        for line in lines:
            line = line.strip()
            if line.startswith('#### ') and '«' in line:
                if current and 'name' in current:
                    paintings.append(current)
                name = line.split('«')[1].split('»')[0]
                current = {"name": name}
            elif '**Сходство:**' in line or '**Similarity:**' in line:
                score_part = line.split('**')[-1].strip().split()[0]
                try:
                    current["score"] = float(score_part)
                except:
                    pass
            elif '**Автор:**' in line or '**Author:**' in line:
                current["author"] = line.split('**')[-1].strip()

        if current and 'name' in current:
            paintings.append(current)

        for i, p in enumerate(paintings, 1):
            score = p.get('score', 0)
            name = p.get('name', 'N/A')
            author = p.get('author', 'N/A')
            print(f"  {i}. [{score:.4f}] {name}")
            print(f"      by {author}")


if __name__ == "__main__":
    query = "сумеречное лиминальное пространство"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])

    compare_single_query(query)
