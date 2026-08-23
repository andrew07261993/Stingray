import fs from "node:fs/promises";
import path from "node:path";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const scriptPath = await fs.realpath(fileURLToPath(import.meta.url));
const scriptDir = path.dirname(scriptPath);
const workDir = path.dirname(scriptDir);
const analysisDir = path.join(workDir, "r2_analysis");
const releaseDir = path.join(workDir, "r2_release");
const metadataDir = path.join(workDir, "r2_metadata");
const previewDir = path.join(analysisDir, "workbook_previews");
const outputPath = path.join(
  releaseDir,
  "STINGRAY_I5S_DF8_R2_CANDIDATE_WIP_REVIEW_WORKBOOK.xlsx",
);

const RELEASE_STATUS = "CREO_VALIDATION_PENDING — WIP — NOT RELEASED";
const COLORS = {
  navy: "#17365D",
  blue: "#1F4E78",
  teal: "#0F6B78",
  cyan: "#DDEBF7",
  pale: "#EAF2F8",
  white: "#FFFFFF",
  ink: "#17202A",
  gray: "#6B7280",
  line: "#CBD5E1",
  green: "#E2F0D9",
  greenInk: "#276221",
  red: "#FCE4D6",
  redInk: "#9C0006",
  amber: "#FFF2CC",
  amberInk: "#9C6500",
  purple: "#E4DFEC",
};

function normalizeKey(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

function firstDefined(...values) {
  return values.find((value) => value !== undefined && value !== null && value !== "");
}

function pick(row, aliases, fallback = "") {
  if (!row || typeof row !== "object") return fallback;
  const indexed = new Map(Object.entries(row).map(([k, v]) => [normalizeKey(k), v]));
  for (const alias of aliases) {
    const value = indexed.get(normalizeKey(alias));
    if (value !== undefined && value !== null && value !== "") return value;
  }
  return fallback;
}

function asNumber(value) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "boolean") return value ? 1 : 0;
  if (value === null || value === undefined || value === "") return null;
  const cleaned = String(value).trim().replace(/,/g, "");
  const numeric = Number(cleaned);
  if (Number.isFinite(numeric)) return numeric;
  const unitMatch = cleaned.match(/^([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*[A-Za-z°³²/_-]*$/);
  return unitMatch ? Number(unitMatch[1]) : null;
}

function asYesNo(value) {
  if (value === true || value === 1) return "YES";
  if (value === false || value === 0) return "NO";
  const text = String(value ?? "").trim().toUpperCase();
  if (["YES", "TRUE", "PASS", "PASSED", "CLEAN", "OK", "SUCCESS"].includes(text)) return "YES";
  if (["NO", "FALSE", "FAIL", "FAILED", "ERROR"].includes(text)) return "NO";
  return "";
}

async function safeJson(fileName, fallback = null, baseDir = analysisDir) {
  try {
    const text = await fs.readFile(path.join(baseDir, fileName), "utf8");
    return JSON.parse(text);
  } catch {
    return fallback;
  }
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += ch;
    }
  }
  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  if (!rows.length) return [];
  const headers = rows.shift().map((h, i) => String(h || `column_${i + 1}`).trim());
  return rows
    .filter((r) => r.some((cell) => String(cell).trim() !== ""))
    .map((r) => Object.fromEntries(headers.map((header, i) => [header, r[i] ?? ""])));
}

async function safeCsv(fileName, baseDir = analysisDir) {
  try {
    const filePath = path.join(baseDir, fileName);
    const raw = await fs.readFile(filePath);
    const bytes = fileName.endsWith(".gz") ? zlib.gunzipSync(raw) : raw;
    return parseCsv(bytes.toString("utf8"));
  } catch {
    return [];
  }
}

async function fileMeta(filePath) {
  try {
    const stat = await fs.stat(filePath);
    return { present: true, size: stat.size };
  } catch {
    return { present: false, size: 0 };
  }
}

function columnLetter(index) {
  let n = index + 1;
  let out = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    out = String.fromCharCode(65 + rem) + out;
    n = Math.floor((n - 1) / 26);
  }
  return out;
}

function excelString(value) {
  return String(value ?? "").replace(/"/g, '""');
}

function csvCell(value) {
  if (value === null || value === undefined) return "";
  const text = value instanceof Date ? value.toISOString() : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function csvText(rows) {
  return `${rows.map((row) => row.map(csvCell).join(",")).join("\r\n")}\r\n`;
}

function inspectionValues(result) {
  for (const line of String(result?.ndjson ?? "").split(/\r?\n/)) {
    if (!line.trim()) continue;
    try {
      const parsed = JSON.parse(line);
      if (Array.isArray(parsed.values)) return parsed.values;
    } catch {
      // Ignore non-JSON diagnostic lines; a missing values record is handled below.
    }
  }
  throw new Error("Workbook inspection did not return a values matrix.");
}

function matrixText(value) {
  if (!Array.isArray(value)) return "";
  return value
    .map((row) => (Array.isArray(row) ? row.map((v) => Number(v).toFixed(6)).join(", ") : ""))
    .join(" | ");
}

function countBy(items, keyFn) {
  const map = new Map();
  for (const item of items) {
    const key = keyFn(item);
    map.set(key, (map.get(key) ?? 0) + 1);
  }
  return map;
}

function flattenGateResults(data) {
  if (!data) return [];
  if (Array.isArray(data)) return data;
  for (const key of ["gates", "gate_results", "results", "validation_gates"]) {
    if (Array.isArray(data[key])) return data[key];
    if (data[key] && typeof data[key] === "object") {
      return Object.entries(data[key]).map(([id, value]) =>
        value && typeof value === "object" ? { gate_id: id, ...value } : { gate_id: id, actual: value },
      );
    }
  }
  if (typeof data === "object") {
    return Object.entries(data)
      .filter(([, value]) => value && typeof value === "object")
      .map(([key, value]) => ({ gate_id: key, ...value }));
  }
  return [];
}

function providedMetric(gates, aliases) {
  const needles = aliases.map(normalizeKey);
  const gate = gates.find((candidate) => {
    const identity = normalizeKey(
      firstDefined(candidate.gate_id, candidate.id, candidate.name, candidate.gate, candidate.requirement),
    );
    const compactIdentity = identity.replace(/_/g, "");
    return needles.some((needle) => {
      const compactNeedle = needle.replace(/_/g, "");
      return identity === needle || identity.includes(needle) || compactIdentity.includes(compactNeedle);
    });
  });
  if (!gate) return null;
  const reportedStatus = String(firstDefined(gate.status, gate.gate_status, gate.result_status, "")).toUpperCase();
  if (/BLOCKED|PENDING|NOT RUN|MISSING/.test(reportedStatus)) return null;
  for (const key of [
    "actual",
    "actual_value",
    "result_value",
    "metric_value",
    "observed_value",
    "measured_value",
    "measured",
    "value",
    "evidence_value",
    "result",
  ]) {
    const value = gate[key];
    if (value !== undefined && value !== null && value !== "") {
      if (value && typeof value === "object") {
        const nested = firstDefined(
          value.value,
          value.actual,
          value.measured,
          value.result,
          value.actual_value,
          value.measured_value,
          value.value_mm,
          value.actual_mm,
          value.measured_mm,
          value.observed_mm,
          value.actual_max_mm,
          value.maximum_observed_mm,
          value.stowed_max_mm,
          value.deployed_max_mm,
          value.max_diameter_mm,
          value.max_od_mm,
          value.diameter_mm,
          value.distance_mm,
          value.travel_mm,
          value.max_mm,
          value.maximum_mm,
          value.count,
          value.total,
        );
        if (nested !== undefined && nested !== null && nested !== "") {
          const nestedNumeric = asNumber(nested);
          return nestedNumeric ?? nested;
        }
        const primitive = Object.values(value).find(
          (entry) => typeof entry === "number" || typeof entry === "boolean" || typeof entry === "string",
        );
        if (primitive !== undefined) {
          const primitiveNumeric = asNumber(primitive);
          return primitiveNumeric ?? primitive;
        }
      }
      const numeric = asNumber(value);
      return numeric ?? value;
    }
  }
  return null;
}

function deepPick(data, aliases, fallback = "") {
  if (!data || typeof data !== "object") return fallback;
  const wanted = new Set(aliases.map(normalizeKey));
  const queue = [data];
  const seen = new Set();
  while (queue.length) {
    const current = queue.shift();
    if (!current || typeof current !== "object" || seen.has(current)) continue;
    seen.add(current);
    for (const [key, value] of Object.entries(current)) {
      if (wanted.has(normalizeKey(key)) && value !== undefined && value !== null && value !== "") return value;
      if (value && typeof value === "object") queue.push(value);
    }
  }
  return fallback;
}

function numericOrBlank(value) {
  return asNumber(value) ?? "";
}

function applyStatusConditionalFormatting(range) {
  range.conditionalFormats.add("containsText", {
    text: "PASS",
    format: { fill: COLORS.green, font: { bold: true, color: COLORS.greenInk } },
  });
  range.conditionalFormats.add("containsText", {
    text: "CLOSED",
    format: { fill: COLORS.green, font: { bold: true, color: COLORS.greenInk } },
  });
  range.conditionalFormats.add("containsText", {
    text: "COMPLETE",
    format: { fill: COLORS.green, font: { bold: true, color: COLORS.greenInk } },
  });
  range.conditionalFormats.add("containsText", {
    text: "VERIFIED",
    format: { fill: COLORS.green, font: { bold: true, color: COLORS.greenInk } },
  });
  range.conditionalFormats.add("containsText", {
    text: "DEFINED",
    format: { fill: COLORS.green, font: { bold: true, color: COLORS.greenInk } },
  });
  range.conditionalFormats.add("containsText", {
    text: "FAIL",
    format: { fill: COLORS.red, font: { bold: true, color: COLORS.redInk } },
  });
  range.conditionalFormats.add("containsText", {
    text: "OPEN",
    format: { fill: COLORS.red, font: { bold: true, color: COLORS.redInk } },
  });
  range.conditionalFormats.add("containsText", {
    text: "INCOMPLETE",
    format: { fill: COLORS.red, font: { bold: true, color: COLORS.redInk } },
  });
  range.conditionalFormats.add("containsText", {
    text: "BLOCKED",
    format: { fill: COLORS.amber, font: { bold: true, color: COLORS.amberInk } },
  });
  range.conditionalFormats.add("containsText", {
    text: "PENDING",
    format: { fill: COLORS.amber, font: { bold: true, color: COLORS.amberInk } },
  });
  range.conditionalFormats.add("containsText", {
    text: "MISSING",
    format: { fill: COLORS.amber, font: { bold: true, color: COLORS.amberInk } },
  });
}

function createTitle(sheet, title, subtitle, columnCount) {
  const last = columnLetter(Math.max(0, columnCount - 1));
  sheet.showGridLines = false;
  sheet.getRange(`A1:${last}1`).merge();
  sheet.getRange("A1").values = [[title]];
  sheet.getRange(`A1:${last}1`).format = {
    fill: COLORS.navy,
    font: { bold: true, color: COLORS.white, size: 16 },
    verticalAlignment: "center",
  };
  sheet.getRange(`A1:${last}1`).format.rowHeight = 28;
  sheet.getRange(`A2:${last}2`).merge();
  sheet.getRange("A2").values = [[RELEASE_STATUS]];
  sheet.getRange(`A2:${last}2`).format = {
    fill: COLORS.amber,
    font: { bold: true, color: COLORS.redInk, size: 11 },
    verticalAlignment: "center",
  };
  sheet.getRange(`A2:${last}2`).format.rowHeight = 23;
  sheet.getRange(`A3:${last}3`).merge();
  sheet.getRange("A3").values = [[subtitle]];
  sheet.getRange(`A3:${last}3`).format = {
    fill: COLORS.pale,
    font: { italic: true, color: COLORS.ink, size: 9 },
    wrapText: true,
    verticalAlignment: "center",
  };
  sheet.getRange(`A3:${last}3`).format.rowHeight = 30;
}

function setColumnWidths(sheet, headers, rows, caps = {}) {
  headers.forEach((header, col) => {
    let length = String(header).length;
    for (const row of rows.slice(0, 500)) {
      const cell = row[col];
      if (cell && typeof cell === "object" && "formula" in cell) continue;
      length = Math.max(length, String(cell ?? "").split("\n")[0].length);
    }
    const cap = caps[col] ?? (/(notes|description|evidence|url|path|feature|retention|matrix)/i.test(header) ? 42 : 24);
    const width = Math.min(cap, Math.max(9, Math.ceil(length * 0.92 + 2)));
    sheet.getRange(`${columnLetter(col)}:${columnLetter(col)}`).format.columnWidth = width;
  });
}

function writeTable(sheet, startRow, headers, rows, options = {}) {
  const lastCol = columnLetter(headers.length - 1);
  const safeRows = rows.length ? rows : [headers.map(() => "")];
  sheet.getRange(`A${startRow}:${lastCol}${startRow}`).values = [headers];
  sheet.getRange(`A${startRow}:${lastCol}${startRow}`).format = {
    fill: COLORS.blue,
    font: { bold: true, color: COLORS.white, size: 9 },
    wrapText: true,
    verticalAlignment: "center",
    borders: { preset: "outside", style: "thin", color: COLORS.navy },
  };
  sheet.getRange(`A${startRow}:${lastCol}${startRow}`).format.rowHeight = 30;
  const values = safeRows.map((row) => row.map((cell) => (cell && typeof cell === "object" && "formula" in cell ? null : cell)));
  const dataStart = startRow + 1;
  const dataEnd = dataStart + safeRows.length - 1;
  sheet.getRange(`A${dataStart}:${lastCol}${dataEnd}`).values = values;
  safeRows.forEach((row, rowIndex) => {
    row.forEach((cell, colIndex) => {
      if (cell && typeof cell === "object" && "formula" in cell) {
        sheet.getCell(dataStart - 1 + rowIndex, colIndex).formulas = [[cell.formula]];
      }
    });
  });
  sheet.getRange(`A${dataStart}:${lastCol}${dataEnd}`).format = {
    font: { color: COLORS.ink, size: 9 },
    wrapText: true,
    verticalAlignment: "top",
    borders: {
      insideHorizontal: { style: "thin", color: COLORS.line },
      bottom: { style: "thin", color: COLORS.line },
    },
  };
  if (safeRows.length > 1) {
    for (let row = dataStart; row <= dataEnd; row += 2) {
      sheet.getRange(`A${row}:${lastCol}${row}`).format.fill = "#F8FAFC";
    }
  }
  if (options.numberFormats) {
    for (const [colIndexText, format] of Object.entries(options.numberFormats)) {
      const colIndex = Number(colIndexText);
      sheet.getRange(`${columnLetter(colIndex)}${dataStart}:${columnLetter(colIndex)}${dataEnd}`).format.numberFormat = format;
    }
  }
  if (options.statusColumns) {
    for (const colIndex of options.statusColumns) {
      applyStatusConditionalFormatting(
        sheet.getRange(`${columnLetter(colIndex)}${dataStart}:${columnLetter(colIndex)}${dataEnd}`),
      );
    }
  }
  setColumnWidths(sheet, headers, safeRows, options.widthCaps ?? {});
  sheet.freezePanes.freezeRows(startRow);
  return { startRow, dataStart, dataEnd, lastCol };
}

function makeStatusFormula(actualCell, criterionCell, operator, valueIsKnown = false) {
  const missing = valueIsKnown
    ? `OR(${actualCell}="PENDING",${actualCell}="MISSING",${actualCell}="NOT RUN")`
    : `OR(${actualCell}="",${actualCell}="PENDING",${actualCell}="MISSING",${actualCell}="NOT RUN")`;
  if (operator === ">=") return `=IF(${missing},"BLOCKED",IF(${actualCell}>=${criterionCell},"PASS","FAIL"))`;
  if (operator === "<=") return `=IF(${missing},"BLOCKED",IF(${actualCell}<=${criterionCell},"PASS","FAIL"))`;
  if (operator === "=") return `=IF(${missing},"BLOCKED",IF(${actualCell}=${criterionCell},"PASS","FAIL"))`;
  if (operator === "YES") return `=IF(${missing},"BLOCKED",IF(${actualCell}="YES","PASS","FAIL"))`;
  if (operator === "PASS") return `=IF(${missing},"BLOCKED",IF(${actualCell}="PASS","PASS","FAIL"))`;
  return `=IF(${missing},"BLOCKED",IF(${actualCell}=${criterionCell},"PASS","FAIL"))`;
}

const stowed = await safeJson("authoring_inventory_stowed.json", {
  state: "STOWED",
  parts: [],
  occurrences: [],
  connections: [],
  routes: [],
  kinematics: {},
});
const deployed = await safeJson("authoring_inventory_deployed.json", {
  state: "DEPLOYED",
  parts: [],
  occurrences: [],
  connections: [],
  routes: [],
  kinematics: {},
});
const manifest = await safeJson("authoring_manifest.json", {
  release_status: RELEASE_STATUS,
  schema: "",
  authoring_kernel: "",
  hard_requirements: {},
  files: {},
});
const gateResultData = await safeJson(
  "validation/gate_results.json",
  await safeJson("gate_results.json", null),
);
const providedGates = flattenGateResults(gateResultData);
const creoData = await safeJson(
  "CREO_VALIDATION.json",
  await safeJson("creo_validation.json", null),
  metadataDir,
);
const loadPathData = await safeJson(
  "validation/connectivity_summary.json",
  await safeJson("load_path_results.json", null),
);
const authoringPairAuditStowed = await safeJson("authoring_pair_audit_stowed.json", null);
const authoringPairAuditDeployed = await safeJson("authoring_pair_audit_deployed.json", null);

const clearanceCsv = await safeCsv("validation/minimum_clearance_register.csv");
const occurrenceInventoryStowedCsv = await safeCsv("validation/xcaf_occurrences_stowed.csv");
const occurrenceInventoryDeployedCsv = await safeCsv("validation/xcaf_occurrences_deployed.csv");
const solidInventoryStowedCsv = await safeCsv("validation/leaf_solids_stowed.csv");
const solidInventoryDeployedCsv = await safeCsv("validation/leaf_solids_deployed.csv");
const motionSamplesCsv = await safeCsv("validation/motion_kinematics_1deg.csv");
const connectivityNodesCsv = await safeCsv("validation/attachment_connectivity_stowed.csv");
const connectivityEdgesCsv = await safeCsv("validation/attachment_connectivity_deployed.csv");
const jointGeometryCsv = await safeCsv("joint_geometry_checks.csv");
const routingTerminationCsv = await safeCsv("routing_termination_register.csv");
const stateDeltaCsv = await safeCsv("validation/state_parity.csv");
const sourceReimportCsv = await safeCsv("source_vs_reimport.csv");
const stowedPairAudit = await safeCsv("validation/endpoint_pair_audit_stowed.csv.gz");
const deployedPairAudit = await safeCsv("validation/endpoint_pair_audit_deployed.csv.gz");
const componentDir = path.join(workDir, "r2_components");
const componentProvenanceCsv = await safeCsv("provenance.csv", componentDir);
const componentProvenanceByPart = new Map(
  componentProvenanceCsv
    .filter((row) => String(row.record_type ?? "") === "CONTROLLED_PART_DEFINITION")
    .map((row) => [String(row.part_number ?? ""), row]),
);

const partMap = new Map((stowed.parts ?? []).map((part) => [part.part_number, part]));
for (const part of deployed.parts ?? []) partMap.set(part.part_number, part);
const parts = [...partMap.values()].sort((a, b) => String(a.part_number).localeCompare(String(b.part_number)));
const stowedQty = countBy(stowed.occurrences ?? [], (occ) => occ.part_number);
const deployedQty = countBy(deployed.occurrences ?? [], (occ) => occ.part_number);

const workbook = Workbook.create();
const sheetNames = [
  "00_README",
  "01_NCR_CLOSURE",
  "02_UNIQUE_PARTS",
  "03_PURCHASED_ITEMS",
  "04_OCCURRENCE_BOM",
  "05_ATTACHMENT_REGISTER",
  "06_HARDWARE_FITTINGS",
  "07_CLEARANCE_REGISTER",
  "08_INTERFERENCE_REGISTER",
  "09_MOTION_SWEEP",
  "10_SOURCE_CAD",
  "11_STATE_MATRIX",
  "12_VALIDATION_GATES",
  "13_MASS_PROPERTIES",
  "14_COMPLIANCE",
  "15_EVIDENCE_INDEX",
  "16_CREO_VALIDATION",
  "17_ROUTING",
  "18_CUSTOM_PARTS",
  "19_CONSUMABLES",
];
const sheets = new Map(sheetNames.map((name) => [name, workbook.worksheets.add(name)]));

// 02_UNIQUE_PARTS
{
  const sheet = sheets.get("02_UNIQUE_PARTS");
  const headers = [
    "Part Number",
    "Rev",
    "Description",
    "Make / Buy",
    "Material",
    "Manufacturer",
    "CAD Classification",
    "Unit Mass kg",
    "Solid Count",
    "Face Count",
    "Source URL",
    "Purchase URL",
    "Release Blocker",
  ];
  createTitle(sheet, "R2 UNIQUE PART MASTER", "One row per authored part definition; status formulas remain live and auditable.", headers.length);
  const solidEvidenceAvailable = solidInventoryStowedCsv.length > 0 && solidInventoryDeployedCsv.length > 0;
  sheet.getRange("A4:F4").values = [[
    "Authored Unique Parts",
    parts.length,
    "Reimport Solid Rows",
    solidEvidenceAvailable ? solidInventoryStowedCsv.length + solidInventoryDeployedCsv.length : "",
    "Reimport Evidence",
    solidEvidenceAvailable ? "AVAILABLE" : "MISSING",
  ]];
  sheet.getRange("A4:F4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  const rows = parts.map((part, index) => {
    const row = 6 + index;
    return [
      part.part_number,
      part.revision,
      part.description,
      part.make_buy,
      part.material,
      part.manufacturer,
      part.cad_classification,
      numericOrBlank(part.mass_kg),
      numericOrBlank(part.solid_count),
      numericOrBlank(part.face_count),
      part.source_url,
      part.purchase_url,
      {
        formula: `=IF(OR(G${row}="PROVISIONAL — BLOCKS FINAL RELEASE",AND(D${row}="BUY",L${row}="")),"YES","NO")`,
      },
    ];
  });
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 7: "0.000", 8: "0", 9: "0" },
    statusColumns: [12],
    widthCaps: { 2: 42, 4: 28, 6: 34, 10: 48, 11: 48 },
  });
}

