"""
Primary and secondary knowledge base management module.

This module handles:
- Managing primary knowledge base (company-specific documents)
- Managing secondary knowledge base (industry research)
- Combining knowledge sources for context-rich prompts
- Searching and retrieving relevant content
"""

from typing import Dict, List, Optional
from pathlib import Path
from document_processor import DocumentProcessor


class KnowledgeBase:
    """Manage primary and secondary knowledge bases."""

    def __init__(self, base_path: str):
        """
        Initialize knowledge base manager.

        Args:
            base_path: Path to knowledge_base directory
        """
        self.base_path = Path(base_path)
        self.primary_path = self.base_path / 'primary'
        self.secondary_path = self.base_path / 'secondary'

        # Initialize document processor
        self.processor = DocumentProcessor(base_path)

        # Cache for loaded documents
        self._primary_cache = None
        self._secondary_cache = None

    def get_primary_knowledge(self, reload: bool = False) -> Dict[str, str]:
        """
        Retrieve company-specific documents from primary knowledge base.

        Primary KB includes:
        - Brand guidelines
        - Product specifications
        - Past successful content
        - Strategic planning documents

        Args:
            reload: Force reload from disk (ignore cache)

        Returns:
            Dictionary mapping document names to content
        """
        if self._primary_cache is None or reload:
            self._primary_cache = self.processor.load_all_documents('primary')

        return self._primary_cache

    def get_secondary_knowledge(self, reload: bool = False) -> Dict[str, str]:
        """
        Retrieve industry research from secondary knowledge base.

        Secondary KB includes:
        - Market trends
        - Competitor analysis
        - Industry reports
        - Customer feedback

        Args:
            reload: Force reload from disk (ignore cache)

        Returns:
            Dictionary mapping document names to content
        """
        if self._secondary_cache is None or reload:
            self._secondary_cache = self.processor.load_all_documents('secondary')

        return self._secondary_cache

    def get_all_knowledge(self, reload: bool = False) -> Dict[str, Dict[str, str]]:
        """
        Get both primary and secondary knowledge bases.

        Args:
            reload: Force reload from disk

        Returns:
            Dictionary with 'primary' and 'secondary' keys
        """
        return {
            'primary': self.get_primary_knowledge(reload),
            'secondary': self.get_secondary_knowledge(reload)
        }

    def get_structured_knowledge(self, reload: bool = False) -> Dict[str, any]:
        """
        Get knowledge organized by document type for easy access.

        Returns structured format:
        {
            'brand_voice': 'content...',
            'product_info': 'content...',
            'market_trends': 'content...',
            etc.
        }

        Args:
            reload: Force reload from disk

        Returns:
            Dictionary organized by document purpose
        """
        primary = self.get_primary_knowledge(reload)
        secondary = self.get_secondary_knowledge(reload)

        structured = {}

        # Map common document types
        for key, content in primary.items():
            if 'brand' in key.lower():
                structured['brand_voice'] = content
            elif 'product' in key.lower():
                structured['product_info'] = content
            elif 'past_content' in key.lower() or 'content' in key.lower():
                structured['past_content'] = content
            elif 'strategy' in key.lower() or 'planning' in key.lower():
                structured['strategy'] = content

        for key, content in secondary.items():
            if 'market' in key.lower() or 'trend' in key.lower():
                structured['market_trends'] = content
            elif 'competitor' in key.lower():
                structured['competitor_analysis'] = content
            elif 'industry' in key.lower():
                structured['industry_insights'] = content
            elif 'customer' in key.lower() or 'feedback' in key.lower():
                structured['customer_feedback'] = content

        return structured

    def search_knowledge(self, query: str, source: str = 'both',
                        case_sensitive: bool = False) -> List[Dict]:
        """
        Search across knowledge bases for specific keywords or phrases.

        Args:
            query: Search term or phrase
            source: Where to search ('primary', 'secondary', or 'both')
            case_sensitive: Whether search should be case-sensitive

        Returns:
            List of dictionaries with search results:
            [{'source': 'primary', 'document': 'brand_guidelines',
              'matches': ['line1', 'line2']}]
        """
        results = []

        # Determine which sources to search
        sources_to_search = []
        if source in ['both', 'primary']:
            sources_to_search.append(('primary', self.get_primary_knowledge()))
        if source in ['both', 'secondary']:
            sources_to_search.append(('secondary', self.get_secondary_knowledge()))

        # Search each source
        for source_name, documents in sources_to_search:
            for doc_name, content in documents.items():
                matches = self.processor.search_content(content, query, case_sensitive)

                if matches:
                    results.append({
                        'source': source_name,
                        'document': doc_name,
                        'matches': matches,
                        'match_count': len(matches)
                    })

        # Sort by match count (most relevant first)
        results.sort(key=lambda x: x['match_count'], reverse=True)

        return results

    def get_document(self, document_name: str, source: str = 'both') -> Optional[str]:
        """
        Get a specific document by name.

        Args:
            document_name: Name of the document (e.g., 'brand_guidelines')
            source: Where to look ('primary', 'secondary', or 'both')

        Returns:
            Document content or None if not found
        """
        if source in ['both', 'primary']:
            primary = self.get_primary_knowledge()
            for key, content in primary.items():
                if document_name in key:
                    return content

        if source in ['both', 'secondary']:
            secondary = self.get_secondary_knowledge()
            for key, content in secondary.items():
                if document_name in key:
                    return content

        return None

    def get_section(self, document_name: str, section_name: str,
                   source: str = 'both') -> Optional[str]:
        """
        Get a specific section from a document.

        Args:
            document_name: Name of the document
            section_name: Name of the section (heading)
            source: Where to look for the document

        Returns:
            Section content or None if not found
        """
        document = self.get_document(document_name, source)

        if document:
            return self.processor.get_section_content(document, section_name)

        return None

    def summarize_knowledge_base(self) -> Dict[str, any]:
        """
        Get an overview of the knowledge base contents.

        Returns:
            Dictionary with summary information
        """
        primary = self.get_primary_knowledge()
        secondary = self.get_secondary_knowledge()

        summary = {
            'primary': {
                'document_count': len(primary),
                'documents': list(primary.keys()),
                'total_words': sum(len(content.split()) for content in primary.values())
            },
            'secondary': {
                'document_count': len(secondary),
                'documents': list(secondary.keys()),
                'total_words': sum(len(content.split()) for content in secondary.values())
            },
            'total_documents': len(primary) + len(secondary),
            'total_words': sum(len(content.split()) for content in primary.values()) +
                          sum(len(content.split()) for content in secondary.values())
        }

        return summary

    def prepare_context_for_prompt(self, include_primary: List[str] = None,
                                   include_secondary: List[str] = None) -> str:
        """
        Prepare formatted context string for LLM prompts.

        Args:
            include_primary: List of primary doc keywords to include (e.g., ['brand', 'product'])
            include_secondary: List of secondary doc keywords to include (e.g., ['market', 'competitor'])

        Returns:
            Formatted string ready for prompt injection
        """
        context_parts = []

        # Add primary knowledge
        if include_primary:
            context_parts.append("=== COMPANY KNOWLEDGE (Primary) ===\n")
            primary = self.get_primary_knowledge()

            for keyword in include_primary:
                for doc_name, content in primary.items():
                    if keyword.lower() in doc_name.lower():
                        doc_title = doc_name.split('/')[-1].replace('_', ' ').title()
                        context_parts.append(f"\n## {doc_title}\n{content}\n")

        # Add secondary knowledge
        if include_secondary:
            context_parts.append("\n=== INDUSTRY KNOWLEDGE (Secondary) ===\n")
            secondary = self.get_secondary_knowledge()

            for keyword in include_secondary:
                for doc_name, content in secondary.items():
                    if keyword.lower() in doc_name.lower():
                        doc_title = doc_name.split('/')[-1].replace('_', ' ').title()
                        context_parts.append(f"\n## {doc_title}\n{content}\n")

        return '\n'.join(context_parts)

    def reload_all(self):
        """Force reload all knowledge bases from disk."""
        self._primary_cache = None
        self._secondary_cache = None
        self.get_primary_knowledge(reload=True)
        self.get_secondary_knowledge(reload=True)
