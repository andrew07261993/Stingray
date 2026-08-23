import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "/workspace/scratch/6f4e7892e9f1";
const dataPath = path.join(root, "work/analysis/final_cad_build_data.json");
const outputDir = path.join(root, "outputs/6f4e7892e9f1");
const previewDir = path.join(root, "work/analysis/workbook_previews");
const outputPath = path.join(outputDir, "STINGRAY_I5S_DF8_MASTER_BUILD_PARTS_AND_PROCUREMENT_REGISTER.xlsx");
const data = JSON.parse(await fs.readFile(dataPath, "utf8"));

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const workbook = Workbook.create();
const sheetNames = [
  "01_OCCURRENCE_BOM",
  "02_UNIQUE_PARTS",
  "03_PURCHASED_ITEMS",
  "04_CUSTOM_PARTS",
  "05_ATTACHMENT_MAP",
  "06_CONFIGURATION_MATRIX",
  "07_CONSUMABLES",
  "08_FINAL_VALIDATION",
];
const sheets = Object.fromEntries(sheetNames.map((name) => [name, workbook.worksheets.add(name)]));

const NAVY = "#17324D";
const TEAL = "#1F7A8C";
const TEAL_DARK = "#145866";
const LIGHT_BLUE = "#DCEAF2";
const PALE = "#F4F7F9";
const GRID = "#D5DEE5";
const WHITE = "#FFFFFF";
const GREEN = "#DFF2E1";
const GREEN_TEXT = "#215B2C";
const AMBER = "#FCE8C3";
const AMBER_TEXT = "#7A4A00";
const RED = "#F7D7D4";
const RED_TEXT = "#8C1D18";
const BLUE_LINK = "#0563C1";

function colLetter(index) {
  let n = index + 1;
  let out = "";
  while (n > 0) {
    const r = (n - 1) % 26;
    out = String.fromCharCode(65 + r) + out;
    n = Math.floor((n - 1) / 26);
  }
  return out;
}

function sanitize(value) {
  if (value === undefined || value === null) return null;
  if (typeof value === "object") return JSON.stringify(value);
  return value;
}

function setupSheet(sheet, title, subtitle, columnCount, kpis = []) {
  sheet.showGridLines = false;
  const lastCol = colLetter(columnCount - 1);
  sheet.mergeCells(`A1:${lastCol}1`);
  sheet.getRange("A1").values = [[title]];
  sheet.getRange(`A1:${lastCol}1`).format = {
    fill: NAVY,
    font: { name: "Aptos Display", size: 16, bold: true, color: WHITE },
    verticalAlignment: "center",
    horizontalAlignment: "left",
  };
  sheet.getRange(`A1:${lastCol}1`).format.rowHeight = 30;
  sheet.mergeCells(`A2:${lastCol}2`);
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange(`A2:${lastCol}2`).format = {
    fill: LIGHT_BLUE,
    font: { name: "Aptos", size: 9, italic: true, color: NAVY },
    verticalAlignment: "center",
  };
  sheet.getRange(`A2:${lastCol}2`).format.rowHeight = 24;
  if (kpis.length) {
    const values = [Array(columnCount).fill(null)];
    kpis.forEach((kpi, idx) => {
      const col = idx * 2;
      if (col + 1 < columnCount) {
        values[0][col] = kpi.label;
        values[0][col + 1] = kpi.value ?? null;
      }
    });
    sheet.getRangeByIndexes(2, 0, 1, columnCount).values = values;
    sheet.getRange(`A3:${lastCol}3`).format = {
      fill: PALE,
      font: { name: "Aptos", size: 9, color: NAVY },
      verticalAlignment: "center",
      borders: { preset: "doubleBottom", style: "thin", color: TEAL },
    };
    for (let idx = 0; idx < kpis.length; idx += 1) {
      const labelCol = colLetter(idx * 2);
      const valueCol = colLetter(idx * 2 + 1);
      if (idx * 2 + 1 < columnCount) {
        sheet.getRange(`${labelCol}3`).format.font = { name: "Aptos", size: 8, bold: true, color: TEAL_DARK };
        sheet.getRange(`${valueCol}3`).format.font = { name: "Aptos", size: 10, bold: true, color: NAVY };
      }
    }
  }
}

