# AI Content Creator

An intelligent content creation platform that leverages AI to generate high-quality, brand-aligned content at scale.

## Features

- 📚 **Dual Knowledge Base System**: Manage company-specific (primary) and industry research (secondary) knowledge
- 🔄 **Complete Content Pipeline**: Automated workflow from document processing to publication
- 🎯 **Advanced Prompt Engineering**: Context-aware templates for optimal content generation
- 🤖 **LLM Integration**: Powered by XY for superior content quality
- ⚙️ **Configurable Workflows**: Customize the content creation process to your needs

## Project Structure

```
ai-content-creator/
├── src/
│   ├── document_processor.py    # Markdown document ingestion and processing
│   ├── knowledge_base.py         # Primary and secondary knowledge base management
│   ├── prompt_templates.py       # Advanced prompt engineering templates
│   ├── content_pipeline.py       # document → monitor → brief → publish → iterate
│   ├── llm_integration.py        # LLM API integration
│   └── main.py                   # Main application entry point
├── knowledge_base/
│   ├── primary/                  # Company-specific documents
│   │   ├── brand_guidelines.md
│   │   ├── product_specs.md
│   │   └── past_content/
│   └── secondary/                # Industry research
│       ├── market_trends.md
│       └── competitor_analysis.md
├── templates/                     # Prompt engineering templates
├── config/
│   └── vscode_agent.json         # VSCode agent configuration
├── requirements.txt
└── .env                          # API keys (not committed)
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Anthropic API key

### Installation

1. Clone the repository or navigate to the project directory:
```bash
cd ai-content-creator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Configuration

1. Update your brand guidelines in `knowledge_base/primary/brand_guidelines.md`
2. Add product specifications in `knowledge_base/primary/product_specs.md`
3. Keep industry research updated in `knowledge_base/secondary/`
4. Customize the VSCode agent configuration in `config/vscode_agent.json`

### Usage

Run the main application:
```bash
python src/main.py
```

## Content Pipeline Stages

1. **Document**: Ingest and process source materials from knowledge bases
2. **Monitor**: Track industry trends and identify content opportunities
3. **Brief**: Generate comprehensive content briefs with context
4. **Publish**: Create final content aligned with brand guidelines
5. **Iterate**: Refine content based on feedback and performance

## Knowledge Base Management

### Primary Knowledge Base
Store company-specific information:
- Brand guidelines and voice
- Product specifications
- Past successful content
- Internal documentation

### Secondary Knowledge Base
Store industry research:
- Market trends and analysis
- Competitor insights
- Industry best practices
- Research papers and reports

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src/
```

### Type Checking
```bash
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and formatting
5. Submit a pull request

## License

[Specify your license here]

## Support

For questions or issues, please open an issue in the repository or contact [your contact information].

## Roadmap

- [ ] Multi-language support
- [ ] Image generation integration
- [ ] SEO optimization tools
- [ ] Analytics dashboard
- [ ] Additional LLM provider support
- [ ] Vector database integration for semantic search
