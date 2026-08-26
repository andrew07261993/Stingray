# COTS, Vendor Data and BOMs

## Master component register

[COTS_MASTER_INDEX.md](../../../context/stingray/COTS_MASTER_INDEX.md) reconciles **74 exact configurations or controlled product families** with manufacturer, part number/family, vendor evidence, CAD availability, recovered specifications, selection status, architecture and classification.

## Current Package 05 COTS truth

| Function | Manufacturer / identity | Current status |
|---|---|---|
| CO2 cartridge | Leland `81121`, one 12 g cartridge | CURRENT DEVELOPMENTAL; compatibility/finished inflation open |
| Automatic/manual inflator | Halkey-Roberts `V95000XXB` / Hydro 1F | CURRENT DEVELOPMENTAL dimensional proxy; exact installed module/application not established |
| Water-sensitive bobbin | Halkey-Roberts `V80040` | CURRENT DEVELOPMENTAL modeled BUY identity |
| External buoy softgoods | Custom approximately 60 L pack | CURRENT DEVELOPMENTAL; not a complete qualified COTS module |
| SECUMAR 350 N / SECUTRONIC | Research family only | UNCERTAIN |
| `470-CG` / `V95000-1F` complete family | Fixed-480 internal-module screen | REJECTED for the 50.700 mm bore |

## GitHub COTS workstreams

| Workstream | Immutable GitHub location | Role / classification |
|---|---|---|
| Targeted COTS retrofit | [docs and procurement evidence at `fc5d76d`](https://github.com/andrew07261993/Stingray/tree/fc5d76dd9f7b15bd5975a667974869414aabd821/docs/engineering/cots/targeted-retrofit) | HISTORICAL developmental alternative |
| COTS-heavy architecture | [trade studies at `974b7f0`](https://github.com/andrew07261993/Stingray/tree/974b7f01ddc97d5ca43ccc595bc2f38e140ddd30/docs/engineering/cots/cots-heavy-architecture) | HISTORICAL documentation/trade |
| Per-part traceability | [mechanical-breakdown checkpoint at `95766a1`](https://github.com/andrew07261993/Stingray/tree/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown) | HISTORICAL part/render/deck evidence |

## Categorized local COTS evidence

The local catalog assigns 30 artifacts to `COTS_VENDOR_BOM`:

| Iteration | Artifact IDs | Contents |
|---|---|---|
| I01 | `LA-090`, `LA-091`, `LA-099`, `LA-100` | Early selected-parts, vendor-source and complete-BOM records |
| I08 | `LA-085` | Per-part COTS traceability |
| I09 | `LA-059`–`LA-061`, `LA-063`, `LA-081`–`LA-083` | Targeted-COTS final BOM, delta/connectivity, ledger, technical closure and RFQ log |
| I10 | `LA-074`–`LA-079` | COTS-heavy candidate/final BOMs, Architecture C selection, interface gate and vendor evidence |
| I12 | `LA-056` | Architecture C developmental validation record |
| I14 | `LA-048` | Distributed-pressure COTS accounting |
| I15 | `LA-042`, `LA-043` | Staged COTS accounting and vendor-proxy register |
| I16 | `LA-029`–`LA-034` | Commercial-module evidence, screens, package gate and non-pass manifest/readme |
| I18 | `LA-012`, `LA-013` | Current external-buoy component register and BOM delta |

Search `navigation_category=COTS_VENDOR_BOM` in [ARTIFACT_CATALOG_BY_TYPE.csv](ARTIFACT_CATALOG_BY_TYPE.csv) for exact paths and hashes.

## Vendor CAD

Vendor/reference STEP files are organized under `CAD_AND_3D` rather than duplicated here. Relevant historical identities include Clippard `MJV-3`, AutomationDirect `A12005SN`, Swagelok `SS-4CD-TW-10` and other exact parts listed in the master COTS index.

## Procurement boundary

RFQ transmission, catalog evidence, dimensional proxies and selected architecture records are not purchase, supplier qualification, acceptance or release authority. Exact suffix, installed envelope, rated interface, application approval, CoC/lot/expiry and received-item verification remain separate gates where marked open.

Return to [artifact navigation](README.md).
