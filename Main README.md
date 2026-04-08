# RAIT MLE Technical Assessment

## Overview
This assessment implements a supplier-agnostic evaluation framework for AI systems, focusing on responsible AI metrics and adversarial robustness testing. The solution uses open-source models exclusively, making it suitable for local execution on Ubuntu systems.

## Architecture Decisions

### 1. Canonical Schema Design
The schema separates required fields (minimal viable data contract) from optional fields:
- **Required**: `interaction_id`, `timestamp`, `prompt`, `response`, `supplier_id`
- **Optional**: `model_metadata`, `confidence_scores`, `token_usage`, `response_time`

This ensures:
- Maximum compatibility across different supplier formats
- Clear identification of missing data for graceful degradation
- Extensibility for future suppliers

### 2. Supplier Abstraction
Each supplier adapter implements a common interface but handles:
- **Supplier A**: Full API simulation with JSON format
- **Supplier B**: CSV batch logs with confidence scores
- **Supplier C**: Limited data from PDF summary + sampled interactions

The adapter pattern ensures evaluation logic remains supplier-agnostic.

### 3. Metric Implementation
Three metrics from different ethical dimensions:
- **Security/Adversarial Robustness**: Prompt injection detection rate using pattern matching and semantic similarity
- **Fairness/Bias**: Sentiment and response quality parity across demographic groups
- **Transparency/Explainability**: Confidence calibration and response attribution

### 4. Graceful Degradation Strategy
The coverage reporter tracks:
- Which fields were available for each supplier
- What metrics could be fully/completely scored
- Partial scores with transparency indicators

### 5. Open-Source LLM Usage
Using `sentence-transformers/all-MiniLM-L6-v2` for embeddings and `HuggingFaceH4/zephyr-7b-beta` for LLM-as-judge:
- All models run locally on Ubuntu
- No API costs or external dependencies
- Suitable for evaluation purposes

## Memory Fix
```bash
# Low RAM? Run this first:
sudo fallocate -l 4G /swapfile && sudo swapon /swapfile
export CUDA_VISIBLE_DEVICES=-1
python run_assessment.py

## Trade-offs

### Made
1. **Local LLM vs Cloud APIs**: Chose local models for reproducibility and zero cost, accepting slower inference
2. **Simple embedding model**: Used MiniLM for speed vs larger models for slightly better accuracy
3. **Synthetic data**: Generated representative test data that mimics real supplier formats
4. **Rule-based + LLM metrics**: Combined approaches for reliability vs pure LLM-based scoring

### Acknowledged
1. Local LLM quality may be lower than GPT-4, but sufficient for evaluation patterns
2. Coverage reporting adds complexity but ensures transparency
3. Partial scoring may require manual interpretation for Supplier C

## Onboarding a Fourth Supplier

To add a new supplier with a different format:

1. **Create adapter class** inheriting from `BaseAdapter`
2. **Implement `load_data()` method** to read supplier-specific format
3. **Implement `transform_to_canonical()` method** mapping to canonical schema
4. **Handle missing fields gracefully** by marking them as None
5. **Register adapter** in factory pattern for automatic discovery

No changes needed to the evaluation layer (metrics, coverage reporting) - they work with canonical schema directly.

## Setup Instructions

### Prerequisites
```bash
# Ubuntu 22.04+ with Python 3.10+
sudo apt update
sudo apt install python3.10 python3-pip

