"""
Main script to orchestrate the CEFR evaluation pipeline.

This script:
1. Loads all transcripts
2. Filters by topics and word count
3. Samples dialogue turns per student
4. Evaluates each turn using OpenAI API (with selected prompt version)
5. Aggregates results and saves to Excel/CSV
6. Tags results with prompt version for comparison
"""

import pandas as pd
from pathlib import Path

# Import from cefr_pipeline modules
from cefr_pipeline import config
from cefr_pipeline.transcripts import load_all_transcripts
from cefr_pipeline.assessment import initialize_openai_client, test_model_availability, evaluate_student_dialogue
from cefr_pipeline.prompt_manager import PromptManager
from cefr_pipeline.utils import (
    install_if_needed,
    filter_by_topics,
    keep_latest_session_per_student,
    calculate_word_count_per_turn,
    filter_by_min_mode_words,
    filter_by_word_count_per_turn,
    sample_turns_per_student,
    aggregate_by_mode,
    save_results_to_excel,
    save_results_to_csv
)


def main():
    """
    Main pipeline for CEFR evaluation.
    """
    print("=" * 80)
    print("CEFR EVALUATION PIPELINE")
    print("=" * 80)
    print()

    # ========================================================================
    # STEP 1: LOAD TRANSCRIPTS
    # ========================================================================
    print("STEP 1: Loading transcripts...")
    print("-" * 80)

    df = load_all_transcripts(config.TRANSCRIPT_DIR)
    print(f"Columns: {list(df.columns)}")
    print()

    # ========================================================================
    # STEP 2: FILTER BY TOPIC
    # ========================================================================
    print("STEP 2: Filtering by topic...")
    print("-" * 80)

    df = filter_by_topics(df, config.TOPICS_TO_KEEP)
    print()

    # ========================================================================
    # STEP 3: KEEP LATEST SESSION PER STUDENT
    # ========================================================================
    print("STEP 3: Keeping latest session per student-activity...")
    print("-" * 80)

    df = keep_latest_session_per_student(df)
    print()

    # ========================================================================
    # STEP 4: FILTER BY MINIMUM MODE WORDS
    # ========================================================================
    print("STEP 4: Filtering students by typical word count...")
    print("-" * 80)

    # Calculate word count per turn
    df = calculate_word_count_per_turn(df)

    # Filter for students with mode >= MIN_MODE_WORDS
    df, qualified_students = filter_by_min_mode_words(df, config.MIN_MODE_WORDS)

    # Remove word count column (no longer needed)
    df = df.drop('total_words', axis=1)
    print()

    # ========================================================================
    # STEP 5: FILTER TURNS BY MINIMUM WORD COUNT
    # ========================================================================
    print("STEP 5: Filtering individual dialogue turns by word count...")
    print("-" * 80)

    df = calculate_word_count_per_turn(df)
    df = filter_by_word_count_per_turn(df, config.MIN_WORDS_PER_TURN)
    print()

    # ========================================================================
    # STEP 6: SAMPLE TURNS PER STUDENT
    # ========================================================================
    print("STEP 6: Sampling dialogue turns per student...")
    print("-" * 80)

    df = sample_turns_per_student(df,
                                  n_samples=config.SAMPLE_PER_STUDENT,
                                  random_state=config.RANDOM_SEED)

    # Remove word count column
    df = df.drop('total_words', axis=1)
    df = df.drop('session_date', axis=1)
    print()

    # ========================================================================
    # STEP 7: LOAD PROMPT VERSION
    # ========================================================================
    print("STEP 7: Loading prompt version...")
    print("-" * 80)

    # Initialize prompt manager
    prompts_file = config.PROJECT_ROOT / "prompts.json"
    prompt_manager = PromptManager(prompts_file)

    # Display available prompts
    prompt_manager.print_available_prompts()

    # Load selected prompt version
    try:
        selected_prompt = prompt_manager.get_prompt(config.PROMPT_VERSION)
        prompt_info = prompt_manager.get_version_info(config.PROMPT_VERSION)
        print(f"\n✅ Using prompt version: {config.PROMPT_VERSION}")
        print(f"   Version: {prompt_info['version']}")
        print(f"   Description: {prompt_info['description']}\n")
    except ValueError as e:
        print(f"\n❌ ERROR: {e}")
        print(f"Please set PROMPT_VERSION in config.py to one of the available versions.")
        return

    # ========================================================================
    # STEP 8: INITIALIZE API CLIENT AND TEST MODELS
    # ========================================================================
    print(f"STEP 8: Setting up {config.API_PROVIDER.upper()} client...")
    print("-" * 80)

    # Install required dependencies
    install_if_needed('openai')

    # Initialize client with OpenAI
    try:
        client = initialize_openai_client(
            config.API_KEY,
            provider=config.API_PROVIDER,
            base_url=config.API_BASE_URL
        )
        print(f"✅ Connected to: {config.API_BASE_URL}")
    except Exception as e:
        print(f"\n❌ ERROR: Failed to initialize client!")
        print(f"   {str(e)}")
        print(f"   Please check your OPENAI_API_KEY and OPENAI_BASE_URL in .env")
        return

    # Use the configured model
    available_model = config.MODEL_NAME

    print(f"\n✅ Using model: {available_model}")
    print(f"   Provider: OpenAI (PayPal Network)")
    print(f"   Base URL: {config.API_BASE_URL}\n")

    # ========================================================================
    # STEP 9: EVALUATE EACH DIALOGUE TURN
    # ========================================================================
    print("STEP 9: Evaluating dialogue turns with OpenAI API...")
    print("-" * 80)

    # Determine which students to evaluate
    if config.EVALUATE_ALL_STUDENTS:
        df_to_evaluate = df.copy()
        print(f"Evaluating ALL students: {df['student_name'].nunique()}")
        print(f"Total dialogue turns: {len(df)}")
    else:
        df_to_evaluate = df[df['student_name'] == config.SINGLE_STUDENT_NAME].copy()
        if len(df_to_evaluate) == 0:
            print(f"❌ ERROR: Student '{config.SINGLE_STUDENT_NAME}' not found!")
            print(f"Available students: {sorted(df['student_name'].unique())}")
            return

        print(f"Evaluating single student: {config.SINGLE_STUDENT_NAME}")
        print(f"Dialogue turns: {len(df_to_evaluate)}")

    print()

    # Evaluate each dialogue turn
    individual_results = []

    for idx, (data_idx, row) in enumerate(df_to_evaluate.iterrows()):
        transcript_id = row['transcript_id']
        student_name = row['student_name']
        student_text = row['student_text']

        # Progress indicator
        if (idx + 1) % 10 == 0:
            print(f"  Progress: {idx + 1}/{len(df_to_evaluate)} dialogue turns evaluated...")

        # Call evaluation function with selected prompt
        result = evaluate_student_dialogue(
            student_text=student_text,
            client=client,
            model_name=available_model,
            system_prompt=selected_prompt,
            provider="openai"  # Using OpenAI-compatible API from OpenRouter
        )

        # Store result with prompt version tag
        individual_results.append({
            'transcript_id': transcript_id,
            'student_name': student_name,
            'dialogue_turn_number': idx + 1,
            'prompt_version': config.PROMPT_VERSION,
            'range': result['range_level'],
            'accuracy': result['accuracy_level'],
            'fluency': result['fluency_level'],
            'coherence': result['coherence_level'],
            'overall_cefr_level': result['overall_cefr_level'],
            'justification': result['justification']
        })

    print(f"\n✅ Evaluated all {len(individual_results)} dialogue turns!")
    print()

    # Convert to DataFrame
    df_individual_results = pd.DataFrame(individual_results)

    # ========================================================================
    # STEP 10: AGGREGATE RESULTS BY STUDENT
    # ========================================================================
    print("STEP 10: Aggregating results by MODE (most frequent level)...")
    print("-" * 80)

    df_aggregated_results = aggregate_by_mode(df_individual_results)
    print()

    # ========================================================================
    # STEP 11: SAVE RESULTS
    # ========================================================================
    print("STEP 11: Saving results...")
    print("-" * 80)

    # Create output filename with prompt version
    if config.EVALUATE_ALL_STUDENTS:
        file_suffix = f"all_students_{config.PROMPT_VERSION}"
    else:
        file_suffix = f"{config.SINGLE_STUDENT_NAME.replace(' ', '_').lower()}_{config.PROMPT_VERSION}"

    # Save to Excel
    excel_path = config.OUTPUT_DIR / f"cefr_results_{file_suffix}.xlsx"
    save_results_to_excel(df_individual_results, df_aggregated_results, excel_path)
    print(f"✅ Excel file: {excel_path}")

    # Save to CSV
    save_results_to_csv(df_individual_results, df_aggregated_results,
                       config.OUTPUT_DIR, file_suffix)

    print()

    # ========================================================================
    # STEP 12: DISPLAY RESULTS SUMMARY
    # ========================================================================
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()

    print(f"📋 Prompt Version Used: {config.PROMPT_VERSION}")
    print(f"   {prompt_info['description']}\n")

    if config.EVALUATE_ALL_STUDENTS:
        print(f"Evaluated {len(df_aggregated_results)} students")
        print(f"Total dialogue turns: {len(df_individual_results)}\n")
        print(df_aggregated_results[['student_name', 'num_dialogue_turns',
                                      'range_mode', 'accuracy_mode',
                                      'fluency_mode', 'overall_mode']].to_string(index=False))
    else:
        for _, row in df_aggregated_results.iterrows():
            print(f"Student: {row['student_name']}")
            print(f"Dialogue turns evaluated: {row['num_dialogue_turns']}\n")
            print("MODE SCORES (Most Frequent Level):")
            print(f"  Range:     {row['range_mode']:15s} (varies: {row['range_variance']})")
            print(f"  Accuracy:  {row['accuracy_mode']:15s} (varies: {row['accuracy_variance']})")
            print(f"  Fluency:   {row['fluency_mode']:15s} (varies: {row['fluency_variance']})")
            print(f"  Coherence: {row['coherence_mode']}")
            print(f"  Overall:   {row['overall_mode']}\n")

    print("=" * 80)
    print("✅ PIPELINE COMPLETE")
    print("=" * 80)
    print("\n💡 TIP: To test a different prompt version:")
    print(f"   1. Edit config.py and change PROMPT_VERSION to another version")
    print(f"   2. Run 'python main.py' again")
    print(f"   3. Results will be saved with the new prompt version in the filename")
    print(f"   4. Use compare_prompts.py to compare different versions\n")


if __name__ == "__main__":
    main()
