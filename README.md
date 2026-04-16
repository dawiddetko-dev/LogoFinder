# Logo And Trademark Verification POC (Azure AI)

Prototype project for detecting and confirming trademark/logo presence on product photos using Azure AI Content Understanding.

## What this project contains

- `data/logos_reference/`: place official logos and trademarks from documentation here.
- `data/products_to_verify/`: place product photos to be verified here.
- `src/logo_verification/`: Python application for running detection and generating reports.
- `infra/bicep/`: Azure Infrastructure-as-Code templates.
- `docs/`: architecture and operating instructions.

## Azure AI Components Used

- Azure AI Content Understanding: analyzer for logo/trademark detection.
- Azure Storage Account (Blob): optional storage for datasets.
- Azure Key Vault: secure secrets storage.

## Quick start

1. Create Python virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy environment template and fill values:

```bash
cp .env.example .env
```

3. Place files:
- Reference logos into `data/logos_reference/`
- Product photos into `data/products_to_verify/`

The app automatically treats all image filenames in `data/logos_reference/`
as target logos to detect. No CSV mapping is required.

4. Run verification:

```bash
PYTHONPATH=src python -m logo_verification.cli
```

5. Review output JSON report in `outputs/verification_report.json`.

## Basic UI for testing

One-click launcher (recommended):

```bash
bash scripts/launch_ui.sh
```

Manual start:

```bash
PYTHONPATH=src streamlit run ui/app.py
```

The UI provides:
- single image upload test
- batch verification for all files in `data/products_to_verify/`

## Deploy Azure resources

```bash
az login
az account set --subscription <subscription-id>
az group create -n rg-logo-verification-poc -l westeurope
az deployment group create \
  --resource-group rg-logo-verification-poc \
  --template-file infra/bicep/main.bicep \
  --parameters infra/bicep/main.parameters.json
```

Detailed setup and model-training flow are in `docs/setup_guide.md`.

## Publish to GitHub

See `docs/publishing_guide.md` for a step-by-step publication checklist and commands.

## Repository cleanup notes

The project is intentionally minimal for GitHub publishing:
- Single detection backend (Content Understanding).
- Optional local reference matcher fallback for recall improvements.
- No CSV expected-logo mapping file; expected logos come from `data/logos_reference/` file names.
