# Quick Start - PayPal Internal LLM Platform

## 🚀 Run in 30 Seconds

```bash
cd "/Users/hshekar/CEFR Evaluation"
python main.py
```

That's it! Results will be in `output/cefr_results_all_students_v1_detailed.xlsx`

---

## 🎯 Change the Model (Optional)

To use a different model like Gemini:

```bash
# Edit config.py
nano cefr_pipeline/config.py

# Find this line:
MODEL_NAME = "gpt-4o"

# Change to:
MODEL_NAME = "gemini-1.5-flash"

# Save and run:
python main.py
```

---

## 📋 Available Models

### Recommended
- `gpt-4o` - Default, most capable
- `gpt-4o-mini` - Faster, good quality
- `claude-sonnet-4-5-20250929` - Excellent reasoning
- `gemini-1.5-flash` - Fast, efficient

### Full List
See `PAYPAL_PLATFORM_CONFIG.md` for all 38+ models

---

## ✅ Status

- **API Key**: ✅ Configured
- **Base URL**: ✅ Configured
- **Models**: ✅ 38+ available
- **Status**: 🟡 Needs valid chat completion token

---

## ⚠️ If Chat Fails

If you get "Invalid or expired auth token":

1. Generate new API token from PayPal platform
2. Update `.env` with new `OPENAI_API_KEY`
3. Run `python main.py` again

---

## 📊 What It Does

```
Loads 1,845 transcripts
  ↓
Filters & samples 90 dialogue turns
  ↓
Connects to PayPal Internal LLM Platform
  ↓
Evaluates with selected model (gpt-4o, gemini, claude, etc.)
  ↓
Saves results with CEFR scores + justifications
  ↓
output/cefr_results_all_students_v1_detailed.xlsx ✅
```

---

## 📚 More Info

- Full config guide: `PAYPAL_PLATFORM_CONFIG.md`
- Available models: `PAYPAL_PLATFORM_CONFIG.md` (Models section)
- Troubleshooting: `PAYPAL_PLATFORM_CONFIG.md` (Troubleshooting section)

---

## Quick Commands

```bash
# Run with default model (gpt-4o)
python main.py

# Check configuration
python -c "from cefr_pipeline import config; print(config.MODEL_NAME)"

# List available files
ls output/
```

---

**That's it! Ready to evaluate CEFR scores?**

```bash
python main.py
```
