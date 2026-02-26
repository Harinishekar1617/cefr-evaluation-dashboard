# Project Structure

Clean and simple organization of the CEFR Pipeline.

## Folder Layout

```
CEFR Evaluation/
│
├── cefr_pipeline/                 ← Main package
│   ├── __init__.py                (package description only)
│   ├── config.py                  (all settings & paths)
│   ├── transcripts.py             (load & parse transcripts)
│   ├── assessment.py              (OpenAI API & CEFR scoring)
│   ├── utils.py                   (data processing helpers)
│   └── prompt_manager.py          (manage prompt versions)
│
├── main.py                        (main pipeline script)
├── compare_prompts.py             (compare results across prompts)
├── prompts.json                   (versioned prompts)
├── det-transcripts/               (input: student transcripts)
├── output/                        (output: results files)
│
├── README.md                      (project overview)
├── PROMPT_VERSIONING_GUIDE.md    (how to version prompts)
└── STRUCTURE.md                   (this file)
```

## How to Use

### Simple: Import Directly from Modules

```python
# main.py
from cefr_pipeline import config
from cefr_pipeline.transcripts import load_all_transcripts
from cefr_pipeline.assessment import initialize_openai_client
from cefr_pipeline.utils import filter_by_topics

# Use it
df = load_all_transcripts(config.TRANSCRIPT_DIR)
```

### Creating a Custom Script

```python
# my_analysis.py
from cefr_pipeline import config
from cefr_pipeline.transcripts import load_all_transcripts
from cefr_pipeline.utils import filter_by_topics, aggregate_by_mode

def analyze():
    # Load and process
    df = load_all_transcripts(config.TRANSCRIPT_DIR)
    df = filter_by_topics(df, config.TOPICS_TO_KEEP)

    # Save
    df.to_csv(config.OUTPUT_DIR / "analysis.csv", index=False)

if __name__ == "__main__":
    analyze()
```

## Key Files

### `cefr_pipeline/__init__.py`
- Minimal - only package description
- Does NOT import everything
- Keep it simple

### `cefr_pipeline/config.py`
- All settings and constants
- Paths, API keys, thresholds
- Edit here to change parameters

### `cefr_pipeline/transcripts.py`
- `load_all_transcripts()` - Load all .txt files
- `parse_transcript()` - Parse single file

### `cefr_pipeline/assessment.py`
- `initialize_openai_client()` - Setup API
- `test_model_availability()` - Check models
- `evaluate_student_dialogue()` - Score one response
- `extract_cefr_level()` - Parse CEFR levels

### `cefr_pipeline/utils.py`
- Data filtering functions
- Aggregation functions
- File I/O functions

### `cefr_pipeline/prompt_manager.py`
- `PromptManager` class
- Load/manage/version prompts

## Running Scripts

```bash
# Main pipeline
python main.py

# Compare prompt versions
python compare_prompts.py

# Custom script
python my_script.py
```

## Importing Pattern

**All scripts import directly from modules:**

```python
from cefr_pipeline import config
from cefr_pipeline.transcripts import load_all_transcripts
from cefr_pipeline.assessment import initialize_openai_client
```

**NOT using a central imports file** - keep it simple and clear.

## Configuration

Edit `cefr_pipeline/config.py` to change:
- Which transcripts to load
- API settings
- Filtering thresholds
- Which prompt version to use
- Single vs. all students mode

## Summary

- **Simple structure** - modules are independent
- **Clear imports** - each script imports what it needs
- **Easy to modify** - add new functions without affecting others
- **No magic** - nothing hidden in `__init__.py`
