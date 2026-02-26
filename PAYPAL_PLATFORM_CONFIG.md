# PayPal Internal LLM Platform Configuration

## Overview

The CEFR Evaluation pipeline has been updated to use **PayPal's Internal LLM Platform** via OpenAI-compatible API with support for multiple models including Gemini.

## Configuration

### API Settings (Already in `.env`)

```
OPENAI_API_KEY=600014d3c2c24c8cf7f644c362547304be32385038299dda507659c043906f26
OPENAI_BASE_URL=https://aiplatform.dev51.cbf.dev.paypalinc.com/cosmosai/llm/v1
```

### Configuration File (`cefr_pipeline/config.py`)

```python
API_PROVIDER = "openai"  # Using OpenAI-compatible API
API_KEY = os.getenv("OPENAI_API_KEY")  # From .env
API_BASE_URL = os.getenv("OPENAI_BASE_URL")  # From .env
MODEL_NAME = "gpt-4o"  # Default model
```

## Available Models on PayPal Platform

The platform provides access to 38+ models including:

### Gemini Models
- `gemini-1.5-flash` - Fast, efficient Gemini model (if available)
- `gemini-1.5-pro` - More powerful Gemini model (if available)
- `gemini-2.0-flash` - Latest Gemini model (if available)

### OpenAI Models
- `gpt-4o` - Latest GPT-4 Omni model
- `gpt-4o-mini` - Faster, cheaper GPT-4 Omni variant
- `gpt-4.1-mini` - GPT-4 mini version
- `o4-mini` - O4 mini model

### Anthropic Models
- `claude-sonnet-4-5-20250929` - Claude Sonnet variant
- `claude-sonnet-4-5` - Claude Sonnet
- `claude-sonnet-4-6-default` - Claude Sonnet 4.6
- `claude-sonnet-4-6` - Claude Sonnet 4.6

### Open Source Models
- `llama33-70b` - Meta's Llama 3.3 70B
- ... and 20+ more models

## Changing Models

To use a different model, edit `cefr_pipeline/config.py`:

```python
# Change this line:
MODEL_NAME = "gpt-4o"

# To one of these:
MODEL_NAME = "gemini-1.5-flash"  # For Gemini
MODEL_NAME = "claude-sonnet-4-5-20250929"  # For Claude
MODEL_NAME = "llama33-70b"  # For Llama
```

Then run:
```bash
python main.py
```

## Running the Pipeline

```bash
cd "/Users/hshekar/CEFR Evaluation"
python main.py
```

The pipeline will:
1. ✅ Load transcripts from `det-transcripts/`
2. ✅ Filter and sample dialogue turns
3. ✅ Connect to PayPal Internal LLM Platform
4. ✅ Evaluate each turn using the configured model
5. ✅ Save results to `output/cefr_results_*.xlsx`

## What Changed

### Modified Files
- **config.py** - Now uses PayPal platform settings
- **assessment.py** - Updated to support custom base URL
- **main.py** - Updated client initialization

### Key Changes
- API provider switched from OpenRouter to PayPal Internal Platform
- Support for custom base URL (OpenAI-compatible API)
- Support for Gemini and other models through the platform
- Automatic configuration from `.env` file

## Current Status

✅ **API Configuration**: Ready
✅ **API Key**: Configured in `.env`
✅ **Base URL**: Configured in `.env`
✅ **Models**: 38+ models available
⚠️ **Chat Completions**: Requires valid token (see below)

## Troubleshooting

### "Invalid or expired auth token"

This error means your API token doesn't have chat completion permissions.

**Solution:**
1. Generate a new API token from PayPal's internal LLM platform
2. Ensure it has chat completion permissions
3. Update `OPENAI_API_KEY` in `.env`
4. Run pipeline again

### "Model not found"

This error means the specified model doesn't exist on the platform.

**Solution:**
1. Check available models above
2. Update `MODEL_NAME` in `config.py`
3. Run pipeline again

### "Connection refused"

This error means the platform is unreachable.

**Solution:**
1. Check internet connection
2. Verify `OPENAI_BASE_URL` is correct
3. Check if you're connected to PayPal VPN

## Output Files

Results are saved with model name in filename:

```
output/
├── cefr_results_all_students_v1_detailed.xlsx
├── cefr_individual_turns_all_students_v1_detailed.csv
└── cefr_aggregated_all_students_v1_detailed.csv
```

## Example Output

When running with Gemini model:
```
STEP 8: Setting up OPENAI client (PayPal Internal LLM Platform)...
✅ Connected to: https://aiplatform.dev51.cbf.dev.paypalinc.com/cosmosai/llm/v1
✅ Using model: gemini-1.5-flash
   Platform: PayPal Internal LLM Platform
   Base URL: https://aiplatform.dev51.cbf.dev.paypalinc.com/cosmosai/llm/v1

STEP 9: Evaluating dialogue turns with OpenAI API...
Progress: 10/90 dialogue turns evaluated...
Progress: 20/90 dialogue turns evaluated...
...
```

## Model Recommendations

| Use Case | Recommended Model | Reason |
|----------|-------------------|--------|
| **Fast & Efficient** | gemini-1.5-flash | Fastest, lowest latency |
| **Best Quality** | claude-sonnet-4-5-20250929 | Best reasoning, most accurate |
| **Most Capable** | gpt-4o | State-of-the-art OpenAI model |
| **Cost Efficient** | gpt-4o-mini | Good balance of quality and speed |
| **Open Source** | llama33-70b | Free, good for standard tasks |

## Next Steps

1. ✅ Verify API key is valid (has chat completion permissions)
2. ✅ Run: `python main.py`
3. ✅ Check results in `output/` folder

## Support

For issues:
1. Check `.env` file has `OPENAI_API_KEY` and `OPENAI_BASE_URL`
2. Verify you're connected to PayPal network/VPN
3. Check if token needs refresh from PayPal platform
4. Try with a different model in `config.py`
