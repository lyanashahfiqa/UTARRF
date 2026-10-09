# AI-SWHC — Research Prototype

**AI-Supported Single-Window Halal Compliance (AI-SWHC)** is a Streamlit research demonstration for Malaysian micro, small and medium food enterprises (MSMFEs), based on the UTARRF proposal.

## Included features
- Dashboard with actual supplier count and illustrative compliance chart
- Supplier record management: add, edit, delete and attach sample PDF/JPG/PNG certificates (max 5 MB)
- Certificate date status **only** (not official verification)
- Document Processing upload preview (OCR not implemented)
- Traceability Monitoring example records (not persisted)
- Compliance Assessment four-item demonstration checklist
- Research Evaluation overview (questionnaire collection not implemented)

**IMPORTANT:** This is a proof-of-concept, NOT an official halal certificate validation service or a JAKIM application portal. Do not upload real certificates, confidential supplier information, or participant data to a public deployment. No login, multi-user isolation, production database, backup, or consent workflow is implemented.

## Run locally

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Upload to GitHub
1. Create a new GitHub repository, e.g. `ai-swhc-prototype`.
2. Upload `app.py`, `requirements.txt`, `README.md`, `.gitignore`, and `.streamlit/config.toml` (keep the folder structure).
3. Do **not** upload the `data/` folder, SQLite files, uploaded documents, or any real personal/business information.

## Deploy with Streamlit Community Cloud
1. Go to https://share.streamlit.io/ and sign in with GitHub.
2. Select **Create app** / **Deploy app**, choose your repository and branch.
3. Set the main file path to `app.py`.
4. Deploy, then open the generated URL.

**Cloud storage warning:** Streamlit Community Cloud local SQLite files and uploaded documents are ephemeral and are not reliable persistent storage. Multiple visitors may share the same local demo database; do not treat it as private. For real data or multi-user use, add authentication, access controls, persistent managed storage and proper security review first.

## Research alignment
Prototype dimensions: documentation accuracy, supplier verification efficiency, traceability completeness, centralised evidence submission, and perceived platform effectiveness. PLS-SEM and ANN analyses are separate research activities, not currently implemented in this website.

## Suggested next stages
1. Separate users/roles and add a hosted database (e.g. Postgres).
2. Add verified reference data and documented compliance rules reviewed by halal experts.
3. Implement OCR with human verification and explicit provenance.
4. Implement an ethics-approved evaluation questionnaire and secure response storage.