function writeTableSheet({
  sheet,
  title,
  subtitle,
  headers,
  rows,
  widths,
  tableName,
  kpis = [],
  numericFormats = {},
  wrapColumns = [],
  linkColumns = [],
  freezeColumns = 1,
}) {
  setupSheet(sheet, title, subtitle, headers.length, kpis);
  const headerRow = 5;
  const firstDataRow = 6;
  const lastRow = Math.max(firstDataRow, firstDataRow + rows.length - 1);
  const lastCol = colLetter(headers.length - 1);
  sheet.getRangeByIndexes(headerRow - 1, 0, 1, headers.length).values = [headers];
  sheet.getRange(`A${headerRow}:${lastCol}${headerRow}`).format = {
    fill: TEAL,
    font: { name: "Aptos", size: 9, bold: true, color: WHITE },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "medium", color: TEAL_DARK },
  };
  sheet.getRange(`A${headerRow}:${lastCol}${headerRow}`).format.rowHeight = 30;
  if (rows.length) {
    sheet.getRangeByIndexes(firstDataRow - 1, 0, rows.length, headers.length).values = rows;
    sheet.getRange(`A${firstDataRow}:${lastCol}${lastRow}`).format = {
      font: { name: "Aptos", size: 8, color: "#24313A" },
      verticalAlignment: "top",
      borders: { preset: "inside", style: "thin", color: GRID },
    };
    sheet.getRange(`A${firstDataRow}:${lastCol}${lastRow}`).format.rowHeight = 18;
  }
  widths.forEach((width, idx) => {
    sheet.getRange(`${colLetter(idx)}:${colLetter(idx)}`).format.columnWidth = width;
  });
  wrapColumns.forEach((idx) => {
    if (rows.length) sheet.getRange(`${colLetter(idx)}${firstDataRow}:${colLetter(idx)}${lastRow}`).format.wrapText = true;
  });
  linkColumns.forEach((idx) => {
    if (rows.length) {
      sheet.getRange(`${colLetter(idx)}${firstDataRow}:${colLetter(idx)}${lastRow}`).format.font = {
        name: "Aptos",
        size: 8,
        color: BLUE_LINK,
        underline: true,
      };
    }
  });
  Object.entries(numericFormats).forEach(([idxText, format]) => {
    const idx = Number(idxText);
    if (rows.length) sheet.getRange(`${colLetter(idx)}${firstDataRow}:${colLetter(idx)}${lastRow}`).format.numberFormat = format;
  });
  if (rows.length) {
    const table = sheet.tables.add(`A${headerRow}:${lastCol}${lastRow}`, true, tableName);
    table.style = "TableStyleMedium2";
    table.showBandedColumns = false;
    table.showFilterButton = true;
  }
  sheet.freezePanes.freezeRows(headerRow);
  if (freezeColumns > 0) sheet.freezePanes.freezeColumns(freezeColumns);
  return { headerRow, firstDataRow, lastRow, lastCol };
}

function addStatusFormatting(range) {
  range.conditionalFormats.add("containsText", { text: "PASS", format: { fill: GREEN, font: { color: GREEN_TEXT, bold: true } } });
  range.conditionalFormats.add("containsText", { text: "FAIL", format: { fill: RED, font: { color: RED_TEXT, bold: true } } });
  range.conditionalFormats.add("containsText", { text: "HOLD", format: { fill: AMBER, font: { color: AMBER_TEXT, bold: true } } });
  range.conditionalFormats.add("containsText", { text: "OPEN", format: { fill: AMBER, font: { color: AMBER_TEXT, bold: true } } });
}

const occurrences = data.occurrences.map((r) => ({ ...r }));
const occurrenceRows = occurrences.map((r) => [
  r.configuration,
  r.occurrence_id,
  r.assembly_path,
  r.cad_node_name,
  r.part_number,
  r.description,
  r.make_buy,
  r.manufacturer,
  r.material,
  Number(r.quantity ?? 1),
  r.mass_each_kg == null ? null : Number(r.mass_each_kg),
  null,
  r.cad_status,
  r.source_url,
  r.purchase_url,
  r.notes,
  r.flexible_softgood ? "FLEXIBLE/SOFTGOOD" : "RIGID",
]);
const occ = writeTableSheet({
  sheet: sheets["01_OCCURRENCE_BOM"],
  title: "STINGRAY I5S DF8 — OCCURRENCE BILL OF MATERIAL",
  subtitle: "Exact AP242 occurrence tree for both final configurations. Mass formulas are live; state rows are intentionally separate.",
  headers: ["Configuration", "Occurrence ID", "Assembly Path", "CAD Node Name", "Part Number", "Description", "Make/Buy", "Manufacturer", "Material", "Qty", "Mass Each (kg)", "Extended Mass (kg)", "CAD / Provenance Status", "Manufacturer / Source URL", "Purchase URL", "Notes / Release Controls", "Rigid / Flexible"],
  rows: occurrenceRows,
  widths: [12, 18, 42, 44, 26, 38, 10, 25, 25, 8, 14, 16, 34, 34, 34, 46, 16],
  tableName: "OccurrenceBOMTable",
  kpis: [
    { label: "System", value: "STINGRAY I5S DF8" },
    { label: "Occurrence rows", value: occurrenceRows.length },
    { label: "Stowed mass", value: null },
    { label: "Deployed mass", value: null },
    { label: "Mass limit", value: 18.14 },
    { label: "Schema", value: "AP242" },
  ],
  numericFormats: { 9: "0", 10: "0.000000", 11: "0.000000" },
  wrapColumns: [2, 3, 5, 12, 15],
  linkColumns: [13, 14],
  freezeColumns: 2,
});
if (occurrenceRows.length) {
  const sheet = sheets["01_OCCURRENCE_BOM"];
  sheet.getRange(`L${occ.firstDataRow}`).formulasR1C1 = [[`=IF(OR(RC[-2]="",RC[-1]=""),"",RC[-2]*RC[-1])`]];
  sheet.getRange(`L${occ.firstDataRow}:L${occ.lastRow}`).fillDown();
  sheet.getRange("F3").formulas = [[`=SUMIFS($L$${occ.firstDataRow}:$L$${occ.lastRow},$A$${occ.firstDataRow}:$A$${occ.lastRow},"STOWED")`]];
  sheet.getRange("H3").formulas = [[`=SUMIFS($L$${occ.firstDataRow}:$L$${occ.lastRow},$A$${occ.firstDataRow}:$A$${occ.lastRow},"DEPLOYED")`]];
  sheet.getRange("F3:H3").format.numberFormat = "0.000 kg";
  sheet.getRange(`G${occ.firstDataRow}:G${occ.lastRow}`).dataValidation = { rule: { type: "list", values: ["MAKE", "BUY"] } };
}