// 18_CUSTOM_PARTS
{
  const sheet = sheets.get("18_CUSTOM_PARTS");
  const headers = [
    "Part Number",
    "Rev",
    "Description",
    "Material",
    "Manufacturing Process",
    "Finish / Treatment",
    "Qty Stowed",
    "Qty Deployed",
    "CAD Classification",
    "Drawing / Process Plan Reference",
    "Controlled CAD Path",
    "Controlled CAD SHA-256",
    "Calculated Definition Status",
    "Disposition",
  ];
  createTitle(
    sheet,
    "R2 CUSTOM PART FABRICATION DEFINITION",
    "Explicit custom-part register. Controlled CAD alone is not a fabrication drawing or process plan; formula status remains BLOCKED until both are evidenced.",
    headers.length,
  );
  const customParts = parts.filter(
    (part) => String(part.make_buy ?? "").toUpperCase() === "MAKE" && !part.external_context,
  );
  const rows = customParts.map((part, index) => {
    const row = 6 + index;
    const provenance = componentProvenanceByPart.get(String(part.part_number ?? "")) ?? {};
    const drawingOrPlan = firstDefined(provenance.source_path, part.drawing_reference, part.process_plan_reference, "") ?? "";
    return [
      part.part_number,
      part.revision,
      part.description,
      part.material,
      part.process,
      part.finish,
      stowedQty.get(part.part_number) ?? 0,
      deployedQty.get(part.part_number) ?? 0,
      part.cad_classification,
      drawingOrPlan,
      provenance.step_path ?? "",
      provenance.step_sha256 ?? "",
      {
        formula: `=IF(OR(A${row}="",D${row}="",E${row}="",K${row}="",L${row}=""),"BLOCKED",IF(OR(I${row}="PROVISIONAL — BLOCKS FINAL RELEASE",J${row}=""),"BLOCKED","DEFINED"))`,
      },
      {
        formula: `=IF(M${row}="DEFINED","FABRICATION DEFINITION EVIDENCED","DRAWING / PROCESS PLAN OR CONTROLLED CAD EVIDENCE REQUIRED")`,
      },
    ];
  });
  const table = writeTable(sheet, 5, headers, rows, {
    numberFormats: { 6: "0", 7: "0" },
    statusColumns: [12],
    widthCaps: { 2: 46, 3: 30, 4: 34, 5: 28, 8: 34, 9: 45, 10: 54, 11: 66, 13: 52 },
  });
  sheet.getRange("A4:H4").values = [[
    "Custom Part Identities",
    customParts.length,
    "Formula Defined",
    null,
    "Formula Blocked",
    null,
    "Fabrication Standing",
    null,
  ]];
  sheet.getRange("D4").formulas = [[`=COUNTIF(M${table.dataStart}:M${table.dataEnd},"DEFINED")`]];
  sheet.getRange("F4").formulas = [[`=COUNTIF(M${table.dataStart}:M${table.dataEnd},"BLOCKED")`]];
  sheet.getRange("H4").formulas = [[`=IF(F4>0,"BLOCKED","DEFINED")`]];
  sheet.getRange("A4:H4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  applyStatusConditionalFormatting(sheet.getRange("H4"));
}

// 19_CONSUMABLES
{
  const sheet = sheets.get("19_CONSUMABLES");
  const headers = [
    "Category ID",
    "Candidate Application / Scope",
    "Applicability Decision",
    "Manufacturer",
    "Part / Specification",
    "Required Quantity",
    "UOM",
    "Shelf Life / Storage",
    "Compatibility / Qualification",
    "Source URL",
    "Calculated Status",
    "Disposition",
  ];
  createTitle(
    sheet,
    "R2 CONSUMABLES & PROCESS MATERIALS",
    "No controlled consumable identities were present in the authoring or validation evidence. Candidate categories remain formula-BLOCKED pending applicability, specification, quantity, compatibility, and source definition.",
    headers.length,
  );
  const consumableCategories = [
    ["CONS-01", "Threadlocking / retaining compound for joints where a released detail drawing requires chemical retention"],
    ["CONS-02", "Assembly lubricant for pivots, guides, springs, seals, and other sliding interfaces where approved"],
    ["CONS-03", "Sealant / potting compound for penetrations and terminations where detail design requires it"],
    ["CONS-04", "Corrosion-isolation / anti-seize material for qualified serviceable or dissimilar-metal interfaces"],
    ["CONS-05", "Softgoods sewing, bonding, chafe-protection, and repair process materials"],
    ["CONS-06", "Cleaning and surface-preparation materials for controlled assembly, sealing, or bonding processes"],
  ];
  const rows = consumableCategories.map((item, index) => {
    const row = 6 + index;
    return [
      item[0],
      item[1],
      "TBD",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      {
        formula: `=IF(OR(C${row}="TBD",D${row}="",E${row}="",F${row}="",G${row}="",H${row}="",I${row}="",J${row}=""),"BLOCKED","DEFINED")`,
      },
      "Applicability and controlled procurement/process definition required; no release credit taken",
    ];
  });
  const table = writeTable(sheet, 5, headers, rows, {
    numberFormats: { 5: "0.000" },
    statusColumns: [10],
    widthCaps: { 1: 58, 3: 28, 4: 38, 7: 36, 8: 52, 9: 48, 11: 58 },
  });
  sheet.getRange("A4:H4").values = [[
    "Candidate Categories",
    consumableCategories.length,
    "Formula Defined",
    null,
    "Formula Blocked",
    null,
    "Register Standing",
    null,
  ]];
  sheet.getRange("D4").formulas = [[`=COUNTIF(K${table.dataStart}:K${table.dataEnd},"DEFINED")`]];
  sheet.getRange("F4").formulas = [[`=COUNTIF(K${table.dataStart}:K${table.dataEnd},"BLOCKED")`]];
  sheet.getRange("H4").formulas = [[`=IF(F4>0,"BLOCKED","DEFINED")`]];
  sheet.getRange("A4:H4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  applyStatusConditionalFormatting(sheet.getRange("H4"));
}

// 03_PURCHASED_ITEMS
{
  const sheet = sheets.get("03_PURCHASED_ITEMS");
  const headers = [
    "Part Number",
    "Description",
    "Manufacturer",
    "CAD Classification",
    "Qty Stowed",
    "Qty Deployed",
    "Unit Mass kg",
    "Purchase URL",
    "Source URL",
    "Procurement Status",
  ];
  createTitle(sheet, "R2 PURCHASED ITEM REGISTER", "Purchased identities, sourcing links, authentic-CAD standing, and release blockers.", headers.length);
  const purchased = parts.filter((part) => String(part.make_buy).toUpperCase() === "BUY");
  const rows = purchased.map((part, index) => {
    const row = 6 + index;
    return [
      part.part_number,
      part.description,
      part.manufacturer,
      part.cad_classification,
      stowedQty.get(part.part_number) ?? 0,
      deployedQty.get(part.part_number) ?? 0,
      numericOrBlank(part.mass_kg),
      part.purchase_url,
      part.source_url,
      {
        formula: `=IF(OR(D${row}="PROVISIONAL — BLOCKS FINAL RELEASE",H${row}=""),"BLOCKED",IF(D${row}="AUTHENTIC_VENDOR_CAD","SOURCE-CONTROLLED","REVIEW"))`,
      },
    ];
  });
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 4: "0", 5: "0", 6: "0.000" },
    statusColumns: [9],
    widthCaps: { 1: 40, 3: 34, 7: 50, 8: 50 },
  });
}

