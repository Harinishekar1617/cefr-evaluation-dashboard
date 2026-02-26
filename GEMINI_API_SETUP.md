# Setting Up and Using Google Gemini API

This guide explains how to configure and use Google's Gemini API with the CEFR Evaluation pipeline.

## Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click "Create API Key"
3. Select "Create new API key in new project" or use an existing project
4. Copy your API key (it will start with `AIza...`)

**Note**: Free tier available with rate limits. Visit [Google AI Studio pricing](https://aistudio.google.com/app/apikeys) for details.

## Step 2: Configure the API Key

You have two options:

### Option A: Using .env file (Recommended)
Create a `.env` file in the project root directory:

```bash
cd "/Users/hshekar/CEFR Evaluation"
echo "GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE" > .env
```

Replace `YOUR_GEMINI_KEY_HERE` with your actual Gemini API key.

### Option B: Direct Configuration in config.py
Edit `cefr_pipeline/config.py` and update:

```python
GEMINI_API_KEY = "YOUR_GEMINI_KEY_HERE"
```

## Step 3: Install Google Generative AI Library

```bash
pip install google-generativeai
```

The pipeline will auto-install this if needed, but it's recommended to install it beforehand.

## Step 4: Configure to Use Gemini

Edit `cefr_pipeline/config.py` and change:

```python
# Choose API provider: "openai", "openrouter", or "gemini"
API_PROVIDER = "gemini"  # Set to "gemini"

# Gemini model options (use one of these):
# MODEL_NAME = "gemini-1.5-flash"   # Faster, cheaper (default)
# MODEL_NAME = "gemini-1.5-pro"     # More powerful
# MODEL_NAME = "gemini-2.0-flash"   # Latest model (if available)
```

## Step 5: Run the Pipeline

```bash
cd "/Users/hshekar/CEFR Evaluation"
python main.py
```

The pipeline will:
1. Test the Gemini API connection
2. Evaluate all dialogue turns using Gemini
3. Generate results with the same compact justification format
4. Save to `output/cefr_results_all_students_gemini.xlsx`

## Available Gemini Models

| Model | Speed | Cost | Capabilities |
|-------|-------|------|--------------|
| `gemini-1.5-flash` | Fast | Low | Good for general tasks |
| `gemini-1.5-pro` | Slower | Higher | More advanced reasoning |
| `gemini-2.0-flash` | Fast | Very Low | Latest model (when available) |

**Recommendation**: Start with `gemini-1.5-flash` for cost efficiency.

## Switching Between API Providers

You can easily switch between providers by editing `config.py`:

```python
# For OpenAI
API_PROVIDER = "openai"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-...")

# For OpenRouter
API_PROVIDER = "openrouter"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "sk-or-...")

# For Gemini
API_PROVIDER = "gemini"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIza...")
```

Then run: `python main.py`

## Comparing Results Across Providers

After running evaluations with different providers, you can compare results:

```bash
python compare_prompts.py
```

This will show how Gemini results differ from OpenAI/OpenRouter results.

## Troubleshooting

### "google-generativeai not installed"
```bash
pip install google-generativeai
```

### "Invalid API Key"
- Double-check your API key in `.env` or `config.py`
- Ensure there are no extra spaces or quotes around the key
- Visit [Google AI Studio](https://aistudio.google.com/app/apikeys) to verify your key is active

### "Rate limit exceeded"
- Gemini has rate limits on the free tier
- Wait a few minutes before retrying
- Consider upgrading to a paid plan

### "Connection timeout"
- Check your internet connection
- Try with a simpler prompt first
- Check if Gemini API is operational at [Google Cloud Status](https://status.cloud.google.com/)

## Output Files

When using Gemini, output files will include "gemini" in the filename:
- `cefr_results_all_students_gemini.xlsx`
- `cefr_individual_turns_all_students_gemini.csv`
- `cefr_aggregated_all_students_gemini.csv`

## Cost Estimate

**Gemini-1.5-Flash** (as of Feb 2026):
- ~90 dialogue turns: Very low cost (often <$0.10)
- 1 prompt evaluation typically: <$0.001 per turn

Monitor your usage at [Google Cloud Console](https://console.cloud.google.com/).

## API Limitations

- **Max tokens**: 1,500 tokens per response
- **Request rate**: Check [Gemini documentation](https://ai.google.dev/) for limits
- **Free tier**: Limited to certain number of requests per day

## Next Steps

1. Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Add it to `.env` or `config.py`
3. Run: `python main.py`
4. Check results in the `output/` directory
