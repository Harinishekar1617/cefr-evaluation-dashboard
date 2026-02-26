"""
Configuration file for CEFR Evaluation.
Stores all constants, paths, and API settings in one place.

Configured to use OpenAI API (PayPal Network).
"""

import os
from pathlib import Path

# ============================================================================
# DIRECTORIES
# ============================================================================
PROJECT_ROOT = Path("/Users/hshekar/CEFR Evaluation")
TRANSCRIPT_DIR = PROJECT_ROOT  # Will load all CSV files in this directory (DET + FSSA)
OUTPUT_DIR = PROJECT_ROOT / "output"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# API SETTINGS - OpenAI (PayPal Network)
# ============================================================================
# Get API key from environment variable
# Load from .env file using python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass  # python-dotenv not installed, will use os.getenv

# Use OpenAI
API_PROVIDER = "openai"

# API Configuration for OpenAI
API_KEY = os.getenv("LLM_API_KEY", "YOUR_LLM_API_KEY_HERE")
API_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# OpenAI models
# Common options: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo, etc.
MODEL_NAME = "gpt-4o-mini"  # Using GPT-4o-mini

# ============================================================================
# ALTERNATIVE PROVIDERS (Commented out - kept for reference)
# ============================================================================
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-YOUR_KEY_HERE")
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "sk-or-YOUR_KEY_HERE")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE")

# ============================================================================
# DATA FILTERING PARAMETERS
# ============================================================================
# Only keep transcripts with these topics
TOPICS_TO_KEEP = ['Introducing Yourself', 'General talk']

# Minimum word count threshold for filtering students
MIN_MODE_WORDS = 30

# Minimum word count for individual dialogue turns
MIN_WORDS_PER_TURN = 30

# Number of dialogue turns to sample per student
SAMPLE_PER_STUDENT = 5

# ============================================================================
# EVALUATION SETTINGS
# ============================================================================
# Set to True to evaluate all students, False for single student
EVALUATE_ALL_STUDENTS = True

# Only used if EVALUATE_ALL_STUDENTS = False
SINGLE_STUDENT_NAME = "Charan Chandru"

# Random seed for reproducibility (sampling)
RANDOM_SEED = 42

# ============================================================================
# PROMPT VERSIONING
# ============================================================================
# Which prompt version to use for CEFR evaluation
# Available versions are defined in prompts.json
# Common options: "v1_key_indicators_only", "v2_full_guidelines", "v3_measurable_evidence", "v3_measurable_evidence_deepseek"
PROMPT_VERSION = "v3_measurable_evidence"

# Note: The actual prompt text is loaded from prompts.json via prompt_manager.py
# To test different prompts, change PROMPT_VERSION above and rerun main.py
# Results will automatically include which prompt version was used
