# Gemini API Setup Checklist

Use this checklist to ensure you've completed all steps to use Gemini API with the CEFR pipeline.

## Pre-Setup

- [ ] You have internet connection
- [ ] Python 3.8+ is installed: `python --version`
- [ ] You're in the project directory: `cd "/Users/hshekar/CEFR Evaluation"`

## Step 1: Get Gemini API Key

- [ ] Visit https://aistudio.google.com/app/apikeys
- [ ] Sign in with Google account (create one if needed)
- [ ] Click "Create API Key"
- [ ] Select "Create new API key in new project"
- [ ] Copy your API key (starts with `AIza...`)
- [ ] **SAVE IT SAFELY** - Don't share with anyone

## Step 2: Store API Key

### Option A: Using .env file (Recommended)
- [ ] Open terminal in project root
- [ ] Run: `echo "GEMINI_API_KEY=YOUR_KEY_HERE" > .env`
- [ ] Replace `YOUR_KEY_HERE` with actual key
- [ ] Verify: `cat .env` (should show your key)

### Option B: In config.py
- [ ] Open `cefr_pipeline/config.py`
- [ ] Find line: `GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE")`
- [ ] Replace `YOUR_GEMINI_KEY_HERE` with actual key
- [ ] Save file

## Step 3: Install Required Library

- [ ] Run: `pip install google-generativeai`
- [ ] Wait for installation to complete
- [ ] Verify: `python -c "import google.generativeai; print('OK')"`

## Step 4: Configure Pipeline

- [ ] Open `cefr_pipeline/config.py`
- [ ] Find: `API_PROVIDER = ...`
- [ ] Ensure it's set to: `API_PROVIDER = "gemini"`
- [ ] Find: `MODEL_NAME = ...`
- [ ] Ensure it's set to: `MODEL_NAME = "gemini-1.5-flash"`
- [ ] Save file

## Step 5: Test Connection

- [ ] Run: `python test_api_connection.py`
- [ ] Check for "✅ ALL TESTS PASSED!"
- [ ] If errors, see Troubleshooting section below

## Step 6: Run Pipeline

- [ ] Run: `python main.py`
- [ ] Monitor progress (should see "Progress: 10/90", etc.)
- [ ] Wait for completion (typically 5-10 minutes)
- [ ] Check for "✅ PIPELINE COMPLETE"

## Step 7: Verify Results

- [ ] Check output directory: `ls -lh output/`
- [ ] Look for: `cefr_results_all_students_gemini.xlsx`
- [ ] Open in Excel/Sheets and verify data

## Troubleshooting

### Issue: "API key not found" or "YOUR_GEMINI_KEY_HERE"

**Solution:**
- [ ] Check `.env` file exists: `ls -la .env`
- [ ] Verify content: `cat .env`
- [ ] Should show: `GEMINI_API_KEY=AIza...`
- [ ] If missing, recreate: `echo "GEMINI_API_KEY=YOUR_KEY" > .env`

### Issue: "google-generativeai not installed"

**Solution:**
- [ ] Install: `pip install google-generativeai`
- [ ] Verify: `python -c "import google.generativeai; print('OK')"`

### Issue: "Invalid API Key"

**Solution:**
- [ ] Verify at https://aistudio.google.com/app/apikeys
- [ ] Key should start with `AIza`
- [ ] Check for extra spaces: `cat .env | cat -A`
- [ ] Create new key if needed

### Issue: "Rate limit exceeded"

**Solution:**
- [ ] Wait 5-10 minutes
- [ ] Try again: `python main.py`
- [ ] Reduce sample size in config.py: `SAMPLE_PER_STUDENT = 3`

### Issue: "Connection timeout"

**Solution:**
- [ ] Check internet: `ping google.com`
- [ ] Try again in a moment
- [ ] Check firewall/VPN settings

## Verification Commands

Run these to verify everything is working:

```bash
# Test 1: Check API key
grep GEMINI_API_KEY .env

# Test 2: Check library
python -c "import google.generativeai; print('OK')"

# Test 3: Check config
python -c "from cefr_pipeline import config; print(f'Provider: {config.API_PROVIDER}')"

# Test 4: Full connection test
python test_api_connection.py

# Test 5: Run pipeline (if all above passed)
python main.py
```

## Success Criteria

✅ All of these should be true:

- [ ] API key format is `AIza...` (not `sk-...` or blank)
- [ ] `.env` file contains: `GEMINI_API_KEY=AIza...`
- [ ] `google-generativeai` is installed
- [ ] `config.py` has `API_PROVIDER = "gemini"`
- [ ] `test_api_connection.py` runs successfully
- [ ] `python main.py` completes without errors
- [ ] Excel file appears in `output/` directory
- [ ] Excel file contains CEFR scores and justifications

## Quick Reference

| What | Where | Value |
|------|-------|-------|
| API Key location | `.env` | `GEMINI_API_KEY=AIza...` |
| Provider config | `cefr_pipeline/config.py` | `API_PROVIDER = "gemini"` |
| Model config | `cefr_pipeline/config.py` | `MODEL_NAME = "gemini-1.5-flash"` |
| Test connection | Run | `python test_api_connection.py` |
| Run pipeline | Run | `python main.py` |
| Results location | Folder | `output/` |

## After Setup

1. ✅ Run pipeline: `python main.py`
2. ✅ Check results: `output/cefr_results_all_students_gemini.xlsx`
3. ✅ Optional: Compare with other providers by changing `API_PROVIDER`
4. ✅ Optional: Check results: `python compare_prompts.py`

## Getting Help

If you get stuck:

1. Check **QUICK_SETUP.txt** for fast answers
2. Check **GEMINI_API_SETUP.md** for detailed guide
3. Check **API_PROVIDER_GUIDE.md** for provider comparison
4. Run `python test_api_connection.py` to diagnose

## Cost Tracking

Monitor your usage at:
- https://console.cloud.google.com/

Typical cost for 90 dialogue turns:
- **Gemini-1.5-flash**: < $0.10
- **Very affordable!**

## Next Steps After First Run

1. Optional: Try different models:
   - `MODEL_NAME = "gemini-1.5-pro"` (more powerful)
   - `MODEL_NAME = "gemini-2.0-flash"` (latest)

2. Optional: Compare with OpenAI:
   - Change `API_PROVIDER = "openai"`
   - Get OpenAI key from https://platform.openai.com
   - Run `python main.py` again
   - Compare results

3. Optional: Run comparisons:
   - Run with different providers
   - Execute `python compare_prompts.py`

---

**Total time to setup**: ~10 minutes
**Total time to run first evaluation**: ~5-10 minutes

✅ You're ready to go!
