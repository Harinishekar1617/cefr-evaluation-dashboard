"""
Calculate daily practice time analytics for students.

This module analyzes student speaking time from DET transcripts and computes:
- Daily practice totals (minutes of student speaking per day)
- Average daily practice duration for each student
- Statistics like min/max daily practice time

Key Feature: Only counts STUDENT speaking time, ignoring interviewer responses.
Speaking duration is extracted from timestamp ranges in transcripts (e.g., "0:01-0:15").
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime


def calculate_daily_practice_averages(transcript_dir: Path):
    """
    Calculate average daily practice time for each student.

    This function performs the following steps:
    1. Loads all transcript files from the directory
    2. Extracts ONLY student speaking time from timestamp ranges
    3. Parses timestamp ranges (e.g., "0:01-0:15") to compute duration
    4. Sums up student practice time per day per student
    5. Calculates average daily practice time and related statistics

    Args:
        transcript_dir: Path to directory containing transcript .txt files
                       (e.g., Path("/Users/hshekar/CEFR Evaluation/det-transcripts"))

    Returns:
        Tuple of two DataFrames:
        - averages: Summary statistics per student
          Columns: student_name, num_practice_days, total_practice_minutes,
                  avg_daily_minutes, min_daily_minutes, max_daily_minutes
        - daily_totals: Daily breakdown per student
          Columns: student_name, session_date, daily_total_minutes
    """

    # ========================================================================
    # STEP 1: FIND AND PREPARE TO PARSE ALL TRANSCRIPT FILES
    # ========================================================================
    print("=" * 80)
    print("CALCULATING STUDENT DAILY PRACTICE TIME")
    print("=" * 80)
    print()

    print("STEP 1: Finding transcript files...")
    print("-" * 80)

    # Find all .txt files in the transcript directory
    transcript_files = sorted(transcript_dir.glob('*.txt'))
    print(f"Found {len(transcript_files)} transcript files")
    print()

    # ========================================================================
    # STEP 2: PARSE RAW TRANSCRIPTS TO EXTRACT STUDENT SPEAKING TIMES
    # ========================================================================
    print("STEP 2: Parsing transcripts and extracting student speaking times...")
    print("-" * 80)

    # List to store all student speaking segments
    all_records = []

    # Iterate through each transcript file
    for file_path in transcript_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # ================================================================
            # Parse metadata from header (between first and second "---")
            # ================================================================
            parts = content.split('---')
            if len(parts) < 3:
                # File doesn't have expected format (header + dialogue sections)
                continue

            # Extract and parse header section (contains metadata)
            header = parts[1].strip()

            # Create dictionary to store metadata
            metadata = {}
            for line in header.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    # Clean up key: lowercase and replace spaces with underscores
                    key = key.strip().replace(' ', '_').lower()
                    metadata[key] = value.strip()

            # Extract key metadata fields
            student_name = metadata.get('student_name', 'Unknown')
            session_time = metadata.get('session_time', '')

            # Parse session date from session_time
            # Expected format: "2025-12-11 21:26:37"
            try:
                session_datetime = pd.to_datetime(session_time)
                session_date = session_datetime.date()
            except:
                # If parsing fails, skip this file
                continue

            # ================================================================
            # Parse dialogue section to find all student speaking segments
            # ================================================================
            dialogue_section = parts[2].strip()

            # Regular expression to match student speaking patterns
            # Pattern: "Student (0:01-0:15): <text>"
            # We extract the timestamps in format "HH:MM-HH:MM" or "M:SS-M:SS"
            student_pattern = r'Student\s*\(([0-9:]+)-([0-9:]+)\):'

            # Find all student speaking segments in this transcript
            for match in re.finditer(student_pattern, dialogue_section):
                start_str = match.group(1)  # e.g., "0:01"
                end_str = match.group(2)     # e.g., "0:15"

                # ============================================================
                # Convert timestamp strings to seconds
                # ============================================================
                try:
                    # Split start timestamp into minutes and seconds
                    start_parts = start_str.split(':')
                    start_min = int(start_parts[0])
                    start_sec = int(start_parts[1])
                    start_total_sec = start_min * 60 + start_sec

                    # Split end timestamp into minutes and seconds
                    end_parts = end_str.split(':')
                    end_min = int(end_parts[0])
                    end_sec = int(end_parts[1])
                    end_total_sec = end_min * 60 + end_sec

                    # Calculate duration in seconds
                    duration_sec = end_total_sec - start_total_sec

                    # Convert duration to minutes (more readable)
                    duration_min = duration_sec / 60

                except (ValueError, IndexError):
                    # If parsing timestamps fails, skip this segment
                    continue

                # ============================================================
                # Store this student speaking segment record
                # ============================================================
                all_records.append({
                    'student_name': student_name,
                    'session_date': session_date,
                    'duration_minutes': duration_min,
                    'transcript_file': file_path.name
                })

        except Exception as e:
            # Log error and continue with next file
            print(f"  Warning: Error processing {file_path.name}: {str(e)}")
            continue

    # Convert list of records to DataFrame
    df_student_time = pd.DataFrame(all_records)

    if len(df_student_time) == 0:
        print("❌ No student speaking segments found in transcripts!")
        return None, None

    print(f"✅ Extracted {len(df_student_time)} student speaking segments")
    print(f"✅ Covering {len(df_student_time['student_name'].unique())} unique students")
    print()

    # ========================================================================
    # STEP 3: SUM UP DAILY PRACTICE TIME PER STUDENT
    # ========================================================================
    print("STEP 3: Aggregating by day...")
    print("-" * 80)

    # Group by (student_name, session_date) and sum up all speaking durations
    # This gives us total student speaking time per day per student
    daily_totals = df_student_time.groupby(
        ['student_name', 'session_date']
    )['duration_minutes'].sum().reset_index()

    # Rename column for clarity
    daily_totals.columns = ['student_name', 'session_date', 'daily_total_minutes']

    # Round to 2 decimal places for readability
    daily_totals['daily_total_minutes'] = daily_totals['daily_total_minutes'].round(2)

    print(f"✅ Created daily totals for {len(daily_totals)} student-day combinations")
    print()

    # Display sample of daily totals
    print("Sample of daily practice totals:")
    print(daily_totals.head(10).to_string(index=False))
    print()

    # ========================================================================
    # STEP 4: CALCULATE AVERAGE DAILY PRACTICE TIME AND STATISTICS
    # ========================================================================
    print("STEP 4: Calculating statistics...")
    print("-" * 80)

    # Group by student and calculate multiple statistics
    averages = daily_totals.groupby('student_name')['daily_total_minutes'].agg([
        ('num_practice_days', 'count'),         # Number of days student practiced
        ('total_practice_minutes', 'sum'),      # Total minutes across all days
        ('avg_daily_minutes', 'mean'),          # Average minutes per practice day
        ('median_daily_minutes', 'median'),     # Median minutes per day
        ('min_daily_minutes', 'min'),           # Minimum in a single day
        ('max_daily_minutes', 'max'),           # Maximum in a single day
        ('std_daily_minutes', 'std')            # Standard deviation (consistency measure)
    ]).reset_index()

    # Round all numeric columns to 2 decimal places
    numeric_columns = [
        'total_practice_minutes', 'avg_daily_minutes', 'median_daily_minutes',
        'min_daily_minutes', 'max_daily_minutes', 'std_daily_minutes'
    ]
    for col in numeric_columns:
        averages[col] = averages[col].round(2)

    # Sort by average daily minutes (descending)
    # Students with highest average practice time appear first
    averages = averages.sort_values('avg_daily_minutes', ascending=False)

    # Reset index for clean display
    averages = averages.reset_index(drop=True)

    print()

    # ========================================================================
    # STEP 5: DISPLAY RESULTS
    # ========================================================================
    print("=" * 100)
    print("STUDENT PRACTICE TIME SUMMARY")
    print("=" * 100)
    print()
    print(averages.to_string(index=False))
    print()

    # ========================================================================
    # STEP 6: DISPLAY ADDITIONAL INSIGHTS
    # ========================================================================
    print("=" * 100)
    print("INSIGHTS")
    print("=" * 100)
    print()

    # Calculate overall statistics
    overall_avg = averages['avg_daily_minutes'].mean()
    overall_min = averages['avg_daily_minutes'].min()
    overall_max = averages['avg_daily_minutes'].max()

    print(f"Total students: {len(averages)}")
    print(f"Overall average daily practice: {overall_avg:.2f} minutes/day")
    print(f"Range: {overall_min:.2f} - {overall_max:.2f} minutes/day")
    print()

    # Show top performers
    print("Top 5 students by average daily practice:")
    for idx, row in averages.head(5).iterrows():
        print(f"  {idx+1}. {row['student_name']}: {row['avg_daily_minutes']:.2f} min/day "
              f"({int(row['num_practice_days'])} days)")
    print()

    return averages, daily_totals


def save_practice_analytics(averages: pd.DataFrame, daily_totals: pd.DataFrame,
                           output_dir: Path):
    """
    Save practice time analytics to Excel and CSV files.

    Args:
        averages: Summary statistics DataFrame from calculate_daily_practice_averages()
        daily_totals: Daily breakdown DataFrame from calculate_daily_practice_averages()
        output_dir: Path to directory where output files will be saved
    """
    print("Saving results...")
    print("-" * 80)

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ========================================================================
    # Save to Excel with two sheets
    # ========================================================================
    excel_path = output_dir / f"practice_analytics_{timestamp}.xlsx"

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Sheet 1: Summary statistics
        averages.to_excel(writer, sheet_name='Student Summary', index=False)

        # Sheet 2: Daily breakdown
        daily_totals_sorted = daily_totals.sort_values(['student_name', 'session_date'])
        daily_totals_sorted.to_excel(writer, sheet_name='Daily Details', index=False)

    print(f"✅ Excel file saved: {excel_path}")

    # ========================================================================
    # Save summary to CSV
    # ========================================================================
    csv_summary_path = output_dir / f"practice_summary_{timestamp}.csv"
    averages.to_csv(csv_summary_path, index=False)
    print(f"✅ Summary CSV saved: {csv_summary_path}")

    # ========================================================================
    # Save daily details to CSV
    # ========================================================================
    csv_daily_path = output_dir / f"practice_daily_{timestamp}.csv"
    daily_totals_sorted = daily_totals.sort_values(['student_name', 'session_date'])
    daily_totals_sorted.to_csv(csv_daily_path, index=False)
    print(f"✅ Daily CSV saved: {csv_daily_path}")

    print()


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    """
    Main execution script.

    To use this script:
    1. Make sure you're in the project root directory
    2. Run: python calculate_practice_time.py
    3. Results will be displayed and saved to the output/ directory
    """

    from cefr_pipeline import config

    # Calculate practice time analytics
    averages, daily_totals = calculate_daily_practice_averages(config.TRANSCRIPT_DIR)

    # Save results if calculations were successful
    if averages is not None and daily_totals is not None:
        save_practice_analytics(averages, daily_totals, config.OUTPUT_DIR)

        print("=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
    else:
        print("❌ Analysis failed - no data available")
