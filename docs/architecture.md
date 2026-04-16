# Architecture (POC)

## Flow

1. Documentation provides required trademarks/logos.
2. Reference logo images are stored in `data/logos_reference/`.
3. Product photos are stored in `data/products_to_verify/`.
4. Azure AI Content Understanding analyzer detects logos on product photos.
5. Pipeline compares detections against expected logos inferred from filenames in `data/logos_reference/`.
6. JSON report is generated for verification decision.
7. Streamlit UI allows single-image and batch tests.

## Azure components

- Content Understanding: inference endpoint used by CLI and UI.
- Azure Blob Storage: optional central repository for training and inference data.
- Azure Key Vault: secure API keys and connection strings.

## Operational recommendation

- Keep one label/tag per trademark class.
- Retrain model when new logos or variants are introduced.
- Start with threshold 0.65 and tune based on precision/recall.