// 04_OCCURRENCE_BOM
let occurrenceTable;
{
  const sheet = sheets.get("04_OCCURRENCE_BOM");
  const headers = [
    "State",
    "Occurrence ID",
    "Part Number",
    "Parent Path",
    "Class",
    "Joint Type",
    "Permitted DOF",
    "Membership",
    "Identity Transform",
    "Volume mm³",
    "Occurrence Mass kg",
    "Transform Matrix 3x4",
    "Notes",
    "Reimport Seen",
    "Reimport Solid Count",
    "Reimport Status",
  ];
  createTitle(sheet, "R2 OCCURRENCE-SPECIFIC BOM", "State-specific placements, joints, hierarchy, mass, and exact 3x4 transforms.", headers.length);
  const reimportEvidenceAvailable = occurrenceInventoryStowedCsv.length > 0 && occurrenceInventoryDeployedCsv.length > 0;
  sheet.getRange("A4:F4").values = [["Authoring Rows", null, "Reimport Evidence", reimportEvidenceAvailable ? "AVAILABLE" : "MISSING", "Reimport Rows", null]];
  sheet.getRange("B4").formulas = [["=COUNTA(B6:B1000)"]];
  sheet.getRange("F4").formulas = [[reimportEvidenceAvailable ? `=${occurrenceInventoryStowedCsv.length + occurrenceInventoryDeployedCsv.length}` : '=""']];
  sheet.getRange("A4:F4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  const reimportByKey = new Map();
  for (const [state, inventory] of [["STOWED", occurrenceInventoryStowedCsv], ["DEPLOYED", occurrenceInventoryDeployedCsv]]) {
    for (const item of inventory) {
      const id = pick(item, ["occurrence_id", "occurrence", "component_id", "instance_name", "name"]);
      if (id) reimportByKey.set(`${state}|${id}`, item);
    }
  }
  const rows = [...(stowed.occurrences ?? []), ...(deployed.occurrences ?? [])].map((occ, index) => {
    const part = partMap.get(occ.part_number) ?? {};
    const reimport = reimportByKey.get(`${occ.state}|${occ.occurrence_id}`);
    const row = 6 + index;
    return [
      occ.state,
      occ.occurrence_id,
      occ.part_number,
      occ.parent_path,
      occ.classification,
      occ.joint_type,
      occ.permitted_dof,
      occ.state_membership,
      occ.identity_transform ? "YES" : "NO",
      numericOrBlank(occ.global_volume_mm3),
      numericOrBlank(part.mass_kg),
      matrixText(occ.transform_matrix_3x4),
      occ.notes,
      reimportEvidenceAvailable ? (reimport ? "YES" : "NO") : "",
      reimport ? numericOrBlank(pick(reimport, ["solid_count", "solids", "leaf_solid_count"])) : "",
      {
        formula: `=IF(N${row}="","BLOCKED",IF(N${row}="YES","VERIFIED","FAIL"))`,
      },
    ];
  });
  occurrenceTable = writeTable(sheet, 5, headers, rows, {
    numberFormats: { 9: "#,##0.000", 10: "0.000", 14: "0" },
    statusColumns: [15],
    widthCaps: { 1: 34, 2: 30, 3: 44, 5: 28, 11: 56, 12: 48 },
  });
}

// 05_ATTACHMENT_REGISTER
let attachmentTable;
{
  const sheet = sheets.get("05_ATTACHMENT_REGISTER");
  const headers = [
    "State",
    "Connection ID",
    "Occurrence ID",
    "Mate Occurrence ID",
    "Own Feature",
    "Mate Feature",
    "Connection Type",
    "DOF",
    "Retaining Hardware",
    "Axial Retention",
    "Lateral Retention",
    "Anti-Rotation",
    "Upstream Load Path",
    "Downstream Load Path",
    "Service Method",
    "Evidence",
    "Record Status",
  ];
  createTitle(sheet, "R2 ATTACHMENT & STRUCTURAL CONNECTION REGISTER", "Occurrence-to-occurrence feature mates; blanket work-package attachment statements are not accepted.", headers.length);
  const rows = [...(stowed.connections ?? []), ...(deployed.connections ?? [])].map((connection, index) => {
    const row = 6 + index;
    return [
      connection.state,
      connection.connection_id,
      connection.occurrence_id,
      connection.mate_occurrence_id,
      connection.own_feature_id,
      connection.mate_feature_id,
      connection.connection_type,
      connection.permitted_dof,
      connection.retaining_hardware,
      connection.axial_retention,
      connection.lateral_retention,
      connection.anti_rotation,
      connection.upstream_load_path,
      connection.downstream_load_path,
      connection.service_method,
      connection.evidence,
      {
        formula: `=IF(OR(C${row}="",D${row}="",E${row}="",F${row}="",G${row}="",I${row}=""),"INCOMPLETE","COMPLETE")`,
      },
    ];
  });
  attachmentTable = writeTable(sheet, 5, headers, rows, {
    statusColumns: [16],
    widthCaps: { 1: 30, 2: 30, 3: 30, 4: 34, 5: 34, 8: 34, 9: 38, 10: 38, 11: 36, 12: 36, 13: 36, 14: 42, 15: 38 },
  });
}

// 06_HARDWARE_FITTINGS
{
  const sheet = sheets.get("06_HARDWARE_FITTINGS");
  const headers = [
    "Part Number",
    "Description",
    "Hardware / Fitting Type",
    "Make / Buy",
    "CAD Classification",
    "Qty Stowed",
    "Qty Deployed",
    "Source / Purchase URL",
    "Definition Status",
  ];
  createTitle(sheet, "R2 HARDWARE, FITTINGS & RETAINERS", "Pins, rings, bushings, washers, fittings, valves, clamps, springs, detents, and terminal hardware.", headers.length);
  const hardwarePattern = /(pin|ring|bush|washer|union|fitting|valve|spring|detent|plunger|latch|clip|retainer|carrier|band|sleeve|thimble|manifold|head)/i;
  const hardware = parts.filter((part) => hardwarePattern.test(`${part.part_number} ${part.description}`));
  const rows = hardware.map((part, index) => {
    const row = 6 + index;
    const text = `${part.part_number} ${part.description}`.toLowerCase();
    let type = "HARDWARE";
    if (/union|fitting|valve|manifold|head/.test(text)) type = "FLUID FITTING";
    else if (/spring|plunger|detent/.test(text)) type = "SPRING / DETENT";
    else if (/pin|ring|clip|retainer/.test(text)) type = "PIN / RETAINER";
    else if (/bush|washer|sleeve/.test(text)) type = "BEARING / SPACER";
    return [
      part.part_number,
      part.description,
      type,
      part.make_buy,
      part.cad_classification,
      stowedQty.get(part.part_number) ?? 0,
      deployedQty.get(part.part_number) ?? 0,
      firstDefined(part.purchase_url, part.source_url, ""),
      {
        formula: `=IF(OR(E${row}="PROVISIONAL — BLOCKS FINAL RELEASE",AND(D${row}="BUY",H${row}="")),"BLOCKED","DEFINED")`,
      },
    ];
  });
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 5: "0", 6: "0" },
    statusColumns: [8],
    widthCaps: { 1: 42, 4: 34, 7: 54 },
  });
}

// 07_CLEARANCE_REGISTER
let clearanceSummaryCell = "'07_CLEARANCE_REGISTER'!D4";
{
  const sheet = sheets.get("07_CLEARANCE_REGISTER");
  const headers = [
    "State",
    "Pair ID",
    "Occurrence A",
    "Occurrence B",
    "Measured Minimum Clearance mm",
    "Required Minimum mm",
    "Motion Angle deg",
    "Evidence / Method",
    "Status",
  ];
  createTitle(sheet, "R2 MEASURED CLEARANCE REGISTER", "Pair-specific minimum distances; blank evidence blocks the associated gate.", headers.length);
  const available = clearanceCsv.length > 0;
  sheet.getRange("A4:F4").values = [["Evidence Availability", available ? "AVAILABLE" : "MISSING", "Global Minimum mm", null, "Failed Pairs", null]];
  sheet.getRange("A4:F4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  const normalized = clearanceCsv.map((row, index) => ({
    state: pick(row, ["state", "assembly_state"]),
    pair: pick(row, ["pair_id", "pair", "pair_index", "check_id"], `CLR-${String(index + 1).padStart(5, "0")}`),
    a: pick(row, ["occurrence_a", "occ_a", "component_a", "a"]),
    b: pick(row, ["occurrence_b", "occ_b", "component_b", "b"]),
    measured: asNumber(pick(row, ["minimum_clearance_mm", "min_clearance_mm", "clearance_mm", "exact_clearance_mm", "distance_mm", "minimum_distance_mm"])),
    required: asNumber(pick(row, ["required_clearance_mm", "minimum_required_mm", "threshold_mm", "required_mm"])),
    angle: asNumber(pick(row, ["angle_deg", "motion_angle_deg", "sample_angle_deg"])),
    evidence: [
      pick(row, ["exact_clearance_status", "exact_distance_status", "status"]),
      pick(row, ["disposition", "result"]),
      pick(row, ["common_volume_mm3"]),
      pick(row, ["error", "notes"]),
    ].filter((value) => value !== "").join(" | "),
  }));
  const rows = (normalized.length ? normalized : [{ state: "", pair: "NO CLEARANCE EVIDENCE", a: "", b: "", measured: null, required: null, angle: null, evidence: "Run validator to populate minimum_clearance_register.csv" }]).map((item, index) => {
    const row = 7 + index;
    return [
      item.state,
      item.pair,
      item.a,
      item.b,
      item.measured ?? "",
      item.required ?? "",
      item.angle ?? "",
      item.evidence,
      {
        formula: `=IF(E${row}="","BLOCKED",IF(ISNUMBER(SEARCH("UNAUTHORIZED_POSITIVE_VOLUME",H${row})),"FAIL",IF(ISNUMBER(SEARCH("BLOCKED",H${row})),"BLOCKED",IF(E${row}>=IF(F${row}="",0,F${row}),"PASS","FAIL"))))`,
      },
    ];
  });
  const table = writeTable(sheet, 6, headers, rows, {
    numberFormats: { 4: "0.0000", 5: "0.0000", 6: "0.0" },
    statusColumns: [8],
    widthCaps: { 1: 30, 2: 34, 3: 34, 7: 48 },
  });
  sheet.getRange("D4").formulas = [[available ? `=MIN(E${table.dataStart}:E${table.dataEnd})` : '=""']];
  sheet.getRange("F4").formulas = [[available ? `=COUNTIF(I${table.dataStart}:I${table.dataEnd},"FAIL")` : '=""']];
  sheet.getRange("D4:F4").format.numberFormat = "0.0000";
}

