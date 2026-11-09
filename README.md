# PikaAI: Pokemon Battle Assistant with RAG + LoRA

> A competitive Pokemon VGC doubles battle assistant combining Retrieval-Augmented Generation (RAG) with LoRA fine-tuning.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        PikaAI Pipeline                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ Data Sources │───▶│  Ingestion   │───▶│  Vector DB   │       │
│  │  (PokéAPI,   │    │  & Chunking  │    │  (Chroma/    │       │
│  │   VGC Rules, │    │              │    │   FAISS)     │       │ 
│  │   Battle     │    │              │    │              │       │
│  │   Logs)      │    │              │    │              │       │
│  └──────────────┘    └──────────────┘    └──────┬───────┘       │
│                                                  │              │
│                                                  ▼              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   LoRA       │◀───│  Generator   │◀───│  Retriever   │       │
│  │  Adapter     │    │  (LLM +      │    │  (Embedding  │       │
│  │              │    │   Context)   │    │   + Search)  │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│        ▲                                       │                │
│        │                                       │                │
│        └───────────────────────────────────────┘                │
│                              │                                  │
│                              ▼                                  │
│                    ┌──────────────────┐                         │
│                    │  Chat Interface  │                         │
│                    │  (CLI / API)     │                         │
│                    └──────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Data Ingestion (`src/data/ingestion.py`)
- Fetches data from **PokéAPI** (pokemon, moves, abilities, items, types)
- Processes VGC rules and regulations
- Ingests battle logs from `master.json`
- Chunks documents for optimal embedding

### 2. RAG Pipeline (`src/rag/`)
- **Retriever** (`retriever.py`): Vector search with ChromaDB or FAISS
  - Similarity search, MMR (Maximal Marginal Relevance)
  - Configurable score thresholds and filtering
- **Generator** (`generator.py`): Context-augmented LLM responses
  - Prompt templates for RAG, chat, and no-context modes
  - Streaming response support
  - Token counting and context window management

### 3. LoRA Training (`src/training/train_lora.py`)
- Fine-tunes base models (Llama-3.2, Mistral, etc.) on Pokemon data
- PEFT/LoRA configuration with configurable rank, alpha, dropout
- Supports 4-bit/8-bit quantization via bitsandbytes
- Weights & Biases integration for experiment tracking

### 4. Chat Interface (`src/inference/chat_bot.py`)
- Interactive CLI with commands (`quit`, `clear`, `stats`, `rag on/off`)
- Streaming and non-streaming response modes
- Chat history management
- RAG toggle for comparison

## Quick Start

### Installation

### Configuration

### Data Ingestion

### Build Vector Database


### Train LoRA Adapter


### Run Chatbot


## Project Structure

```
pikaai/
├── configs/
│   ├── training_config.yaml      # LoRA training config template
│   └── ragn_config.yaml          # Vector DB & embedding config template
├── data/
│   ├── raw/                      # Raw PokéAPI JSON dumps or text documentation
│   ├── processed/                # Chunked and cleaned documents for embedding
│   └── vector_db/                # Local vector database storage (Chroma/FAISS)
├── notebooks/
│   ├── 01_data_exploration.ipynb # Data exploration and analysis
│   └── 02_rag_retrieval_test.ipynb # RAG retrieval testing and evaluation
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── ingestion.py          # Fetch/parse PokéAPI data and chunk it
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── retriever.py          # Vector search and document retrieval
│   │   └── generator.py          # Context augmentation and prompt formatting
│   ├── training/
│   │   └── train_lora.py         # LoRA fine-tuning script
│   └── inference/
│       └── chat_bot.py           # Main chatbot integrating LoRA + RAG
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Configuration Details

### Training Config (`training_config.yaml`)

Key sections:
- **model**: Base model selection, dtype, trust_remote_code
- **lora**: LoRA hyperparameters (r, alpha, dropout, target_modules)
- **training**: TrainingArguments (batch size, epochs, lr, scheduler, etc.)
- **data**: Dataset paths, max_seq_length, text field
- **wandb**: Experiment tracking settings

### RAG Config (`ragn_config.yaml`)

Key sections:
- **vector_db**: Provider (chromadb/faiss), persist directory, collection name
- **embedding**: Model name, device, batch size, normalization
- **chunking**: Strategy, chunk_size, chunk_overlap, separators
- **retrieval**: top_k, score_threshold, search_type (similarity/mmr)
- **generation**: System prompt, temperature, max_tokens, context window
- **data_sources**: PokéAPI endpoints, VGC rules, battle logs paths

## Data Sources

| Source | Type | Description |
|--------|------|-------------|
| PokéAPI | REST API | Pokemon, moves, abilities, items, types, natures |
| VGC Rules | Text file | Regulation rules, banlists, format specifications |
| Battle Logs | JSONL | Historical battles from `pikabot` (../pikabot/battle_logs/master.json) |

## Development

### Running Notebooks

```bash
jupyter lab notebooks/
```

### Code Style

```bash
# Format
black src/
ruff check --fix src/

# Type check
mypy src/
```

### Testing

```bash
pytest tests/ -v
```

## Roadmap

- [ ] Complete data ingestion implementation
- [ ] Build vector database with Pokemon knowledge
- [ ] Implement retrieval with hybrid search (dense + sparse)
- [ ] Create training dataset from battle logs + synthetic QA
- [ ] Train LoRA adapter on VGC strategy data
- [ ] Evaluate RAG vs. LoRA vs. RAG+LoRA performance
- [ ] Add web UI / Discord bot interface
- [ ] Integrate with `pikabot` for real-time battle assistance

## Related Projects

- **[pikabot](../pikabot/)**: Competitive VGC doubles battle bot

## License

MIT