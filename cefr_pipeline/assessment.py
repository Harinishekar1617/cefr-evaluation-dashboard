"""
CEFR assessment functions.
Calls OpenAI, OpenRouter, or Google Gemini API to evaluate student dialogue turns and scores them on CEFR levels.
"""

import json
import re
from typing import Dict, Union
from openai import OpenAI


def initialize_client(api_key: str, provider: str = "openai"):
    """
    Initialize and return an API client for the specified provider.

    Args:
        api_key: API key for the provider
        provider: "openai", "openrouter", or "gemini"

    Returns:
        Initialized client (OpenAI object or Gemini GenerativeModel)
    """
    if provider == "gemini":
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            return genai.GenerativeModel("gemini-1.5-flash")
        except ImportError:
            raise ImportError("google-generativeai not installed. Install with: pip install google-generativeai")
    elif provider == "openrouter":
        # OpenRouter uses OpenAI-compatible API with custom endpoint
        return OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    else:
        # Standard OpenAI
        return OpenAI(api_key=api_key)


def initialize_openai_client(api_key: str, provider: str = "openai", base_url: str = None) -> OpenAI:
    """
    Initialize and return an OpenAI-compatible client.

    Args:
        api_key: API key (OpenAI or OpenRouter)
        provider: "openai" or "openrouter"
        base_url: Optional custom base URL (e.g., for PayPal internal platform)

    Returns:
        Initialized OpenAI client
    """
    if provider == "openrouter":
        # OpenRouter uses OpenAI-compatible API with custom endpoint
        return OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    elif base_url:
        # Custom base URL provided (e.g., PayPal internal platform)
        return OpenAI(api_key=api_key, base_url=base_url)
    else:
        # Standard OpenAI
        return OpenAI(api_key=api_key)


def test_model_availability(client, provider: str = "openai", models_to_test: list = None) -> str:
    """
    Test which models are available with the given API key.

    Args:
        client: API client (OpenAI client or Gemini GenerativeModel)
        provider: "openai", "openrouter", or "gemini"
        models_to_test: List of model names to test (defaults based on provider)

    Returns:
        Name of first available model, or None if no models work
    """
    if models_to_test is None:
        if provider == "gemini":
            models_to_test = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
        else:
            models_to_test = ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"]

    print("Testing available models with your API key...\n")

    for model in models_to_test:
        try:
            print(f"Testing {model}...", end=" ")

            if provider == "gemini":
                # For Gemini, test with a simple generation
                response = client.generate_content(
                    "test",
                    generation_config={"max_output_tokens": 5}
                )
                if response.text:
                    print("✅ WORKS")
                    return model
            else:
                # For OpenAI/OpenRouter
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                print("✅ WORKS")
                return model
        except Exception as e:
            print(f"✗ {type(e).__name__}")

    print("\n❌ No models available.")
    return None


def extract_cefr_level(value: str) -> str:
    """
    Extract CEFR level from a string that might contain multiple levels or extra text.

    Examples:
        "A1|A2|B1|B2" → "A1"
        "A2 (strong)" → "A2"
        "B1" → "B1"

    Args:
        value: String that might contain CEFR level

    Returns:
        First valid CEFR level found, or "Unknown" if none found
    """
    if not value or value == 'Unknown':
        return 'Unknown'

    if not isinstance(value, str):
        return 'Unknown'

    # Valid CEFR levels
    valid_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'Strong A1']

    # If string contains pipes, take the first one
    if '|' in value:
        first = value.split('|')[0].strip()
        return first if first in valid_levels else 'Unknown'

    # Look for any valid level in the string
    for level in valid_levels:
        if level in value:
            return level

    return 'Unknown'