// 08_INTERFERENCE_REGISTER
let interferenceSummaryCell = "'08_INTERFERENCE_REGISTER'!D4";
{
  const sheet = sheets.get("08_INTERFERENCE_REGISTER");
  const headers = [
    "State",
    "Pair ID",
    "Occurrence A",
    "Occurrence B",
    "Positive Volume mm³",
    "Classification",
    "Exception ID",
    "Documentation",
    "Disposition",
    "Status",
  ];
  createTitle(sheet, "R2 INTERFERENCE & EXCEPTION REGISTER", "Every positive-volume intersection requires pair-specific classification and documentation.", headers.length);
  const exactPairRows = [
    ...stowedPairAudit.map((row) => ({ ...row, __state: "STOWED" })),
    ...deployedPairAudit.map((row) => ({ ...row, __state: "DEPLOYED" })),
  ];
  const authoringPairRows = [
    ...((authoringPairAuditStowed?.overlaps ?? []).map((row) => ({
      ...row,
      __state: "STOWED",
      classification: "UNDOCUMENTED_POSITIVE_VOLUME — AUTHORING OCCT AUDIT",
      documentation: "Intermediate authoring-kernel audit; exact reimport pair register not yet available.",
    }))),
    ...((authoringPairAuditDeployed?.overlaps ?? []).map((row) => ({
      ...row,
      __state: "DEPLOYED",
      classification: "UNDOCUMENTED_POSITIVE_VOLUME — AUTHORING OCCT AUDIT",
      documentation: "Intermediate authoring-kernel audit; exact reimport pair register not yet available.",
    }))),
  ];
  const pairRows = exactPairRows.length ? exactPairRows : authoringPairRows;
  const normalized = pairRows
    .map((row, index) => {
      const volume = asNumber(pick(row, ["intersection_volume_mm3", "positive_volume_mm3", "common_volume_mm3", "overlap_volume_mm3", "volume_mm3"]));
      const classification = pick(row, ["classification", "contact_category", "result", "pair_class"]);
      return {
        state: firstDefined(pick(row, ["state", "assembly_state"]), row.__state),
        pair: pick(row, ["pair_id", "pair", "pair_index", "check_id"], `PAIR-${String(index + 1).padStart(6, "0")}`),
        a: pick(row, ["occurrence_a", "occ_a", "component_a", "a"]),
        b: pick(row, ["occurrence_b", "occ_b", "component_b", "b"]),
        volume,
        classification,
        exceptionId: pick(row, ["exception_id", "fit_exception_id", "documented_exception"]),
        documentation: pick(row, ["documentation", "exception_documentation", "evidence", "notes"]),
        disposition: pick(row, ["disposition", "action", "resolution"]),
      };
    })
    .filter((row) => {
      if ((row.volume ?? 0) > 0.000001 || row.exceptionId) return true;
      const classification = String(row.classification ?? "");
      return (
        /exception|interference|overlap|penetration/i.test(classification) &&
        !/no[_ -]?interference|clear|valid|none/i.test(classification)
      );
    });
  const available =
    (stowedPairAudit.length > 0 && deployedPairAudit.length > 0) ||
    Boolean(authoringPairAuditStowed && authoringPairAuditDeployed);
  sheet.getRange("A4:F4").values = [["Evidence Availability", available ? "AVAILABLE" : "MISSING", "Undocumented Positive-Volume Pairs", null, "Registered Exceptions", null]];
  sheet.getRange("A4:F4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  const rows = (normalized.length ? normalized : [{ state: "", pair: available ? "NO POSITIVE-VOLUME PAIRS" : "NO PAIR AUDIT EVIDENCE", a: "", b: "", volume: available ? 0 : null, classification: available ? "CLEAR" : "", exceptionId: "", documentation: available ? "Exhaustive endpoint audit contained no positive-volume intersections." : "Run exhaustive endpoint pair audits.", disposition: "" }]).map((item, index) => {
    const row = 7 + index;
    return [
      item.state,
      item.pair,
      item.a,
      item.b,
      item.volume ?? "",
      item.classification,
      item.exceptionId,
      item.documentation,
      item.disposition,
      { formula: `=IF(E${row}="","BLOCKED",IF(E${row}<=0.000001,"CLEAR",IF(AND(G${row}<>"",H${row}<>""),"DOCUMENTED","FAIL")))` },
    ];
  });
  const table = writeTable(sheet, 6, headers, rows, {
    numberFormats: { 4: "0.000000" },
    statusColumns: [9],
    widthCaps: { 1: 32, 2: 34, 3: 34, 5: 24, 6: 24, 7: 48, 8: 36 },
  });
  sheet.getRange("D4").formulas = [[available ? `=COUNTIF(J${table.dataStart}:J${table.dataEnd},"FAIL")` : '=""']];
  sheet.getRange("F4").formulas = [[available ? `=COUNTIF(J${table.dataStart}:J${table.dataEnd},"DOCUMENTED")` : '=""']];
  sheet.getRange("D4:F4").format.numberFormat = "0";
}

// 09_MOTION_SWEEP
let motionSummaryCells = { sampleCount: "'09_MOTION_SWEEP'!D4", failures: "'09_MOTION_SWEEP'!H4" };
{
  const sheet = sheets.get("09_MOTION_SWEEP");
  const headers = [
    "Sample ID",
    "Arm Angle deg",
    "Crosshead Z mm",
    "Crosshead Travel mm",
    "Minimum Clearance mm",
    "Undocumented Intersections",
    "Worst Pair",
    "Evidence",
    "Status",
  ];
  createTitle(sheet, "R2 CONTINUOUS-MOTION SWEEP", "Intermediate configurations supplement endpoint pair audits; any undocumented collision fails the sweep.", headers.length);
  const available = motionSamplesCsv.length > 0;
  sheet.getRange("A4:H4").values = [["Evidence Availability", available ? "AVAILABLE" : "MISSING", "Samples", null, "Minimum Clearance mm", null, "Failed Samples", null]];
  sheet.getRange("A4:H4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  const rows = (motionSamplesCsv.length ? motionSamplesCsv : [{ sample_id: "NO MOTION EVIDENCE", evidence: "Run validator to populate motion_samples.csv.gz" }]).map((item, index) => {
    const row = 7 + index;
    const sampleId = pick(item, ["sample_id", "sample", "index", "step"], `MOTION-${index + 1}`);
    const angle = numericOrBlank(pick(item, ["arm_angle_deg", "angle_deg", "theta_deg"]));
    const crosshead = numericOrBlank(pick(item, ["crosshead_z_mm", "crosshead_position_mm", "z_mm"]));
    const travel = numericOrBlank(pick(item, ["crosshead_travel_mm", "travel_mm"]));
    const minClearance = numericOrBlank(pick(item, ["minimum_clearance_mm", "min_clearance_mm", "clearance_mm"]));
    const intersections = numericOrBlank(pick(item, ["undocumented_intersections", "invalid_interference_count", "collision_count", "positive_volume_count"]));
    const worstPair = pick(item, ["worst_pair", "minimum_pair", "pair_id"]);
    const evidence = pick(item, ["evidence", "source", "notes"], motionSamplesCsv.length ? "motion_samples.csv.gz" : item.evidence);
    return [
      sampleId,
      angle,
      crosshead,
      travel,
      minClearance,
      intersections,
      worstPair,
      evidence,
      { formula: `=IF(OR(B${row}="",F${row}=""),"BLOCKED",IF(AND(F${row}=0,OR(E${row}="",E${row}>=0)),"PASS","FAIL"))` },
    ];
  });
  const table = writeTable(sheet, 6, headers, rows, {
    numberFormats: { 1: "0.0", 2: "0.000000", 3: "0.000000", 4: "0.0000", 5: "0" },
    statusColumns: [8],
    widthCaps: { 0: 24, 6: 42, 7: 48 },
  });
  sheet.getRange("D4").formulas = [[available ? `=COUNTA(A${table.dataStart}:A${table.dataEnd})` : '=""']];
  sheet.getRange("F4").formulas = [[available ? `=MIN(E${table.dataStart}:E${table.dataEnd})` : '=""']];
  sheet.getRange("H4").formulas = [[available ? `=COUNTIF(I${table.dataStart}:I${table.dataEnd},"FAIL")` : '=""']];
  sheet.getRange("D4").format.numberFormat = "0";
  sheet.getRange("F4").format.numberFormat = "0.0000";
  sheet.getRange("H4").format.numberFormat = "0";
}

// 10_SOURCE_CAD
{
  const sheet = sheets.get("10_SOURCE_CAD");
  const headers = [
    "Part Number",
    "Description",
    "CAD Classification",
    "Source URL",
    "Purchase URL",
    "Source File",
    "Source SHA-256",
    "Reimport Method",
    "Maximum Deviation mm",
    "Source Status",
  ];
  createTitle(sheet, "R2 SOURCE CAD & REIMPORT REGISTER", "Authentic vendor CAD, drawing-derived definitions, hashes, URLs, and source-vs-reimport evidence.", headers.length);
  const sourceByPart = new Map();
  for (const row of sourceReimportCsv) {
    const pn = pick(row, ["part_number", "pn", "item_id", "component"]);
    if (pn) sourceByPart.set(pn, row);
  }
  const provenanceByPart = new Map();
  for (const row of componentProvenanceCsv) {
    const pn = pick(row, ["part_number", "pn"]);
    if (pn) provenanceByPart.set(pn, row);
  }
  const rows = parts.map((part, index) => {
    const row = 6 + index;
    const source = sourceByPart.get(part.part_number) ?? {};
    const provenance = provenanceByPart.get(part.part_number) ?? {};
    return [
      part.part_number,
      part.description,
      part.cad_classification,
      part.source_url,
      part.purchase_url,
      firstDefined(
        pick(source, ["source_file", "cad_file", "file_name"]),
        pick(provenance, ["source_path", "step_path"]),
      ),
      firstDefined(
        pick(source, ["source_sha256", "sha256", "hash"]),
        pick(provenance, ["source_sha256", "step_sha256"]),
      ),
      pick(source, ["reimport_method", "target_cad", "comparison_method"]),
      numericOrBlank(pick(source, ["maximum_deviation_mm", "max_deviation_mm", "deviation_mm"])),
      {
        formula: `=IF(C${row}="PROVISIONAL — BLOCKS FINAL RELEASE","BLOCKED",IF(C${row}="AUTHENTIC_VENDOR_CAD",IF(OR(D${row}="",F${row}=""),"INCOMPLETE","SOURCE-CONTROLLED"),"DRAWING-DERIVED"))`,
      },
    ];
  });
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 8: "0.000000" },
    statusColumns: [9],
    widthCaps: { 1: 42, 2: 34, 3: 50, 4: 50, 5: 40, 6: 50, 7: 32 },
  });
}

// 11_STATE_MATRIX
{
  const sheet = sheets.get("11_STATE_MATRIX");
  const headers = [
    "Occurrence ID",
    "Part Number",
    "Membership",
    "Class",
    "Stowed Present",
    "Deployed Present",
    "Stowed Identity",
    "Deployed Identity",
    "Translation Delta mm",
    "Matrix Max Abs Delta",
    "State Rule Status",
  ];
  createTitle(sheet, "R2 STOWED / DEPLOYED STATE MATRIX", "Occurrence-level state membership and transform deltas; identity placements require explicit justification.", headers.length);
  const stowedById = new Map((stowed.occurrences ?? []).map((occ) => [occ.occurrence_id, occ]));
  const deployedById = new Map((deployed.occurrences ?? []).map((occ) => [occ.occurrence_id, occ]));
  const ids = [...new Set([...stowedById.keys(), ...deployedById.keys()])].sort();
  const rows = ids.map((id, index) => {
    const a = stowedById.get(id);
    const b = deployedById.get(id);
    const ma = a?.transform_matrix_3x4;
    const mb = b?.transform_matrix_3x4;
    let translationDelta = null;
    let maxDelta = null;
    if (Array.isArray(ma) && Array.isArray(mb)) {
      const diffs = [];
      for (let r = 0; r < 3; r += 1) for (let c = 0; c < 4; c += 1) diffs.push(Math.abs(Number(ma[r][c]) - Number(mb[r][c])));
      translationDelta = Math.sqrt(
        (Number(ma[0][3]) - Number(mb[0][3])) ** 2 +
        (Number(ma[1][3]) - Number(mb[1][3])) ** 2 +
        (Number(ma[2][3]) - Number(mb[2][3])) ** 2,
      );
      maxDelta = Math.max(...diffs);
    }
    const row = 6 + index;
    return [
      id,
      firstDefined(a?.part_number, b?.part_number),
      firstDefined(a?.state_membership, b?.state_membership),
      firstDefined(a?.classification, b?.classification),
      a ? "YES" : "NO",
      b ? "YES" : "NO",
      a ? (a.identity_transform ? "YES" : "NO") : "",
      b ? (b.identity_transform ? "YES" : "NO") : "",
      translationDelta ?? "",
      maxDelta ?? "",
      {
        formula: `=IF(AND(C${row}="BOTH",OR(E${row}="NO",F${row}="NO")),"FAIL",IF(AND(E${row}="NO",F${row}="NO"),"FAIL","COMPLETE"))`,
      },
    ];
  });
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 8: "0.000000", 9: "0.000000" },
    statusColumns: [10],
    widthCaps: { 0: 34, 1: 34, 2: 18, 3: 24 },
  });
}

