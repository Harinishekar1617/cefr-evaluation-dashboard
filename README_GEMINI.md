# CEFR Evaluation Pipeline - Gemini API Edition

Welcome! Your pipeline now supports Google Gemini API for fast, cost-effective CEFR evaluations.

## 🚀 Quick Start (5 Minutes)

### 1. Get API Key
Visit: https://aistudio.google.com/app/apikeys
- Click "Create API Key"
- Copy your key (starts with `AIza...`)

### 2. Save Key
```bash
cd "/Users/hshekar/CEFR Evaluation"
echo "GEMINI_API_KEY=YOUR_KEY_HERE" > .env
```

### 3. Install Library
```bash
pip install google-generativeai
```

### 4. Run Pipeline
```bash
python main.py
```

### 5. Check Results
```
output/cefr_results_all_students_gemini.xlsx
```

**Done!** ✅

---

## 📚 Documentation Guide

Choose your starting point:

| Document | Best For | Time |
|----------|----------|------|
| **QUICK_SETUP.txt** | Getting started fast | 5 min |
| **SETUP_CHECKLIST.md** | Step-by-step guidance | 10 min |
| **GEMINI_API_SETUP.md** | Detailed Gemini setup | 15 min |
| **API_PROVIDER_GUIDE.md** | Comparing all providers | 20 min |
| **GEMINI_INTEGRATION_SUMMARY.md** | Technical details | 30 min |

---

## 🎯 Choose Your Path

### I Want Fast Setup
→ Read: **QUICK_SETUP.txt**

### I Need Step-by-Step Help
→ Read: **SETUP_CHECKLIST.md**

### I Want to Compare Providers
→ Read: **API_PROVIDER_GUIDE.md**

### I Want Technical Details
→ Read: **GEMINI_INTEGRATION_SUMMARY.md**

### I Want to Test My Setup
→ Run: `python test_api_connection.py`

### I Want Automated Setup
→ Run: `bash setup_gemini.sh`

---

## 💰 Cost Comparison

For evaluating 90 student dialogue turns:

| Provider | Cost | Speed | Quality |
|----------|------|-------|---------|
| **Gemini-1.5-flash** | < $0.10 | ⚡⚡⚡ | ✅ |
| OpenAI gpt-4o-mini | ~$0.20-0.50 | ⚡⚡ | ✅ |
| Gemini-1.5-pro | ~$0.50 | ⚡⚡ | ✅✅ |
| OpenAI gpt-4o | ~$0.50-2.00 | ⚡⚡ | ✅✅ |

**Recommendation**: Use Gemini-1.5-flash for best value.

---

## 🔄 Switching Between Providers

### To Use OpenAI:
Edit `cefr_pipeline/config.py`:
```python
API_PROVIDER = "openai"
```

Get key from: https://platform.openai.com/api-keys
Add to .env: `OPENAI_API_KEY=sk-...`

### To Use OpenRouter:
Edit `cefr_pipeline/config.py`:
```python
API_PROVIDER = "openrouter"
```

Get key from: https://openrouter.ai/keys
Add to .env: `OPENROUTER_API_KEY=sk-or-...`

### To Use Gemini:
Edit `cefr_pipeline/config.py`:
```python
API_PROVIDER = "gemini"
```

Get key from: https://aistudio.google.com/app/apikeys
Add to .env: `GEMINI_API_KEY=AIza...`

---

## 📊 Output Format

Results now include provider in filename:

```
output/
├── cefr_results_all_students_gemini.xlsx      ← Gemini results
├── cefr_individual_turns_all_students_gemini.csv
├── cefr_aggregated_all_students_gemini.csv
├── cefr_results_all_students_openai.xlsx      ← If run with OpenAI
└── cefr_results_all_students_openrouter.xlsx  ← If run with OpenRouter
```

**Justification Format** (clean and organized):
```
• Fluency: Evidence about speech flow
• Accuracy: Grammar errors found
• Range: Vocabulary examples
• Coherence: Organization quality
```

---

## ✅ What's New

### Changes Made:
1. ✅ Multi-provider support (OpenAI, OpenRouter, Gemini)
2. ✅ Gemini API integration
3. ✅ Cost-effective evaluation (<$0.10 per run)
4. ✅ Easy provider switching (1-line config change)
5. ✅ Comprehensive documentation

### Backward Compatible:
- ✅ Existing OpenAI/OpenRouter setups still work
- ✅ No breaking changes to output format
- ✅ Can mix providers (compare results)

---

## 🧪 Testing Your Setup

Before running the full pipeline, test your configuration:

```bash
python test_api_connection.py
```

Expected output:
```
✅ Gemini API key found
✅ google-generativeai is installed
✅ Gemini client initialized successfully
✅ Model 'gemini-1.5-flash' is available
✅ ALL TESTS PASSED!
```