def evaluate_student_dialogue(student_text: str,
                             client,
                             model_name: str,
                             system_prompt: str,
                             provider: str = "openai") -> Dict:
    """
    Evaluate a single student dialogue turn using OpenAI, OpenRouter, or Gemini API.

    Calls the API with the student text and system prompt, parses the JSON response,
    and extracts CEFR scores.

    Args:
        student_text: The student's response to evaluate
        client: API client (OpenAI client or Gemini GenerativeModel)
        model_name: Name of the model to use (e.g., "gpt-4o-mini" or "gemini-1.5-flash")
        system_prompt: System prompt with CEFR evaluation instructions
        provider: "openai", "openrouter", or "gemini"

    Returns:
        Dictionary with keys:
        - range_level: Vocabulary range (A1, A2, B1, B2)
        - accuracy_level: Grammar accuracy
        - fluency_level: Speech fluency
        - coherence_level: Idea organization
        - overall_cefr_level: Overall assessment
        - justification: Full JSON response from API
    """
    try:
        # Prepare the user message with the student transcript
        user_message = f"""Here is the student transcript you will be assessing:

<transcript>
{student_text}
</transcript>

Please evaluate this transcript according to CEFR guidelines as instructed. Return only valid JSON."""

        # Combine system prompt and user message for Gemini (doesn't support system role)
        if provider == "gemini":
            full_message = f"{system_prompt}\n\n{user_message}"
            response = client.generate_content(
                full_message,
                generation_config={"temperature": 0.2, "max_output_tokens": 1500}
            )
            response_text = response.text
        else:
            # Call OpenAI/OpenRouter API
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2,  # Low temperature for consistent scoring
                max_tokens=1500
            )
            response_text = response.choices[0].message.content

        # Parse JSON from response with better error handling
        result = _extract_json_from_response(response_text)

        # Extract scores from the API response
        # The API returns results in 'cefr_scores' object
        if 'cefr_scores' in result:
            fluency = extract_cefr_level(result['cefr_scores'].get('fluency', 'Unknown'))
            accuracy = extract_cefr_level(result['cefr_scores'].get('accuracy', 'Unknown'))
            range_level = extract_cefr_level(result['cefr_scores'].get('range', 'Unknown'))
            coherence = extract_cefr_level(result['cefr_scores'].get('coherence', 'Unknown'))
            overall = extract_cefr_level(result.get('overall_level', 'Unknown'))

            return {
                'range_level': range_level,
                'accuracy_level': accuracy,
                'fluency_level': fluency,
                'coherence_level': coherence,
                'overall_cefr_level': overall,
                'justification': format_justification_for_storage(result, format_type="compact")
            }
        else:
            # Fallback for different JSON structure
            return {
                'range_level': extract_cefr_level(result.get('range_level', 'Unknown')),
                'accuracy_level': extract_cefr_level(result.get('accuracy_level', 'Unknown')),
                'fluency_level': extract_cefr_level(result.get('fluency_level', 'Unknown')),
                'coherence_level': extract_cefr_level(result.get('coherence_level', 'Unknown')),
                'overall_cefr_level': extract_cefr_level(result.get('overall_cefr_level', 'Unknown')),
                'justification': format_justification_for_storage(result, format_type="compact")
            }

    except Exception as e:
        # Return error response if anything goes wrong
        error_msg = f"{type(e).__name__}: {str(e)}"
        return _create_error_response(error_msg)


