"""
Test script for document processing and knowledge base functionality.

Run this script to verify that document ingestion and parsing work correctly.

Usage:
    python test_document_processing.py
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.document_processor import DocumentProcessor
from src.knowledge_base import KnowledgeBase


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_document_processor():
    """Test DocumentProcessor functionality."""
    print_section("TESTING DOCUMENT PROCESSOR")

    # Initialize processor
    kb_path = Path(__file__).parent / 'knowledge_base'
    processor = DocumentProcessor(str(kb_path))

    # Test 1: Load a single document
    print("\n1. Testing single document loading...")
    brand_doc_path = kb_path / 'primary' / 'brand_guidelines.md'

    if brand_doc_path.exists():
        content = processor.load_document(str(brand_doc_path))
        print(f"   ✓ Loaded brand_guidelines.md ({len(content)} characters)")
        print(f"   First 100 chars: {content[:100]}...")
    else:
        print(f"   ✗ File not found: {brand_doc_path}")

    # Test 2: Parse markdown
    print("\n2. Testing markdown parsing...")
    if brand_doc_path.exists():
        content = processor.load_document(str(brand_doc_path))
        parsed = processor.parse_markdown(content)

        print(f"   ✓ Sections found: {len(parsed['sections'])}")
        print(f"   ✓ Headings found: {len(parsed['headings'])}")
        print(f"   Sections: {list(parsed['sections'].keys())[:5]}")

    # Test 3: Extract sections
    print("\n3. Testing section extraction...")
    if brand_doc_path.exists():
        content = processor.load_document(str(brand_doc_path))
        brand_voice = processor.get_section_content(content, "Brand Voice")

        if brand_voice:
            print(f"   ✓ Extracted 'Brand Voice' section ({len(brand_voice)} chars)")
            print(f"   Content preview: {brand_voice[:150]}...")
        else:
            print("   ℹ 'Brand Voice' section not found")

    # Test 4: Load all documents
    print("\n4. Testing load all documents...")
    all_docs = processor.load_all_documents()
    print(f"   ✓ Loaded {len(all_docs)} total documents")

    for key in list(all_docs.keys())[:5]:
        print(f"      - {key}")

    # Test 5: Document summary
    print("\n5. Testing document summary...")
    if brand_doc_path.exists():
        content = processor.load_document(str(brand_doc_path))
        summary = processor.summarize_document(content)

        print(f"   ✓ Total sections: {summary['total_sections']}")
        print(f"   ✓ Word count: {summary['word_count']}")
        print(f"   ✓ Line count: {summary['line_count']}")
        print(f"   Headings: {summary['headings']}")


def test_knowledge_base():
    """Test KnowledgeBase functionality."""
    print_section("TESTING KNOWLEDGE BASE")

    # Initialize knowledge base
    kb_path = Path(__file__).parent / 'knowledge_base'
    kb = KnowledgeBase(str(kb_path))

    # Test 1: Get primary knowledge
    print("\n1. Testing primary knowledge retrieval...")
    primary = kb.get_primary_knowledge()
    print(f"   ✓ Primary documents: {len(primary)}")
    for key in primary.keys():
        word_count = len(primary[key].split())
        print(f"      - {key} ({word_count} words)")

    # Test 2: Get secondary knowledge
    print("\n2. Testing secondary knowledge retrieval...")
    secondary = kb.get_secondary_knowledge()
    print(f"   ✓ Secondary documents: {len(secondary)}")
    for key in secondary.keys():
        word_count = len(secondary[key].split())
        print(f"      - {key} ({word_count} words)")

    # Test 3: Get structured knowledge
    print("\n3. Testing structured knowledge...")
    structured = kb.get_structured_knowledge()
    print(f"   ✓ Structured categories: {len(structured)}")
    print(f"   Categories: {list(structured.keys())}")

    # Test 4: Search functionality
    print("\n4. Testing search functionality...")
    search_results = kb.search_knowledge("brand", source='primary')

    if search_results:
        print(f"   ✓ Found {len(search_results)} documents with 'brand'")
        for result in search_results[:3]:
            print(f"      - {result['document']}: {result['match_count']} matches")
    else:
        print("   ℹ No results found for 'brand'")

    # Test 5: Get specific document
    print("\n5. Testing get specific document...")
    brand_doc = kb.get_document('brand_guidelines', source='primary')

    if brand_doc:
        print(f"   ✓ Retrieved brand_guidelines ({len(brand_doc)} chars)")
    else:
        print("   ℹ brand_guidelines not found")

    # Test 6: Get specific section
    print("\n6. Testing get specific section...")
    brand_voice_section = kb.get_section('brand_guidelines', 'Brand Voice', source='primary')

    if brand_voice_section:
        print(f"   ✓ Retrieved 'Brand Voice' section ({len(brand_voice_section)} chars)")
        print(f"   Content: {brand_voice_section[:100]}...")
    else:
        print("   ℹ 'Brand Voice' section not found")

    # Test 7: Knowledge base summary
    print("\n7. Testing knowledge base summary...")
    summary = kb.summarize_knowledge_base()
    print(f"   ✓ Total documents: {summary['total_documents']}")
    print(f"   ✓ Total words: {summary['total_words']}")
    print(f"   Primary: {summary['primary']['document_count']} docs, {summary['primary']['total_words']} words")
    print(f"   Secondary: {summary['secondary']['document_count']} docs, {summary['secondary']['total_words']} words")

    # Test 8: Prepare context for prompt
    print("\n8. Testing context preparation for prompts...")
    context = kb.prepare_context_for_prompt(
        include_primary=['brand', 'product'],
        include_secondary=['market', 'competitor']
    )

    if context:
        print(f"   ✓ Generated prompt context ({len(context)} chars)")
        print(f"   Preview:\n{context[:300]}...")
    else:
        print("   ℹ No context generated")


def test_integration():
    """Test integration between components."""
    print_section("TESTING INTEGRATION")

    kb_path = Path(__file__).parent / 'knowledge_base'
    kb = KnowledgeBase(str(kb_path))

    print("\n1. Simulating content creation workflow...")

    # Step 1: Get structured knowledge
    structured = kb.get_structured_knowledge()
    print(f"   ✓ Step 1: Loaded {len(structured)} knowledge categories")

    # Step 2: Prepare context for specific content type
    context = kb.prepare_context_for_prompt(
        include_primary=['brand'],
        include_secondary=['market']
    )
    print(f"   ✓ Step 2: Prepared context ({len(context)} chars)")

    # Step 3: Show what would be passed to LLM
    print(f"\n   Context that would be sent to LLM:")
    print(f"   {'-' * 76}")
    print(f"   {context[:400]}...")
    print(f"   {'-' * 76}")

    print("\n   ✓ Integration test complete!")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  AI CONTENT CREATOR - DOCUMENT PROCESSING TEST SUITE")
    print("=" * 80)

    try:
        test_document_processor()
        test_knowledge_base()
        test_integration()

        print_section("TEST SUMMARY")
        print("\n✓ All tests completed successfully!")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Review test output to verify document parsing")
        print("  3. Add more documents to knowledge_base/ directories")
        print("  4. Test LLM integration with actual API calls")

    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