// 13_MASS_PROPERTIES
let massSummaryCell = "'13_MASS_PROPERTIES'!H4";
{
  const sheet = sheets.get("13_MASS_PROPERTIES");
  const headers = [
    "Part Number",
    "Description",
    "Unit Mass kg",
    "Qty Stowed",
    "Qty Deployed",
    "Stowed Extended kg",
    "Deployed Extended kg",
    "Mass Status",
  ];
  createTitle(sheet, "R2 MASS PROPERTIES", "Occurrence-weighted mass rollup; any unresolved unit mass blocks the total-mass gate.", headers.length);
  const rows = parts.map((part, index) => {
    const row = 8 + index;
    return [
      part.part_number,
      part.description,
      numericOrBlank(part.mass_kg),
      stowedQty.get(part.part_number) ?? 0,
      deployedQty.get(part.part_number) ?? 0,
      { formula: `=IF(C${row}="","",C${row}*D${row})` },
      { formula: `=IF(C${row}="","",C${row}*E${row})` },
      { formula: `=IF(AND(C${row}="",OR(D${row}>0,E${row}>0)),"BLOCKED","DEFINED")` },
    ];
  });
  const dataEnd = 8 + Math.max(1, rows.length) - 1;
  const validatorMass = providedMetric(providedGates, ["G11", "total_mass", "complete_mass", "mass_kg"]);
  sheet.getRange("A4:H5").values = [
    ["State", "Known Mass kg", "Unresolved Parts", "Assessed Mass kg", "Maximum kg", "Margin kg", "Gate Evidence kg", "Validator Mass kg"],
    ["STOWED", null, null, null, numericOrBlank(manifest.hard_requirements?.mass_max_kg), null, null, numericOrBlank(validatorMass)],
  ];
  sheet.getRange("A6:H6").values = [["DEPLOYED", null, null, null, numericOrBlank(manifest.hard_requirements?.mass_max_kg), null, null, ""]];
  sheet.getRange("A4:H4").format = { fill: COLORS.teal, font: { bold: true, color: COLORS.white } };
  sheet.getRange("A5:H6").format = { fill: COLORS.cyan, font: { color: COLORS.ink } };
  sheet.getRange("B5").formulas = [[`=SUM(F8:F${dataEnd})`]];
  sheet.getRange("B6").formulas = [[`=SUM(G8:G${dataEnd})`]];
  sheet.getRange("C5").formulas = [[`=COUNTIF(H8:H${dataEnd},"BLOCKED")`]];
  sheet.getRange("C6").formulas = [[`=COUNTIF(H8:H${dataEnd},"BLOCKED")`]];
  sheet.getRange("D5").formulas = [[`=IF(C5=0,B5,"")`]];
  sheet.getRange("D6").formulas = [[`=IF(C6=0,B6,"")`]];
  sheet.getRange("F5").formulas = [[`=IF(D5="","",E5-D5)`]];
  sheet.getRange("F6").formulas = [[`=IF(D6="","",E6-D6)`]];
  sheet.getRange("G5").formulas = [[`=IF(H5<>"",H5,IF(OR(D5="",D6=""),"",MAX(D5,D6)))`]];
  sheet.getRange("B5:H6").format.numberFormat = "0.000";
  writeTable(sheet, 7, headers, rows, {
    numberFormats: { 2: "0.000", 3: "0", 4: "0", 5: "0.000", 6: "0.000" },
    statusColumns: [7],
    widthCaps: { 0: 40, 1: 44 },
  });
  massSummaryCell = "'13_MASS_PROPERTIES'!G5";
}

// 15_EVIDENCE_INDEX
{
  const sheet = sheets.get("15_EVIDENCE_INDEX");
  const headers = ["Evidence File", "Category", "Required", "Present", "Bytes", "SHA-256", "Purpose / Source URL", "Status"];
  createTitle(sheet, "R2 EVIDENCE INDEX", "Release evidence inventory with file presence, size, hashes, and plain-text source URLs.", headers.length);
  const expected = [
    ["authoring_inventory_stowed.json", "AUTHORING", "YES", "Occurrence, part, connection, and route inventory"],
    ["authoring_inventory_deployed.json", "AUTHORING", "YES", "Occurrence, part, connection, and route inventory"],
    ["authoring_manifest.json", "AUTHORING", "YES", "Schema, requirements, and product file hashes"],
    ["authoring_pair_audit_stowed.json", "AUTHORING", "YES", "Intermediate authoring-kernel positive-volume audit"],
    ["authoring_pair_audit_deployed.json", "AUTHORING", "YES", "Intermediate authoring-kernel positive-volume audit"],
    ["validation/gate_results.json", "VALIDATION", "YES", "Calculated 23-gate validation result set"],
    ["validation/validation_manifest.json", "VALIDATION", "YES", "Frozen-hash validation evidence manifest"],
    ["validation/validation_summary.json", "VALIDATION", "YES", "Validation summary and counts"],
    ["validation/step_text_inspection.json", "VALIDATION", "YES", "AP242 schema, names, and tessellation inspection"],
    ["validation/xcaf_occurrences_stowed.csv", "VALIDATION", "YES", "Reimport occurrence inventory"],
    ["validation/xcaf_occurrences_deployed.csv", "VALIDATION", "YES", "Reimport occurrence inventory"],
    ["validation/leaf_solids_stowed.csv", "VALIDATION", "YES", "Solid-level B-rep inventory"],
    ["validation/leaf_solids_deployed.csv", "VALIDATION", "YES", "Solid-level B-rep inventory"],
    ["validation/endpoint_pair_audit_stowed.csv.gz", "VALIDATION", "YES", "Exhaustive endpoint pair audit"],
    ["validation/endpoint_pair_audit_deployed.csv.gz", "VALIDATION", "YES", "Exhaustive endpoint pair audit"],
    ["validation/endpoint_interference_register.csv", "VALIDATION", "YES", "Positive-volume interference register"],
    ["validation/endpoint_pair_summary.json", "VALIDATION", "YES", "Endpoint pair-audit summary"],
    ["validation/minimum_clearance_register.csv", "VALIDATION", "YES", "Critical measured clearance subset"],
    ["validation/key_dimensions.json", "VALIDATION", "YES", "Envelope, arm, travel, length, and mass measurements"],
    ["validation/motion_kinematics_1deg.csv", "VALIDATION", "YES", "One-degree motion kinematics"],
    ["validation/motion_arm_clearance_audit.csv.gz", "VALIDATION", "YES", "Principal-arm one-degree collision audit"],
    ["validation/motion_audit_summary.json", "VALIDATION", "YES", "Motion-scope summary and blockers"],
    ["validation/attachment_connectivity_stowed.csv", "VALIDATION", "YES", "Stowed attachment graph"],
    ["validation/attachment_connectivity_deployed.csv", "VALIDATION", "YES", "Deployed attachment graph"],
    ["validation/connectivity_summary.json", "VALIDATION", "YES", "Attachment cohesion and recovery load path"],
    ["validation/state_parity.csv", "VALIDATION", "YES", "State occurrence identity parity"],
    ["CREO_VALIDATION.json", "METADATA", "YES", "Creo clean-session gate status; explicitly blocked until target-CAD evidence exists"],
    ["PACKAGE_STATUS.txt", "METADATA", "YES", "Required package status label"],
    ["DEPENDENCIES.json", "METADATA", "YES", "Exact build and validation dependency capture"],
    ["BUILD_INSTRUCTIONS.md", "METADATA", "YES", "Deterministic source, validation, component-export, and workbook build procedure"],
    ["provenance.csv", "COMPONENT CAD", "YES", "Controlled-part AP242/BREP inventory, hashes, and source classifications"],
    ["provenance.json", "COMPONENT CAD", "YES", "Machine-readable controlled-part and source-CAD provenance"],
  ];
  for (const fileName of Object.keys(manifest.files ?? {})) expected.push([fileName, "PRODUCT CAD", "YES", "AP242 product or controlled external context"]);
  const rows = [];
  for (let i = 0; i < expected.length; i += 1) {
    const [fileName, category, required, purpose] = expected[i];
    const filePath =
      category === "PRODUCT CAD"
        ? path.join(releaseDir, fileName)
        : category === "COMPONENT CAD"
          ? path.join(componentDir, fileName)
          : category === "METADATA"
            ? path.join(metadataDir, fileName)
          : path.join(analysisDir, fileName);
    const meta = await fileMeta(filePath);
    const sha = manifest.files?.[fileName]?.sha256 ?? "";
    const row = 6 + i;
    rows.push([
      fileName,
      category,
      required,
      meta.present ? "YES" : "NO",
      meta.size,
      sha,
      purpose,
      { formula: `=IF(D${row}="YES","AVAILABLE",IF(C${row}="YES","MISSING","OPTIONAL"))` },
    ]);
  }
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 4: "#,##0" },
    statusColumns: [7],
    widthCaps: { 0: 58, 5: 54, 6: 56 },
  });
}

// 16_CREO_VALIDATION
let creoOverallCell = "'16_CREO_VALIDATION'!B4";
{
  const sheet = sheets.get("16_CREO_VALIDATION");
  const headers = ["Check ID", "Creo Clean-Session Check", "Required", "Evidence Value", "Evidence Reference", "Computed Status"];
  createTitle(sheet, "R2 CREO TARGET-CAD VALIDATION", "Final release remains blocked until a real Creo clean-session AP242 reimport, regeneration, and verification passes.", headers.length);
  const checks = [
    ["CREO-01", "Creo validation metadata present", "YES", creoData ? "YES" : "NO", "work/r2_metadata/CREO_VALIDATION.json", "YES"],
    ["CREO-02", "Clean Creo session declared", "YES", asYesNo(deepPick(creoData, ["clean_session", "clean_session_confirmed", "fresh_session", "clean_creo_session_available"])), "Creo session metadata", "YES"],
    ["CREO-03", "Stowed AP242 import succeeded", "YES", asYesNo(deepPick(creoData, ["stowed_import_pass", "stowed_import_succeeded", "stowed_import", "reimport_performed"])), "Creo import log", "YES"],
    ["CREO-04", "Deployed AP242 import succeeded", "YES", asYesNo(deepPick(creoData, ["deployed_import_pass", "deployed_import_succeeded", "deployed_import", "reimport_performed"])), "Creo import log", "YES"],
    ["CREO-05", "Regeneration completed without failures", "YES", asYesNo(deepPick(creoData, ["regeneration_pass", "regen_pass", "regenerated_cleanly", "regeneration_performed", "clean_creo_passed"])), "Creo regeneration report", "YES"],
    ["CREO-06", "Missing references", "0", numericOrBlank(deepPick(creoData, ["missing_reference_count", "missing_references", "unresolved_reference_count"])), "Creo model tree report", "ZERO"],
    ["CREO-07", "Failed features", "0", numericOrBlank(deepPick(creoData, ["failed_feature_count", "failed_features", "feature_failures"])), "Creo regeneration report", "ZERO"],
    ["CREO-08", "Unresolved components", "0", numericOrBlank(deepPick(creoData, ["unresolved_component_count", "unresolved_components"])), "Creo model tree report", "ZERO"],
    ["CREO-09", "Creo interference verification executed", "YES", asYesNo(deepPick(creoData, ["interference_check_executed", "global_interference_run", "interference_verified"])), "Creo clearance/interference report", "YES"],
  ];
  sheet.getRange("A4:B4").values = [["Computed Creo Gate", null]];
  sheet.getRange("A4:B4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  const rows = checks.map((check, index) => {
    const row = 7 + index;
    let formula;
    if (check[5] === "ZERO") formula = `=IF(D${row}="","BLOCKED",IF(D${row}=0,"PASS","FAIL"))`;
    else if (check[0] === "CREO-01") formula = `=IF(D${row}="YES","PASS","BLOCKED")`;
    else formula = `=IF(D${row}="","BLOCKED",IF(D${row}="YES","PASS",IF(D${row}="NO","BLOCKED","FAIL")))`;
    return [check[0], check[1], check[2], check[3], check[4], { formula }];
  });
  const table = writeTable(sheet, 6, headers, rows, {
    numberFormats: { 3: "0" },
    statusColumns: [5],
    widthCaps: { 1: 48, 4: 44 },
  });
  sheet.getRange("B4").formulas = [[`=IF(COUNTIF(F${table.dataStart}:F${table.dataEnd},"FAIL")>0,"FAIL",IF(COUNTIF(F${table.dataStart}:F${table.dataEnd},"BLOCKED")>0,"PENDING","PASS"))`]];
  applyStatusConditionalFormatting(sheet.getRange("B4"));
}

// 17_ROUTING
let routingIncompleteCell = "'17_ROUTING'!D4";
{
  const sheet = sheets.get("17_ROUTING");
  const headers = [
    "State",
    "Route Occurrence",
    "Origin",
    "Destination",
    "Termination Fittings",
    "Controlled Penetrations",
    "Supports",
    "Minimum Bend Radius mm",
    "Service Slack mm",
    "Pressure Rating",
    "Authoring Note",
    "Validation Result",
    "Validation Evidence",
    "Route Status",
  ];
  createTitle(sheet, "R2 ROUTING, PENETRATIONS & TERMINATIONS", "Every route is occurrence-specific and includes termini, wall penetrations, support, bend radius, and service definition.", headers.length);
  const validationByKey = new Map();
  for (const row of routingTerminationCsv) {
    const key = `${String(pick(row, ["state"])).toUpperCase()}|${pick(row, ["route_occurrence_id", "route_id", "occurrence_id"])}`;
    validationByKey.set(key, row);
  }
  const authoredRoutes = [...(stowed.routes ?? []), ...(deployed.routes ?? [])];
  const rows = (authoredRoutes.length ? authoredRoutes : [{ state: "", route_occurrence_id: "NO ROUTE AUTHORING EVIDENCE" }]).map((route, index) => {
    const row = 7 + index;
    const validation = validationByKey.get(`${route.state}|${route.route_occurrence_id}`) ?? {};
    return [
      route.state,
      route.route_occurrence_id,
      route.origin_occurrence,
      route.destination_occurrence,
      route.termination_fittings,
      route.controlled_penetrations,
      route.supports,
      numericOrBlank(route.minimum_bend_radius_mm),
      numericOrBlank(route.service_slack_mm),
      route.pressure_rating,
      route.status,
      pick(validation, ["validation_status", "status", "termination_status", "result"]),
      pick(validation, ["evidence", "notes", "validation_reference", "source_file"]),
      {
        formula: `=IF(OR(C${row}="",D${row}="",E${row}="",F${row}="",G${row}=""),"INCOMPLETE",IF(OR(L${row}="",M${row}=""),"BLOCKED",IF(OR(L${row}="FAIL",L${row}="INVALID",L${row}="INCOMPLETE"),"FAIL","COMPLETE")))`,
      },
    ];
  });
  const available = routingTerminationCsv.length > 0;
  sheet.getRange("A4:D4").values = [["Validation Evidence", available ? "AVAILABLE" : "MISSING", "Incomplete / Blocked Routes", null]];
  sheet.getRange("A4:D4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  const table = writeTable(sheet, 6, headers, rows, {
    numberFormats: { 7: "0.0", 8: "0.0" },
    statusColumns: [13],
    widthCaps: { 1: 32, 2: 32, 3: 32, 4: 48, 5: 46, 6: 46, 9: 30, 10: 42, 11: 24, 12: 42 },
  });
  sheet.getRange("D4").formulas = [[available ? `=COUNTIF(N${table.dataStart}:N${table.dataEnd},"INCOMPLETE")+COUNTIF(N${table.dataStart}:N${table.dataEnd},"BLOCKED")+COUNTIF(N${table.dataStart}:N${table.dataEnd},"FAIL")` : '=""']];
}

