# Intelligence Assessment AI

This project implements an AI system that can assess human intelligence based on theories like Howard Gardner's Multiple Intelligences. The system uses Retrieval-Augmented Generation (RAG) with Google's Gemini model to ask questions and analyze responses.

## Features

- PDF document processing and vectorization
- RAG-based context retrieval for intelligence theories
- Interactive question-answer assessment flow
- Adaptive questioning based on previous responses
- Comprehensive intelligence profile generation

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Obtain a Google Gemini API key and set it:
   ```
   export GEMINI_API_KEY=your_api_key_here
   ```
4. Place intelligence theory PDFs in the `docs` folder

## Usage

### Process Documents

Before running the assessment, process the PDFs in the docs folder:

```
python main.py --process
```

This will:
- Extract text from all PDFs
- Split text into chunks
- Create embeddings
- Store them in a vector database

### Run Assessment

Start the intelligence assessment:

```
python main.py --assess
```

The AI will:
1. Ask questions one at a time
2. Analyze responses
3. Adapt questions based on previous answers
4. Generate a comprehensive intelligence profile

## Adding New Intelligence Theories

To add new intelligence theories:
1. Add PDF documents to the `docs` folder
2. Run `python main.py --process` to update the vector store
3. The new theories will be incorporated into assessments

## Extending the System

This system can be extended to support:
- Additional intelligence theories
- Custom scoring algorithms
- Age-specific assessments
- Visual or audio-based assessments
- Educational recommendations based on profiles

## License

MIT