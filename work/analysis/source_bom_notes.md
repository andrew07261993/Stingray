# Source BOM aggregation notes

The normalized aggregate contains **102 engineering-BOM records**, **19 COTS/source-evidence records**, and **8 authentic-vendor-CAD request records**.

| Package | BOM records | Known line masses | Missing masses | Sum of available line masses (kg) | Complete mass total? |
|---|---:|---:|---:|---:|---|
| WP01 | 16 | 14 | 2 | 13.837336361019 | No |
| WP02 | 34 | 34 | 0 | 3.492839014 | Yes |
| WP03 | 8 | 0 | 8 | 0 | No |
| WP04 | 31 | 31 | 0 | 0.845693499464 | Yes |
| WP05 | 13 | 9 | 4 | 0.031577620765 | No |

Missing normalized fields across the 102 BOM records: source item number 8; description 0; part number/model 0; quantity 0; mass 14; material 8; make/buy 0; manufacturer 0; primary vendor URL 81; CAD authenticity/status 8; source path 0.

Important source constraints:

- WP03's engineering BOM has eight aggregate descriptive labels, no item-number column, no material column, and no mass column. Those fields are deliberately null; the detailed WP03 modeled-mass register is not forced onto non-1:1 aggregate BOM rows.
- WP01's two COTS BOM rows report mass as `UNKNOWN`. WP05's four external service-tool rows have no mass entries. These account for the remaining missing masses.
- WP04 and WP05 operational masses are exact item-ID joins to their STOWED mass registers. Values are source line/set masses and were not multiplied by BOM quantity.
- WP02 and WP03 make/buy values are transparent deterministic mappings from their explicit `COTS` / `CUSTOM` classification fields; every such record is marked in `make_buy_source`.
- Public URLs are expected mainly for COTS/vendor-evidence rows. Custom parts retain their exact CAD/source references instead of invented URLs.
- The exact WP04 BOM used is `work/input/wp04/STINGRAY_I5S_DF8_WP04_SPRING_EJECTOR_AND_BUOY_PACK/08_BOM_SOURCES_AND_MANUFACTURING/ENGINEERING_BOM.csv`.
- The exact WP05 BOM used is `work/input/wp05/STINGRAY_I5S_DF8_WP05_AFT_CLOSURE_SERVICE_AND_RESET/08_BOM_SOURCES_AND_MANUFACTURING/WP05_ENGINEERING_BOM.csv`.
- The WP01 legacy Accu COTS record and all drawing/catalog-only evidence records remain in `source_evidence_register_records` even where they do not match a current BOM line.