// Derived validation metrics.
const endpointLength = (() => {
  const extents = [stowed, deployed].map((inventory) => {
    const relevant = (inventory.occurrences ?? []).filter(
      (occ) => !/FLEXIBLE|SOFTGOOD|EXTERNAL/i.test(String(occ.classification)),
    );
    if (!relevant.length) return null;
    const zmin = Math.min(...relevant.map((occ) => asNumber(occ.global_bbox_mm?.zmin)).filter((v) => v !== null));
    const zmax = Math.max(...relevant.map((occ) => asNumber(occ.global_bbox_mm?.zmax)).filter((v) => v !== null));
    return Number.isFinite(zmin) && Number.isFinite(zmax) ? zmax - zmin : null;
  });
  const valid = extents.filter((value) => value !== null);
  return valid.length ? Math.max(...valid) : null;
})();
const armFaceMax = Math.max(
  0,
  ...parts.filter((part) => /ARM-BLADE/i.test(part.part_number)).map((part) => asNumber(part.face_count) ?? 0),
);
const invalidIdentityCount = (stowed.occurrences ?? []).filter(
  (occ) =>
    occ.identity_transform &&
    !/flexible|external/i.test(String(occ.classification)) &&
    !/justified|flexible|datum origin/i.test(String(occ.notes)),
).length;
const floatingNodes = connectivityNodesCsv.length
  ? connectivityNodesCsv.filter((row) => /floating|unattached|orphan|fail/i.test(String(pick(row, ["status", "connectivity_status", "result"])))).length
  : null;
const jointFailures = jointGeometryCsv.length
  ? jointGeometryCsv.filter((row) => /fail|invalid|missing|unretained/i.test(String(pick(row, ["status", "result", "check_status"])))).length
  : null;
const loadPathPass = loadPathData
  ? asYesNo(firstDefined(deepPick(loadPathData, ["pass", "load_path_pass", "continuous_structural_path"]), deepPick(loadPathData, ["status"])))
  : "";

function metric(aliases, fallback = null) {
  return firstDefined(providedMetric(providedGates, aliases), fallback);
}

const canonicalFallbackGates = [
  { id: "G01", requirement: "AP242 schema", criterion: "AP242", op: "=", actualFormula: "='00_README'!B13", evidence: "authoring_manifest.json" },
  { id: "G02", requirement: "Named assembly hierarchy and reimport occurrence inventory", criterion: 1, op: ">=", actualFormula: "='04_OCCURRENCE_BOM'!F4", evidence: "occurrence_inventory_stowed/deployed.csv" },
  { id: "G03", requirement: "Undocumented positive-volume intersections", criterion: 0, op: "<=", actualFormula: `=${interferenceSummaryCell}`, evidence: "endpoint_pair_audit_*.csv.gz or authoring_pair_audit_*.json" },
  { id: "G04", requirement: "Measured global minimum clearance", criterion: 0, op: ">=", actualFormula: `=${clearanceSummaryCell}`, evidence: "minimum_clearance_register.csv" },
  { id: "G05", requirement: "Maximum stowed arm-module diameter mm", criterion: 57.15, op: "<=", actual: metric(["G05", "arm_module_od", "stowed_arm_module_diameter"], null), evidence: "gate_results.json / measured envelope" },
  { id: "G06", requirement: "Normal body diameter mm", criterion: 53.0, op: "<=", actual: metric(["G06", "normal_body_od", "body_diameter"], null), evidence: "gate_results.json / measured envelope" },
  { id: "G07", requirement: "Maximum arm clocking deviation deg", criterion: 0.001, op: "<=", actual: metric(["G07", "arm_clocking", "clocking_deviation"], null), evidence: "gate_results.json / occurrence transforms" },
  { id: "G08", requirement: "Deployed arm angle deg", criterion: 80.0, op: "=", actual: metric(["G08", "deployed_arm_angle"], deployed.kinematics?.arm_angle_deg), evidence: "authoring_inventory_deployed.json" },
  { id: "G09", requirement: "Pivot-to-tip length mm", criterion: 733.806, op: "=", actual: metric(["G09", "pivot_to_tip"], null), evidence: "gate_results.json / arm geometry" },
  { id: "G10", requirement: "Maximum rigid axial extent in either state mm", criterion: 2032.0, op: "<=", actual: metric(["G10", "rigid_length", "product_length"], endpointLength), evidence: "authoring occurrence bounding boxes / gate_results.json" },
  { id: "G11", requirement: "Maximum complete occurrence-weighted mass kg", criterion: 18.14, op: "<=", actualFormula: `=${massSummaryCell}`, evidence: "13_MASS_PROPERTIES" },
  { id: "G12", requirement: "Crosshead travel at full precision mm", criterion: 15.05, op: ">=", actual: metric(["G12", "crosshead_travel"], manifest.crosshead_travel_mm), evidence: "authoring_manifest.json / motion sweep" },
  { id: "G13", requirement: "Floating / orphaned product occurrences", criterion: 0, op: "<=", actual: metric(["G13", "floating_bodies", "floating_occurrences"], floatingNodes), evidence: "connectivity_nodes.csv + connectivity_edges.csv" },
  { id: "G14", requirement: "Incomplete or blocked routes", criterion: 0, op: "<=", actualFormula: `=${routingIncompleteCell}`, evidence: "routing_termination_register.csv" },
  { id: "G15", requirement: "Invalid or unretained joint checks", criterion: 0, op: "<=", actual: metric(["G15", "unretained_hardware", "joint_failures"], jointFailures), evidence: "joint_geometry_checks.csv" },
  { id: "G16", requirement: "Continuous structural recovery load path", criterion: "YES", op: "YES", actual: metric(["G16", "load_path"], loadPathPass), evidence: "load_path_results.json" },
  { id: "G17", requirement: "Failed continuous-motion samples", criterion: 0, op: "<=", actualFormula: `=${motionSummaryCells.failures}`, evidence: "motion_samples.csv.gz + motion_pair_results.csv.gz" },
  { id: "G18", requirement: "Creo clean-session AP242 validation", criterion: "PASS", op: "PASS", actualFormula: `=${creoOverallCell}`, evidence: "creo_validation.json" },
  { id: "G19", requirement: "Unjustified identity transforms", criterion: 0, op: "<=", actual: metric(["G19", "identity_transforms", "unjustified_identity"], invalidIdentityCount), evidence: "occurrence inventories" },
  { id: "G20", requirement: "Maximum face count per smooth arm blade", criterion: 100, op: "<=", actual: metric(["G20", "arm_face_count", "smooth_arm_geometry"], armFaceMax || null), evidence: "unique part geometry inventory" },
];

function measured(gate, aliases, fallback = "") {
  return deepPick(gate?.measured, aliases, fallback);
}

function numericMeasured(gate, aliases, fallback = null) {
  return asNumber(measured(gate, aliases, fallback));
}

function collectNumbers(value, output = []) {
  if (typeof value === "number" && Number.isFinite(value)) output.push(value);
  else if (Array.isArray(value)) value.forEach((item) => collectNumbers(item, output));
  else if (value && typeof value === "object") Object.values(value).forEach((item) => collectNumbers(item, output));
  return output;
}

function compactMeasured(value) {
  if (value === null || value === undefined) return "";
  const text = JSON.stringify(value);
  return text.length > 360 ? `${text.slice(0, 357)}...` : text;
}

function exactGateModel(gate) {
  const id = String(gate.gate_id ?? gate.id ?? "UNMAPPED-GATE");
  const model = {
    id,
    requirement: gate.requirement ?? id,
    primaryCriterion: "",
    primaryEvidence: "",
    auxiliaryCriterion: "",
    auxiliaryEvidence: compactMeasured(gate.measured),
    evidence: gate.evidence ?? "validation/gate_results.json",
    note: gate.note ?? "",
    reportedStatus: String(gate.status ?? "BLOCKED").toUpperCase(),
    mode: "EQ",
  };
  switch (id) {
    case "AP242-STOWED":
    case "AP242-DEPLOYED": {
      const schema = String(measured(gate, ["schema"]));
      const defectCount =
        (numericMeasured(gate, ["faceted_or_tessellated_total"], 0) ?? 0) +
        (numericMeasured(gate, ["unnamed_products"], 0) ?? 0) +
        (numericMeasured(gate, ["unnamed_nauos"], 0) ?? 0);
      model.primaryCriterion = "YES";
      model.primaryEvidence = schema.includes("AP242") && defectCount === 0 ? "YES" : "NO";
      model.mode = "EQ";
      break;
    }
    case "BREP-VALID-STOWED":
    case "BREP-VALID-DEPLOYED":
      model.primaryCriterion = 0;
      model.primaryEvidence = numericMeasured(gate, ["invalid_solid_count"]);
      model.mode = "LE";
      break;
    case "INTERFERENCE-STOWED":
    case "INTERFERENCE-DEPLOYED":
      model.primaryCriterion = 0;
      model.primaryEvidence = numericMeasured(gate, ["unauthorized_positive_volume_pairs"]);
      model.mode = "LE";
      break;
    case "CLEARANCE-EVIDENCE-STOWED":
    case "CLEARANCE-EVIDENCE-DEPLOYED":
      model.primaryCriterion = 0;
      model.primaryEvidence = numericMeasured(gate, ["distance_blocked_pairs"]);
      model.mode = "BLOCKED_COUNT";
      break;
    case "STATE-PARITY":
      model.primaryCriterion = 0;
      model.primaryEvidence = numericMeasured(gate, ["mismatch_count"]);
      model.mode = "LE";
      break;
    case "OCCURRENCE-TRANSFORMS":
      model.primaryCriterion = 0;
      model.primaryEvidence =
        (numericMeasured(gate, ["unmapped_leaf_occurrences"], 0) ?? 0) +
        (numericMeasured(gate, ["identity_occurrences_without_justification"], 0) ?? 0);
      model.mode = "LE";
      break;
    case "ARM-KINEMATICS-ENDPOINTS":
      model.primaryCriterion = 0.001;
      model.primaryEvidence = Math.max(
        numericMeasured(gate, ["maximum_clock_error_deg"], 0) ?? 0,
        numericMeasured(gate, ["maximum_stowed_angle_error_deg"], 0) ?? 0,
        numericMeasured(gate, ["maximum_deployed_angle_error_deg"], 0) ?? 0,
      );
      model.mode = "LE";
      break;
    case "ARM-LENGTH":
      model.primaryCriterion = 0.001;
      model.primaryEvidence = numericMeasured(gate, ["maximum_absolute_error_mm"]);
      model.mode = "LE";
      break;
    case "CROSSHEAD-TRAVEL":
      model.primaryCriterion = numericMeasured(gate, ["minimum_mm"], 15.05) ?? 15.05;
      model.primaryEvidence = numericMeasured(gate, ["travel_mm"]);
      model.mode = "GE";
      break;
    case "NORMAL-BODY-OML": {
      const spans = measured(gate, ["measured_xy_spans_mm"], {});
      const spanNumbers = collectNumbers(spans);
      model.primaryCriterion = numericMeasured(gate, ["target_max_mm"], 53.0) ?? 53.0;
      model.primaryEvidence = spanNumbers.length ? Math.max(...spanNumbers) : null;
      model.auxiliaryCriterion = 0.001;
      model.auxiliaryEvidence = model.primaryEvidence === null ? null : Math.max(0, model.primaryEvidence - model.primaryCriterion);
      model.mode = "LE_WITH_TOLERANCE";
      break;
    }
    case "ARM-MODULE-HARD-ENVELOPE":
      model.primaryCriterion = numericMeasured(gate, ["limit_mm"], 57.15) ?? 57.15;
      model.primaryEvidence = numericMeasured(gate, ["measured_span_mm"]);
      model.mode = "LE";
      break;
    case "RIGID-LENGTH": {
      const lengths = collectNumbers(measured(gate, ["measured_mm"], {}));
      model.primaryCriterion = numericMeasured(gate, ["limit_mm"], 2032) ?? 2032;
      model.primaryEvidence = lengths.length ? Math.max(...lengths) : null;
      model.mode = "LE";
      break;
    }
    case "SYSTEM-MASS": {
      const unresolved = measured(gate, ["unresolved_occurrence_ids"], []);
      model.primaryCriterion = 0;
      model.primaryEvidence = Array.isArray(unresolved) ? unresolved.length : numericOrBlank(unresolved);
      model.auxiliaryCriterion = 17.14;
      model.auxiliaryEvidence = numericMeasured(gate, ["resolved_mass_kg"]);
      model.mode = "MASS";
      break;
    }
    case "ATTACHMENT-COHESION":
      model.primaryCriterion = 0;
      model.primaryEvidence =
        (numericMeasured(gate, ["floating_rigid_rows_across_states"], 0) ?? 0) +
        (numericMeasured(gate, ["dangling_connections_across_states"], 0) ?? 0) +
        (numericMeasured(gate, ["self_connections_across_states"], 0) ?? 0) +
        (numericMeasured(gate, ["generic_evidence_rows_across_states"], 0) ?? 0);
      model.mode = "LE";
      break;
    case "RECOVERY-LOAD-PATH": {
      const stowedPath = measured(gate, ["STOWED"], []);
      const deployedPath = measured(gate, ["DEPLOYED"], []);
      model.primaryCriterion = "YES";
      model.primaryEvidence =
        Array.isArray(stowedPath) && stowedPath.length > 1 && Array.isArray(deployedPath) && deployedPath.length > 1
          ? "YES"
          : "NO";
      model.mode = "EQ";
      break;
    }
    case "PROCUREMENT-DEFINITION": {
      const provisional = measured(gate, ["provisional_part_numbers"], []);
      const missingLinks = measured(gate, ["bought_without_purchase_link"], []);
      model.primaryCriterion = 0;
      model.primaryEvidence =
        (Array.isArray(provisional) ? provisional.length : 0) +
        (Array.isArray(missingLinks) ? missingLinks.length : 0);
      model.mode = "LE";
      break;
    }
    case "MOTION-ARM-BODIES-1DEG":
      model.primaryCriterion = 0;
      model.primaryEvidence =
        (numericMeasured(gate, ["positive_volume_pairs"], 0) ?? 0) +
        (numericMeasured(gate, ["boolean_blocked_pairs"], 0) ?? 0);
      model.mode = "LE";
      break;
    case "MOTION-FULL-MECHANISM":
      model.primaryCriterion = "COMPLETE";
      model.primaryEvidence = measured(gate, ["missing_scope"]) ? "INCOMPLETE" : "COMPLETE";
      model.mode = "BLOCKED_EQ";
      break;
    case "CREO-CLEAN-SESSION":
      model.primaryCriterion = "AVAILABLE";
      model.primaryEvidence =
        asYesNo(measured(gate, ["creo_session_available"])) === "YES" && measured(gate, ["report"])
          ? "AVAILABLE"
          : "NOT AVAILABLE";
      model.mode = "BLOCKED_EQ";
      break;
    default:
      model.primaryCriterion = model.reportedStatus;
      model.primaryEvidence = model.reportedStatus;
      model.mode = "EQ";
      model.note = `${model.note} Workbook mapping fallback used for an unrecognized gate ID.`.trim();
  }
  return model;
}