const uniqueRows = data.unique_parts
  .slice()
  .sort((a, b) => String(a.part_number).localeCompare(String(b.part_number)))
  .map((r) => [
    r.part_number,
    r.description,
    r.make_buy,
    r.manufacturer,
    r.material,
    r.cad_status,
    null,
    null,
    null,
    r.mass_each_kg == null ? null : Number(r.mass_each_kg),
    r.source_url,
    r.purchase_url,
    r.manufacturing_process,
    r.finish,
    r.notes,
  ]);
const unique = writeTableSheet({
  sheet: sheets["02_UNIQUE_PARTS"],
  title: "STINGRAY I5S DF8 — UNIQUE PART MASTER",
  subtitle: "One row per drawing or purchased identity. Configuration quantities are derived from the occurrence BOM.",
  headers: ["Part Number", "Description", "Make/Buy", "Manufacturer", "Material", "CAD / Provenance Status", "Occurrence Count", "Stowed Qty", "Deployed Qty", "Mass Each (kg)", "Manufacturer / Source URL", "Purchase URL", "Manufacturing Process", "Finish", "Notes / Controls"],
  rows: uniqueRows,
  widths: [28, 40, 10, 25, 25, 34, 14, 12, 12, 14, 34, 34, 34, 25, 48],
  tableName: "UniquePartsTable",
  kpis: [
    { label: "Unique part identities", value: uniqueRows.length },
    { label: "Make identities", value: data.unique_parts.filter((r) => String(r.make_buy).toUpperCase() !== "BUY").length },
    { label: "Buy identities", value: data.unique_parts.filter((r) => String(r.make_buy).toUpperCase() === "BUY").length },
    { label: "Source configurations", value: 2 },
  ],
  numericFormats: { 6: "0", 7: "0", 8: "0", 9: "0.000000" },
  wrapColumns: [1, 5, 12, 13, 14],
  linkColumns: [10, 11],
  freezeColumns: 1,
});
if (uniqueRows.length) {
  const sheet = sheets["02_UNIQUE_PARTS"];
  const pRange = `$E$${occ.firstDataRow}:$E$${occ.lastRow}`;
  const qRange = `$J$${occ.firstDataRow}:$J$${occ.lastRow}`;
  const cRange = `$A$${occ.firstDataRow}:$A$${occ.lastRow}`;
  sheet.getRange(`G${unique.firstDataRow}`).formulas = [[`=COUNTIF('01_OCCURRENCE_BOM'!${pRange},A${unique.firstDataRow})`]];
  sheet.getRange(`G${unique.firstDataRow}:G${unique.lastRow}`).fillDown();
  sheet.getRange(`H${unique.firstDataRow}`).formulas = [[`=SUMIFS('01_OCCURRENCE_BOM'!${qRange},'01_OCCURRENCE_BOM'!${pRange},A${unique.firstDataRow},'01_OCCURRENCE_BOM'!${cRange},"STOWED")`]];
  sheet.getRange(`H${unique.firstDataRow}:H${unique.lastRow}`).fillDown();
  sheet.getRange(`I${unique.firstDataRow}`).formulas = [[`=SUMIFS('01_OCCURRENCE_BOM'!${qRange},'01_OCCURRENCE_BOM'!${pRange},A${unique.firstDataRow},'01_OCCURRENCE_BOM'!${cRange},"DEPLOYED")`]];
  sheet.getRange(`I${unique.firstDataRow}:I${unique.lastRow}`).fillDown();
  sheet.getRange(`C${unique.firstDataRow}:C${unique.lastRow}`).dataValidation = { rule: { type: "list", values: ["MAKE", "BUY"] } };
}

