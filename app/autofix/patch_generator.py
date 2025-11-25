import reflex as rx
import anthropic
import os
import logging
from app.core.models import SecurityFinding

logger = logging.getLogger(__name__)


class PatchGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def _get_file_content(self, file_path: str) -> str | None:
        """Reads content from a file within the project."""
        try:
            full_path = os.path.join(os.getcwd(), file_path)
            if not os.path.exists(full_path):
                logger.error(f"File not found at path: {full_path}")
                return None
            with open(full_path, "r") as f:
                return f.read()
        except Exception as e:
            logger.exception(f"Failed to read file content for {file_path}: {e}")
            return None

    def generate_patch(self, finding: SecurityFinding) -> str | None:
        """Generates a code patch for a given security finding."""
        if not self.client:
            logger.error(
                "Anthropic client is not initialized. Check ANTHROPIC_API_KEY."
            )
            return None
        file_content = self._get_file_content(finding.file_path)
        if not file_content:
            return None
        prompt = f"\nYou are an AI code assistant specializing in security. Your task is to fix a security vulnerability in the provided Python code.\nGenerate only the new, corrected code for the specified file. Do not include any explanation or surrounding text, only the complete, updated file content.\nRespect the existing code style and make the minimal change necessary to resolve the issue.\n\nVulnerability Details:\n- Description: {finding.description}\n- Severity: {finding.severity}\n- File: {finding.file_path}\n- Line: {finding.line_number}\n\nOriginal file content of `{finding.file_path}`:\n\n{file_content}\n\n\nBased on the vulnerability, provide the full, corrected content for `{finding.file_path}`.\n"
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            if response.content and len(response.content) > 0:
                patched_code_block = response.content[0].text.strip()
                if patched_code_block.startswith("```"):
                    patched_code = "\n".join(
                        patched_code_block.split("\n")[1:-1]
                    )
                else:
                    patched_code = patched_code_block
                return patched_code
            else:
                logger.error("Anthropic API returned an empty content block.")
                return None
        except Exception as e:
            logger.exception(f"Error calling Anthropic API for patch generation: {e}")
            return None