function exactStatusFormula(row, model) {
  const missing = `COUNTA(D${row})=0`;
  switch (model.mode) {
    case "LE":
      return `=IF(${missing},"BLOCKED",IF(D${row}<=C${row},"PASS","FAIL"))`;
    case "GE":
      return `=IF(${missing},"BLOCKED",IF(D${row}>=C${row},"PASS","FAIL"))`;
    case "LE_WITH_TOLERANCE":
      return `=IF(${missing},"BLOCKED",IF(D${row}<=C${row}+E${row},"PASS","FAIL"))`;
    case "BLOCKED_COUNT":
      return `=IF(${missing},"BLOCKED",IF(D${row}>C${row},"BLOCKED","PASS"))`;
    case "MASS":
      return `=IF(${missing},"BLOCKED",IF(D${row}>C${row},"BLOCKED",IF(COUNTA(F${row})=0,"BLOCKED",IF(F${row}<=E${row},"PASS","FAIL"))))`;
    case "BLOCKED_EQ":
      return `=IF(${missing},"BLOCKED",IF(D${row}=C${row},"PASS","BLOCKED"))`;
    case "EQ":
    default:
      return `=IF(${missing},"BLOCKED",IF(D${row}=C${row},"PASS","FAIL"))`;
  }
}

const gateModels = providedGates.length
  ? providedGates.map(exactGateModel)
  : canonicalFallbackGates.map((gate) => ({
      id: gate.id,
      requirement: gate.requirement,
      primaryCriterion: gate.criterion,
      primaryEvidence: gate.actual ?? "",
      actualFormula: gate.actualFormula,
      auxiliaryCriterion: "",
      auxiliaryEvidence: "",
      evidence: gate.evidence,
      note: "Validation outputs absent; fallback authoring gate retained.",
      reportedStatus: "BLOCKED",
      fallbackOperator: gate.op,
    }));

// 12_VALIDATION_GATES
const gateRowsById = new Map();
{
  const sheet = sheets.get("12_VALIDATION_GATES");
  const headers = [
    "Gate ID",
    "Requirement",
    "Primary Criterion",
    "Primary Evidence",
    "Aux Criterion",
    "Aux Evidence",
    "Computed Status",
    "Evidence Source",
    "Note",
    "Validator Status",
  ];
  createTitle(sheet, "R2 CALCULATED VALIDATION GATES", "All statuses are formulas comparing evidence cells to explicit criteria; no static PASS values are used.", headers.length);
  sheet.getRange("A4:J5").values = [
    ["Computed Total", null, "Computed PASS", null, "Computed FAIL", null, "Computed BLOCKED", null, "Count Reconciliation", null],
    ["Validator Total", providedGates.length, "Validator PASS", gateResultData?.gate_counts?.PASS ?? "", "Validator FAIL", gateResultData?.gate_counts?.FAIL ?? "", "Validator BLOCKED", gateResultData?.gate_counts?.BLOCKED ?? "", "Reported Release", gateResultData?.computed_release_status ?? RELEASE_STATUS],
  ];
  sheet.getRange("A4:J4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  sheet.getRange("A5:J5").format = { fill: COLORS.pale, font: { bold: true, color: COLORS.ink } };
  const rows = gateModels.map((gate, index) => {
    const row = 8 + index;
    gateRowsById.set(gate.id, row);
    const actual = gate.actualFormula ? { formula: gate.actualFormula } : (gate.primaryEvidence ?? "");
    const statusFormula = !providedGates.length
      ? '="BLOCKED"'
      : gate.fallbackOperator
        ? makeStatusFormula(`D${row}`, `C${row}`, gate.fallbackOperator, gate.primaryEvidence !== "")
        : exactStatusFormula(row, gate);
    return [
      gate.id,
      gate.requirement,
      gate.primaryCriterion,
      actual,
      gate.auxiliaryCriterion,
      gate.auxiliaryEvidence,
      { formula: statusFormula },
      gate.evidence,
      gate.note,
      gate.reportedStatus,
    ];
  });
  const table = writeTable(sheet, 7, headers, rows, {
    numberFormats: { 2: "0.000000", 3: "0.000000", 4: "0.000000", 5: "0.000000" },
    statusColumns: [6, 9],
    widthCaps: { 1: 58, 5: 52, 7: 50, 8: 60 },
  });
  sheet.getRange("B4").formulas = [[`=COUNTA(A${table.dataStart}:A${table.dataEnd})`]];
  sheet.getRange("D4").formulas = [[`=COUNTIF(G${table.dataStart}:G${table.dataEnd},"PASS")`]];
  sheet.getRange("F4").formulas = [[`=COUNTIF(G${table.dataStart}:G${table.dataEnd},"FAIL")`]];
  sheet.getRange("H4").formulas = [[`=COUNTIF(G${table.dataStart}:G${table.dataEnd},"BLOCKED")`]];
  sheet.getRange("J4").formulas = [[providedGates.length
    ? `=IF(AND(B4=B5,D4=D5,F4=F5,H4=H5),"MATCH","MISMATCH")`
    : '="VALIDATOR OUTPUT ABSENT"']];
  sheet.getRange("B4:H5").format.numberFormat = "0";
  applyStatusConditionalFormatting(sheet.getRange("J4"));
}

// 01_NCR_CLOSURE
let ncrTable;
{
  const sheet = sheets.get("01_NCR_CLOSURE");
  const headers = ["NCR", "Rejected Condition", "Required Correction", "Controlling Gates", "Evidence", "Formula Status", "Owner / Disposition"];
  createTitle(sheet, "R2 NCR CLOSURE MATRIX", "Closure requires evidence-backed gate results; no NCR is closed by authoring assertion alone.", headers.length);
  const ncrs = [
    ["NCR-01", "Uncontrolled assembly context and ambiguous external crane/ORION/load-cell hardware.", "Classify product versus external context, control the boundary, remove duplicates, and prove the product load path reaches it.", ["AP242-STOWED", "AP242-DEPLOYED", "STATE-PARITY", "ATTACHMENT-COHESION", "RECOVERY-LOAD-PATH"], "Named AP242 hierarchy, state parity, separately named external context, and structural connectivity evidence"],
    ["NCR-02", "Incomplete deployed-system cohesion across buoy, harness, terminal, tether, hardpoint, and primary structure.", "Model and retain the complete deployed recovery chain with both flexible-member termini physically connected.", ["STATE-PARITY", "ATTACHMENT-COHESION", "RECOVERY-LOAD-PATH"], "State parity and occurrence-specific attachment/load-path evidence"],
    ["NCR-03", "Unsupported routing and improperly placed small hardware.", "Define origins, destinations, penetrations, clamps, fairleads, glands, strain relief, bend radius, service slack, tool access, and engagement.", ["PROCUREMENT-DEFINITION", "CLEARANCE-EVIDENCE-STOWED", "CLEARANCE-EVIDENCE-DEPLOYED", "MOTION-FULL-MECHANISM"], "Procurement, near-clearance, routing, and full-motion evidence"],
    ["NCR-04", "Wall, boss, and spring-envelope interference.", "Provide manufactured passages and reinforcement while eliminating every undocumented intersection through full travel.", ["INTERFERENCE-STOWED", "INTERFERENCE-DEPLOYED", "CLEARANCE-EVIDENCE-STOWED", "CLEARANCE-EVIDENCE-DEPLOYED", "MOTION-FULL-MECHANISM"], "Endpoint pair audits, critical clearance register, and full-mechanism motion sweep"],
    ["NCR-05", "Floating or unretained mechanism components.", "Provide pivots/guides/seats, axial and lateral retention, anti-rotation, defined DOF, stops/locks, and service method.", ["ATTACHMENT-COHESION", "PROCUREMENT-DEFINITION", "MOTION-FULL-MECHANISM"], "Attachment graph, retained hardware definition, and motion evidence"],
    ["NCR-06", "Open-ended line and unattached hardware.", "Terminate every line at modeled hardware, add support and controlled penetrations, and verify collision-free movement.", ["ATTACHMENT-COHESION", "PROCUREMENT-DEFINITION", "MOTION-FULL-MECHANISM"], "Attachment, procurement, and full-mechanism motion evidence"],
    ["NCR-07", "Faceted arm geometry built from excessive planar patches.", "Use smooth analytic or curvature-continuous exact B-rep arm geometry with no tessellated proxy.", ["AP242-STOWED", "BREP-VALID-STOWED", "AP242-DEPLOYED", "BREP-VALID-DEPLOYED"], "AP242 text inspection, exact B-rep validity, and unique-part face/surface inventory"],
    ["NCR-08", "Globally baked component geometry and unjustified identity placements.", "Use stable local part coordinates, meaningful occurrence transforms, reused part definitions, and consistent moving identities.", ["STATE-PARITY", "OCCURRENCE-TRANSFORMS"], "XCAF occurrence inventories, state parity, and transform-justification evidence"],
  ];
  const rows = ncrs.map((ncr) => {
    const gateCells = ncr[3].map((id) => {
      const row = gateRowsById.get(id);
      return row ? `'12_VALIDATION_GATES'!G${row}` : '"BLOCKED"';
    });
    const closed = `AND(${gateCells.map((cell) => `${cell}="PASS"`).join(",")})`;
    const failed = `OR(${gateCells.map((cell) => `${cell}="FAIL"`).join(",")})`;
    return [
      ncr[0],
      ncr[1],
      ncr[2],
      ncr[3].join(", "),
      ncr[4],
      { formula: `=IF(${closed},"CLOSED",IF(${failed},"OPEN","BLOCKED"))` },
      "R2 corrective engineering; release authority withheld pending all evidence",
    ];
  });
  ncrTable = writeTable(sheet, 5, headers, rows, {
    statusColumns: [5],
    widthCaps: { 1: 52, 2: 52, 4: 46, 6: 48 },
  });
}

// 14_COMPLIANCE
{
  const sheet = sheets.get("14_COMPLIANCE");
  const headers = ["Requirement ID", "Requirement", "Primary Criterion", "Primary Evidence", "Aux Criterion", "Aux Evidence", "Formula Status", "Evidence Source", "Notes"];
  createTitle(sheet, "R2 REQUIREMENT COMPLIANCE MATRIX", "Hard requirements are linked to calculated validation gates and retain full precision.", headers.length);
  const compliance = gateModels.map((gate) => {
    const gateRow = gateRowsById.get(gate.id);
    return [
      gate.id,
      gate.requirement,
      { formula: `='12_VALIDATION_GATES'!C${gateRow}` },
      { formula: `='12_VALIDATION_GATES'!D${gateRow}` },
      { formula: `='12_VALIDATION_GATES'!E${gateRow}` },
      { formula: `='12_VALIDATION_GATES'!F${gateRow}` },
      { formula: `='12_VALIDATION_GATES'!G${gateRow}` },
      gate.evidence,
      gate.note,
    ];
  });
  writeTable(sheet, 5, headers, compliance, {
    numberFormats: { 2: "0.000000", 3: "0.000000", 4: "0.000000", 5: "0.000000" },
    statusColumns: [6],
    widthCaps: { 1: 54, 5: 50, 7: 48, 8: 56 },
  });
}

// 00_README (last because it links to completed sheet layouts)
{
  const sheet = sheets.get("00_README");
  createTitle(sheet, "STINGRAY I5S DF8 — R2 COHESION CORRECTION REVIEW", "Evidence-backed engineering review workbook for the R2 candidate. This workbook is not a fabrication or test-release authorization.", 8);
  sheet.getRange("A4:H4").values = [["Validation Gates", null, "PASS", null, "FAIL", null, "BLOCKED", null]];
  sheet.getRange("A5:H5").values = [[null, null, null, null, null, null, null, null]];
  sheet.getRange("A4:H4").format = { fill: COLORS.teal, font: { bold: true, color: COLORS.white }, horizontalAlignment: "center" };
  sheet.getRange("A5:H5").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.navy, size: 14 }, horizontalAlignment: "center" };
  sheet.getRange("B5").formulas = [["='12_VALIDATION_GATES'!B4"]];
  sheet.getRange("D5").formulas = [["='12_VALIDATION_GATES'!D4"]];
  sheet.getRange("F5").formulas = [["='12_VALIDATION_GATES'!F4"]];
  sheet.getRange("H5").formulas = [["='12_VALIDATION_GATES'!H4"]];
  applyStatusConditionalFormatting(sheet.getRange("C4:H5"));

  sheet.getRange("A7:H7").values = [["NCRs Closed", null, "NCRs Open", null, "NCRs Blocked", null, "Creo Gate", null]];
  sheet.getRange("A8:H8").values = [[null, null, null, null, null, null, null, null]];
  sheet.getRange("A7:H7").format = { fill: COLORS.blue, font: { bold: true, color: COLORS.white }, horizontalAlignment: "center" };
  sheet.getRange("A8:H8").format = { fill: COLORS.pale, font: { bold: true, color: COLORS.navy, size: 13 }, horizontalAlignment: "center" };
  sheet.getRange("B8").formulas = [[`=COUNTIF('01_NCR_CLOSURE'!F${ncrTable.dataStart}:F${ncrTable.dataEnd},"CLOSED")`]];
  sheet.getRange("D8").formulas = [[`=COUNTIF('01_NCR_CLOSURE'!F${ncrTable.dataStart}:F${ncrTable.dataEnd},"OPEN")`]];
  sheet.getRange("F8").formulas = [[`=COUNTIF('01_NCR_CLOSURE'!F${ncrTable.dataStart}:F${ncrTable.dataEnd},"BLOCKED")`]];
  sheet.getRange("H8").formulas = [["='16_CREO_VALIDATION'!B4"]];
  applyStatusConditionalFormatting(sheet.getRange("H8"));

  const fileEntries = Object.entries(manifest.files ?? {});
  const metadata = [
    ["Package status", RELEASE_STATUS],
    ["Authoring kernel", manifest.authoring_kernel ?? ""],
    ["Exchange schema", manifest.schema ?? ""],
    ["Crosshead travel, full precision mm", numericOrBlank(manifest.crosshead_travel_mm)],
    ["Stowed occurrence count", stowed.occurrences?.length ?? 0],
    ["Deployed occurrence count", deployed.occurrences?.length ?? 0],
    ["Unique authored part count", parts.length],
    ["Workbook generation time", new Date()],
  ];
  sheet.getRange("A10:B10").values = [["Package Metadata", "Value"]];
  sheet.getRange("A10:B10").format = { fill: COLORS.blue, font: { bold: true, color: COLORS.white } };
  sheet.getRange(`A11:B${10 + metadata.length}`).values = metadata;
  sheet.getRange(`A11:A${10 + metadata.length}`).format = { fill: COLORS.pale, font: { bold: true, color: COLORS.ink } };
  sheet.getRange(`B11:B${10 + metadata.length}`).format = { font: { color: COLORS.ink }, wrapText: true };
  sheet.getRange("B14").format.numberFormat = "0.000000";
  sheet.getRange("B18").format.numberFormat = "yyyy-mm-dd hh:mm";

  sheet.getRange("D10:H10").values = [["Product / Context File", "SHA-256", "Bytes", "Schema", "Release Standing"]];
  sheet.getRange("D10:H10").format = { fill: COLORS.blue, font: { bold: true, color: COLORS.white } };
  const fileRows = fileEntries.map(([name, info]) => [name, info.sha256, info.size_bytes, manifest.schema, name.includes("EXTERNAL") ? "CONTROLLED EXTERNAL CONTEXT — NOT PRODUCT" : RELEASE_STATUS]);
  if (fileRows.length) sheet.getRange(`D11:H${10 + fileRows.length}`).values = fileRows;
  sheet.getRange(`D11:H${Math.max(11, 10 + fileRows.length)}`).format = { font: { size: 9, color: COLORS.ink }, wrapText: true, borders: { insideHorizontal: { style: "thin", color: COLORS.line } } };
  sheet.getRange(`F11:F${Math.max(11, 10 + fileRows.length)}`).format.numberFormat = "#,##0";

  sheet.getRange("A20:H20").merge();
  sheet.getRange("A20").values = [["Release rule: only a clean Creo session may clear G18. OCCT/XCAF evidence is intermediate and cannot change this package from WIP to released."]];
  sheet.getRange("A20:H20").format = { fill: COLORS.amber, font: { bold: true, color: COLORS.redInk }, wrapText: true };
  sheet.getRange("A20:H20").format.rowHeight = 34;
  sheet.getRange("A22:H22").merge();
  sheet.getRange("A22").values = [["Source URLs are recorded in 03_PURCHASED_ITEMS, 10_SOURCE_CAD, 18_CUSTOM_PARTS, and 19_CONSUMABLES. External crane-hook / ORION / load-cell context is excluded from the product BOM and retained only as provisional test context."]];
  sheet.getRange("A22:H22").format = { fill: COLORS.pale, font: { italic: true, color: COLORS.ink }, wrapText: true };
  sheet.getRange("A22:H22").format.rowHeight = 38;
  sheet.getRange("A:A").format.columnWidth = 34;
  sheet.getRange("B:B").format.columnWidth = 31;
  sheet.getRange("C:C").format.columnWidth = 14;
  sheet.getRange("D:D").format.columnWidth = 45;
  sheet.getRange("E:E").format.columnWidth = 52;
  sheet.getRange("F:F").format.columnWidth = 16;
  sheet.getRange("G:G").format.columnWidth = 22;
  sheet.getRange("H:H").format.columnWidth = 44;
  sheet.freezePanes.freezeRows(3);
}

