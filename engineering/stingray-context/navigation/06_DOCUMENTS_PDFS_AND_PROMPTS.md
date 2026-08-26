# Documents, PDFs and Prompts

## Controlling documents on this branch

Read these before historical reports or prompts:

1. [CONTEXT_INDEX.md](../../../context/stingray/CONTEXT_INDEX.md)
2. [CURRENT_STATE.md](../../../context/stingray/CURRENT_STATE.md)
3. [CAD_PROVENANCE.md](../../../context/stingray/CAD_PROVENANCE.md)
4. [VALIDATION_STATUS.md](../../../context/stingray/VALIDATION_STATUS.md)
5. [REQUIREMENTS.md](../../../context/stingray/REQUIREMENTS.md)
6. [DECISION_REGISTER.md](../../../context/stingray/DECISION_REGISTER.md)
7. [OPEN_ITEMS.md](../../../context/stingray/OPEN_ITEMS.md)
8. [RETRIEVAL_GAPS.md](../../../context/stingray/RETRIEVAL_GAPS.md)

The cross-device engineering narrative is [CHATGPT_PROJECT_CONTEXT_SNAPSHOT_2026-08-25.md](../CHATGPT_PROJECT_CONTEXT_SNAPSHOT_2026-08-25.md). Exact session provenance is split between [SESSION_LEDGER.md](../SESSION_LEDGER.md) and [CODEX_SESSION_INDEX.md](../../../context/stingray/CODEX_SESSION_INDEX.md).

## Local engineering documents

The 110-artifact source index contains 24 Markdown files. They are organized by engineering role in the categorized catalog:

- design reports and comparisons → `ANALYSES_AND_REPORTS`;
- validation summaries → `VALIDATION_AND_TEST`;
- COTS decisions, gates and RFQ records → `COTS_VENDOR_BOM`;
- package readme → `DOCUMENTS_AND_PDFS`.

Use [ARTIFACT_CATALOG_BY_TYPE.csv](ARTIFACT_CATALOG_BY_TYPE.csv) to sort or search these records while retaining their exact local source paths and hashes.

## Prompts and commissions

Important historical prompts/commissions are indexed in:

- [early transition/reference prompts](../FILE_LIBRARY_MANIFEST.md#a-early-transition--reference-model-packages-and-manifests);
- [Iteration-5/DF7 corrective prompts](../FILE_LIBRARY_MANIFEST.md#b-iteration-5--df7-corrective-and-continuation-artifacts);
- [DF8 WP01–WP06 prompts](../FILE_LIBRARY_MANIFEST.md#c-df8-architecture-and-subsystem-prompts--source-records);
- [cross-device ChatGPT chronology](../SESSION_LEDGER.md);
- [local Codex session index](../../../context/stingray/CODEX_SESSION_INDEX.md).

Prompts preserve requirements and provenance, but they do not prove that requested CAD or validation was completed.

## PDF and Word status

| Format | Found in 110-artifact local index | Found in observed GitHub branch trees | Disposition |
|---|---:|---:|---|
| `.pdf` | 0 | 0 | No PDF artifact indexed |
| `.doc` / `.docx` | 0 | 0 | No Word artifact indexed |
| `.md` | 24 | Many context/engineering records | Primary readable document format |
| `.txt` | 0 local-index rows | SHA manifests and prompt references exist elsewhere | Indexed where engineering-relevant |

No empty PDF/Word placeholders were created. If future exports add these formats, record their exact source/configuration/hash before adding them to this navigation layer.

Return to [artifact navigation](README.md).