def _extract_json_from_response(response_text: str) -> Dict:
    """
    Extract and parse JSON from API response with robust error handling.

    Tries multiple strategies:
    1. Direct JSON parse
    2. Extract from first { to last }
    3. Try to fix common JSON formatting issues
    4. Use json.JSONDecoder in non-strict mode and repair manually

    Args:
        response_text: Raw response text from API

    Returns:
        Parsed JSON dictionary or error response
    """
    # Strategy 1: Try direct parsing (response is pure JSON)
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from first { to last }
    first_brace = response_text.find('{')
    last_brace = response_text.rfind('}')

    if first_brace == -1 or last_brace == -1 or first_brace >= last_brace:
        return _create_error_response('Could not find JSON object in response')

    json_str = response_text[first_brace:last_brace + 1]

    # Strategy 3: Try to parse extracted JSON directly
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Strategy 4: Try to fix common JSON formatting issues
    try:
        # Fix unescaped newlines and problematic quotes within strings
        json_str_fixed = json_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        return json.loads(json_str_fixed)
    except json.JSONDecodeError:
        pass

    # Strategy 5: Replace problematic quotes with escaped versions
    try:
        # More aggressive fix for quotes within JSON strings
        # This finds patterns where quotes appear within string values
        json_str_fixed = re.sub(r'": "([^"]*)"([^"]*)"', r'": "\1\\\"\2"', json_str)
        return json.loads(json_str_fixed)
    except json.JSONDecodeError:
        pass

    # Strategy 6: If all else fails, try using ast.literal_eval or building a minimal response
    try:
        # Last resort: try to extract individual fields using regex
        result = {}

        # Try to find cefr_scores block
        cefr_match = re.search(r'"cefr_scores"\s*:\s*\{([^}]+)\}', json_str, re.DOTALL)
        if cefr_match:
            cefr_content = cefr_match.group(1)
            result['cefr_scores'] = {}
            for level_type in ['fluency', 'accuracy', 'range', 'coherence']:
                level_match = re.search(rf'"{level_type}"\s*:\s*"([^"]*)"', cefr_content)
                if level_match:
                    result['cefr_scores'][level_type] = level_match.group(1)

        # Try to find overall_level
        overall_match = re.search(r'"overall_level"\s*:\s*"([^"]*)"', json_str)
        if overall_match:
            result['overall_level'] = overall_match.group(1)

        # Try to find evidence/reasoning
        evidence_match = re.search(r'"key_evidence"\s*:\s*(\{[^}]+(?:\[[^\]]*\][^}]*)*\})', json_str, re.DOTALL)
        if evidence_match:
            try:
                result['key_evidence'] = json.loads(evidence_match.group(1))
            except:
                pass

        if 'cefr_scores' in result:
            return result
    except Exception:
        pass

    # If all strategies fail, return error response
    return _create_error_response('Could not parse JSON from response after multiple attempts')


def _create_error_response(error_message: str) -> Dict:
    """
    Create a standardized error response when evaluation fails.

    Args:
        error_message: Description of the error

    Returns:
        Dictionary with all scores set to 'Error' and error message
    """
    return {
        'range_level': 'Error',
        'accuracy_level': 'Error',
        'fluency_level': 'Error',
        'coherence_level': 'Error',
        'overall_cefr_level': 'Error',
        'justification': error_message
    }


def format_justification_compact(result: Dict) -> str:
    """
    Format justification by extracting evidence for each parameter without repeating scores.

    Extracts evidence/reasoning for fluency, accuracy, range, and coherence from the API response,
    including one example from the transcript where available.

    Args:
        result: Dictionary with the API response containing cefr_scores and evidence

    Returns:
        Formatted string with compact justification organized by parameter
    """
    if isinstance(result, str):
        # If already a string (error message), return as is
        return result

    lines = []

    # Extract evidence from different prompt formats
    key_evidence = result.get('key_evidence', {})
    reasoning = result.get('reasoning', {})

    # Define the parameters in order
    parameters = [
        ('fluency', 'fluency_evidence', 'fluency_note'),
        ('accuracy', 'accuracy_errors', 'accuracy_note'),
        ('range', 'range_vocabulary', 'range_note'),
        ('coherence', 'coherence_structure', 'coherence_note')
    ]

    for param_name, v1_key, v2_key in parameters:
        # Try v1 format first (detailed evidence)
        if v1_key in key_evidence:
            evidence = key_evidence[v1_key]
            if isinstance(evidence, list):
                evidence_str = "; ".join(str(e) for e in evidence)
            else:
                evidence_str = str(evidence)
            lines.append(f"• {param_name.capitalize()}: {evidence_str}")
        # Then try v2 format (brief notes)
        elif v2_key in reasoning:
            lines.append(f"• {param_name.capitalize()}: {reasoning[v2_key]}")

    # If no evidence found, return original JSON as fallback
    if not lines:
        return json.dumps(result, indent=2)

    return "\n".join(lines)


def format_justification_for_storage(result: Dict, format_type: str = "compact") -> str:
    """
    Format the API response justification based on the desired format.

    Args:
        result: Dictionary with the API response
        format_type: "compact" (default) for concise evidence-only format,
                    "full" for complete JSON response

    Returns:
        Formatted justification string
    """
    if format_type == "compact":
        return format_justification_compact(result)
    else:
        # Return full JSON
        return json.dumps(result, indent=2)