// Apply workbook-wide polish to populated ranges only.
for (const [sheetName, width] of [
  ["04_OCCURRENCE_BOM", 18],
  ["07_CLEARANCE_REGISTER", 20],
  ["08_INTERFERENCE_REGISTER", 20],
  ["16_CREO_VALIDATION", 24],
  ["17_ROUTING", 20],
]) {
  sheets.get(sheetName).getRange("A:A").format.columnWidth = width;
}

for (const name of sheetNames) {
  const sheet = sheets.get(name);
  const used = sheet.getUsedRange();
  if (used) {
    used.format.verticalAlignment = "top";
    used.format.font = { name: "Aptos", color: COLORS.ink };
    sheet.getRange("A1").format.font = { name: "Aptos Display", bold: true, color: COLORS.white, size: 16 };
  }
}

// Compact verification: key formula/value inspection and formula-error scan.
const gateInspection = await workbook.inspect({
  kind: "table",
  range: "12_VALIDATION_GATES!A1:J35",
  include: "values,formulas",
  tableMaxRows: 35,
  tableMaxCols: 10,
  maxChars: 20000,
});
console.log("GATE_INSPECTION\n" + gateInspection.ndjson);

const ncrInspection = await workbook.inspect({
  kind: "table",
  range: "01_NCR_CLOSURE!A1:G16",
  include: "values,formulas",
  tableMaxRows: 16,
  tableMaxCols: 7,
  maxChars: 12000,
});
console.log("NCR_INSPECTION\n" + ncrInspection.ndjson);

// Export the exact, formula-resolved review tables so downstream package checks
// consume the same values shown in the workbook rather than a parallel status
// calculation.  These compact inspections deliberately include only the table
// header and its data rows.
const resolvedGateInspection = await workbook.inspect({
  kind: "table",
  range: `12_VALIDATION_GATES!A7:J${7 + gateModels.length}`,
  include: "values",
  tableMaxRows: 1 + gateModels.length,
  tableMaxCols: 10,
  maxChars: 120000,
});
const resolvedGateRows = inspectionValues(resolvedGateInspection);
if (resolvedGateRows.length !== 1 + gateModels.length) {
  throw new Error(
    `Resolved gate export has ${resolvedGateRows.length - 1} data rows; expected ${gateModels.length}.`,
  );
}
const resolvedGateCounts = { PASS: 0, FAIL: 0, BLOCKED: 0 };
for (const row of resolvedGateRows.slice(1)) {
  const status = String(row[6] ?? "").trim().toUpperCase();
  if (!(status in resolvedGateCounts)) {
    throw new Error(`Unexpected formula-resolved gate status '${status}' for ${row[0] ?? "unknown gate"}.`);
  }
  resolvedGateCounts[status] += 1;
}
for (const status of ["PASS", "FAIL", "BLOCKED"]) {
  if (!providedGates.length) break;
  const reported = Number(gateResultData?.gate_counts?.[status]);
  if (!Number.isFinite(reported) || resolvedGateCounts[status] !== reported) {
    throw new Error(
      `Formula-resolved ${status} gate count ${resolvedGateCounts[status]} does not match validator count ${gateResultData?.gate_counts?.[status] ?? "missing"}.`,
    );
  }
}

const resolvedNcrInspection = await workbook.inspect({
  kind: "table",
  range: `01_NCR_CLOSURE!A5:G${ncrTable.dataEnd}`,
  include: "values",
  tableMaxRows: 9,
  tableMaxCols: 7,
  maxChars: 80000,
});
const resolvedNcrRows = inspectionValues(resolvedNcrInspection);
if (resolvedNcrRows.length !== 9) {
  throw new Error(`Resolved NCR export has ${resolvedNcrRows.length - 1} data rows; expected exactly 8.`);
}
const resolvedNcrCounts = { CLOSED: 0, OPEN: 0, BLOCKED: 0 };
for (const row of resolvedNcrRows.slice(1)) {
  const status = String(row[5] ?? "").trim().toUpperCase();
  if (!(status in resolvedNcrCounts)) {
    throw new Error(`Unexpected formula-resolved NCR status '${status}' for ${row[0] ?? "unknown NCR"}.`);
  }
  resolvedNcrCounts[status] += 1;
}

const workbookExportDir = path.join(analysisDir, "workbook_exports");
await fs.mkdir(workbookExportDir, { recursive: true });
await fs.writeFile(
  path.join(workbookExportDir, "validation_gate_table.csv"),
  csvText(resolvedGateRows),
  "utf8",
);
await fs.writeFile(
  path.join(workbookExportDir, "ncr_closure_register.csv"),
  csvText(resolvedNcrRows),
  "utf8",
);
console.log(
  `FINAL_GATE_COUNTS PASS=${resolvedGateCounts.PASS} FAIL=${resolvedGateCounts.FAIL} BLOCKED=${resolvedGateCounts.BLOCKED} FAILED_PLUS_BLOCKED=${resolvedGateCounts.FAIL + resolvedGateCounts.BLOCKED}`,
);
console.log(
  `FINAL_NCR_COUNTS CLOSED=${resolvedNcrCounts.CLOSED} OPEN=${resolvedNcrCounts.OPEN} BLOCKED=${resolvedNcrCounts.BLOCKED}`,
);

const errorScan = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "R2 workbook formula error scan",
});
console.log("FORMULA_ERROR_SCAN\n" + errorScan.ndjson);

await fs.mkdir(previewDir, { recursive: true });
for (const fileName of await fs.readdir(previewDir)) {
  if (fileName.endsWith(".png")) await fs.unlink(path.join(previewDir, fileName));
}
const renderFailures = [];
for (const name of sheetNames) {
  try {
    if (name === "07_CLEARANCE_REGISTER" && clearanceCsv.length > 440) {
      const lastRow = 6 + clearanceCsv.length;
      let part = 1;
      for (let start = 1; start <= lastRow; start += 440) {
        const end = Math.min(lastRow, start + 439);
        const preview = await workbook.render({
          sheetName: name,
          range: `A${start}:I${end}`,
          scale: 0.65,
          format: "png",
        });
        await fs.writeFile(
          path.join(previewDir, `${name}_${String(part).padStart(2, "0")}.png`),
          new Uint8Array(await preview.arrayBuffer()),
        );
        part += 1;
      }
    } else {
      const preview = await workbook.render({ sheetName: name, autoCrop: "all", scale: 0.65, format: "png" });
      await fs.writeFile(path.join(previewDir, `${name}.png`), new Uint8Array(await preview.arrayBuffer()));
    }
  } catch (error) {
    renderFailures.push(`${name}: ${error.message}`);
  }
}
if (renderFailures.length) throw new Error(`Sheet render failures:\n${renderFailures.join("\n")}`);

await fs.mkdir(releaseDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
await fs.rm(`${outputPath}.inspect.ndjson`, { force: true });
console.log(`EXPORTED ${outputPath}`);
console.log(`RENDERED ${sheetNames.length} sheets to ${previewDir}`);
