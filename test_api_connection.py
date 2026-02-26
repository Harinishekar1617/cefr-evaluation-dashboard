#!/usr/bin/env python3
"""
Test script to verify API connection and configuration.
Run this before running the main pipeline to ensure everything is set up correctly.
"""

import sys
from pathlib import Path

# Add the cefr_pipeline to the path
sys.path.insert(0, str(Path(__file__).parent))

from cefr_pipeline import config
from cefr_pipeline.assessment import initialize_client, test_model_availability
from cefr_pipeline.utils import install_if_needed


def test_api_connection():
    """Test the configured API connection."""
    print("=" * 80)
    print("API CONNECTION TEST")
    print("=" * 80)
    print()

    # Display configuration
    print("Configuration:")
    print(f"  Provider: {config.API_PROVIDER}")
    print(f"  Model: {config.MODEL_NAME}")
    print()

    # Check API key
    print("Checking API Key:")
    if config.API_PROVIDER == "gemini":
        if config.API_KEY == "YOUR_GEMINI_KEY_HERE":
            print("  ❌ ERROR: Gemini API key not configured!")
            print("     Set GEMINI_API_KEY in .env or config.py")
            return False
        else:
            print(f"  ✅ Gemini API key found (length: {len(config.API_KEY)})")
    elif config.API_PROVIDER == "openai":
        if config.API_KEY == "sk-YOUR_KEY_HERE":
            print("  ❌ ERROR: OpenAI API key not configured!")
            print("     Set OPENAI_API_KEY in .env or config.py")
            return False
        else:
            print(f"  ✅ OpenAI API key found (starts with: {config.API_KEY[:10]}...)")
    elif config.API_PROVIDER == "openrouter":
        if config.API_KEY == "sk-or-YOUR_KEY_HERE":
            print("  ❌ ERROR: OpenRouter API key not configured!")
            print("     Set OPENROUTER_API_KEY in .env or config.py")
            return False
        else:
            print(f"  ✅ OpenRouter API key found (starts with: {config.API_KEY[:10]}...)")
    print()

    # Install required libraries
    print("Checking Dependencies:")
    if config.API_PROVIDER == "gemini":
        try:
            import google.generativeai
            print("  ✅ google-generativeai is installed")
        except ImportError:
            print("  ⚠️  Installing google-generativeai...")
            install_if_needed('google-generativeai', 'google.generativeai')
    else:
        try:
            import openai
            print("  ✅ openai is installed")
        except ImportError:
            print("  ⚠️  Installing openai...")
            install_if_needed('openai')
    print()

    # Initialize client
    print("Initializing API Client:")
    try:
        client = initialize_client(config.API_KEY, provider=config.API_PROVIDER)
        print(f"  ✅ {config.API_PROVIDER.upper()} client initialized successfully")
    except Exception as e:
        print(f"  ❌ ERROR: Failed to initialize client!")
        print(f"     {str(e)}")
        return False
    print()

    # Test model availability
    print("Testing Model Availability:")
    try:
        available_model = test_model_availability(client, provider=config.API_PROVIDER)
        if available_model:
            print(f"  ✅ Model '{available_model}' is available")
        else:
            print(f"  ❌ No models available")
            return False
    except Exception as e:
        print(f"  ❌ ERROR: Failed to test model!")
        print(f"     {str(e)}")
        return False
    print()

    return True


def main():
    """Run all tests."""
    print()
    success = test_api_connection()
    print("=" * 80)
    if success:
        print("✅ ALL TESTS PASSED!")
        print()
        print("You can now run the pipeline with:")
        print("  python main.py")
        print("=" * 80)
        return 0
    else:
        print("❌ TESTS FAILED")
        print()
        print("Please fix the issues above and try again.")
        print("For setup help, see: API_PROVIDER_GUIDE.md or QUICK_SETUP.txt")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
