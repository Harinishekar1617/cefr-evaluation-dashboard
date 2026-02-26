"""
Prompt versioning and management system.
Allows storing, loading, and switching between different CEFR evaluation prompts.
"""

import json
from pathlib import Path
from typing import Dict, List


class PromptManager:
    """
    Manages versioned CEFR evaluation prompts.

    Stores multiple prompt versions in prompts.json and provides functions
    to load, list, and retrieve them.
    """

    def __init__(self, prompts_file: Path):
        """
        Initialize the prompt manager.

        Args:
            prompts_file: Path to prompts.json file
        """
        self.prompts_file = prompts_file
        self.prompts_data = self._load_prompts()

    def _load_prompts(self) -> Dict:
        """
        Load all prompts from prompts.json file.

        Returns:
            Dictionary containing all prompts and metadata
        """
        try:
            with open(self.prompts_file, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"Error: {self.prompts_file} not found!")
            return {"prompts": {}, "metadata": {}}
        except json.JSONDecodeError:
            print(f"Error: {self.prompts_file} is not valid JSON!")
            return {"prompts": {}, "metadata": {}}

    def get_prompt(self, version: str) -> str:
        """
        Get the full prompt text for a specific version.

        Loads prompt from the corresponding .txt file.

        Args:
            version: Version key (e.g., "v1_detailed", "v2_simplified")

        Returns:
            Prompt text, or error message if version not found
        """
        if version not in self.prompts_data["prompts"]:
            available = self.list_versions()
            raise ValueError(f"Prompt version '{version}' not found. Available: {available}")

        prompt_info = self.prompts_data["prompts"][version]

        # Get the file path
        file_path = prompt_info.get("file")
        if not file_path:
            raise ValueError(f"Prompt version '{version}' has no file specified")

        # Load from file (relative to prompts.json location)
        full_path = self.prompts_file.parent / file_path

        try:
            with open(full_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise ValueError(f"Prompt file not found: {full_path}")

    def list_versions(self) -> List[str]:
        """
        List all available prompt versions.

        Returns:
            List of version keys
        """
        return list(self.prompts_data["prompts"].keys())

    def get_version_info(self, version: str) -> Dict:
        """
        Get metadata about a specific prompt version.

        Args:
            version: Version key

        Returns:
            Dictionary with version, date_created, description, author
        """
        if version not in self.prompts_data["prompts"]:
            raise ValueError(f"Prompt version '{version}' not found")

        prompt_data = self.prompts_data["prompts"][version]
        return {
            "version": prompt_data.get("version", "unknown"),
            "date_created": prompt_data.get("date_created", "unknown"),
            "description": prompt_data.get("description", ""),
            "author": prompt_data.get("author", "")
        }

    def print_available_prompts(self) -> None:
        """
        Print a nicely formatted list of all available prompts.
        """
        versions = self.list_versions()
        print("\n" + "=" * 80)
        print("AVAILABLE PROMPT VERSIONS")
        print("=" * 80)

        for version in versions:
            info = self.get_version_info(version)
            print(f"\n📌 {version}")
            print(f"   Version:     {info['version']}")
            print(f"   Created:     {info['date_created']}")
            print(f"   Author:      {info['author']}")
            print(f"   Description: {info['description']}")

        default = self.prompts_data.get("metadata", {}).get("default_prompt", "unknown")
        print(f"\n   Default:     {default}")
        print("\n" + "=" * 80)

    def add_prompt(self, version_key: str, content: str, metadata: Dict) -> None:
        """
        Add a new prompt version to prompts.json.

        Args:
            version_key: Unique version identifier (e.g., "v3_experimental")
            content: Full prompt text
            metadata: Dictionary with keys: version, date_created, description, author

        Example:
            manager.add_prompt(
                "v3_experimental",
                "You are a CEFR assessor...",
                {
                    "version": "3.0",
                    "date_created": "2025-02-18",
                    "description": "Testing different scoring approach",
                    "author": "Your Name"
                }
            )
        """
        metadata["content"] = content
        self.prompts_data["prompts"][version_key] = metadata

        # Save back to file
        with open(self.prompts_file, 'w') as f:
            json.dump(self.prompts_data, f, indent=2)

        print(f"✅ Added prompt version: {version_key}")

    def get_default_prompt(self) -> str:
        """
        Get the default prompt version.

        Returns:
            Prompt text for the default version
        """
        default_version = self.prompts_data.get("metadata", {}).get("default_prompt")
        if not default_version:
            # If no default set, use first available
            available = self.list_versions()
            default_version = available[0] if available else None

        if not default_version:
            raise ValueError("No prompts available!")

        return self.get_prompt(default_version)

    def set_default_prompt(self, version: str) -> None:
        """
        Set which prompt version should be used by default.

        Args:
            version: Version key to set as default
        """
        if version not in self.prompts_data["prompts"]:
            raise ValueError(f"Prompt version '{version}' not found")

        self.prompts_data["metadata"]["default_prompt"] = version

        with open(self.prompts_file, 'w') as f:
            json.dump(self.prompts_data, f, indent=2)

        print(f"✅ Set default prompt to: {version}")
