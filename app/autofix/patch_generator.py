from __future__ import annotations

import logging
import os
from typing import Optional

import anthropic

from app.core.models import SecurityFinding

logger = logging.getLogger(__name__)


class PatchGenerator:
    """Generate minimal patches for security findings using Anthropic models."""

    def __init__(self, client: Optional[anthropic.Anthropic] = None) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if client is not None:
            self.client = client
        elif api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            logger.warning(
                "ANTHROPIC_API_KEY is not configured. Patch generation is disabled."
            )
            self.client = None

    def _get_file_content(self, file_path: str) -> Optional[str]:
        """Read and return the project file content when the path exists."""

        full_path = os.path.join(os.getcwd(), file_path)
        if not os.path.exists(full_path):
            logger.error("File not found at path: %s", full_path)
            return None
        try:
            with open(full_path, "r", encoding="utf-8") as file_handle:
                return file_handle.read()
        except OSError as exc:
            logger.exception("Failed to read file content for %s: %s", file_path, exc)
            return None

    @staticmethod
    def _normalise_payload(payload: str) -> Optional[str]:
        """Strip markdown fences and return clean code content."""

        text = payload.strip()
        if not text:
            return None
        if text.startswith("```"):
            segments = [
                segment
                for segment in text.split("```")
                if segment
                and not segment.lstrip().startswith(("diff", "python", "bash"))
            ]
            text = "\n".join(segment.strip("\n") for segment in segments).strip()
        return text or None

    def generate_patch(self, finding: SecurityFinding) -> Optional[str]:
        """Generate a patch for the provided finding, if configuration allows."""

        if not self.client:
            logger.error(
                "Anthropic client is not initialized. Check ANTHROPIC_API_KEY."
            )
            return None

        file_content = self._get_file_content(finding.file_path)
        if file_content is None:
            return None

        prompt = (
            "\nYou are an AI code assistant specializing in security. "
            "Your task is to fix a security vulnerability in the provided code.\n"
            "Generate only the new, corrected code for the specified file. Do not "
            "include any explanation or surrounding text, only the complete, "
            "updated file content. Respect the existing code style and make the "
            "minimal change necessary to resolve the issue.\n\n"
            f"Vulnerability Details:\n- Description: {finding.description}\n"
            f"- Severity: {finding.severity}\n- File: {finding.file_path}\n"
            f"- Line: {finding.line_number}\n\nOriginal file content of "
            f"`{finding.file_path}`:\n\n{file_content}\n\n"
            f"Based on the vulnerability, provide the full, corrected content for "
            f"`{finding.file_path}`.\n"
        )

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:  # pragma: no cover - network failure
            logger.exception(
                "Error calling Anthropic API for patch generation: %s", exc
            )
            return None

        if not response.content:
            logger.error("Anthropic API returned an empty content block.")
            return None

        patched_code = self._normalise_payload(response.content[0].text)
        if not patched_code:
            logger.error("Failed to normalise patch content from Anthropic response.")
            return None

        return patched_code
