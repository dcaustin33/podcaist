#!/usr/bin/env python3
"""
Blind Testing Script for Podcast Generation

This script generates podcasts for research papers using different models and context settings
for blind evaluation. It creates non-descriptive filenames and tracks metadata in a CSV file.
"""

import csv
import os
import random
import tempfile
import uuid
from pathlib import Path
from typing import List, Tuple

from podcaist.contributions import summarize_contributions
from podcaist.generate_sections import generate_podcast
from podcaist.limitations import limitations
from podcaist.method import method
from podcaist.model_garden import generate_text_response
from podcaist.pdf_utils import compress_pdf
from podcaist.results import results
from podcaist.utils import format_contributions, write_text_file

# Available models for testing
AVAILABLE_MODELS = [
    "o3-2025-04-16",
    "gemini-2.5-pro-preview-06-05",
]


class BlindTester:
    def __init__(self, output_dir: str = "blind_test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.csv_file = self.output_dir / "test_metadata.csv"
        self.test_counter = 1

        # Initialize CSV file
        with open(self.csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "test_id",
                    "original_pdf_name",
                    "model",
                    "context_flag",
                    "script_filename",
                    "generation_timestamp",
                ]
            )

    def generate_test_id(self) -> str:
        """Generate a non-descriptive test ID"""
        test_id = f"test_{self.test_counter:03d}"
        self.test_counter += 1
        return test_id

    def select_models_for_paper(self) -> Tuple[str, str]:
        """Randomly select 2 different models for a paper"""
        return tuple(random.sample(AVAILABLE_MODELS, 2))

    def generate_with_context(self, pdf_path: str, model: str) -> str:
        """Generate podcast using full context pipeline"""
        # Generate all analysis components
        contributions = summarize_contributions(pdf_file_path=pdf_path, model=model)
        method_text = method(pdf_path, contributions, model)
        results_text = results(pdf_path, contributions, model)
        limitation_text = limitations(pdf_path, contributions, model)

        # Generate final podcast
        return generate_podcast(
            pdf_path, contributions, method_text, results_text, limitation_text, model
        )

    def process_paper(self, pdf_path: str, pdf_name: str) -> List[dict]:
        """Process a single paper with random model selection and both context settings"""
        # Select 2 random models
        model1, model2 = self.select_models_for_paper()

        # Compress PDF
        compressed_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        compress_pdf(pdf_path, compressed_pdf.name)

        results = []

        try:
            # Generate 4 variants: 2 models × 2 context settings
            for model in [model1, model2]:
                for context_flag in [True]:
                    test_id = self.generate_test_id()
                    script_filename = f"{test_id}.txt"

                    # Generate podcast script
                    if context_flag:
                        script = self.generate_with_context(compressed_pdf.name, model)
                    else:
                        raise ValueError("Context flag must be True")

                    # Save script with non-descriptive filename
                    script_path = self.output_dir / script_filename
                    write_text_file(str(script_path), script)

                    # Record metadata
                    metadata = {
                        "test_id": test_id,
                        "original_pdf_name": pdf_name,
                        "model": model,
                        "context_flag": context_flag,
                        "script_filename": script_filename,
                        "generation_timestamp": __import__("datetime")
                        .datetime.now()
                        .isoformat(),
                    }
                    results.append(metadata)

                    # Write to CSV immediately
                    with open(self.csv_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                metadata["test_id"],
                                metadata["original_pdf_name"],
                                metadata["model"],
                                metadata["context_flag"],
                                metadata["script_filename"],
                                metadata["generation_timestamp"],
                            ]
                        )

        finally:
            # Clean up compressed PDF
            os.unlink(compressed_pdf.name)

        return results

    def run_blind_test(self, pdf_directory: str, pdf_names: List[str]) -> None:
        """Run blind test on all specified PDFs"""
        print(f"Starting blind test with {len(pdf_names)} papers")
        print(f"Output directory: {self.output_dir}")
        print(f"Available models: {AVAILABLE_MODELS}")

        all_results = []

        for i, pdf_name in enumerate(pdf_names, 1):
            pdf_path = os.path.join(pdf_directory, pdf_name)

            if not os.path.exists(pdf_path):
                print(f"Warning: PDF not found: {pdf_path}")
                continue

            print(f"\nProcessing paper {i}/{len(pdf_names)}: {pdf_name}")

            try:
                paper_results = self.process_paper(pdf_path, pdf_name)
                all_results.extend(paper_results)
                print(f"Generated {len(paper_results)} test cases for {pdf_name}")

            except Exception as e:
                print(f"Error processing {pdf_name}: {e}")
                continue

        print(f"\nBlind test complete!")
        print(f"Total test cases generated: {len(all_results)}")
        print(f"Results saved to: {self.output_dir}")
        print(f"Metadata CSV: {self.csv_file}")


if __name__ == "__main__":

    pdf_directory = "/Users/derek/Desktop/podcaist/podcaist/pdf_directory"
    pdf_names = ["v-jepa2.pdf"]
    output_directory = "/Users/derek/Desktop/podcaist/podcaist/blind_test_results3"

    # Initialize tester
    tester = BlindTester(output_directory)

    # Run tests
    tester.run_blind_test(pdf_directory, pdf_names)
