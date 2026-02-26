"""
Compare CEFR evaluation results from different prompt versions.

This script helps you analyze which prompt version produces better results
by comparing scores, consistency, and distribution across different prompts.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict
import json


class PromptComparator:
    """
    Compare evaluation results from different prompt versions.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize comparator.

        Args:
            output_dir: Directory containing CSV/Excel output files
        """
        self.output_dir = output_dir

    def find_results_by_version(self, prompt_version: str) -> Dict[str, Path]:
        """
        Find result files for a specific prompt version.

        Args:
            prompt_version: Prompt version (e.g., "v1_detailed")

        Returns:
            Dictionary with paths to individual and aggregated CSV files
        """
        results = {
            'individual': None,
            'aggregated': None
        }

        # Look for files with this prompt version in the name
        for file in self.output_dir.glob(f"*{prompt_version}.csv"):
            if "individual" in file.name:
                results['individual'] = file
            elif "aggregated" in file.name:
                results['aggregated'] = file

        return results

    def load_all_versions(self) -> Dict[str, Dict]:
        """
        Load results from all available prompt versions.

        Returns:
            Dictionary mapping prompt version to dataframes
        """
        versions = {}

        # Find all CSV files
        csv_files = list(self.output_dir.glob("*aggregated*.csv"))

        for csv_file in csv_files:
            # Extract prompt version from filename
            # Format: cefr_aggregated_<all_students_v1_detailed>.csv
            filename = csv_file.stem
            parts = filename.replace("cefr_aggregated_", "").split("_")

            # Reconstruct version (last 1-2 parts)
            if "all_students" in filename:
                prompt_version = "_".join(parts[-2:])  # v1_detailed, v2_simplified
            else:
                prompt_version = "_".join(parts[-2:])

            try:
                df = pd.read_csv(csv_file)
                versions[prompt_version] = {
                    'dataframe': df,
                    'file': csv_file
                }
            except Exception as e:
                print(f"Error loading {csv_file}: {e}")

        return versions

    def compare_score_distributions(self, versions: Dict[str, Dict], dimension: str = 'overall_mode') -> pd.DataFrame:
        """
        Compare score distributions for a specific dimension across prompt versions.

        Args:
            versions: Dictionary of loaded versions
            dimension: Column to compare (e.g., 'overall_mode', 'range_mode', 'accuracy_mode')

        Returns:
            DataFrame with score distribution statistics per version
        """
        comparison = []

        for version, data in versions.items():
            df = data['dataframe']

            # Get the mode column (handle both naming conventions)
            score_col = dimension
            if score_col not in df.columns:
                print(f"Warning: Column '{score_col}' not found in {version}")
                continue

            scores = df[score_col].value_counts()

            comparison.append({
                'prompt_version': version,
                'A1': scores.get('A1', 0),
                'A2': scores.get('A2', 0),
                'B1': scores.get('B1', 0),
                'B2': scores.get('B2', 0),
                'Strong A1': scores.get('Strong A1', 0),
                'Strong A2': scores.get('Strong A2', 0),
                'Error': scores.get('Error', 0),
                'total_students': len(df)
            })

        return pd.DataFrame(comparison)

    def compare_by_student(self, versions: Dict[str, Dict]) -> pd.DataFrame:
        """
        Compare how different prompts score the same students.

        Shows if different prompts agree or disagree on student proficiency levels.

        Args:
            versions: Dictionary of loaded versions

        Returns:
            DataFrame comparing overall_mode across versions for each student
        """
        # Get unique students from first version
        first_df = list(versions.values())[0]['dataframe']
        students = first_df['student_name'].unique()

        comparison = []

        for student in sorted(students):
            row_data = {'student_name': student}

            # Get score from each prompt version
            for version, data in sorted(versions.items()):
                df = data['dataframe']
                student_data = df[df['student_name'] == student]

                if len(student_data) > 0:
                    row_data[f"{version}_overall"] = student_data['overall_mode'].values[0]
                    row_data[f"{version}_range"] = student_data['range_mode'].values[0]
                    row_data[f"{version}_accuracy"] = student_data['accuracy_mode'].values[0]
                else:
                    row_data[f"{version}_overall"] = "N/A"
                    row_data[f"{version}_range"] = "N/A"
                    row_data[f"{version}_accuracy"] = "N/A"

            comparison.append(row_data)

        return pd.DataFrame(comparison)

    def get_agreement_score(self, versions: Dict[str, Dict]) -> Dict:
        """
        Calculate how much different prompts agree on overall CEFR level.

        Args:
            versions: Dictionary of loaded versions

        Returns:
            Dictionary with agreement statistics
        """
        if len(versions) < 2:
            return {"error": "Need at least 2 prompt versions to compare"}

        # Get students in all versions
        all_dfs = [v['dataframe'] for v in versions.values()]
        common_students = set(all_dfs[0]['student_name'])
        for df in all_dfs[1:]:
            common_students = common_students.intersection(set(df['student_name']))

        if not common_students:
            return {"error": "No common students across all versions"}

        # Count agreements
        agreements = 0
        total = len(common_students)
        differences = []

        version_list = list(sorted(versions.keys()))

        for student in sorted(common_students):
            scores = []
            for version in version_list:
                df = versions[version]['dataframe']
                score = df[df['student_name'] == student]['overall_mode'].values[0]
                scores.append(score)

            # Check if all scores are the same
            if len(set(scores)) == 1:
                agreements += 1
            else:
                differences.append({
                    'student': student,
                    'scores': dict(zip(version_list, scores))
                })

        return {
            'total_students': total,
            'agreements': agreements,
            'disagreements': total - agreements,
            'agreement_percentage': (agreements / total * 100) if total > 0 else 0,
            'differences': differences
        }

    def print_comparison_report(self) -> None:
        """
        Print a comprehensive comparison report of all prompt versions.
        """
        print("\n" + "=" * 80)
        print("PROMPT VERSION COMPARISON REPORT")
        print("=" * 80)

        # Load all versions
        versions = self.load_all_versions()

        if not versions:
            print("\n❌ No result files found!")
            print("Run 'python main.py' with different PROMPT_VERSION settings first.")
            return

        print(f"\n📊 Found {len(versions)} prompt version(s)")
        for version in sorted(versions.keys()):
            print(f"   - {version}")

        # ====================================================================
        # OVERALL SCORE DISTRIBUTION
        # ====================================================================
        print("\n" + "-" * 80)
        print("OVERALL CEFR LEVEL DISTRIBUTION")
        print("-" * 80)

        comparison_df = self.compare_score_distributions(versions, 'overall_mode')
        print("\n" + comparison_df.to_string(index=False))

        # Calculate percentages
        print("\nPercentage Distribution:")
        for _, row in comparison_df.iterrows():
            print(f"\n{row['prompt_version']}:")
            total = row['total_students']
            for level in ['A1', 'A2', 'B1', 'B2']:
                count = row[level]
                pct = (count / total * 100) if total > 0 else 0
                print(f"  {level:15s}: {count:2d} students ({pct:5.1f}%)")

        # ====================================================================
        # AGREEMENT ANALYSIS
        # ====================================================================
        if len(versions) >= 2:
            print("\n" + "-" * 80)
            print("AGREEMENT ACROSS PROMPT VERSIONS")
            print("-" * 80)

            agreement = self.get_agreement_score(versions)

            if "error" not in agreement:
                print(f"\nCommon students evaluated: {agreement['total_students']}")
                print(f"Agreements: {agreement['agreements']}/{agreement['total_students']} ({agreement['agreement_percentage']:.1f}%)")
                print(f"Disagreements: {agreement['disagreements']}/{agreement['total_students']}")

                if agreement['differences']:
                    print("\nWhere prompts disagree:")
                    for diff in agreement['differences'][:10]:  # Show first 10
                        print(f"\n  {diff['student']}:")
                        for version, score in diff['scores'].items():
                            print(f"    {version:20s}: {score}")

                    if len(agreement['differences']) > 10:
                        print(f"\n  ... and {len(agreement['differences']) - 10} more disagreements")

        # ====================================================================
        # STUDENT-BY-STUDENT COMPARISON
        # ====================================================================
        if len(versions) >= 2:
            print("\n" + "-" * 80)
            print("STUDENT-BY-STUDENT COMPARISON")
            print("-" * 80)

            comparison_table = self.compare_by_student(versions)
            print("\n" + comparison_table.to_string(index=False))

        # ====================================================================
        # DIMENSION-SPECIFIC ANALYSIS
        # ====================================================================
        print("\n" + "-" * 80)
        print("DIMENSION ANALYSIS - RANGE")
        print("-" * 80)
        range_comparison = self.compare_score_distributions(versions, 'range_mode')
        print("\n" + range_comparison.to_string(index=False))

        print("\n" + "-" * 80)
        print("DIMENSION ANALYSIS - ACCURACY")
        print("-" * 80)
        accuracy_comparison = self.compare_score_distributions(versions, 'accuracy_mode')
        print("\n" + accuracy_comparison.to_string(index=False))

        print("\n" + "-" * 80)
        print("DIMENSION ANALYSIS - FLUENCY")
        print("-" * 80)
        fluency_comparison = self.compare_score_distributions(versions, 'fluency_mode')
        print("\n" + fluency_comparison.to_string(index=False))

        print("\n" + "=" * 80)
        print("END OF REPORT")
        print("=" * 80)

    def export_comparison_to_excel(self, output_file: Path = None) -> None:
        """
        Export comparison analysis to Excel with multiple sheets.

        Args:
            output_file: Path to save Excel file (defaults to output/prompt_comparison.xlsx)
        """
        if output_file is None:
            output_file = self.output_dir / "prompt_comparison.xlsx"

        versions = self.load_all_versions()

        if not versions:
            print("❌ No result files found!")
            return

        try:
            import openpyxl
        except ImportError:
            print("Installing openpyxl...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet 1: Overall distribution
            overall_dist = self.compare_score_distributions(versions, 'overall_mode')
            overall_dist.to_excel(writer, sheet_name='Overall Distribution', index=False)

            # Sheet 2: Range distribution
            range_dist = self.compare_score_distributions(versions, 'range_mode')
            range_dist.to_excel(writer, sheet_name='Range Distribution', index=False)

            # Sheet 3: Accuracy distribution
            accuracy_dist = self.compare_score_distributions(versions, 'accuracy_mode')
            accuracy_dist.to_excel(writer, sheet_name='Accuracy Distribution', index=False)

            # Sheet 4: Student comparison
            if len(versions) >= 2:
                student_comparison = self.compare_by_student(versions)
                student_comparison.to_excel(writer, sheet_name='Student Comparison', index=False)

        print(f"✅ Comparison exported to: {output_file}")


def main():
    """
    Main function to run prompt comparison analysis.
    """
    from cefr_pipeline import config

    comparator = PromptComparator(config.OUTPUT_DIR)

    # Print detailed report
    comparator.print_comparison_report()

    # Export to Excel
    comparator.export_comparison_to_excel()

    print("\n💡 TIPS:")
    print("   - Run main.py with different PROMPT_VERSION values")
    print("   - Then run this script to compare results")
    print("   - Check output/prompt_comparison.xlsx for detailed analysis")


if __name__ == "__main__":
    main()
