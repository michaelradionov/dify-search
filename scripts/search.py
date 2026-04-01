#!/usr/bin/env python3
"""
Helper script for Dify artwork search.
Usage: python search.py "your query"
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any


def setup_config() -> Dict[str, str]:
    """
    Interactive setup for first-time configuration.
    Prompts user for credentials and saves to .env file.
    """
    config_dir = Path(__file__).parent.parent / "config"
    env_file = config_dir / ".env"
    env_example = config_dir / ".env.example"

    print("🔧 Dify Search Skill - First Time Setup")
    print("=" * 60)
    print()
    print("This skill needs your Dify API credentials to work.")
    print()

    # Get credentials from user
    base_url = input("Enter your Dify base URL (e.g., https://dify.example.com): ").strip()
    if not base_url:
        print("❌ Base URL is required!")
        sys.exit(1)

    # Remove trailing slash if present
    base_url = base_url.rstrip('/')

    api_token = input("Enter your Dify API token (e.g., app-xxxxx): ").strip()
    if not api_token:
        print("❌ API token is required!")
        sys.exit(1)

    # Save to .env
    config_dir.mkdir(parents=True, exist_ok=True)
    with open(env_file, 'w') as f:
        f.write(f"DIFY_BASE_URL={base_url}\n")
        f.write(f"DIFY_API_TOKEN={api_token}\n")

    print()
    print("✅ Configuration saved to:", env_file)
    print()
    print("You can update these values anytime by editing:")
    print(f"  {env_file}")
    print()

    return {
        "DIFY_BASE_URL": base_url,
        "DIFY_API_TOKEN": api_token
    }


def load_config() -> Dict[str, str]:
    """
    Load configuration from .env file.
    If file doesn't exist or contains placeholder values, runs setup.
    """
    config_dir = Path(__file__).parent.parent / "config"
    env_file = config_dir / ".env"

    # If .env doesn't exist, run setup
    if not env_file.exists():
        print("⚠️  Config file not found. Starting first-time setup...\n")
        return setup_config()

    # Read existing config
    config = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                config[key] = value

    # Check if config has placeholder values
    placeholder_values = [
        "https://your-dify-instance.com",
        "app-your-token-here",
        "your-dify-instance.com"
    ]

    needs_setup = False
    for key in ["DIFY_BASE_URL", "DIFY_API_TOKEN"]:
        if key not in config or not config[key] or config[key] in placeholder_values:
            needs_setup = True
            break

    if needs_setup:
        print("⚠️  Config contains placeholder values. Starting setup...\n")
        return setup_config()

    return config


def search_paintings(
    query: str,
    use_refiner: bool = True,
    clip_model: str = "clip-large",
    search_mode: str = "image",
    jina_reranking: str = "multimodal",
    relevance_treshold: float = 0.5,
    limit: int = 20,
    clip_fallback_treshold: float = 0.0,
    user: str = "cli-user",
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Search for paintings using Dify workflow.

    Args:
        query: Search query
        use_refiner: Use GPT query refiner
        clip_model: CLIP model ("clip-base" or "clip-large")
        search_mode: Search mode ("none", "image", "text", "both")
        jina_reranking: Reranking type ("none", "text", "multimodal")
        relevance_treshold: Relevance threshold (0-1)
        limit: Number of results
        clip_fallback_treshold: CLIP fallback threshold
        user: User ID
        verbose: Print debug info

    Returns:
        API response as dict
    """
    config = load_config()

    url = f"{config['DIFY_BASE_URL']}/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {config['DIFY_API_TOKEN']}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": {
            "query": query,
            "use_refiner": use_refiner,
            "clip_model": clip_model,
            "search_mode": search_mode,
            "jina_reranking": jina_reranking,
            "relevance_treshold": relevance_treshold,
            "limit": limit,
            "clip_fallback_treshold": clip_fallback_treshold
        },
        "response_mode": "blocking",
        "user": user
    }

    if verbose:
        print(f"🔍 Query: {query}")
        print(f"⚙️  Parameters: {json.dumps(payload['inputs'], indent=2)}")
        print()

    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()

    result = response.json()

    if verbose:
        print(f"✅ Success!")
        print(f"⏱️  Time: {result['data']['elapsed_time']:.2f}s")
        print(f"🎯 Tokens: {result['data']['total_tokens']}")
        print()

    return result


def print_results(result: Dict[str, Any]) -> None:
    """Print search results in a readable format."""
    data = result.get("data", {})
    outputs = data.get("outputs", {})

    # Print refined query
    if refined_query := outputs.get("english_clip_query"):
        print(f"🇬🇧 Refined query: {refined_query}")
        print()

    # Print main output (markdown)
    if output := outputs.get("output"):
        print(output)

    # Print errors if any
    if error := outputs.get("error"):
        print(f"\n❌ Error: {error}")
    if error1 := outputs.get("error_1"):
        print(f"ℹ️  Reranking status: {error1}")

    # Print performance
    print()
    print("=" * 60)
    print(f"⏱️  Elapsed time: {data.get('elapsed_time', 0):.2f}s")
    print(f"🎯 Total tokens: {data.get('total_tokens', 0)}")
    print(f"📊 Total steps: {data.get('total_steps', 0)}")
    print("=" * 60)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python search.py <query> [--verbose]")
        print("\nExample:")
        print('  python search.py "закат на море"')
        print('  python search.py "portrait of a woman" --verbose')
        sys.exit(1)

    # Parse arguments
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    query = " ".join(arg for arg in sys.argv[1:] if not arg.startswith("-"))

    try:
        result = search_paintings(query, verbose=verbose)
        print_results(result)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