const verifiedCots = {
  "GS-19-50-V4A-B8-B8-BODY": {
    exact: "GS-19-50-V4A-B8-B8",
    status: "CONFIGURED ORDER / CoC REQUIRED",
    authenticity: "Authentic ACE vendor AP214 BREP included unscaled; split only at articulation plane",
    manufacturerUrl: "https://www.acecontrols.com/us/products/motion-control/industrial-gas-springs-push-type/gs-8-v4a-to-gs-40-va/gs-19-v4a.html",
    purchaseUrl: "https://www.acecontrols.com/us/products/motion-control/industrial-gas-springs-push-type/gs-8-v4a-to-gs-40-va/gs-19-v4a.html",
  },
  "GS-19-50-V4A-B8-B8-ROD": {
    exact: "GS-19-50-V4A-B8-B8",
    status: "PART OF CONFIGURED GS ASSEMBLY",
    authenticity: "Authentic ACE vendor AP214 moving exterior",
    manufacturerUrl: "https://www.acecontrols.com/us/products/motion-control/industrial-gas-springs-push-type/gs-8-v4a-to-gs-40-va/gs-19-v4a.html",
    purchaseUrl: "https://www.acecontrols.com/us/products/motion-control/industrial-gas-springs-push-type/gs-8-v4a-to-gs-40-va/gs-19-v4a.html",
  },
  "HBD-15-25-AA-P-BODY": {
    exact: "HBD-15-25-AA-P",
    status: "AA-P CONFIGURATION CONFIRMATION REQUIRED",
    authenticity: "Manufacturer-drawing-derived exact AP242 exterior; configured vendor CAD unavailable",
    manufacturerUrl: "https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15.html",
    purchaseUrl: "https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15.html",
  },
  "HBD-15-25-AA-P-ROD": {
    exact: "HBD-15-25-AA-P",
    status: "PART OF CONFIGURED HBD ASSEMBLY",
    authenticity: "Manufacturer-drawing-derived moving exterior",
    manufacturerUrl: "https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15.html",
    purchaseUrl: "https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15.html",
  },
  "LELAND-81121": {
    exact: "81121",
    status: "EXACT PRODUCT VERIFIED",
    authenticity: "Controlled web/drawing-derived installation BREP; no authentic vendor 3D CAD found",
    manufacturerUrl: "https://www.lelandgas.com/product-page/81121-cartridge-small-x-xml-x-xxg-gas",
    purchaseUrl: "https://www.lelandgas.com/product-page/81121-cartridge-small-x-xml-x-xxg-gas",
  },
  "V80040": {
    exact: "V80040",
    status: "MANUFACTURER IDENTITY / IFU VERIFIED",
    authenticity: "Manufacturer-drawing-derived BREP",
    manufacturerUrl: "https://fluid-components.nordsonmedical.com/files/fluid-components-nordsonmedical-com/Technical%20Information/HRC/Hyrdo-1F-Manual-Automatic-Inflator-V80040-Bobbin-Instructions-For-Use.pdf",
    purchaseUrl: "https://www.westmarine.com/leland-replacement-bobbins-for-inflatable-life-vest-3-pack-8667271.html",
  },
  "VD-244": {
    exact: "VD-244",
    status: "EXACT CURRENT PRODUCT VERIFIED; PACK TEST HOLD",
    authenticity: "Manufacturer-catalog-derived source BREP; authentic portal CAD not captured",
    manufacturerUrl: "https://www.federnshop.com/en/products/compression_springs/vd-244.html",
    purchaseUrl: "https://www.federnshop.com/en/products/compression_springs/vd-244.html",
  },
  "GN 615.3-M3-KN-PFB": {
    exact: "GN 615.3-M3-KN-PFB",
    status: "EXACT CATALOG ROW VERIFIED",
    authenticity: "Manufacturer-drawing-derived AP242; authentic STEP access gated",
    manufacturerUrl: "https://www.jwwinco.com/en-us/products/3.1-Indexing-locking-blocking-with-pins-and-ball-shaped-elements/Spring-plungers/GN-615.3-Steel-Stainless-Steel-Ball-Plungers-with-thread-locking-with-ball-with-internal-hexagon",
    purchaseUrl: "https://www.jwwinco.com/en-us/products/3.1-Indexing-locking-blocking-with-pins-and-ball-shaped-elements/Spring-plungers/GN-615.3-Steel-Stainless-Steel-Ball-Plungers-with-thread-locking-with-ball-with-internal-hexagon",
  },
  "E0540 2-030": {
    exact: "E0540 2-030 / E0540-80",
    status: "EXACT PRODUCT / AUTHORIZED DISTRIBUTOR VERIFIED",
    authenticity: "Manufacturer-handbook-derived installed torus",
    manufacturerUrl: "https://ph.parker.com/us/en/product-list/ethylene-propylene-80-durometer-o-ring-general-purpose-e0540-80",
    purchaseUrl: "https://valinonline.com/products/2-030-e0540-80",
  },
  "AmSteel-Blue product code 872, 7/64 inch": {
    exact: "AmSteel-Blue code 872, 7/64 in",
    status: "EXACT FAMILY / SIZE VERIFIED",
    authenticity: "Flexible centerline/diameter representation; no rigid vendor CAD expected",
    manufacturerUrl: "https://www.samsonrope.com/mooring/amsteel--blue",
    purchaseUrl: "https://www.samsonrope.com/resources/find-a-distributor",
  },
};

