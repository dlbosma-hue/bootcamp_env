"""
Markdown document ingestion and processing module.

This module handles:
- Loading markdown files from knowledge base directories
- Parsing markdown content into structured format
- Extracting sections, metadata, and content
- Supporting both primary and secondary knowledge bases
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import markdown
from markdown.extensions import tables, fenced_code


class DocumentProcessor:
    """Process and ingest markdown documents from the knowledge base."""

    def __init__(self, knowledge_base_path: str):
        """
        Initialize document processor.

        Args:
            knowledge_base_path: Path to the knowledge base root directory
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        self.md_parser = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])

    def load_document(self, file_path: str) -> str:
        """
        Load a single markdown document.

        Args:
            file_path: Path to the markdown file

        Returns:
            Raw markdown content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: File not found: {file_path}")
            return ""
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            return ""

    def load_all_documents(self, category: str = None) -> Dict[str, str]:
        """
        Load all markdown documents from the knowledge base.

        Args:
            category: Optional category to filter ('primary' or 'secondary')

        Returns:
            Dictionary mapping file names to their content
        """
        documents = {}

        if category:
            # Load from specific category
            category_path = self.knowledge_base_path / category
            if category_path.exists():
                documents.update(self._load_from_directory(category_path, category))
        else:
            # Load from all categories
            for cat in ['primary', 'secondary']:
                cat_path = self.knowledge_base_path / cat
                if cat_path.exists():
                    documents.update(self._load_from_directory(cat_path, cat))

        return documents

    def _load_from_directory(self, directory: Path, category: str) -> Dict[str, str]:
        """
        Recursively load all .md files from a directory.

        Args:
            directory: Directory path to search
            category: Category name (primary or secondary)

        Returns:
            Dictionary of documents
        """
        documents = {}

        for file_path in directory.rglob('*.md'):
            # Create a key that includes category and relative path
            relative_path = file_path.relative_to(self.knowledge_base_path)
            key = f"{category}/{file_path.stem}"

            content = self.load_document(str(file_path))
            if content:
                documents[key] = content

        return documents

    def parse_markdown(self, content: str) -> Dict:
        """
        Parse markdown content into structured format.

        Extracts:
        - Headings and their levels
        - Sections and subsections
        - Lists (bullet and numbered)
        - Metadata from front matter (if present)

        Args:
            content: Raw markdown string

        Returns:
            Dictionary with structured content
        """
        parsed = {
            'raw': content,
            'html': self.md_parser.convert(content),
            'sections': self._extract_sections(content),
            'headings': self._extract_headings(content),
            'lists': self._extract_lists(content),
            'metadata': self._extract_metadata(content)
        }

        # Reset parser for next use
        self.md_parser.reset()

        return parsed

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """
        Extract sections based on headings.

        Args:
            content: Markdown content

        Returns:
            Dictionary mapping heading text to section content
        """
        sections = {}

        # Split by headings (# Header)
        lines = content.split('\n')
        current_heading = "Introduction"
        current_content = []

        for line in lines:
            # Check if line is a heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if heading_match:
                # Save previous section
                if current_content:
                    sections[current_heading] = '\n'.join(current_content).strip()

                # Start new section
                current_heading = heading_match.group(2).strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_heading] = '\n'.join(current_content).strip()

        return sections

    def _extract_headings(self, content: str) -> List[Dict[str, any]]:
        """
        Extract all headings with their levels.

        Args:
            content: Markdown content

        Returns:
            List of heading dictionaries with 'level' and 'text'
        """
        headings = []

        for line in content.split('\n'):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headings.append({
                    'level': level,
                    'text': text
                })

        return headings

    def _extract_lists(self, content: str) -> Dict[str, List[str]]:
        """
        Extract bullet and numbered lists.

        Args:
            content: Markdown content

        Returns:
            Dictionary with 'bullet' and 'numbered' lists
        """
        lists = {
            'bullet': [],
            'numbered': []
        }

        for line in content.split('\n'):
            # Bullet lists (-, *, +)
            if re.match(r'^\s*[-*+]\s+(.+)$', line):
                item = re.match(r'^\s*[-*+]\s+(.+)$', line).group(1)
                lists['bullet'].append(item.strip())

            # Numbered lists
            elif re.match(r'^\s*\d+\.\s+(.+)$', line):
                item = re.match(r'^\s*\d+\.\s+(.+)$', line).group(1)
                lists['numbered'].append(item.strip())

        return lists

    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """
        Extract metadata from markdown (simple key-value format in comments or front matter).

        Args:
            content: Markdown content

        Returns:
            Dictionary of metadata key-value pairs
        """
        metadata = {}

        # Look for HTML comments with metadata format
        # <!-- key: value -->
        comment_pattern = r'<!--\s*(\w+):\s*(.+?)\s*-->'
        for match in re.finditer(comment_pattern, content):
            key = match.group(1).strip()
            value = match.group(2).strip()
            metadata[key] = value

        return metadata

    def get_section_content(self, content: str, section_name: str) -> Optional[str]:
        """
        Get content from a specific section by heading name.

        Args:
            content: Markdown content
            section_name: Name of the heading/section

        Returns:
            Section content or None if not found
        """
        sections = self._extract_sections(content)

        # Try exact match first
        if section_name in sections:
            return sections[section_name]

        # Try case-insensitive match
        for key, value in sections.items():
            if key.lower() == section_name.lower():
                return value

        return None

    def search_content(self, content: str, keyword: str, case_sensitive: bool = False) -> List[str]:
        """
        Search for keyword in content and return matching lines.

        Args:
            content: Markdown content
            keyword: Keyword to search for
            case_sensitive: Whether search should be case-sensitive

        Returns:
            List of lines containing the keyword
        """
        matches = []

        search_content = content if case_sensitive else content.lower()
        search_keyword = keyword if case_sensitive else keyword.lower()

        for line in content.split('\n'):
            search_line = line if case_sensitive else line.lower()
            if search_keyword in search_line:
                matches.append(line.strip())

        return matches

    def summarize_document(self, content: str) -> Dict[str, any]:
        """
        Create a summary of the document structure.

        Args:
            content: Markdown content

        Returns:
            Dictionary with document summary
        """
        parsed = self.parse_markdown(content)

        return {
            'total_sections': len(parsed['sections']),
            'headings': [h['text'] for h in parsed['headings']],
            'section_names': list(parsed['sections'].keys()),
            'has_lists': len(parsed['lists']['bullet']) > 0 or len(parsed['lists']['numbered']) > 0,
            'word_count': len(content.split()),
            'line_count': len(content.split('\n'))
        }
