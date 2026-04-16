# Setup Guide - Azure Logo Verification POC

## 1. Azure resources

Deploy resources from Bicep templates in `infra/bicep`:

- Storage Account + Blob Container (`images`)
- Azure AI Content Understanding account
- Azure AI Custom Vision Training account (optional fallback)
- Azure AI Custom Vision Prediction account (optional fallback)
- Key Vault

After deployment, configure Content Understanding analyzer for logo extraction:

1. Open Azure AI Foundry / Content Understanding.
2. Create analyzer for visual content.
3. Configure analyzer output schema to include logo labels (for example `detected_logos`).
4. Test analyzer and note analyzer id.
5. Copy endpoint, API key, and analyzer id to `.env`.

## 2. Local project setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 3. Data preparation

- Put reference logos into `data/logos_reference/`.
- Put photos to verify into `data/products_to_verify/`.

The pipeline automatically uses all image filenames from `data/logos_reference/`
as target logos to detect, so CSV configuration is not required.

## 4. Run verification

```bash
PYTHONPATH=src python -m logo_verification.cli
```

## 5. Run basic user interface

```bash
PYTHONPATH=src streamlit run ui/app.py
```

## 6. Interpret report

Output report is generated at `outputs/verification_report.json`.

For each file, report includes:
- detected logos above threshold
- matched expected logos
- missing expected logos
- final verification flag