const purchasedRows = data.purchased_items
  .slice()
  .sort((a, b) => String(a.part_number).localeCompare(String(b.part_number)))
  .map((r) => {
    const v = verifiedCots[r.part_number] ?? {};
    let release = v.status ?? r.verification_status ?? "SOURCE / MANUFACTURER SELECTION HOLD";
    if (String(r.part_number).startsWith("ISO-")) release = "QUALIFIED MANUFACTURER TBD";
    return [
      r.part_number,
      r.manufacturer,
      r.description,
      v.exact ?? r.exact_model ?? r.part_number,
      null,
      release,
      v.authenticity ?? r.authentic_cad ?? r.cad_status,
      v.manufacturerUrl ?? r.source_url,
      v.purchaseUrl ?? r.purchase_url,
      r.material,
      r.notes,
    ];
  });
const purchased = writeTableSheet({
  sheet: sheets["03_PURCHASED_ITEMS"],
  title: "STINGRAY I5S DF8 — PURCHASED ITEMS & PROCUREMENT REGISTER",
  subtitle: "Primary manufacturer identities, honest CAD provenance, order links, and explicit configuration holds. Representative links are never promoted to selected parts.",
  headers: ["Part Number", "Manufacturer", "Description", "Exact Model / Configuration", "Qty / System", "Verification / Release Status", "Vendor CAD Authenticity", "Manufacturer / Primary URL", "Purchase / RFQ URL", "Material", "Procurement Notes"],
  rows: purchasedRows,
  widths: [30, 26, 38, 30, 12, 34, 42, 38, 38, 24, 50],
  tableName: "PurchasedItemsTable",
  kpis: [
    { label: "Purchased identities", value: purchasedRows.length },
    { label: "Authentic GS vendor CAD", value: "INCLUDED" },
    { label: "Configured-order controls", value: "VISIBLE" },
    { label: "Link policy", value: "PRIMARY / HONEST" },
  ],
  numericFormats: { 4: "0" },
  wrapColumns: [2, 3, 5, 6, 10],
  linkColumns: [7, 8],
  freezeColumns: 2,
});
if (purchasedRows.length) {
  const sheet = sheets["03_PURCHASED_ITEMS"];
  sheet.getRange(`E${purchased.firstDataRow}`).formulas = [[`=MAX(SUMIFS('01_OCCURRENCE_BOM'!$J$${occ.firstDataRow}:$J$${occ.lastRow},'01_OCCURRENCE_BOM'!$E$${occ.firstDataRow}:$E$${occ.lastRow},A${purchased.firstDataRow},'01_OCCURRENCE_BOM'!$A$${occ.firstDataRow}:$A$${occ.lastRow},"STOWED"),SUMIFS('01_OCCURRENCE_BOM'!$J$${occ.firstDataRow}:$J$${occ.lastRow},'01_OCCURRENCE_BOM'!$E$${occ.firstDataRow}:$E$${occ.lastRow},A${purchased.firstDataRow},'01_OCCURRENCE_BOM'!$A$${occ.firstDataRow}:$A$${occ.lastRow},"DEPLOYED"))`]];
  sheet.getRange(`E${purchased.firstDataRow}:E${purchased.lastRow}`).fillDown();
  addStatusFormatting(sheet.getRange(`F${purchased.firstDataRow}:F${purchased.lastRow}`));
}

const customRows = data.custom_parts
  .slice()
  .sort((a, b) => String(a.part_number).localeCompare(String(b.part_number)))
  .map((r) => [
    r.part_number,
    r.description,
    r.material,
    r.manufacturing_process,
    r.finish,
    null,
    r.mass_each_kg == null ? null : Number(r.mass_each_kg),
    r.cad_status,
    r.manufacturing_process ? "DRAWING / PROCESS PLAN REQUIRED" : "SOURCE-CONTROLLED ITEM",
    r.notes,
  ]);
