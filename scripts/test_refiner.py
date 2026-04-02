#!/usr/bin/env python3
"""
Test script for evaluating query refiner's author extraction.
Tests if the refiner correctly extracts author name from queries.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from search import search_paintings


def test_refiner_author_extraction(queries: List[str], verbose: bool = True) -> List[Dict[str, Any]]:
    """
    Test query refiner on a list of queries with authors.

    Args:
        queries: List of queries containing author names
        verbose: Print detailed info for each query

    Returns:
        List of test results with query, refined output, and evaluation
    """
    results = []

    print("=" * 80)
    print("TESTING QUERY REFINER - AUTHOR EXTRACTION")
    print("=" * 80)
    print()

    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Testing: {query}")
        print("-" * 80)

        try:
            # Call Dify API with search disabled (search_mode="none")
            response = search_paintings(
                query=query,
                use_refiner=True,
                search_mode="none",  # Disable search, only test refiner
                jina_reranking="none",
                limit=1,
                verbose=False
            )

            # Extract outputs
            outputs = response.get("data", {}).get("outputs", {})

            # Get all output fields
            english_query = outputs.get("english_clip_query", "")
            main_output = outputs.get("output", "")
            error = outputs.get("error", "")
            error_1 = outputs.get("error_1", "")

            # Performance metrics
            elapsed_time = response.get("data", {}).get("elapsed_time", 0)
            total_tokens = response.get("data", {}).get("total_tokens", 0)

            # Try to extract author from outputs (check if there's a separate author field)
            # This depends on Dify workflow structure
            author_field = outputs.get("author", None)

            # Display results
            print(f"✓ Refined query: {english_query}")
            if author_field:
                print(f"✓ Extracted author: {author_field}")
            if main_output:
                print(f"ℹ️  Main output: {main_output[:200]}...")
            if error:
                print(f"❌ Error: {error}")
            if error_1:
                print(f"ℹ️  Error_1: {error_1}")

            print(f"⏱️  Time: {elapsed_time:.2f}s | Tokens: {total_tokens}")

            # Store result
            result = {
                "query": query,
                "english_clip_query": english_query,
                "author": author_field,
                "main_output": main_output,
                "error": error,
                "elapsed_time": elapsed_time,
                "total_tokens": total_tokens,
                "success": not error
            }
            results.append(result)

        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                "query": query,
                "error": str(e),
                "success": False
            })

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    successful = sum(1 for r in results if r.get("success", False))
    print(f"Successful: {successful}/{len(queries)}")
    print(f"Failed: {len(queries) - successful}/{len(queries)}")
    print()

    # Show full response structure for first query (debug)
    if results and verbose:
        print("=" * 80)
        print("SAMPLE FULL RESPONSE (first query)")
        print("=" * 80)
        print(json.dumps(results[0], indent=2, ensure_ascii=False))
        print()

    return results


def main():
    """CLI entry point."""
    # Example queries with authors - waiting for user input
    print("This script tests the query refiner's author extraction.")
    print("Please provide queries as command-line arguments.")
    print()
    print("Example:")
    print('  python test_refiner.py "закат Айвазовского" "девушки в шляпах Андрея Елецкого"')
    print()

    if len(sys.argv) < 2:
        print("❌ No queries provided!")
        print()
        print("Usage: python test_refiner.py <query1> [query2] [query3] ...")
        sys.exit(1)

    queries = sys.argv[1:]

    # Run tests
    results = test_refiner_author_extraction(queries, verbose=True)

    # Save results to file
    output_file = Path(__file__).parent.parent / "test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Results saved to: {output_file}")


if __name__ == "__main__":
    main()
