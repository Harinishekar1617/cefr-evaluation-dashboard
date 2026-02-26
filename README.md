# CEFR Evaluation Pipeline

A modularized Python project for evaluating English proficiency using the CEFR (Common European Framework of Reference for Languages) framework. Uses OpenAI API to analyze student interview transcripts.

## Project Structure

```
CEFR Evaluation/
├── main.py                 # Main orchestration script - runs the full pipeline
├── config.py               # Configuration: paths, API keys, parameters
├── transcripts.py          # Functions to load and parse transcript files
├── assessment.py           # Functions to call OpenAI API for CEFR evaluation
├── utils.py                # Helper functions for data filtering and aggregation
├── det-transcripts/        # Input folder with student interview transcripts (.txt files)
├── output/                 # Output folder for results (Excel and CSV files)
└── README.md              # This file
```

## Module Descriptions

### `config.py`
**Purpose:** Centralized configuration management

Contains:
- File paths (transcripts, output directories)
- API settings (OpenAI API key, model name)
- Data filtering parameters (topics, word count thresholds)
- Evaluation configuration (which students to evaluate)
- CEFR evaluation system prompt

**Why separate?** Makes it easy to adjust parameters without editing code. Keeps sensitive data in one place.

### `transcripts.py`
**Purpose:** Load and parse student interview transcripts

Functions:
- `parse_transcript(file_path)` - Parse a single .txt transcript file
- `load_all_transcripts(transcript_dir)` - Load all transcripts from a directory

**Why separate?** All transcript I/O logic in one place. Easy to modify parsing rules if transcript format changes.

### `assessment.py`
**Purpose:** CEFR evaluation using OpenAI API

Functions:
- `initialize_openai_client(api_key)` - Setup OpenAI client
- `test_model_availability(client)` - Check which models are available
- `evaluate_student_dialogue(student_text, client, model_name, system_prompt)` - Evaluate one dialogue turn
- `extract_cefr_level(value)` - Clean up CEFR level strings

**Why separate?** All API-related logic in one place. Easy to switch models, adjust prompts, or change API behavior.

### `utils.py`
**Purpose:** Reusable data processing functions

Key functions:
- **Data filtering:** `filter_by_topics()`, `filter_by_min_mode_words()`, `filter_by_word_count_per_turn()`
- **Data cleaning:** `calculate_word_count_per_turn()`, `get_mode_words_per_student()`
- **Aggregation:** `aggregate_by_mode()` - summarize results by student
- **File I/O:** `save_results_to_excel()`, `save_results_to_csv()`