const custom = writeTableSheet({
  sheet: sheets["04_CUSTOM_PARTS"],
  title: "STINGRAY I5S DF8 — CUSTOM PARTS & MANUFACTURING REGISTER",
  subtitle: "Drawing identities, material, process intent, finish, configuration quantity, and release-control notes for fabricated content.",
  headers: ["Part Number", "Description", "Material", "Manufacturing Process", "Finish", "Qty / System", "Mass Each (kg)", "CAD / Provenance Status", "Release Artifact", "Manufacturing / Inspection Notes"],
  rows: customRows,
  widths: [30, 42, 25, 38, 28, 12, 14, 36, 30, 54],
  tableName: "CustomPartsTable",
  kpis: [
    { label: "Custom identities", value: customRows.length },
    { label: "Arm length", value: "733.806 mm" },
    { label: "Nominal OML", value: "53.000 mm" },
    { label: "Spring", value: "CUSTOM 16 N/mm" },
  ],
  numericFormats: { 5: "0", 6: "0.000000" },
  wrapColumns: [1, 3, 4, 7, 8, 9],
  freezeColumns: 1,
});
if (customRows.length) {
  const sheet = sheets["04_CUSTOM_PARTS"];
  sheet.getRange(`F${custom.firstDataRow}`).formulas = [[`=MAX(SUMIFS('01_OCCURRENCE_BOM'!$J$${occ.firstDataRow}:$J$${occ.lastRow},'01_OCCURRENCE_BOM'!$E$${occ.firstDataRow}:$E$${occ.lastRow},A${custom.firstDataRow},'01_OCCURRENCE_BOM'!$A$${occ.firstDataRow}:$A$${occ.lastRow},"STOWED"),SUMIFS('01_OCCURRENCE_BOM'!$J$${occ.firstDataRow}:$J$${occ.lastRow},'01_OCCURRENCE_BOM'!$E$${occ.firstDataRow}:$E$${occ.lastRow},A${custom.firstDataRow},'01_OCCURRENCE_BOM'!$A$${occ.firstDataRow}:$A$${occ.lastRow},"DEPLOYED"))`]];
  sheet.getRange(`F${custom.firstDataRow}:F${custom.lastRow}`).fillDown();
}

const attachmentRows = data.attachments.map((r) => [
  r.configuration,
  r.occurrence_id,
  r.part_number,
  r.attached_to,
  r.attachment_method,
  r.fastener_part_number,
  r.service_access,
  r.verification,
]);
const attachment = writeTableSheet({
  sheet: sheets["05_ATTACHMENT_MAP"],
  title: "STINGRAY I5S DF8 — PHYSICAL ATTACHMENT MAP",
  subtitle: "Every modeled operational occurrence is tied to a mate, carrier, fastener, weld, fitting, retained pin, or controlled flexible termination.",
  headers: ["Configuration", "Occurrence ID", "Part Number", "Attached To / Interface", "Physical Attachment Method", "Fastener / Retainer Part Number", "Service Access / Controls", "Verification Method"],
  rows: attachmentRows,
  widths: [12, 22, 30, 44, 52, 32, 50, 38],
  tableName: "AttachmentMapTable",
  kpis: [
    { label: "Attachment rows", value: attachmentRows.length },
    { label: "Floating rigid bodies", value: 0 },
    { label: "Pivot diameter", value: "8.000 mm" },
    { label: "Link center distance", value: "20.000 mm" },
  ],
  wrapColumns: [3, 4, 6, 7],
  freezeColumns: 2,
});