If you see errors, check **QUICK_SETUP.txt** troubleshooting section.

---

## 🐛 Troubleshooting

### "google-generativeai not installed"
```bash
pip install google-generativeai
```

### "Invalid API Key"
- Verify key at: https://aistudio.google.com/app/apikeys
- Key should start with `AIza`
- Check no extra spaces in .env

### "Rate limit exceeded"
- Wait 5 minutes (free tier has limits)
- Reduce `SAMPLE_PER_STUDENT` in config.py
- Consider paid tier

### Still having issues?
See: **QUICK_SETUP.txt** or **SETUP_CHECKLIST.md**

---

## 📋 File Structure

```
/Users/hshekar/CEFR Evaluation/
├── .env                          ← Your API keys go here
├── cefr_pipeline/
│   ├── config.py                 ← Change API_PROVIDER here
│   ├── assessment.py             ← Gemini integration
│   └── ...
├── main.py                       ← Run this
├── output/                       ← Results saved here
├── test_api_connection.py        ← Test your setup
├── QUICK_SETUP.txt               ← 5-min guide
├── SETUP_CHECKLIST.md            ← Step-by-step
├── GEMINI_API_SETUP.md           ← Gemini details
├── API_PROVIDER_GUIDE.md         ← Provider comparison
├── GEMINI_INTEGRATION_SUMMARY.md ← Technical details
└── CHANGES_LOG.md                ← What changed
```

---

## 🎓 Complete Workflow

### Step 1: Configure
1. Get Gemini API key
2. Save in `.env`
3. Run `test_api_connection.py` to verify

### Step 2: Evaluate
1. Run: `python main.py`
2. Monitor progress
3. Wait for completion (5-10 minutes)

### Step 3: Review Results
1. Open: `output/cefr_results_all_students_gemini.xlsx`
2. Check individual turns with justifications
3. Review aggregated student scores

### Step 4 (Optional): Compare
1. Run with different provider
2. Run: `python compare_prompts.py`
3. Analyze differences

---

## 🚀 Next Steps

1. **Get started**: Read **QUICK_SETUP.txt**
2. **Detailed help**: Read **SETUP_CHECKLIST.md**
3. **Learn about providers**: Read **API_PROVIDER_GUIDE.md**
4. **Test connection**: Run `python test_api_connection.py`
5. **Run evaluation**: Run `python main.py`

---

## ❓ FAQ

**Q: Is Gemini cheaper than OpenAI?**
A: Yes! Gemini-1.5-flash costs < $0.10 for 90 evaluations vs. $0.20-2.00 for OpenAI.

**Q: Can I use my existing OpenAI key?**
A: Yes! Just change `API_PROVIDER = "openai"` in config.py.

**Q: What if I want to compare providers?**
A: Run evaluation with different providers - results are saved separately. Use `python compare_prompts.py`.

**Q: Is there a free tier?**
A: Yes! Gemini has a free tier (limited usage). OpenAI requires paid account.

**Q: How do I switch providers?**
A: Change 1 line in `cefr_pipeline/config.py`: `API_PROVIDER = "gemini"` (or "openai" or "openrouter")

**Q: What if my API key is wrong?**
A: Run `python test_api_connection.py` to test. It will tell you what's wrong.

**Q: Can I evaluate the same students with different providers?**
A: Yes! Results are saved with provider name. Easy to compare!

---

## 📚 Resources

- **Google AI Studio**: https://aistudio.google.com/app/apikeys
- **OpenAI API**: https://platform.openai.com/api-keys
- **OpenRouter**: https://openrouter.ai/keys
- **Gemini Docs**: https://ai.google.dev/

---

## 🎯 Recommended Setup

For best results:

1. **Use**: Gemini-1.5-flash (default)
2. **Cost**: < $0.10 per evaluation
3. **Speed**: Very fast (seconds per dialogue)
4. **Quality**: Excellent CEFR assessment
5. **Free tier**: Available for testing

---

## 💡 Tips

- ✅ Start with Gemini for cost savings
- ✅ Test setup with `test_api_connection.py` first
- ✅ Monitor costs on Google Cloud Console
- ✅ Run with different providers to compare quality
- ✅ Keep all API keys in `.env` for easy switching

---

## 📞 Support

If you get stuck:

1. Run: `python test_api_connection.py`
2. Check: **QUICK_SETUP.txt** (FAQ section)
3. Read: **SETUP_CHECKLIST.md** (troubleshooting)
4. Refer: **GEMINI_API_SETUP.md** (detailed guide)

---

## ✨ Summary

Your CEFR pipeline now supports **3 API providers** with **automatic library installation**, **robust error handling**, and **comprehensive documentation**.

**Start in 5 minutes**: See **QUICK_SETUP.txt**

**Questions?** Check the documentation files above.

**Ready?** Run: `python main.py`

---

**Happy evaluating! 🎓**
