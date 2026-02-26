# API Provider Guide - OpenAI, OpenRouter, or Gemini

This guide explains how to switch between different API providers for the CEFR Evaluation pipeline.

## Quick Start

### 1. Get Your API Key
Choose your provider and get an API key:

| Provider | Link | Key Format |
|----------|------|-----------|
| **OpenAI** | [platform.openai.com](https://platform.openai.com/api-keys) | `sk-...` |
| **OpenRouter** | [openrouter.ai](https://openrouter.ai/keys) | `sk-or-...` |
| **Google Gemini** | [aistudio.google.com](https://aistudio.google.com/app/apikeys) | `AIza...` |

### 2. Store Your API Key

Create a `.env` file in the project root:

```bash
cd "/Users/hshekar/CEFR Evaluation"
cat > .env << 'EOF'
# Your chosen provider's API key
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
GEMINI_API_KEY=AIza...
EOF
```

### 3. Configure config.py

Edit `cefr_pipeline/config.py` and set your provider:

```python
# Choose one: "openai", "openrouter", or "gemini"
API_PROVIDER = "gemini"
```

### 4. Run the Pipeline

```bash
python main.py
```

## Provider Details

### OpenAI
**Best for**: High quality, reliable evaluations

**Setup:**
1. Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create API key (requires paid account with balance)
3. Add to `.env`: `OPENAI_API_KEY=sk-...`
4. In `config.py`: `API_PROVIDER = "openai"`

**Models:**
```python
MODEL_NAME = "gpt-4o-mini"  # Fast and affordable
MODEL_NAME = "gpt-4o"       # More powerful
```

**Cost estimate** (90 dialogue turns):
- gpt-4o-mini: ~$0.10-0.50
- gpt-4o: ~$0.50-2.00

---

### OpenRouter
**Best for**: Multi-model comparison, flexibility

**Setup:**
1. Visit [openrouter.ai](https://openrouter.ai/keys)
2. Create API key (free to start)
3. Add to `.env`: `OPENROUTER_API_KEY=sk-or-...`
4. In `config.py`: `API_PROVIDER = "openrouter"`

**Models:**
```python
MODEL_NAME = "openai/gpt-4o-mini"     # OpenAI via OpenRouter
MODEL_NAME = "anthropic/claude-opus"   # Claude via OpenRouter
MODEL_NAME = "meta-llama/llama-2"      # Llama via OpenRouter
```

**Cost estimate** (90 dialogue turns):
- Varies by model, typically $0.05-1.00

**Note**: OpenRouter often has better rates than direct providers

---

### Google Gemini
**Best for**: Cost-effective, fast evaluations

**Setup:**
1. Visit [aistudio.google.com/app/apikeys](https://aistudio.google.com/app/apikeys)
2. Click "Create API Key"
3. Add to `.env`: `GEMINI_API_KEY=AIza...`
4. In `config.py`: `API_PROVIDER = "gemini"`
5. Install library: `pip install google-generativeai`

**Models:**
```python
MODEL_NAME = "gemini-1.5-flash"   # Fast, cheap (RECOMMENDED)
MODEL_NAME = "gemini-1.5-pro"     # More powerful
MODEL_NAME = "gemini-2.0-flash"   # Latest (when available)
```

**Cost estimate** (90 dialogue turns):
- gemini-1.5-flash: <$0.10 (very cheap!)
- gemini-1.5-pro: ~$0.50-1.00

**Free tier**: Limited usage, sufficient for testing

---

## Switching Providers

### From OpenAI to Gemini:

```python
# In cefr_pipeline/config.py
API_PROVIDER = "gemini"  # Changed from "openai"
# API_KEY will automatically use GEMINI_API_KEY from .env
```

Then run:
```bash
python main.py
```

### Quick Comparison Table

| Feature | OpenAI | OpenRouter | Gemini |
|---------|--------|-----------|--------|
| **Cost** | $$$ | $$ | $ |
| **Speed** | Fast | Fast | Very Fast |
| **Quality** | Excellent | Good-Excellent | Very Good |
| **Models** | GPT-4, GPT-3.5 | 50+ models | Gemini family |
| **Free tier** | No | Limited | Yes (limited) |
| **Setup** | Easy | Easy | Very Easy |
| **Support** | Excellent | Good | Good |

---

## Output File Naming

The output files include your API provider in the name:

| Provider | File Example |
|----------|------------|
| OpenAI | `cefr_results_all_students_openai.xlsx` |
| OpenRouter | `cefr_results_all_students_openrouter.xlsx` |
| Gemini | `cefr_results_all_students_gemini.xlsx` |

This allows you to evaluate the same students with different providers and compare results.

---

## Comparing Results Across Providers

Run evaluations with different providers:

```bash
# Test with Gemini
API_PROVIDER = "gemini"
python main.py

# Test with OpenAI
API_PROVIDER = "openai"
python main.py

# Compare results
python compare_prompts.py
```

---

## Troubleshooting

### "API key not found"
✓ Check that `.env` file exists in project root
✓ Verify key format: `PROVIDER_API_KEY=your_key`
✓ No quotes around the key

### "Module not found" (google-generativeai)
```bash
pip install google-generativeai
```

### "Invalid API key"
- Verify your API key at the provider's website
- Ensure the key hasn't expired or been revoked
- Try recreating a new API key

### "Rate limit exceeded"
- Wait a few minutes before retrying
- Reduce `SAMPLE_PER_STUDENT` in config.py
- Consider upgrading your plan

### "Connection timeout"
- Check internet connection
- Try a different provider
- Check service status pages

---

## Environment Variables (.env)

Example `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-abc123...

# OpenRouter
OPENROUTER_API_KEY=sk-or-xyz789...

# Google Gemini
GEMINI_API_KEY=AIzaSyD...

# Optional: Project-specific settings
PYTHON_ENV=development
```

---

## Monitoring Usage

### OpenAI
- Visit [platform.openai.com/account/billing/overview](https://platform.openai.com/account/billing/overview)
- View usage by model and date

### OpenRouter
- Visit [openrouter.ai/activity](https://openrouter.ai/activity)
- Monitor usage and costs in real-time

### Gemini
- Visit [console.cloud.google.com](https://console.cloud.google.com/)
- Check billing under APIs & Services

---

## Recommendations

**For fastest setup**: Use **Gemini**
- Free tier available
- Simplest integration
- Very fast responses
- Lowest cost

**For best quality**: Use **OpenAI**
- Most reliable
- GPT-4o is state-of-the-art
- Excellent support

**For flexibility**: Use **OpenRouter**
- Compare multiple models easily
- Often cheaper than direct providers
- Access to latest models

---

## Next Steps

1. Choose your provider
2. Get an API key
3. Add it to `.env`
4. Edit `config.py` to set `API_PROVIDER`
5. Run: `python main.py`
6. Results will be in the `output/` directory

For detailed setup instructions, see:
- [GEMINI_API_SETUP.md](GEMINI_API_SETUP.md) - For Gemini
- [README.md](README.md) - General information