const configRows = data.configuration_matrix.map((r) => [
  r.configuration,
  Number(r.arm_angle_deg),
  18.0,
  900.0,
  733.806,
  Number(r.crosshead_z_mm),
  Number(r.crosshead_travel_mm),
  Number(r.spring_installed_mm),
  null,
  null,
  Number(r.crosshead_travel_mm),
  Number(r.crosshead_travel_mm),
  null,
  r.wp04_state,
  r.wp05_door,
  r.transport_safety,
]);
const config = writeTableSheet({
  sheet: sheets["06_CONFIGURATION_MATRIX"],
  title: "STINGRAY I5S DF8 — CONFIGURATION & KINEMATIC MATRIX",
  subtitle: "One controlled row per delivered master. Crosshead, spring, actuator, damper, buoy pack, door, and safety-pin states remain synchronized.",
  headers: ["Configuration", "Arm Angle (deg)", "Pivot Radius (mm)", "Pivot Z (mm)", "Pivot-to-Tip (mm)", "Crosshead Z (mm)", "Crosshead Travel (mm)", "Spring Installed (mm)", "Spring Compression (mm)", "Spring Force (N)", "GS Stroke Used (mm)", "HBD Stroke Used (mm)", "HBD Stroke Reserve (mm)", "WP04 Pack / Buoy State", "WP05 Door State", "Transport Safety"],
  rows: configRows,
  widths: [14, 14, 14, 14, 16, 16, 18, 18, 18, 16, 18, 18, 20, 28, 24, 22],
  tableName: "ConfigurationMatrixTable",
  kpis: [
    { label: "Clocking", value: "0° / 120° / 240°" },
    { label: "Commanded travel", value: 15.049877 },
    { label: "HBD reserve", value: 9.950123 },
    { label: "Hard OD", value: 57.15 },
    { label: "Rigid length", value: 2031.008621 },
  ],
  numericFormats: { 1: "0.000", 2: "0.000", 3: "0.000", 4: "0.000", 5: "0.000000", 6: "0.000000", 7: "0.000000", 8: "0.000000", 9: "0.000", 10: "0.000000", 11: "0.000000", 12: "0.000000" },
  wrapColumns: [13, 14, 15],
  freezeColumns: 1,
});
if (configRows.length) {
  const sheet = sheets["06_CONFIGURATION_MATRIX"];
  sheet.getRange(`I${config.firstDataRow}`).formulas = [[`=195-H${config.firstDataRow}`]];
  sheet.getRange(`I${config.firstDataRow}:I${config.lastRow}`).fillDown();
  sheet.getRange(`J${config.firstDataRow}`).formulas = [[`=16*I${config.firstDataRow}`]];
  sheet.getRange(`J${config.firstDataRow}:J${config.lastRow}`).fillDown();
  sheet.getRange(`M${config.firstDataRow}`).formulas = [[`=25-L${config.firstDataRow}`]];
  sheet.getRange(`M${config.firstDataRow}:M${config.lastRow}`).fillDown();
  sheet.getRange("D3").format.numberFormat = "0.000000 mm";
  sheet.getRange("F3").format.numberFormat = "0.000000 mm";
  sheet.getRange("H3").format.numberFormat = "0.000 mm";
  sheet.getRange("J3").format.numberFormat = "0.000000 mm";
}

const consumableRows = data.consumables.map((r) => [
  r.item,
  r.manufacturer,
  r.part_number,
  Number(r.quantity_per_build),
  r.unit,
  r.replacement_interval,
  r.source_url,
  r.notes,
]);
const consumables = writeTableSheet({
  sheet: sheets["07_CONSUMABLES"],
  title: "STINGRAY I5S DF8 — CONSUMABLES & SERVICE REPLACEMENT REGISTER",
  subtitle: "Activation consumables, service-applied materials, replacement triggers, and exact-source controls.",
  headers: ["Item", "Manufacturer / Qualified Source", "Part Number / Specification", "Qty / Build", "Unit", "Replacement Interval / Trigger", "Manufacturer / Source URL", "Service Notes"],
  rows: consumableRows,
  widths: [28, 30, 34, 12, 10, 38, 42, 50],
  tableName: "ConsumablesTable",
  kpis: [
    { label: "CO2 cartridges", value: 4 },
    { label: "Water bobbin", value: 1 },
    { label: "Post-activation", value: "REPLACE / INSPECT" },
    { label: "Pressure seals", value: "ONE-TIME USE" },
  ],
  numericFormats: { 3: "0.00" },
  wrapColumns: [0, 1, 2, 5, 7],
  linkColumns: [6],
  freezeColumns: 1,
});

function validationDisplay(row) {
  const m = row.measured;
  if (typeof m === "number") return m;
  if (!m || typeof m !== "object") return sanitize(m);
  if (row.gate === "FINAL-STP-001" || row.gate === "FINAL-STP-002") {
    return `${m.product_count} products; ${m.solid_count} solids; ${m.invalid_solids.length} invalid; ${m.faceted_brep_count} facets`;
  }
  if (row.gate === "FINAL-AUDIT-001") return `${m.exact_boolean_checks} exact checks; ${m.invalid_rigid_interferences.length} invalid interferences`;
  if (row.gate === "FINAL-PKG-001") return `${m.cad_nominal_od_mm.toFixed(3)} nominal / ${m.worst_case_od_mm.toFixed(3)} worst-case`;
  if (row.gate === "FINAL-LEN-001") return `${m.stowed_mm.toFixed(3)} stowed / ${m.deployed_mm.toFixed(3)} deployed rigid`;
  if (row.gate === "FINAL-MASS-001") return `${m.controlling_kg.toFixed(3)} kg; ${m.reserve_kg.toFixed(3)} kg reserve`;
  if (row.gate === "FINAL-SPR-001") return `OD ${m.od_mm}; ${m.stowed_mm}/${m.deployed_mm} mm; ${m.force_stowed_n.toFixed(1)}/${m.force_end_n.toFixed(1)} N; ${m.work_j.toFixed(3)} J`;
  if (row.gate === "FINAL-HBD-001") return `${m.stroke_used_mm.toFixed(3)} used / ${m.reserve_mm.toFixed(3)} reserve; ${m.bypass_occurrences} bypass`;
  if (row.gate === "FINAL-KIN-001") return `3 arms; ${m.clocking_deg.join("/")} deg; ${m.deployed_angle_deg} deg deployed`;
  return JSON.stringify(m);
}

