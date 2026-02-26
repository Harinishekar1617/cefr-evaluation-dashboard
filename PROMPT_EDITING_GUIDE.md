# Prompt Editing Guide

Easy way for CEFR experts to review and edit prompts.

## File Structure

```
CEFR Evaluation/
├── prompts.json                 ← Metadata (which versions exist)
└── prompts/                     ← Actual prompt files
    ├── v1_detailed.txt
    ├── v2_simplified.txt
    └── [your new prompts here]
```

## Editing a Prompt

### Step 1: Open the Prompt File
Open `prompts/v1_detailed.txt` in any text editor (VS Code, Sublime, even Notepad).

### Step 2: Edit Directly
No JSON escaping, no special characters - just plain text!

```
## DIMENSION 1: FLUENCY (Speech Flow)

Question: "Does speech flow continuously, or is it broken/fragmented?"

**A1**: Many fillers (3-4 per sentence), frequent restarts
**A2**: Some fillers (1-2 per sentence), occasional pauses
**B1**: Minimal fillers (0-1), clean start, smooth delivery
```

Edit as much as you want - add examples, change descriptions, clarify criteria.

### Step 3: Save
Just save the file. Done! It's automatically loaded by the system.

## Adding a New Prompt Version

### Step 1: Create New File
Create `prompts/v3_your_name.txt`

Copy content from an existing prompt and modify:
- Change definitions
- Add/remove examples
- Adjust scoring criteria
- etc.

### Step 2: Update prompts.json
Add entry to `prompts/prompts.json`:

```json
"v3_your_name": {
  "version": "3.0",
  "date_created": "2025-02-20",
  "description": "What's different about this version",
  "author": "Your Name",
  "file": "prompts/v3_your_name.txt"
}
```

### Step 3: Use It
Edit `cefr_pipeline/config.py`:
```python
PROMPT_VERSION = "v3_your_name"
```

Run:
```bash
python main.py
```

## Example: Creating a Stricter Version

### 1. Copy Template
Copy `prompts/v1_detailed.txt` → `prompts/v3_stricter.txt`

### 2. Edit the File
Change A1/A2 boundary criteria to be stricter:

**Before:**
```
**A2**: Some fillers (1-2 per sentence), occasional pauses
```

**After:**
```
**A2**: Some fillers (1-2 per sentence), occasional pauses,
       BUT shows consistent effort to complete thoughts
```

### 3. Update prompts.json
```json
"v3_stricter": {
  "version": "3.0",
  "date_created": "2025-02-20",
  "description": "Stricter A1/A2 boundary - focuses on consistency",
  "author": "CEFR Expert Name",
  "file": "prompts/v3_stricter.txt"
}
```

### 4. Test It
Change config and run:
```python
PROMPT_VERSION = "v3_stricter"
```

## Tips

✅ **Do This:**
- Edit the .txt files directly
- Keep formatting consistent
- Add comments explaining changes
- Use clear, specific criteria

❌ **Don't Do This:**
- Edit the raw JSON if content is in the file field
- Delete a prompt without backing it up
- Use special characters without escaping
- Change the metadata file reference

## Comparing Versions

After creating a new prompt, compare results:

```bash
# Run with v1_detailed
python main.py

# Change config to v3_stricter
python main.py

# Compare results
python compare_prompts.py
```

See which version produces better results!

## File Format

Each prompt file should contain:

1. **Intro paragraph** - Who this is for, what it does
2. **Critical instructions** - How to score (independently, etc.)
3. **Dimensions** - Separate section for each dimension
4. **Indian English** - What NOT to penalize
5. **Scoring process** - Step-by-step instructions
6. **Output format** - Expected JSON structure

## Backup

Keep old versions of prompts.json by renaming:
- `prompts_backup_2025-02-20.json`

Easy to rollback if needed!

## Questions?

If something breaks:
1. Check `prompts.json` - make sure file path is correct
2. Check file exists in `prompts/` folder
3. Check `config.py` - make sure PROMPT_VERSION matches the key in prompts.json
4. Run `python main.py` - error message will tell you what's wrong