**Why separate?** These functions are reusable and called from multiple places. Keeps code DRY (Don't Repeat Yourself).

### `main.py`
**Purpose:** Orchestrate the entire pipeline

This is the main script you run. It:
1. Loads transcripts
2. Filters by topic and word count
3. Samples dialogue turns per student
4. Evaluates each turn using OpenAI
5. Aggregates results
6. Saves to Excel/CSV

Think of it as a conductor directing the orchestra of functions.

## Setup

### 1. Install Dependencies
```bash
pip install pandas openpyxl openai scipy
```

### 2. Configure Settings
Edit `config.py`:
```python
API_KEY = "your-openai-api-key"  # Or use environment variable
TRANSCRIPT_DIR = "/path/to/transcripts"
EVALUATE_ALL_STUDENTS = True  # or False for single student mode
```

### 3. Prepare Input Data
Place transcript .txt files in the `det-transcripts/` directory.

Expected format:
```
---
Student Name: John Doe
Topic: Introducing Yourself
Activity Name: Interview
Session Time: 2024-01-15 10:30:00
---
Interviewer (neutral): Can you tell me about yourself?
Student (neutral): Sure, my name is John...
```

## Running the Pipeline

```bash
python main.py
```

## Output Files

The pipeline creates:
- **Excel file** (`cefr_results_*.xlsx`) with:
  - Individual Turns sheet - scores for each dialogue turn
  - Aggregated by MODE sheet - summary by student
  - Summary sheet - overview statistics

- **CSV backups** for easy import into other tools

## CEFR Evaluation Dimensions

Each student is scored on 4 independent dimensions:

1. **Fluency** - Does speech flow continuously or is it broken?
   - A1: Many fillers, frequent restarts
   - A2: Some pauses, completes most thoughts
   - B1: Smooth delivery, minimal pauses
   - B2: Natural flow

2. **Accuracy** - How correct is the grammar?
   - A1: Missing verbs, severe tense errors
   - A2: Basic structures work but systematic errors
   - B1: Correct tense, proper agreement
   - B2: Near-flawless

3. **Range** - How varied and precise is vocabulary?
   - A1: Repetitive, high-frequency words only
   - A2: Abstract concepts, common descriptive words
   - B1: Professional vocabulary, varied connectors
   - B2: Sophisticated, industry-specific

4. **Coherence** - Is the response organized logically?
   - A1: No context, vague
   - A2: Lists points but may drift
   - B1: Linear structure, clear progression
   - B2: Rich narrative with sophisticated transitions

**Important:** These dimensions are scored independently. A student can have different levels in different dimensions (e.g., B1 Fluency + A2 Accuracy).

## Customization

### Evaluate Single Student
In `config.py`:
```python
EVALUATE_ALL_STUDENTS = False
SINGLE_STUDENT_NAME = "John Doe"
```

### Change Filtering Thresholds
In `config.py`:
```python
MIN_MODE_WORDS = 30          # Minimum typical word count per student
MIN_WORDS_PER_TURN = 30      # Minimum words in a dialogue turn
SAMPLE_PER_STUDENT = 5       # Number of turns to evaluate per student
```

### Change Topics
In `config.py`:
```python
TOPICS_TO_KEEP = ['Introducing Yourself', 'General talk']
```

### Use Different Model
In `config.py`:
```python
MODEL_NAME = "gpt-4"  # Change from gpt-4o-mini
```

## Troubleshooting

**Error: "No models available"**
- Check your API key in `config.py`
- Verify you have credit on your OpenAI account

**Error: "Student not found"**
- Check spelling in `SINGLE_STUDENT_NAME`
- Run with `EVALUATE_ALL_STUDENTS = True` to see available students

**Slow performance**
- Each dialogue turn requires an API call
- 90 turns (18 students × 5 turns) takes several minutes
- Use `EVALUATE_ALL_STUDENTS = False` with a single student for testing

## File Details

### Input Transcript Format
- One file per interview
- Metadata in header section
- Dialogue turns marked with "Interviewer" and "Student" prefixes
- Sections separated by "---"

### Prompt Files

Prompts are stored separately for easy editing:

```
prompts/
├── v1_detailed.txt          (detailed prompt with full examples)
└── v2_simplified.txt        (simplified prompt)
```

To edit a prompt:
1. Open the corresponding `.txt` file
2. Edit directly (no JSON escaping needed!)
3. Save - it's automatically loaded next time

To add a new prompt:
1. Create a new `.txt` file in `prompts/` folder
2. Add entry to `prompts.json` with `file` reference
3. Change `PROMPT_VERSION` in `config.py` to use it

### Output Columns
- `student_name` - Student identifier
- `range`, `accuracy`, `fluency`, `coherence` - CEFR level for each dimension
- `overall_cefr_level` - Overall assessment (mode of the 4 dimensions)
- `num_dialogue_turns` - Number of turns evaluated (aggregated only)

## Notes for Indian English
The evaluation is tolerant of common Indian English expressions:
- "I am having a doubt"
- "I passed out of college"
- "Cousin brother/sister"
- "I am working since 3 years"

These are not penalized as grammar errors.

## License & Attribution
Uses CEFR-J Vocabulary Profile from Tokyo University of Foreign Studies (free for research and commercial use with proper citation).