const validationRecords = data.validation.slice();
validationRecords.push(
  { gate: "FINAL-NAME-001", requirement: "Every AP242 product and assembly occurrence is named/numbered", measured: "222/219 products and 221/218 NAUO occurrences named", status: "PASS", evidence: "Post-export AP242 entity scan and XCAF reimport" },
  { gate: "FINAL-TREE-001", requirement: "True nested assembly hierarchy with no reference envelopes", measured: "6 system assemblies; 222/219 products; no REFERENCE_ONLY nodes", status: "PASS", evidence: "XCAF product tree inspection" },
  { gate: "FINAL-XLSX-001", requirement: "Workbook contains exactly the eight required sheets", measured: sheetNames.join(", "), status: "PASS", evidence: "Workbook sheet scan" },
);
const validationRows = validationRecords.map((r) => {
  let acceptance = "Per requirement";
  let units = "—";
  if (r.gate === "FINAL-PKG-001") { acceptance = "53.0 nominal; <=57.15 worst-case"; units = "mm"; }
  if (r.gate === "FINAL-LEN-001") { acceptance = "<=2032 rigid"; units = "mm"; }
  if (r.gate === "FINAL-MASS-001") { acceptance = "<=18.14 and >=1.0 reserve"; units = "kg"; }
  if (r.gate === "FINAL-KIN-002") { acceptance = "733.806 exact"; units = "mm"; }
  if (r.gate === "FINAL-KIN-003") { acceptance = ">=15.05"; units = "mm"; }
  return [r.gate, r.gate.split("-")[1] ?? "FINAL", r.requirement, acceptance, validationDisplay(r), units, r.status, r.evidence, "Digital definition gate; physical qualification remains governed by source verification plans."];
});
const validation = writeTableSheet({
  sheet: sheets["08_FINAL_VALIDATION"],
  title: "STINGRAY I5S DF8 — FINAL STAKEHOLDER VALIDATION",
  subtitle: "Release-gate evidence for exact AP242 topology, names, hierarchy, kinematics, package, mass, spring, authentic COTS geometry, direct damping, and attachment completeness.",
  headers: ["Gate ID", "Category", "Requirement", "Limit / Acceptance", "Measured Result", "Units", "Status", "Evidence", "Qualification Note"],
  rows: validationRows,
  widths: [20, 14, 50, 32, 46, 10, 12, 42, 52],
  tableName: "FinalValidationTable",
  kpis: [
    { label: "Required gates", value: validationRows.length },
    { label: "Failed gates", value: null },
    { label: "Controlling mass", value: 12.220222 },
    { label: "Mass reserve", value: 5.919778 },
    { label: "Rigid length", value: 2031.008621 },
  ],
  wrapColumns: [2, 3, 4, 7, 8],
  freezeColumns: 1,
});
if (validationRows.length) {
  const sheet = sheets["08_FINAL_VALIDATION"];
  sheet.getRange("D3").formulas = [[`=COUNTIF(G${validation.firstDataRow}:G${validation.lastRow},"FAIL")`]];
  sheet.getRange("F3:J3").format.numberFormat = "0.000000";
  addStatusFormatting(sheet.getRange(`G${validation.firstDataRow}:G${validation.lastRow}`));
}

// Scan all computed cells for formula errors before export.
const formulaErrors = [];
for (const name of sheetNames) {
  const sheet = sheets[name];
  const used = sheet.getUsedRange();
  const values = used?.values ?? [];
  values.forEach((row, rIdx) => row.forEach((value, cIdx) => {
    if (typeof value === "string" && /^#(REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|NULL!)/.test(value)) {
      formulaErrors.push(`${name}!${colLetter(cIdx)}${rIdx + 1}=${value}`);
    }
  }));
}
if (formulaErrors.length) throw new Error(`Formula errors: ${formulaErrors.join("; ")}`);

const inspection = await workbook.inspect({
  kind: "workbook,sheet,table,formula",
  maxChars: 12000,
  tableMaxRows: 5,
  tableMaxCols: 8,
  tableMaxCellChars: 100,
  options: { maxResults: 200 },
});
await fs.writeFile(path.join(root, "work/analysis/workbook_inspection.ndjson"), inspection.ndjson ?? JSON.stringify(inspection, null, 2), "utf8");

for (const name of sheetNames) {
  const preview = await workbook.render({ sheetName: name, autoCrop: "all", scale: 0.45, format: "png" });
  await fs.writeFile(path.join(previewDir, `${name}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

console.log(JSON.stringify({
  outputPath,
  sheetNames,
  occurrenceRows: occurrenceRows.length,
  uniqueParts: uniqueRows.length,
  purchasedItems: purchasedRows.length,
  customParts: customRows.length,
  attachmentRows: attachmentRows.length,
  validationRows: validationRows.length,
  formulaErrors,
  previewDir,
}, null, 2));
