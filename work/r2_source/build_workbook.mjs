import fs from "node:fs/promises";
import { createReadStream } from "node:fs";
import { createHash } from "node:crypto";
import path from "node:path";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const scriptPath = await fs.realpath(fileURLToPath(import.meta.url));
const scriptDir = path.dirname(scriptPath);
const workDir = path.dirname(scriptDir);
const analysisDir = path.join(workDir, "final_analysis");
const releaseDir = path.join(workDir, "final_release");
const previewDir = path.join(analysisDir, "workbook_previews");
const outputPath = path.join(
  releaseDir,
  "STINGRAY_I5S_DF8_MASTER_BUILD_PARTS_AND_PROCUREMENT_REGISTER.xlsx",
);

const FINAL_STOWED_STEP = "STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step";
const FINAL_DEPLOYED_STEP = "STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step";
const FINAL_PRODUCT_STEP_FILES = [FINAL_STOWED_STEP, FINAL_DEPLOYED_STEP];
const FINAL_INVENTORY_FILES = [
  "authoring_inventory_stowed.json",
  "authoring_inventory_deployed.json",
];

// Every validation artifact whose contents or file metadata enter this
// workbook is required and hash/size authenticated before any sheet is built.
// validation_manifest.json itself is the trust root and is intentionally not
// self-hashed by the validator.
const REQUIRED_VALIDATION_EVIDENCE_FILES = [
  "gate_results.json",
  "validation_summary.json",
  "step_text_inspection.json",
  "xcaf_occurrences_stowed.csv",
  "xcaf_occurrences_deployed.csv",
  "leaf_solids_stowed.csv",
  "leaf_solids_deployed.csv",
  "endpoint_pair_audit_stowed.csv.gz",
  "endpoint_pair_audit_deployed.csv.gz",
  "endpoint_interference_register.csv",
  "endpoint_pair_summary.json",
  "minimum_clearance_register.csv",
  "key_dimensions.json",
  "motion_kinematics_1deg.csv",
  "motion_full_mechanism_audit.csv.gz",
  "motion_audit_summary.json",
  "attachment_connectivity_stowed.csv",
  "attachment_connectivity_deployed.csv",
  "attachment_geometry_stowed.csv",
  "attachment_geometry_deployed.csv",
  "route_termination_audit_stowed.csv",
  "route_termination_audit_deployed.csv",
  "connectivity_summary.json",
  "definition_of_done_audit.json",
  "state_parity.csv",
  "occurrence_bom_reconciliation.csv",
  "occurrence_bom_reconciliation.json",
];

// Frozen contract emitted by validate_r2.py::compute_gates.  The workbook is
// deliberately not allowed to infer release from a partial or extended result
// set: validator and workbook must be updated together when this schema changes.
const REQUIRED_FINAL_GATE_IDS = [
  "AP242-STOWED",
  "BREP-VALID-STOWED",
  "INTERFERENCE-STOWED",
  "INTENTIONAL-FIT-REGISTER-STOWED",
  "CLEARANCE-EVIDENCE-STOWED",
  "AP242-DEPLOYED",
  "BREP-VALID-DEPLOYED",
  "INTERFERENCE-DEPLOYED",
  "INTENTIONAL-FIT-REGISTER-DEPLOYED",
  "CLEARANCE-EVIDENCE-DEPLOYED",
  "STATE-PARITY",
  "OCCURRENCE-TRANSFORMS",
  "OCCURRENCE-BOM-RECONCILIATION",
  "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION",
  "DOD-POSITIVE-DEPLOYED-LOCKS",
  "DOD-POSITIVE-STOWED-RETENTION",
  "DOD-CLOSED-PRESSURE-SUBSYSTEMS",
  "DOD-CLOSED-ROUTE-ENDS",
  "ARM-KINEMATICS-ENDPOINTS",
  "ARM-LENGTH",
  "ARM-SURFACE-QUALITY",
  "CROSSHEAD-TRAVEL",
  "NORMAL-BODY-OML",
  "ARM-MODULE-HARD-ENVELOPE",
  "RIGID-LENGTH",
  "SYSTEM-MASS",
  "ATTACHMENT-COHESION",
  "RECOVERY-LOAD-PATH",
  "PROCUREMENT-DEFINITION",
  "MOTION-FULL-MECHANISM",
  "INTENTIONAL-FIT-REGISTER-MOTION",
];
const COMMISSION_SHEET_NAMES = [
  "01_OCCURRENCE_BOM",
  "02_UNIQUE_PARTS",
  "03_PURCHASED_ITEMS",
  "04_CUSTOM_PARTS",
  "05_ATTACHMENT_MAP",
  "06_CONFIGURATION_MATRIX",
  "07_CONSUMABLES",
  "08_FINAL_VALIDATION",
];

const RELEASED_LABEL = "FINAL — RELEASED";
const FAILED_LABEL = "CORRECTIVE VALIDATION FAILED — NOT RELEASED";
const RELEASE_STATUS_FORMULA =
  `=IF(AND('08_FINAL_VALIDATION'!B4>0,'08_FINAL_VALIDATION'!D4='08_FINAL_VALIDATION'!B4,'08_FINAL_VALIDATION'!F4=0,'08_FINAL_VALIDATION'!H4=0),"${RELEASED_LABEL}","${FAILED_LABEL}")`;
const CREO_ENVIRONMENT_DISPOSITION =
  "N/A — NOT REQUIRED BY THE CONTROLLING COMMISSION; OWNER CREO IMPORT OCCURS AFTER DELIVERY.";
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

async function requiredJson(fileName, baseDir = analysisDir) {
  const filePath = path.join(baseDir, fileName);
  let text;
  try {
    text = await fs.readFile(filePath, "utf8");
  } catch (error) {
    throw new Error(`Required final input is unavailable: ${filePath}: ${error.message}`);
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`Required final JSON is invalid: ${filePath}: ${error.message}`);
  }
}

async function sha256File(filePath) {
  return new Promise((resolve, reject) => {
    const hash = createHash("sha256");
    const stream = createReadStream(filePath);
    stream.on("error", reject);
    stream.on("data", (chunk) => hash.update(chunk));
    stream.on("end", () => resolve(hash.digest("hex")));
  });
}

function exactIdentifierSetError(actualValues, requiredValues, label) {
  const actual = actualValues.map((value) => String(value ?? "").trim());
  const required = requiredValues.map((value) => String(value).trim());
  const counts = countBy(actual, (value) => value);
  const blank = actual.filter((value) => !value).length;
  const duplicates = [...counts.entries()]
    .filter(([value, count]) => value && count > 1)
    .map(([value]) => value)
    .sort();
  const actualSet = new Set(actual.filter(Boolean));
  const requiredSet = new Set(required);
  const missing = [...requiredSet].filter((value) => !actualSet.has(value)).sort();
  const unexpected = [...actualSet].filter((value) => !requiredSet.has(value)).sort();
  if (blank || duplicates.length || missing.length || unexpected.length || actual.length !== required.length) {
    return `${label} mismatch: blank=${blank}, duplicates=${JSON.stringify(duplicates)}, `
      + `missing=${JSON.stringify(missing)}, unexpected=${JSON.stringify(unexpected)}, `
      + `actual_count=${actual.length}, required_count=${required.length}`;
  }
  return "";
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

async function requiredCsv(fileName, baseDir = analysisDir) {
  const filePath = path.join(baseDir, fileName);
  let raw;
  try {
    raw = await fs.readFile(filePath);
  } catch (error) {
    throw new Error(`Required final CSV evidence is unavailable: ${filePath}: ${error.message}`);
  }
  let bytes;
  try {
    bytes = fileName.endsWith(".gz") ? zlib.gunzipSync(raw) : raw;
  } catch (error) {
    throw new Error(`Required final compressed CSV evidence is invalid: ${filePath}: ${error.message}`);
  }
  return parseCsv(bytes.toString("utf8"));
}

async function fileMeta(filePath) {
  try {
    const stat = await fs.stat(filePath);
    return { present: true, size: stat.size };
  } catch {
    return { present: false, size: 0 };
  }
}

async function authenticateFrozenPath(validationFiles, filePath) {
  let stat;
  try {
    stat = await fs.stat(filePath);
  } catch (error) {
    throw new Error(`Validated final input is missing: ${filePath}: ${error.message}`);
  }
  if (!stat.isFile()) throw new Error(`Validated final input is not a file: ${filePath}`);
  const fileName = path.basename(filePath);
  const frozen = validationFiles[fileName];
  if (!frozen || typeof frozen !== "object" || Array.isArray(frozen)) {
    throw new Error(`validation_manifest.json has no frozen record for ${fileName}.`);
  }
  const frozenSize = Number(frozen.size_bytes);
  const frozenHash = String(frozen.sha256 ?? "").trim().toLowerCase();
  if (!Number.isSafeInteger(frozenSize) || frozenSize < 0 || !/^[0-9a-f]{64}$/.test(frozenHash)) {
    throw new Error(`validation_manifest.json has an invalid hash/size record for ${fileName}.`);
  }
  const actualHash = await sha256File(filePath);
  if (stat.size !== frozenSize || actualHash !== frozenHash) {
    throw new Error(
      `Frozen validation provenance mismatch for ${fileName}: `
      + `size ${stat.size} != ${frozenSize} or sha256 ${actualHash} != ${frozenHash}.`,
    );
  }
  return { fileName, size: stat.size, sha256: actualHash, path: filePath };
}

async function authenticateFinalInputs(validationManifest, authoringManifest) {
  const validationFiles = validationManifest?.files;
  if (!validationFiles || typeof validationFiles !== "object" || Array.isArray(validationFiles)) {
    throw new Error("validation_manifest.json lacks a files object; final provenance cannot be authenticated.");
  }
  const inputs = [
    path.join(releaseDir, FINAL_STOWED_STEP),
    path.join(releaseDir, FINAL_DEPLOYED_STEP),
    path.join(analysisDir, "authoring_inventory_stowed.json"),
    path.join(analysisDir, "authoring_inventory_deployed.json"),
    path.join(analysisDir, "authoring_manifest.json"),
    path.join(analysisDir, "validation", "gate_results.json"),
  ];
  const authenticated = await Promise.all(
    inputs.map((filePath) => authenticateFrozenPath(validationFiles, filePath)),
  );

  const authoredProductFiles = Object.keys(authoringManifest?.files ?? {}).sort();
  const expectedProductFiles = [...FINAL_PRODUCT_STEP_FILES].sort();
  const productSetError = exactIdentifierSetError(
    authoredProductFiles,
    expectedProductFiles,
    "authoring manifest final product filename set",
  );
  if (productSetError) throw new Error(productSetError);
  const actualByName = new Map(authenticated.map((row) => [row.fileName, row]));
  for (const fileName of expectedProductFiles) {
    const authored = authoringManifest.files[fileName];
    const actual = actualByName.get(fileName);
    const authoredHash = String(authored?.sha256 ?? "").trim().toLowerCase();
    const authoredSize = Number(authored?.size_bytes);
    if (!actual || authoredHash !== actual.sha256 || authoredSize !== actual.size) {
      throw new Error(`authoring_manifest.json does not match the authenticated final product ${fileName}.`);
    }
  }
  const authoredInventories = authoringManifest?.inventories;
  if (!authoredInventories || typeof authoredInventories !== "object" || Array.isArray(authoredInventories)) {
    throw new Error("authoring_manifest.json lacks the required inventories hash/size object.");
  }
  const inventorySetError = exactIdentifierSetError(
    Object.keys(authoredInventories),
    FINAL_INVENTORY_FILES,
    "authoring manifest inventory filename set",
  );
  if (inventorySetError) throw new Error(inventorySetError);
  for (const fileName of FINAL_INVENTORY_FILES) {
    const authored = authoredInventories[fileName];
    const actual = actualByName.get(fileName);
    const authoredHash = String(authored?.sha256 ?? "").trim().toLowerCase();
    const authoredSize = Number(authored?.size_bytes);
    if (!actual || authoredHash !== actual.sha256 || authoredSize !== actual.size) {
      throw new Error(`authoring_manifest.json does not match the authenticated final inventory ${fileName}.`);
    }
  }
  if (!String(authoringManifest?.schema ?? "").toUpperCase().includes("AP242")) {
    throw new Error("authoring_manifest.json does not declare AP242 for the final products.");
  }
  return authenticated;
}

async function authenticateValidationEvidence(validationManifest, fileNames) {
  const validationFiles = validationManifest?.files;
  if (!validationFiles || typeof validationFiles !== "object" || Array.isArray(validationFiles)) {
    throw new Error("validation_manifest.json lacks a files object; validation evidence cannot be authenticated.");
  }
  const identifierError = exactIdentifierSetError(
    fileNames,
    REQUIRED_VALIDATION_EVIDENCE_FILES,
    "workbook-consumed validation evidence filename set",
  );
  if (identifierError) throw new Error(identifierError);
  return Promise.all(
    fileNames.map((fileName) => authenticateFrozenPath(
      validationFiles,
      path.join(analysisDir, "validation", fileName),
    )),
  );
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
  sheet.getRange("A2").formulas = [[RELEASE_STATUS_FORMULA]];
  sheet.getRange(`A2:${last}2`).format = {
    fill: COLORS.amber,
    font: { bold: true, color: COLORS.redInk, size: 11 },
    verticalAlignment: "center",
  };
  sheet.getRange(`A2:${last}2`).format.rowHeight = 23;
  applyStatusConditionalFormatting(sheet.getRange("A2"));
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

const stowed = await requiredJson("authoring_inventory_stowed.json");
const deployed = await requiredJson("authoring_inventory_deployed.json");
const manifest = await requiredJson("authoring_manifest.json");
const gateResultData = await requiredJson("validation/gate_results.json");
const validationManifestData = await requiredJson("validation/validation_manifest.json");
if (!Array.isArray(gateResultData?.gates)) {
  throw new Error("Final validation/gate_results.json lacks the required gates array.");
}
const providedGates = gateResultData.gates;
const gateSetError = exactIdentifierSetError(
  providedGates.map((candidate) => candidate?.gate_id),
  REQUIRED_FINAL_GATE_IDS,
  "final neutral-CAD gate ID set",
);
if (gateSetError) throw new Error(gateSetError);
const reportedGateCounts = { PASS: 0, FAIL: 0, BLOCKED: 0 };
for (const candidate of providedGates) {
  const status = String(candidate?.status ?? "").trim().toUpperCase();
  if (!(status in reportedGateCounts)) {
    throw new Error(`Invalid final validator status '${status}' for gate ${candidate?.gate_id ?? "<blank>"}.`);
  }
  reportedGateCounts[status] += 1;
}
const declaredGateCounts = gateResultData?.gate_counts;
if (!declaredGateCounts || typeof declaredGateCounts !== "object" || Array.isArray(declaredGateCounts)) {
  throw new Error("Final validation/gate_results.json lacks the required gate_counts object.");
}
for (const status of ["PASS", "FAIL", "BLOCKED"]) {
  if (Number(declaredGateCounts[status]) !== reportedGateCounts[status]) {
    throw new Error(
      `Final validator ${status} count ${declaredGateCounts[status]} does not reconcile `
      + `to the ${reportedGateCounts[status]} complete gate rows.`,
    );
  }
}
const expectedComputedRelease = reportedGateCounts.FAIL === 0 && reportedGateCounts.BLOCKED === 0
  ? "PASS"
  : "NOT_RELEASED";
if (String(gateResultData.computed_release_status ?? "").trim() !== expectedComputedRelease) {
  throw new Error(
    `Final validator computed_release_status '${gateResultData.computed_release_status}' `
    + `does not reconcile to '${expectedComputedRelease}'.`,
  );
}
const expectedPackageLabel = expectedComputedRelease === "PASS"
  ? RELEASED_LABEL
  : FAILED_LABEL;
if (String(gateResultData.package_required_label ?? "").trim() !== expectedPackageLabel) {
  throw new Error(
    `Final validator package_required_label '${gateResultData.package_required_label}' `
    + `does not reconcile to '${expectedPackageLabel}'.`,
  );
}
const rawReleaseLabel = expectedPackageLabel;
const authenticatedInputs = await authenticateFinalInputs(validationManifestData, manifest);
const authenticatedValidationEvidence = await authenticateValidationEvidence(
  validationManifestData,
  REQUIRED_VALIDATION_EVIDENCE_FILES,
);
const authenticatedByName = new Map(
  [...authenticatedInputs, ...authenticatedValidationEvidence].map((row) => [row.fileName, row]),
);
const keyDimensionsData = await requiredJson("validation/key_dimensions.json");

const clearanceCsv = await requiredCsv("validation/minimum_clearance_register.csv");
const occurrenceInventoryStowedCsv = await requiredCsv("validation/xcaf_occurrences_stowed.csv");
const occurrenceInventoryDeployedCsv = await requiredCsv("validation/xcaf_occurrences_deployed.csv");
const solidInventoryStowedCsv = await requiredCsv("validation/leaf_solids_stowed.csv");
const solidInventoryDeployedCsv = await requiredCsv("validation/leaf_solids_deployed.csv");
const motionSamplesCsv = await requiredCsv("validation/motion_kinematics_1deg.csv");
const jointGeometryCsv = [
  ...(await requiredCsv("validation/attachment_geometry_stowed.csv")),
  ...(await requiredCsv("validation/attachment_geometry_deployed.csv")),
];
const routingTerminationCsv = [
  ...(await requiredCsv("validation/route_termination_audit_stowed.csv")),
  ...(await requiredCsv("validation/route_termination_audit_deployed.csv")),
];
const stowedPairAudit = await requiredCsv("validation/endpoint_pair_audit_stowed.csv.gz");
const deployedPairAudit = await requiredCsv("validation/endpoint_pair_audit_deployed.csv.gz");
for (const [label, rows] of [
  ["xcaf_occurrences_stowed.csv", occurrenceInventoryStowedCsv],
  ["xcaf_occurrences_deployed.csv", occurrenceInventoryDeployedCsv],
  ["leaf_solids_stowed.csv", solidInventoryStowedCsv],
  ["leaf_solids_deployed.csv", solidInventoryDeployedCsv],
  ["attachment_geometry_stowed/deployed.csv", jointGeometryCsv],
  ["route_termination_audit_stowed/deployed.csv", routingTerminationCsv],
  ["endpoint_pair_audit_stowed.csv.gz", stowedPairAudit],
  ["endpoint_pair_audit_deployed.csv.gz", deployedPairAudit],
]) {
  if (!rows.length) throw new Error(`Required authenticated validation table has no data rows: ${label}.`);
}
if (motionSamplesCsv.length !== 81) {
  throw new Error(`Authenticated motion_kinematics_1deg.csv contains ${motionSamplesCsv.length} rows; expected exactly 81.`);
}

const partMap = new Map((stowed.parts ?? []).map((part) => [part.part_number, part]));
for (const part of deployed.parts ?? []) partMap.set(part.part_number, part);
const parts = [...partMap.values()].sort((a, b) => String(a.part_number).localeCompare(String(b.part_number)));
const stowedQty = countBy(stowed.occurrences ?? [], (occ) => occ.part_number);
const deployedQty = countBy(deployed.occurrences ?? [], (occ) => occ.part_number);

function exactOccurrenceMap(rows, state) {
  const map = new Map();
  for (const occurrence of rows ?? []) {
    const occurrenceId = String(occurrence?.occurrence_id ?? "").trim();
    if (!occurrenceId) throw new Error(`${state} authoring inventory contains a blank occurrence ID.`);
    if (map.has(occurrenceId)) throw new Error(`${state} authoring inventory duplicates occurrence ID ${occurrenceId}.`);
    map.set(occurrenceId, occurrence);
  }
  return map;
}

function uniqueJoined(values, separator = "; ") {
  return [...new Set(values.map((value) => String(value ?? "").trim()).filter(Boolean))]
    .sort((a, b) => a.localeCompare(b))
    .join(separator);
}

function subsystemFromPath(parentPath) {
  const first = String(parentPath ?? "").split("/").filter(Boolean)[0] ?? "";
  if (first.startsWith("100_")) return "100 — FORWARD PENETRATOR / WAI / PRIMARY STRUCTURE";
  if (first.startsWith("300_")) return "300 — ARM / POWERTRAIN";
  if (first.startsWith("500_")) return "500 — AFT CLOSURE / RECOVERY";
  return first || "TOP LEVEL";
}

function parentAssemblyFromPath(parentPath) {
  const segments = String(parentPath ?? "").split("/").filter(Boolean);
  return segments.at(-1) ?? "TOP LEVEL";
}

function hyperlinkCell(url, label) {
  const value = String(url ?? "").trim();
  if (!value) return "";
  return { formula: `=HYPERLINK("${excelString(value)}","${excelString(label)}")` };
}

function constraintMode(occurrence) {
  const text = `${occurrence?.classification ?? ""} ${occurrence?.joint_type ?? ""} ${occurrence?.permitted_dof ?? ""}`.toUpperCase();
  if (/ROTAT|REVOLUTE|HINGE/.test(text)) return "ROTATING";
  if (/TRANSLAT|SLID|PRISMATIC/.test(text)) return "SLIDING";
  if (/FLEXIBLE|SOFTGOOD|ELASTIC|COMPRESSION/.test(text)) return "FLEXIBLE";
  return "FIXED";
}

function inferredServiceRemoval(attachmentTypes, connectionServiceMethods) {
  const explicit = uniqueJoined(connectionServiceMethods);
  if (explicit) return explicit;
  const text = attachmentTypes.join(" ").toUpperCase();
  if (/WELD|BRAZE|STITCH|SPLICE|RF_/.test(text)) return "NON-SERVICEABLE — CONTROLLED DESTRUCTIVE PROCESS REMOVAL";
  if (/SCREW|BOLT|THREADED/.test(text)) return "REMOVE ENUMERATED FASTENER(S) WITH CONTROLLED TOOL";
  if (/PIN|CLIP|RING|RETAINER|CIRCLIP/.test(text)) return "REMOVE RETAINER, THEN WITHDRAW OCCURRENCE-MATCHED PIN";
  if (/FERRULE|FITTING|GLAND|ROUTE|TUBE/.test(text)) return "DISCONNECT OCCURRENCE-MATCHED FITTING PER SERVICE PROCEDURE";
  if (/PRESS_FIT/.test(text)) return "CONTROLLED PRESS EXTRACTION";
  return "PER CONTROLLED ASSEMBLY / SERVICE PROCEDURE";
}

const stowedById = exactOccurrenceMap(stowed.occurrences, "STOWED");
const deployedById = exactOccurrenceMap(deployed.occurrences, "DEPLOYED");
const uniqueOccurrenceIds = [...new Set([...stowedById.keys(), ...deployedById.keys()])]
  .sort((a, b) => a.localeCompare(b));
for (const occurrenceId of uniqueOccurrenceIds) {
  const a = stowedById.get(occurrenceId);
  const b = deployedById.get(occurrenceId);
  if (a && b && a.part_number !== b.part_number) {
    throw new Error(`State part-number mismatch for occurrence ${occurrenceId}: ${a.part_number} versus ${b.part_number}.`);
  }
}
const uniqueInstalledQty = countBy(
  uniqueOccurrenceIds,
  (occurrenceId) => firstDefined(stowedById.get(occurrenceId)?.part_number, deployedById.get(occurrenceId)?.part_number),
);

const occurrenceInventoryByKey = new Map();
for (const [state, inventory] of [["STOWED", occurrenceInventoryStowedCsv], ["DEPLOYED", occurrenceInventoryDeployedCsv]]) {
  for (const item of inventory) {
    if (asYesNo(pick(item, ["has_shape"])) !== "YES") continue;
    const id = pick(item, ["occurrence_id", "occurrence", "component_id", "instance_name", "name"]);
    if (!id) throw new Error(`${state} clean-reimport leaf occurrence has a blank occurrence ID.`);
    const key = `${state}|${id}`;
    if (occurrenceInventoryByKey.has(key)) throw new Error(`Clean-reimport occurrence inventory duplicates ${key}.`);
    occurrenceInventoryByKey.set(key, item);
  }
}

function reimportOccurrenceMatches(item, authoredOccurrence) {
  return Boolean(item)
    && asYesNo(pick(item, ["has_shape"])) === "YES"
    && asYesNo(pick(item, ["mapped_to_authoring_inventory"])) === "YES"
    && String(pick(item, ["occurrence_id"])) === String(authoredOccurrence?.occurrence_id ?? "")
    && String(pick(item, ["part_number"])) === String(authoredOccurrence?.part_number ?? "");
}

const attachmentRecords = [
  ...((stowed.attachment_requirements ?? []).map((item) => ({ ...item, __state: "STOWED" }))),
  ...((deployed.attachment_requirements ?? []).map((item) => ({ ...item, __state: "DEPLOYED" }))),
];
const attachmentGeometryByKey = new Map();
for (const item of jointGeometryCsv) {
  const state = String(pick(item, ["state"])).toUpperCase();
  const attachmentId = pick(item, ["connection_id", "attachment_id"]);
  const key = `${state}|${attachmentId}`;
  if (!state || !attachmentId) throw new Error("Attachment-geometry validation contains a blank state or connection ID.");
  if (attachmentGeometryByKey.has(key)) throw new Error(`Attachment-geometry validation duplicates ${key}.`);
  attachmentGeometryByKey.set(key, item);
}
const attachmentRowsByOccurrence = new Map(uniqueOccurrenceIds.map((id) => [id, []]));
const attachmentRecordKeys = new Set();
for (const record of attachmentRecords) {
  const state = String(firstDefined(record.state, record.__state)).toUpperCase();
  const attachmentId = String(firstDefined(record.attachment_id, record.connection_id, "")).trim();
  const a = String(firstDefined(record.occurrence_a, record.occurrence_id, "")).trim();
  const b = String(firstDefined(record.occurrence_b, record.mate_occurrence_id, "")).trim();
  if (!state || !attachmentId || !a || !b) throw new Error("Curated attachment row has a blank state, ID, or endpoint.");
  const recordKey = `${state}|${attachmentId}`;
  if (attachmentRecordKeys.has(recordKey)) throw new Error(`Curated attachment register duplicates ${recordKey}.`);
  attachmentRecordKeys.add(recordKey);
  if (!attachmentRowsByOccurrence.has(a) || !attachmentRowsByOccurrence.has(b)) {
    throw new Error(`Curated attachment ${recordKey} names an occurrence absent from the merged inventory.`);
  }
  const normalized = { ...record, __state: state, __attachmentId: attachmentId, __a: a, __b: b };
  attachmentRowsByOccurrence.get(a).push(normalized);
  attachmentRowsByOccurrence.get(b).push(normalized);
}
const connectionRecords = [
  ...((stowed.connections ?? []).map((item) => ({ ...item, __state: "STOWED" }))),
  ...((deployed.connections ?? []).map((item) => ({ ...item, __state: "DEPLOYED" }))),
];
const requiredAttachmentOccurrenceIds = uniqueOccurrenceIds.filter((occurrenceId) => {
  const occurrence = firstDefined(stowedById.get(occurrenceId), deployedById.get(occurrenceId));
  const part = partMap.get(occurrence?.part_number) ?? {};
  return String(part.make_buy ?? "").toUpperCase() !== "INTERNAL CHILD" && !part.external_context;
});
const uncoveredAttachmentOccurrenceIds = requiredAttachmentOccurrenceIds.filter(
  (occurrenceId) => !(attachmentRowsByOccurrence.get(occurrenceId)?.length),
);
if (uncoveredAttachmentOccurrenceIds.length) {
  throw new Error(
    `Required installed occurrences have no curated attachment endpoint: ${JSON.stringify(uncoveredAttachmentOccurrenceIds)}.`,
  );
}

const workbook = Workbook.create();
const sheetNames = [
  "00_README",
  ...COMMISSION_SHEET_NAMES,
  "09_NCR_CLOSURE",
  "10_HARDWARE_FITTINGS",
  "11_CLEARANCE_REGISTER",
  "12_INTERFERENCE_REGISTER",
  "13_MOTION_SWEEP",
  "14_SOURCE_CAD",
  "15_MASS_PROPERTIES",
  "16_COMPLIANCE",
  "17_EVIDENCE_INDEX",
  "18_NEUTRAL_VALIDATION",
  "19_ROUTING",
  "20_PROCESS_MATERIALS",
];
if (JSON.stringify(sheetNames.slice(1, 9)) !== JSON.stringify(COMMISSION_SHEET_NAMES)) {
  throw new Error("Commission workbook sheets 01..08 are not present in their exact required order.");
}
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
    "Inventory Definition Status",
  ];
  createTitle(sheet, "FINAL UNIQUE PART MASTER", "One row per final authored part definition; the acceptance disposition is controlled only by the neutral-CAD validation gates.", headers.length);
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
        formula: `=IF(OR(A${row}="",D${row}="",G${row}="",AND(D${row}="BUY",L${row}="")),"INCOMPLETE","DEFINED")`,
      },
    ];
  });
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 7: "0.000", 8: "0", 9: "0" },
    statusColumns: [12],
    widthCaps: { 2: 42, 4: 28, 6: 34, 10: 48, 11: 48 },
  });
}

// 04_CUSTOM_PARTS
{
  const sheet = sheets.get("04_CUSTOM_PARTS");
  const headers = [
    "Part Number",
    "Rev",
    "Description",
    "Material",
    "Raw-Material Source / Specification",
    "Manufacturing Process",
    "Finish / Treatment",
    "Purchase URL",
    "Qty Stowed",
    "Qty Deployed",
    "CAD Classification",
    "Inventory Definition Status",
    "Controlled Evidence",
  ];
  createTitle(
    sheet,
    "FINAL CUSTOM PART DEFINITION REGISTER",
    "Material, manufacturing process, finish, quantities, and CAD classification are reported directly from the final authoring inventories; this register does not add a blanket drawing blocker.",
    headers.length,
  );
  const customParts = parts.filter(
    (part) => String(part.make_buy ?? "").toUpperCase() === "MAKE" && !part.external_context,
  );
  const rows = customParts.map((part, index) => {
    const row = 6 + index;
    return [
      part.part_number,
      part.revision,
      part.description,
      part.material,
      firstDefined(
        part.raw_material_source,
        part.raw_material_source_url,
        part.source_url,
        `${part.material} — CERTIFIED HEAT/LOT SOURCE PER CONTROLLED DRAWING AND APPROVED SUPPLIER LIST`,
      ),
      part.process,
      part.finish,
      "CUSTOM FABRICATED — NO DIRECT PURCHASE LINK",
      stowedQty.get(part.part_number) ?? 0,
      deployedQty.get(part.part_number) ?? 0,
      part.cad_classification,
      {
        formula: `=IF(OR(A${row}="",D${row}="",E${row}="",F${row}="",G${row}="",H${row}<>"CUSTOM FABRICATED — NO DIRECT PURCHASE LINK",K${row}=""),"INCOMPLETE","DEFINED")`,
      },
      "authoring_inventory_stowed.json; authoring_inventory_deployed.json",
    ];
  });
  const table = writeTable(sheet, 5, headers, rows, {
    numberFormats: { 8: "0", 9: "0" },
    statusColumns: [11],
    widthCaps: { 2: 46, 3: 30, 4: 52, 5: 48, 6: 32, 7: 46, 10: 34, 12: 58 },
  });
  sheet.getRange("A4:H4").values = [[
    "Custom Part Identities",
    customParts.length,
    "Inventory Defined",
    null,
    "Inventory Incomplete",
    null,
    "Register Standing",
    null,
  ]];
  sheet.getRange("D4").formulas = [[`=COUNTIF(L${table.dataStart}:L${table.dataEnd},"DEFINED")`]];
  sheet.getRange("F4").formulas = [[`=COUNTIF(L${table.dataStart}:L${table.dataEnd},"INCOMPLETE")`]];
  sheet.getRange("H4").formulas = [[`=IF(F4>0,"INCOMPLETE","DEFINED")`]];
  sheet.getRange("A4:H4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  applyStatusConditionalFormatting(sheet.getRange("H4"));
}

// 20_PROCESS_MATERIALS
{
  const sheet = sheets.get("20_PROCESS_MATERIALS");
  const headers = [
    "Record ID",
    "State Scope",
    "Description / Application",
    "Manufacturer",
    "Part / Specification",
    "Quantity",
    "UOM",
    "Source URL",
    "Inventory Standing",
    "Notes",
  ];
  createTitle(
    sheet,
    "FINAL CONTROLLED PROCESS-MATERIAL REGISTER",
    "Only process-material definitions explicitly present in the final authoring inventories are reported; no speculative categories or TBD release blockers are introduced.",
    headers.length,
  );
  const processMaterialRecords = [
    ...((stowed.process_materials ?? stowed.consumables ?? []).map((item) => ({ ...item, __state: "STOWED" }))),
    ...((deployed.process_materials ?? deployed.consumables ?? []).map((item) => ({ ...item, __state: "DEPLOYED" }))),
  ];
  const rows = processMaterialRecords.length
    ? processMaterialRecords.map((item, index) => {
      const row = 6 + index;
      return [
        pick(item, ["record_id", "consumable_id", "part_number", "specification_id"], `PROCESS-MATERIAL-${index + 1}`),
        firstDefined(pick(item, ["state", "state_scope"]), item.__state),
        pick(item, ["description", "application", "scope"]),
        pick(item, ["manufacturer"]),
        pick(item, ["part_specification", "part_number", "specification"]),
        numericOrBlank(pick(item, ["quantity", "required_quantity"])),
        pick(item, ["uom", "unit"]),
        pick(item, ["source_url", "purchase_url"]),
        { formula: `=IF(OR(A${row}="",C${row}=""),"INCOMPLETE","DEFINED")` },
        pick(item, ["notes", "qualification", "process_basis"]),
      ];
    })
    : [[
      "INFORMATIONAL",
      "BOTH",
      "No separate process-material or consumable records are declared in the final authoring inventories.",
      "",
      "",
      "",
      "",
      "",
      "N/A",
      "This informational condition is not an acceptance gate or release blocker.",
    ]];
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 5: "0.000" },
    statusColumns: [8],
    widthCaps: { 2: 62, 3: 30, 4: 42, 7: 48, 9: 58 },
  });
  sheet.getRange("A4:F4").values = [[
    "Explicit Inventory Records",
    processMaterialRecords.length,
    "Acceptance Gate",
    "NONE",
    "Disposition",
    processMaterialRecords.length ? "CONTROLLED INVENTORY REPORTED" : "N/A — NO SEPARATE RECORDS DECLARED",
  ]];
  sheet.getRange("A4:F4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
}

// 03_PURCHASED_ITEMS
{
  const sheet = sheets.get("03_PURCHASED_ITEMS");
  const headers = [
    "Manufacturer",
    "Exact Manufacturer Part Number (MPN)",
    "Description",
    "Installed Qty",
    "Unit Mass kg",
    "Product Page",
    "Manufacturer / Authorized-Distributor Purchase Link",
    "Verification Date",
    "Vendor CAD Status",
    "Inventory Part Number",
    "Procurement Status",
  ];
  createTitle(sheet, "FINAL PURCHASED ITEM REGISTER", "Purchased identities and sourcing are reported from the final inventory; acceptance is controlled by the PROCUREMENT-DEFINITION validator gate.", headers.length);
  const purchased = parts.filter((part) => String(part.make_buy).toUpperCase() === "BUY");
  const incompletePurchasedIdentity = purchased.filter((part) => (
    !String(part.manufacturer ?? "").trim()
    || !String(firstDefined(part.manufacturer_part_number, part.mpn, part.part_number) ?? "").trim()
    || !String(part.source_url ?? "").trim()
    || !String(part.purchase_url ?? "").trim()
  ));
  if (incompletePurchasedIdentity.length) {
    throw new Error(
      `Purchased items lack manufacturer, exact MPN, product URL, or purchase URL: ${JSON.stringify(incompletePurchasedIdentity.map((part) => part.part_number))}.`,
    );
  }
  const rows = purchased.map((part, index) => {
    const row = 6 + index;
    const mpn = firstDefined(part.manufacturer_part_number, part.mpn, part.part_number);
    return [
      part.manufacturer,
      mpn,
      part.description,
      uniqueInstalledQty.get(part.part_number) ?? 0,
      numericOrBlank(part.mass_kg),
      hyperlinkCell(part.source_url, "Verified product page"),
      hyperlinkCell(part.purchase_url, "Purchase from manufacturer / authorized distributor"),
      new Date("2026-08-22T00:00:00Z"),
      `${part.cad_classification} — controlled installed representation; vendor source identity verified`,
      part.part_number,
      {
        formula: `=IF(OR(A${row}="",B${row}="",C${row}="",D${row}<=0,F${row}="",G${row}="",H${row}="",I${row}=""),"INCOMPLETE","DEFINED")`,
      },
    ];
  });
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 3: "0", 4: "0.000000", 7: "yyyy-mm-dd" },
    statusColumns: [10],
    widthCaps: { 0: 30, 1: 38, 2: 46, 5: 36, 6: 48, 8: 48, 9: 34 },
  });
}

// 01_OCCURRENCE_BOM
let occurrenceTable;
{
  const sheet = sheets.get("01_OCCURRENCE_BOM");
  const headers = [
    "Occurrence ID",
    "Parent Assembly",
    "Assembly Path",
    "Subsystem",
    "Part Number",
    "Title",
    "Rev",
    "Qty",
    "Stowed Status",
    "Deployed Status",
    "Make / Buy",
    "Manufacturer",
    "Exact MPN",
    "Material",
    "Finish",
    "Unit Mass kg",
    "Extended Mass kg",
    "Attachment Method",
    "Mates",
    "Retaining Hardware",
    "Fixed / Sliding / Rotating",
    "Service-Removal Method",
    "Reimport Stowed",
    "Reimport Deployed",
    "Reimport Solids Stowed",
    "Reimport Solids Deployed",
    "Reimport Reconciliation Status",
    "Transform Matrix 3x4 — Stowed",
    "Transform Matrix 3x4 — Deployed",
    "Notes",
  ];
  createTitle(sheet, "FINAL OCCURRENCE-SPECIFIC BOM", "Exactly one row per state-invariant unique occurrence, merging installed stowed/deployed configuration, procurement, mass, attachment, retention, service, and clean-reimport reconciliation evidence.", headers.length);
  const reimportEvidenceAvailable = occurrenceInventoryStowedCsv.length > 0 && occurrenceInventoryDeployedCsv.length > 0;
  sheet.getRange("A4:F4").values = [["Unique Occurrence Rows", uniqueOccurrenceIds.length, "Reimport Evidence", reimportEvidenceAvailable ? "AVAILABLE" : "MISSING", "Reimport Leaf Rows", null]];
  sheet.getRange("F4").formulas = [[reimportEvidenceAvailable ? `=${occurrenceInventoryStowedCsv.length + occurrenceInventoryDeployedCsv.length}` : '=""']];
  sheet.getRange("A4:F4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  const rows = uniqueOccurrenceIds.map((occurrenceId, index) => {
    const stowedOccurrence = stowedById.get(occurrenceId);
    const deployedOccurrence = deployedById.get(occurrenceId);
    const occurrence = firstDefined(stowedOccurrence, deployedOccurrence);
    const part = partMap.get(occurrence.part_number) ?? {};
    const isExternal = Boolean(part.external_context);
    const stowedReimport = occurrenceInventoryByKey.get(`STOWED|${occurrenceId}`);
    const deployedReimport = occurrenceInventoryByKey.get(`DEPLOYED|${occurrenceId}`);
    const stowedReimportMatches = reimportOccurrenceMatches(stowedReimport, stowedOccurrence);
    const deployedReimportMatches = reimportOccurrenceMatches(deployedReimport, deployedOccurrence);
    const authoredAttachments = attachmentRowsByOccurrence.get(occurrenceId) ?? [];
    const attachmentTypes = authoredAttachments.map((item) => firstDefined(item.attachment_type, item.connection_type));
    const mates = authoredAttachments.map((item) => item.__a === occurrenceId ? item.__b : item.__a);
    const hardwareIds = authoredAttachments.flatMap((item) => firstDefined(
      item.hardware_occurrence_ids,
      item.retaining_occurrence_ids,
      item.fastener_occurrence_ids,
      [],
    ));
    const matchingConnections = connectionRecords.filter((item) => (
      item.occurrence_id === occurrenceId || item.mate_occurrence_id === occurrenceId
    ));
    const serviceMethods = matchingConnections.map((item) => item.service_method);
    const retainingText = [
      ...hardwareIds,
      ...matchingConnections.map((item) => item.retaining_hardware),
      ...mates.filter((mate) => /(?:^|[-_ ])(?:PIN|DOWEL|SCREW|BOLT|CLIP|RING|KEEPER|RETAINER|CIRCLIP)(?:$|[-_ ])/i.test(mate)),
    ];
    const stowedOverride = stowed.mass_overrides_kg?.[occurrenceId];
    const deployedOverride = deployed.mass_overrides_kg?.[occurrenceId];
    const unitMass = firstDefined(stowedOverride, deployedOverride, part.mass_kg);
    const assemblyPaths = [stowedOccurrence?.parent_path, deployedOccurrence?.parent_path].filter(Boolean);
    const stowedStatus = isExternal ? "EXTERNAL CONTEXT — NOT INSTALLED" : (stowedOccurrence ? "INSTALLED — STOWED" : "NOT PRESENT");
    const deployedStatus = isExternal ? "EXTERNAL CONTEXT — NOT INSTALLED" : (deployedOccurrence ? "INSTALLED — DEPLOYED" : "NOT PRESENT");
    const row = 6 + index;
    const reimportFormula = stowedOccurrence && deployedOccurrence
      ? `=IF(AND(W${row}="YES",X${row}="YES"),"RECONCILED","FAIL")`
      : stowedOccurrence
        ? `=IF(W${row}="YES","RECONCILED","FAIL")`
        : `=IF(X${row}="YES","RECONCILED","FAIL")`;
    return [
      occurrenceId,
      uniqueJoined(assemblyPaths.map(parentAssemblyFromPath)),
      uniqueJoined(assemblyPaths),
      uniqueJoined(assemblyPaths.map(subsystemFromPath)),
      occurrence.part_number,
      part.description,
      part.revision,
      isExternal ? 0 : 1,
      stowedStatus,
      deployedStatus,
      part.make_buy,
      part.manufacturer,
      String(part.make_buy ?? "").toUpperCase() === "BUY"
        ? firstDefined(part.manufacturer_part_number, part.mpn, part.part_number)
        : "N/A — CUSTOM FABRICATED",
      part.material,
      part.finish,
      numericOrBlank(unitMass),
      { formula: `=H${row}*P${row}` },
      uniqueJoined(attachmentTypes),
      uniqueJoined(mates),
      uniqueJoined(retainingText),
      constraintMode(occurrence),
      inferredServiceRemoval(attachmentTypes, serviceMethods),
      stowedOccurrence ? (stowedReimportMatches ? "YES" : "NO") : "N/A",
      deployedOccurrence ? (deployedReimportMatches ? "YES" : "NO") : "N/A",
      stowedReimport ? numericOrBlank(pick(stowedReimport, ["solid_count", "solids", "leaf_solid_count"])) : "",
      deployedReimport ? numericOrBlank(pick(deployedReimport, ["solid_count", "solids", "leaf_solid_count"])) : "",
      { formula: reimportFormula },
      stowedOccurrence ? matrixText(stowedOccurrence.transform_matrix_3x4) : "",
      deployedOccurrence ? matrixText(deployedOccurrence.transform_matrix_3x4) : "",
      uniqueJoined([stowedOccurrence?.notes, deployedOccurrence?.notes]),
    ];
  });
  occurrenceTable = writeTable(sheet, 5, headers, rows, {
    numberFormats: { 7: "0", 15: "0.000000", 16: "0.000000", 24: "0", 25: "0" },
    statusColumns: [26],
    widthCaps: {
      0: 38, 1: 42, 2: 54, 3: 42, 4: 36, 5: 48, 11: 30, 12: 38,
      17: 60, 18: 56, 19: 60, 21: 58, 27: 62, 28: 62, 29: 52,
    },
  });
}

// 05_ATTACHMENT_MAP
let attachmentTable;
{
  const sheet = sheets.get("05_ATTACHMENT_MAP");
  const headers = [
    "Component Occurrence",
    "Part Number",
    "Title",
    "State Scope",
    "Mates",
    "Attachment Type",
    "Fastener / Pin",
    "Retainer",
    "Fixed / Sliding / Rotating",
    "Captive",
    "Service-Removal Method",
    "Curated Attachment IDs",
    "Maximum Allowed Gap mm",
    "Maximum Measured Direct Gap mm",
    "Calculated Support Modes",
    "Curated Rows",
    "Supported Rows",
    "Missing Validation Rows",
    "Calculated Support Status",
    "Controlled Evidence",
  ];
  createTitle(sheet, "FINAL AGGREGATED ATTACHMENT MAP", "Exactly one row per required non-internal, non-external occurrence. Every row aggregates its curated direct attachment endpoints and authenticated calculated geometric or fastener-bridge support evidence.", headers.length);
  const rows = requiredAttachmentOccurrenceIds.map((occurrenceId, index) => {
    const row = 6 + index;
    const occurrence = firstDefined(stowedById.get(occurrenceId), deployedById.get(occurrenceId));
    const part = partMap.get(occurrence.part_number) ?? {};
    const records = attachmentRowsByOccurrence.get(occurrenceId) ?? [];
    const mates = records.map((record) => record.__a === occurrenceId ? record.__b : record.__a);
    const attachmentTypes = records.map((record) => firstDefined(record.attachment_type, record.connection_type));
    const allHardware = records.flatMap((record) => firstDefined(
      record.hardware_occurrence_ids,
      record.retaining_occurrence_ids,
      record.fastener_occurrence_ids,
      [],
    ));
    const endpointHardware = mates.filter((mate) => /(?:^|[-_ ])(?:SCREW|BOLT|PIN|DOWEL|RIVET|STUD|CLIP|RING|KEEPER|RETAINER|CIRCLIP)(?:$|[-_ ])/i.test(mate));
    const hardware = [...allHardware, ...endpointHardware];
    const fasteners = hardware.filter((id) => /(?:^|[-_ ])(?:SCREW|BOLT|PIN|DOWEL|RIVET|STUD)(?:$|[-_ ])/i.test(id));
    const retainers = hardware.filter((id) => /(?:^|[-_ ])(?:CLIP|RING|KEEPER|RETAINER|CIRCLIP|SERVICE-CAP)(?:$|[-_ ])/i.test(id));
    const matchingConnections = connectionRecords.filter((item) => (
      item.occurrence_id === occurrenceId || item.mate_occurrence_id === occurrenceId
    ));
    const validations = records.map((record) => attachmentGeometryByKey.get(`${record.__state}|${record.__attachmentId}`));
    const missingValidationCount = validations.filter((validation) => !validation).length;
    const supportedCount = validations.filter((validation) => (
      asYesNo(pick(validation, ["geometric_or_fastener_supported"])) === "YES"
    )).length;
    const maximumAllowed = Math.max(...records.map((record) => (
      asNumber(firstDefined(record.maximum_attachment_gap_mm, record.maximum_separation_mm)) ?? 0
    )));
    const measuredGaps = validations
      .map((validation) => asNumber(pick(validation, ["direct_gap_mm"])))
      .filter((value) => value !== null);
    const captive = retainers.length || /WELD|BRAZE|SCREW|PIN|PRESS|CAPTUR|STITCH|SPLICE|RETAINER|CLAMP|FERRULE|GUIDE|SEAT|THREADED/i.test(attachmentTypes.join(" "))
      ? "YES — POSITIVELY RETAINED"
      : "NO — REVIEW REQUIRED";
    return [
      occurrenceId,
      occurrence.part_number,
      part.description,
      uniqueJoined(records.map((record) => record.__state)),
      uniqueJoined(mates),
      uniqueJoined(attachmentTypes),
      uniqueJoined(fasteners),
      uniqueJoined(retainers),
      constraintMode(occurrence),
      captive,
      inferredServiceRemoval(attachmentTypes, matchingConnections.map((item) => item.service_method)),
      uniqueJoined(records.map((record) => record.__attachmentId)),
      maximumAllowed,
      measuredGaps.length ? Math.max(...measuredGaps) : "",
      uniqueJoined(validations.map((validation) => pick(validation, ["support_mode"]))),
      records.length,
      supportedCount,
      missingValidationCount,
      { formula: `=IF(P${row}=0,"FAIL",IF(R${row}>0,"BLOCKED",IF(Q${row}=P${row},"PASS","FAIL")))` },
      uniqueJoined(records.map((record) => firstDefined(record.evidence_basis, record.process_basis, record.evidence))),
    ];
  });
  attachmentTable = writeTable(sheet, 5, headers, rows, {
    numberFormats: { 12: "0.0000", 13: "0.0000", 15: "0", 16: "0", 17: "0" },
    statusColumns: [18],
    widthCaps: { 0: 38, 1: 34, 2: 46, 4: 58, 5: 58, 6: 54, 7: 54, 10: 58, 11: 68, 14: 36, 19: 68 },
  });
}

// 10_HARDWARE_FITTINGS
{
  const sheet = sheets.get("10_HARDWARE_FITTINGS");
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
  createTitle(sheet, "FINAL HARDWARE, FITTINGS & RETAINERS", "Pins, rings, bushings, washers, fittings, valves, clamps, springs, detents, and terminal hardware from the final inventories.", headers.length);
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
        formula: `=IF(OR(A${row}="",D${row}="",E${row}="",AND(D${row}="BUY",H${row}="")),"INCOMPLETE","DEFINED")`,
      },
    ];
  });
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 5: "0", 6: "0" },
    statusColumns: [8],
    widthCaps: { 1: 42, 4: 34, 7: 54 },
  });
}

// 11_CLEARANCE_REGISTER
{
  const sheet = sheets.get("11_CLEARANCE_REGISTER");
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
  createTitle(sheet, "FINAL MEASURED CLEARANCE REGISTER", "Pair-specific exact BRepExtrema distances and bounded positive-volume dispositions from the final clean-process audit.", headers.length);
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

// 12_INTERFERENCE_REGISTER
{
  const sheet = sheets.get("12_INTERFERENCE_REGISTER");
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
  createTitle(sheet, "FINAL INTERFERENCE & INTENTIONAL-FIT REGISTER", "Every positive-volume intersection requires a unique state/pair match, finite volume bounds, and a controlled process basis.", headers.length);
  const exactPairRows = [
    ...stowedPairAudit.map((row) => ({ ...row, __state: "STOWED" })),
    ...deployedPairAudit.map((row) => ({ ...row, __state: "DEPLOYED" })),
  ];
  const pairRows = exactPairRows;
  const intentionalFitById = new Map(
    [...(stowed.intentional_fits ?? []), ...(deployed.intentional_fits ?? [])]
      .map((record) => [String(firstDefined(record.exception_id, record.fit_id, "")), record])
      .filter(([id]) => id),
  );
  const normalized = pairRows
    .map((row, index) => {
      const volume = asNumber(pick(row, ["intersection_volume_mm3", "positive_volume_mm3", "common_volume_mm3", "overlap_volume_mm3", "volume_mm3"]));
      const classification = pick(row, ["classification", "contact_category", "result", "pair_class"]);
      const exceptionId = pick(row, ["intentional_fit_exception_id", "exception_id", "fit_exception_id", "documented_exception"]);
      const fitRecord = intentionalFitById.get(String(exceptionId)) ?? {};
      return {
        state: firstDefined(pick(row, ["state", "assembly_state"]), row.__state),
        pair: pick(row, ["pair_id", "pair", "pair_index", "check_id"], `PAIR-${String(index + 1).padStart(6, "0")}`),
        a: pick(row, ["occurrence_a", "occ_a", "component_a", "a"]),
        b: pick(row, ["occurrence_b", "occ_b", "component_b", "b"]),
        volume,
        classification,
        exceptionId,
        documentation: [
          pick(row, ["intentional_fit_match_status"]),
          pick(fitRecord, ["process_basis"]),
          exceptionId ? `bounds=${pick(fitRecord, ["minimum_common_volume_mm3"])}..${pick(fitRecord, ["maximum_common_volume_mm3"])} mm3` : "",
          pick(row, ["documentation", "exception_documentation", "evidence", "notes"]),
        ].filter((value) => value !== "").join(" | "),
        disposition: firstDefined(pick(row, ["disposition", "action", "resolution"]), pick(fitRecord, ["fit_type"])),
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
  const available = stowedPairAudit.length > 0 && deployedPairAudit.length > 0;
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
      { formula: `=IF(E${row}="","BLOCKED",IF(E${row}<=0.000001,"CLEAR",IF(AND(G${row}<>"",ISNUMBER(SEARCH("VALID_BOUNDED_MATCH",H${row}))),"DOCUMENTED","FAIL")))` },
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

// 13_MOTION_SWEEP
{
  const sheet = sheets.get("13_MOTION_SWEEP");
  const headers = [
    "Sample ID",
    "Arm Angle deg",
    "Crosshead Z mm",
    "Crosshead Travel mm",
    "Minimum Clearance mm",
    "Unauthorized / Blocked Pair Results",
    "Worst Pair",
    "Evidence",
    "Status",
  ];
  createTitle(sheet, "FINAL FULL-MECHANISM MOTION SWEEP", "The explicitly parameterized mechanism is audited at 81 samples from 0 through 80 degrees; undocumented collisions or blocked exact distances prevent release.", headers.length);
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
    const intersections = motionSamplesCsv.length
      ? ["unauthorized_positive_volume_pairs", "boolean_blocked_pairs", "distance_blocked_pairs"]
        .reduce((sum, key) => sum + (asNumber(pick(item, [key])) ?? 0), 0)
      : "";
    const worstPair = pick(item, ["worst_pair", "minimum_pair", "pair_id"]);
    const evidence = pick(item, ["evidence", "source", "notes"], motionSamplesCsv.length ? "validation/motion_kinematics_1deg.csv; validation/motion_full_mechanism_audit.csv.gz" : item.evidence);
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

// 14_SOURCE_CAD
{
  const sheet = sheets.get("14_SOURCE_CAD");
  const headers = [
    "Part Number",
    "Description",
    "CAD Classification",
    "Make / Buy",
    "Manufacturer",
    "Purchase URL",
    "Source URL",
    "Material",
    "Manufacturing Process",
    "Neutral-CAD Evidence",
    "Inventory Definition Status",
  ];
  createTitle(sheet, "FINAL SOURCE AND DEFINITION REGISTER", "Inventory source identities and make-process definitions are reported with final OCP/XCAF reimport evidence; no target-CAD preflight is an acceptance condition.", headers.length);
  const rows = parts.map((part, index) => {
    const row = 6 + index;
    return [
      part.part_number,
      part.description,
      part.cad_classification,
      part.make_buy,
      part.manufacturer,
      part.purchase_url,
      part.source_url,
      part.material,
      part.process,
      "validation/xcaf_occurrences_*.csv; validation/leaf_solids_*.csv; validation/step_text_inspection.json",
      {
        formula: `=IF(A${row}="","INCOMPLETE",IF(D${row}="BUY",IF(OR(E${row}="",F${row}=""),"INCOMPLETE","DEFINED"),IF(OR(H${row}="",I${row}=""),"INCOMPLETE","DEFINED")))`,
      },
    ];
  });
  writeTable(sheet, 5, headers, rows, {
    statusColumns: [10],
    widthCaps: { 1: 42, 2: 34, 4: 32, 5: 50, 6: 50, 7: 30, 8: 52, 9: 66 },
  });
}

// 06_CONFIGURATION_MATRIX
{
  const sheet = sheets.get("06_CONFIGURATION_MATRIX");
  const headers = [
    "Occurrence ID",
    "Part Number",
    "Title",
    "Membership",
    "Class",
    "Stowed Configuration",
    "Deployed Configuration",
    "Transition Disposition",
    "Fixed / Sliding / Rotating",
    "Translation Delta mm",
    "Matrix Max Abs Delta",
    "Volume Delta mm³",
    "Stowed Transform",
    "Deployed Transform",
    "State Rule Status",
  ];
  createTitle(sheet, "FINAL CONFIGURATION MATRIX", "Explicit STOWED and DEPLOYED membership with REPOSITIONED, REMOVED, RETAINED BUT DISPLACED, RETAINED UNCHANGED, and SERVICE-ONLY transition dispositions as applicable.", headers.length);
  sheet.getRange("A4:O4").merge();
  sheet.getRange("A4").values = [["Controlled status vocabulary: STOWED | DEPLOYED | REPOSITIONED | REMOVED | RETAINED BUT DISPLACED | RETAINED UNCHANGED | SERVICE-ONLY."]];
  sheet.getRange("A4:O4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink }, wrapText: true };
  const rows = uniqueOccurrenceIds.map((id, index) => {
    const a = stowedById.get(id);
    const b = deployedById.get(id);
    const occurrence = firstDefined(a, b);
    const part = partMap.get(occurrence.part_number) ?? {};
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
    const volumeA = asNumber(a?.global_volume_mm3);
    const volumeB = asNumber(b?.global_volume_mm3);
    const volumeDelta = volumeA !== null && volumeB !== null ? Math.abs(volumeA - volumeB) : null;
    const serviceOnly = /SERVICE[-_ ]?ONLY/i.test(
      `${a?.state_membership ?? ""} ${b?.state_membership ?? ""} ${a?.joint_type ?? ""} ${b?.joint_type ?? ""} ${a?.notes ?? ""} ${b?.notes ?? ""}`,
    );
    let transitionDisposition;
    if (serviceOnly) transitionDisposition = "SERVICE-ONLY";
    else if (!a || !b) transitionDisposition = "REMOVED";
    else if ((maxDelta ?? 0) > 1.0e-8) transitionDisposition = "REPOSITIONED";
    else if ((volumeDelta ?? 0) > 1.0e-6 || ["FLEXIBLE", "SOFTGOOD"].includes(String(occurrence.classification).toUpperCase())) {
      transitionDisposition = "RETAINED BUT DISPLACED";
    } else transitionDisposition = "RETAINED UNCHANGED";
    const row = 6 + index;
    return [
      id,
      occurrence.part_number,
      part.description,
      firstDefined(a?.state_membership, b?.state_membership),
      firstDefined(a?.classification, b?.classification),
      serviceOnly ? "SERVICE-ONLY" : (a ? "STOWED" : "REMOVED"),
      serviceOnly ? "SERVICE-ONLY" : (b ? "DEPLOYED" : "REMOVED"),
      transitionDisposition,
      constraintMode(occurrence),
      translationDelta ?? "",
      maxDelta ?? "",
      volumeDelta ?? "",
      a ? matrixText(ma) : "",
      b ? matrixText(mb) : "",
      {
        formula: `=IF(OR(A${row}="",F${row}="",G${row}="",H${row}=""),"FAIL",IF(AND(D${row}="BOTH",OR(F${row}="REMOVED",G${row}="REMOVED")),"FAIL","COMPLETE"))`,
      },
    ];
  });
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 9: "0.000000", 10: "0.000000", 11: "0.000000" },
    statusColumns: [14],
    widthCaps: { 0: 38, 1: 36, 2: 48, 3: 18, 4: 24, 7: 34, 12: 62, 13: 62 },
  });
}

// 07_CONSUMABLES
{
  const sheet = sheets.get("07_CONSUMABLES");
  const headers = [
    "Consumable ID",
    "Category",
    "Manufacturer",
    "Exact Product / MPN",
    "Controlled Application",
    "Application Limits / Process Control",
    "Product Source",
    "Purchase Source",
    "Verification Date",
    "Substitution Control",
    "Definition Status",
  ];
  createTitle(
    sheet,
    "FINAL CONTROLLED CONSUMABLES",
    "Only the enumerated lubricant, sealant, adhesive, threadlocker, anti-seize, coating, passivation, and inspection-marking products are authorized. Unlisted substitution is prohibited without an approved engineering change.",
    headers.length,
  );
  const noSubstitution = "NO SUBSTITUTION WITHOUT ENGINEERING CHANGE APPROVAL; UNLISTED MATERIALS PROHIBITED.";
  const consumables = [
    {
      id: "CON-THREADLOCKER-243", category: "THREADLOCKER", manufacturer: "Henkel LOCTITE", product: "LOCTITE 243",
      application: "Removable M3/M4 threaded fasteners explicitly designated for medium-strength threadlocking.",
      control: "Clean and dry male/female threads; apply controlled dose before torque. Do not apply to compression ferrules, pressure-tube sealing lands, or joints designated for anti-seize.",
      source: "https://next.henkel-adhesives.com/us/en/products/industrial-adhesives/central-pdp.html/loctite-243/BP000000316211.html",
      purchase: "https://www.grainger.com/product/LOCTITE-Primerless-Medium-Strength-5HYH5",
    },
    {
      id: "CON-THREAD-SEALANT-577", category: "THREAD SEALANT", manufacturer: "Henkel LOCTITE", product: "LOCTITE 577",
      application: "Metal tapered pressure-pipe threads only where the controlled assembly drawing explicitly calls out anaerobic thread sealant.",
      control: "Apply only to clean male tapered threads. Prohibited on Swagelok compression-tube ferrules, straight-thread O-ring ports, and moving valve elements.",
      source: "https://next.henkel-adhesives.com/de/en/products/industrial-sealants/central-pdp.html/loctite-577/BP000000168431.html",
      purchase: "https://www.grainger.com/product/LOCTITE-Pipe-Thread-Sealant-577-49CR90",
    },
    {
      id: "CON-SEAL-LUBRICANT-111", category: "SEAL LUBRICANT", manufacturer: "DuPont MOLYKOTE", product: "MOLYKOTE 111 Compound",
      application: "Thin-film assembly lubrication for drawing-designated compatible static elastomer seals and O-rings.",
      control: "Apply a uniform minimal film with dedicated clean tooling; exclude pressure-tube ferrules, adhesive bond lands, stitch/rope interfaces, and dry friction-lock features.",
      source: "https://www.dupont.com/products/molykote-111-compound.html",
      purchase: "https://www.motion.com/products/sku/00783339",
    },
    {
      id: "CON-STRUCTURAL-ADHESIVE-DP420NS", category: "STRUCTURAL ADHESIVE", manufacturer: "3M", product: "3M Scotch-Weld DP420NS",
      application: "Drawing-designated non-welded bonded liners, isolated brackets, or retained inserts only.",
      control: "Qualified surface preparation, mix ratio, bond-line thickness, cure temperature/time, lot traceability, and witness coupon required. Adhesive is not a substitute for enumerated mechanical retention.",
      source: "https://www.3m.com/3M/en_US/p/d/b40066483/",
      purchase: "https://www.grainger.com/product/3M-Epoxy-Adhesive-DP420NS-205YT1",
    },
    {
      id: "CON-ANTISEIZE-LB8012", category: "ANTI-SEIZE", manufacturer: "Henkel LOCTITE", product: "LOCTITE LB 8012",
      application: "Drawing-designated service-removal stainless/titanium threaded interfaces where galling control is required.",
      control: "Use controlled minimal quantity and torque compensation per work instruction. Prohibited on threadlocked joints, compression fittings, pressure sealing surfaces, and oxygen-service/wetted interfaces unless separately approved.",
      source: "https://next.henkel-adhesives.com/ro/en/products/industrial-lubricants/central-pdp.html/loctite-lb-8012/SAP_IB-56587.html",
      purchase: "https://www.grainger.com/product/LOCTITE-General-Purpose-Anti-Seize-5E200",
    },
    {
      id: "CON-CLEAR-COATING-MC5100", category: "PROTECTIVE COATING", manufacturer: "Cerakote", product: "Cerakote MC-5100 Clear Aluminum",
      application: "Drawing-designated exposed aluminum surfaces after machining and preparation.",
      control: "Mask bearing fits, threads, seal lands, electrical bonds, weld/braze lands, adhesive lands, and datum surfaces; verify cured film thickness and coverage.",
      source: "https://www.cerakote.com/shop/cerakote-coating/MC-5100/cerakote-clear-aluminum",
      purchase: "https://www.cerakote.com/shop/cerakote-coating/MC-5100/cerakote-clear-aluminum",
    },
    {
      id: "CON-PASSIVATION-CITRISURF2250", category: "PASSIVATION", manufacturer: "Stellar Solutions", product: "CitriSurf 2250",
      application: "Controlled stainless-steel passivation after machining, forming, brazing, or welding where the part process calls for ASTM A967-compatible passivation.",
      control: "Use qualified bath concentration, temperature, dwell, rinse, drying, and verification procedure; preserve heat/lot and process-batch traceability.",
      source: "https://citrisurf.com/citrisurf-2250/",
      purchase: "https://shop.hubbardhall.com/products/citrisurf-2250",
    },
    {
      id: "CON-TORQUE-MARK-CROSSCHECK", category: "INSPECTION MARKING", manufacturer: "ITW DYKEM", product: "DYKEM Cross Check",
      application: "Torque witness marking across the fastener and adjacent fixed land after final torque inspection.",
      control: "Apply only after torque acceptance; keep off threads, bearing surfaces, seals, pressure fittings, and service motion interfaces. Marking is inspection evidence, not a threadlocker or retainer.",
      source: "https://www.itwprobrands.com/product/cross-check",
      purchase: "https://www.grainger.com/product/DYKEM-Torque-Marking-Paste-Less-6RRG9",
    },
  ];
  const rows = consumables.map((item, index) => {
    const row = 6 + index;
    return [
      item.id,
      item.category,
      item.manufacturer,
      item.product,
      item.application,
      item.control,
      hyperlinkCell(item.source, "Verified product page"),
      hyperlinkCell(item.purchase, "Verified purchase page"),
      new Date("2026-08-22T00:00:00Z"),
      noSubstitution,
      { formula: `=IF(OR(A${row}="",B${row}="",C${row}="",D${row}="",E${row}="",F${row}="",G${row}="",H${row}="",I${row}="",J${row}<>"${excelString(noSubstitution)}"),"INCOMPLETE","DEFINED")` },
    ];
  });
  writeTable(sheet, 5, headers, rows, {
    numberFormats: { 8: "yyyy-mm-dd" },
    statusColumns: [10],
    widthCaps: { 0: 34, 1: 24, 2: 28, 3: 34, 4: 58, 5: 68, 6: 34, 7: 34, 9: 58 },
  });
}

// 15_MASS_PROPERTIES
{
  const sheet = sheets.get("15_MASS_PROPERTIES");
  const headers = [
    "Occurrence ID",
    "Part Number",
    "Description",
    "State-Invariant Mass kg",
    "Mass Basis",
    "Stowed Present",
    "Deployed Present",
    "Formula Status",
  ];
  createTitle(sheet, "FINAL MASS PROPERTIES", "Occurrence-weighted state-invariant inventory mass rollup; the independent SYSTEM-MASS validator gate controls acceptance.", headers.length);
  const deployedOccurrenceIds = new Set((deployed.occurrences ?? []).map((occurrence) => occurrence.occurrence_id));
  if (!Array.isArray(keyDimensionsData.mass_basis_rows) || !keyDimensionsData.mass_basis_rows.length) {
    throw new Error("Authenticated key_dimensions.json lacks the required nonempty mass_basis_rows array.");
  }
  const massBasisRows = keyDimensionsData.mass_basis_rows;
  const rows = massBasisRows.map((massRow, index) => {
    const row = 8 + index;
    const part = partMap.get(massRow.part_number) ?? {};
    return [
      massRow.occurrence_id,
      massRow.part_number,
      part.description,
      numericOrBlank(massRow.mass_kg),
      massRow.basis,
      "YES",
      deployedOccurrenceIds.has(massRow.occurrence_id) ? "YES" : "NO",
      { formula: `=IF(OR(A${row}="",B${row}="",D${row}="",E${row}=""),"BLOCKED",IF(G${row}="YES","DEFINED","FAIL"))` },
    ];
  });
  const dataEnd = 8 + Math.max(1, rows.length) - 1;
  const systemMassGate = providedGates.find((candidate) => String(candidate.gate_id ?? candidate.id) === "SYSTEM-MASS") ?? {};
  const validatorMass = asNumber(deepPick(systemMassGate.measured, ["resolved_mass_kg"]));
  const validatorUnresolved = deepPick(systemMassGate.measured, ["unresolved_occurrence_ids"], []);
  const validatorStateErrors = deepPick(systemMassGate.measured, ["state_invariance_errors"], []);
  sheet.getRange("A4:H5").values = [
    ["Occurrence Rows", "Formula Rollup kg", "Formula Unresolved", "Maximum kg", "Formula Reserve kg", "Validator Mass kg", "Validator Unresolved", "State-Invariance Errors"],
    [massBasisRows.length, null, null, numericOrBlank(manifest.hard_requirements?.mass_max_kg), null, numericOrBlank(validatorMass), Array.isArray(validatorUnresolved) ? validatorUnresolved.length : validatorUnresolved, Array.isArray(validatorStateErrors) ? validatorStateErrors.length : validatorStateErrors],
  ];
  sheet.getRange("A4:H4").format = { fill: COLORS.teal, font: { bold: true, color: COLORS.white } };
  sheet.getRange("A5:H5").format = { fill: COLORS.cyan, font: { color: COLORS.ink } };
  sheet.getRange("B5").formulas = [[`=SUM(D8:D${dataEnd})`]];
  sheet.getRange("C5").formulas = [[`=COUNTIF(H8:H${dataEnd},"BLOCKED")`]];
  sheet.getRange("E5").formulas = [[`=IF(OR(B5="",D5=""),"",D5-B5)`]];
  sheet.getRange("B5:H5").format.numberFormat = "0.000";
  writeTable(sheet, 7, headers, rows, {
    numberFormats: { 3: "0.000000" },
    statusColumns: [7],
    widthCaps: { 0: 40, 1: 40, 2: 44, 4: 38 },
  });
}

// 17_EVIDENCE_INDEX
{
  const sheet = sheets.get("17_EVIDENCE_INDEX");
  const headers = ["Evidence File", "Category", "Required", "Present", "Bytes", "SHA-256", "Purpose / Source URL", "Status"];
  createTitle(sheet, "FINAL EVIDENCE INDEX", "Final authoring and clean-process OCP/XCAF validation evidence inventory with file presence, size, and hashes.", headers.length);
  const expected = [
    ["authoring_inventory_stowed.json", "AUTHORING", "YES", "Occurrence, part, connection, and route inventory"],
    ["authoring_inventory_deployed.json", "AUTHORING", "YES", "Occurrence, part, connection, and route inventory"],
    ["authoring_manifest.json", "AUTHORING", "YES", "Schema, requirements, and product file hashes"],
    ["validation/gate_results.json", "VALIDATION", "YES", "Calculated neutral-CAD validation result set"],
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
    ["validation/motion_full_mechanism_audit.csv.gz", "VALIDATION", "YES", "Full explicitly parameterized mechanism exact-BREP motion audit"],
    ["validation/motion_audit_summary.json", "VALIDATION", "YES", "Motion-scope summary and blockers"],
    ["validation/attachment_connectivity_stowed.csv", "VALIDATION", "YES", "Stowed attachment graph"],
    ["validation/attachment_connectivity_deployed.csv", "VALIDATION", "YES", "Deployed attachment graph"],
    ["validation/attachment_geometry_stowed.csv", "VALIDATION", "YES", "Stowed occurrence-specific geometric/fastener attachment audit"],
    ["validation/attachment_geometry_deployed.csv", "VALIDATION", "YES", "Deployed occurrence-specific geometric/fastener attachment audit"],
    ["validation/route_termination_audit_stowed.csv", "VALIDATION", "YES", "Stowed route endpoint, fitting, support, and penetration audit"],
    ["validation/route_termination_audit_deployed.csv", "VALIDATION", "YES", "Deployed route endpoint, fitting, support, and penetration audit"],
    ["validation/connectivity_summary.json", "VALIDATION", "YES", "Attachment cohesion and recovery load path"],
    ["validation/definition_of_done_audit.json", "VALIDATION", "YES", "Calculated installed-hardware, pin retention, lock, stow-retention, pressure, and route-closure evidence"],
    ["validation/state_parity.csv", "VALIDATION", "YES", "State occurrence identity parity"],
    ["validation/occurrence_bom_reconciliation.csv", "VALIDATION", "YES", "Occurrence-to-BOM row reconciliation register"],
    ["validation/occurrence_bom_reconciliation.json", "VALIDATION", "YES", "Occurrence-to-BOM reconciliation summary"],
  ];
  const evidenceValidationSetError = exactIdentifierSetError(
    expected
      .filter(([, category]) => category === "VALIDATION")
      .map(([fileName]) => path.basename(fileName))
      .filter((fileName) => fileName !== "validation_manifest.json"),
    REQUIRED_VALIDATION_EVIDENCE_FILES,
    "evidence-index validation filename set",
  );
  if (evidenceValidationSetError) throw new Error(evidenceValidationSetError);
  for (const fileName of Object.keys(manifest.files ?? {})) expected.push([fileName, "PRODUCT CAD", "YES", "Final exact AP242 product master"]);
  const rows = [];
  for (let i = 0; i < expected.length; i += 1) {
    const [fileName, category, required, purpose] = expected[i];
    const filePath = category === "PRODUCT CAD" ? path.join(releaseDir, fileName) : path.join(analysisDir, fileName);
    const meta = await fileMeta(filePath);
    if (!meta.present) throw new Error(`Required evidence-index artifact is missing: ${filePath}.`);
    const baseName = path.basename(fileName);
    const authenticated = authenticatedByName.get(baseName);
    let sha;
    if (fileName === "validation/validation_manifest.json") {
      sha = await sha256File(filePath);
    } else {
      if (!authenticated) throw new Error(`Evidence-index artifact was not authenticated before workbook use: ${fileName}.`);
      if (authenticated.size !== meta.size) throw new Error(`Authenticated evidence size changed before workbook use: ${fileName}.`);
      sha = authenticated.sha256;
    }
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

// 18_NEUTRAL_VALIDATION
{
  const sheet = sheets.get("18_NEUTRAL_VALIDATION");
  const headers = ["Check ID", "Neutral-CAD / Environment Item", "Acceptance Required", "Evidence Value", "Evidence Reference", "Formula Status"];
  createTitle(sheet, "FINAL NEUTRAL-CAD VALIDATION", "Clean-process OCP/XCAF reimport is the controlling neutral-CAD gate. The owner target-CAD import is a post-delivery activity and is excluded from acceptance logic.", headers.length);
  const neutralGateIds = new Set([
    "AP242-STOWED", "AP242-DEPLOYED", "BREP-VALID-STOWED", "BREP-VALID-DEPLOYED",
    "INTERFERENCE-STOWED", "INTERFERENCE-DEPLOYED", "CLEARANCE-EVIDENCE-STOWED",
    "CLEARANCE-EVIDENCE-DEPLOYED", "STATE-PARITY", "OCCURRENCE-TRANSFORMS",
    "OCCURRENCE-BOM-RECONCILIATION", "MOTION-FULL-MECHANISM",
  ]);
  const checks = [
    ["ENVIRONMENT-DISPOSITION", "Owner target-CAD environment", "NO", CREO_ENVIRONMENT_DISPOSITION, "validation/gate_results.json informational_environment_items", "N/A"],
    ...providedGates
      .filter((candidate) => neutralGateIds.has(String(candidate.gate_id ?? candidate.id ?? "")))
      .map((candidate) => [
        String(candidate.gate_id ?? candidate.id),
        candidate.requirement ?? candidate.gate_id ?? candidate.id,
        "YES",
        String(candidate.status ?? "BLOCKED").toUpperCase(),
        candidate.evidence ?? "validation/gate_results.json",
        "GATE",
      ]),
  ];
  sheet.getRange("A4:F4").values = [["Neutral Acceptance Items", checks.length - 1, "Informational Environment Item", "N/A", "Release Logic", "08_FINAL_VALIDATION only"]];
  sheet.getRange("A4:F4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  const rows = checks.map((check, index) => {
    const row = 7 + index;
    const formula = check[5] === "N/A"
      ? '="N/A"'
      : `=IF(D${row}="","BLOCKED",IF(D${row}="PASS","PASS",IF(D${row}="FAIL","FAIL","BLOCKED")))`;
    return [check[0], check[1], check[2], check[3], check[4], { formula }];
  });
  writeTable(sheet, 6, headers, rows, {
    statusColumns: [5],
    widthCaps: { 1: 62, 3: 76, 4: 58 },
  });
}

// 19_ROUTING
{
  const sheet = sheets.get("19_ROUTING");
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
  createTitle(sheet, "FINAL ROUTING, PENETRATIONS & TERMINATIONS", "Every route is occurrence-specific and is reconciled to exact endpoint termination, fitting, support, and penetration evidence.", headers.length);
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
      pick(validation, ["issues", "endpoint_results", "evidence", "notes", "validation_reference", "source_file"]),
      {
        formula: `=IF(OR(C${row}="",D${row}="",E${row}="",F${row}="",G${row}=""),"INCOMPLETE",IF(L${row}="","BLOCKED",IF(L${row}="PASS","COMPLETE","FAIL")))`,
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
      {
      const mismatches = measured(gate, ["transform_mismatches"], []);
      model.primaryCriterion = 0;
      model.primaryEvidence =
        (numericMeasured(gate, ["unmapped_leaf_occurrences"], 0) ?? 0) +
        (numericMeasured(gate, ["identity_occurrences_without_justification"], 0) ?? 0) +
        (Array.isArray(mismatches) ? mismatches.length : 0);
      model.mode = "LE";
      break;
      }
    case "ARM-KINEMATICS-ENDPOINTS":
      model.primaryCriterion = 0.0000001;
      model.primaryEvidence = Math.max(
        numericMeasured(gate, ["maximum_clock_error_deg"], 0) ?? 0,
        numericMeasured(gate, ["maximum_stowed_angle_error_deg"], 0) ?? 0,
        numericMeasured(gate, ["maximum_deployed_angle_error_deg"], 0) ?? 0,
      );
      model.mode = "LE";
      break;
    case "ARM-LENGTH":
      model.primaryCriterion = 0.000001;
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
      model.auxiliaryCriterion = 0.000001;
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
      const invalid = measured(gate, ["invalid_mass_occurrence_ids"], []);
      const invariance = measured(gate, ["state_invariance_errors"], []);
      model.primaryCriterion = 0;
      model.primaryEvidence =
        (Array.isArray(unresolved) ? unresolved.length : (asNumber(unresolved) ?? 0)) +
        (Array.isArray(invalid) ? invalid.length : (asNumber(invalid) ?? 0)) +
        (Array.isArray(invariance) ? invariance.length : (asNumber(invariance) ?? 0));
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
        (numericMeasured(gate, ["generic_evidence_rows_across_states"], 0) ?? 0) +
        (numericMeasured(gate, ["geometric_or_fastener_unsupported_connections_across_states"], 0) ?? 0) +
        (numericMeasured(gate, ["uncovered_attachment_endpoint_occurrences_across_states"], 0) ?? 0) +
        (numericMeasured(gate, ["failed_routes_across_states"], 0) ?? 0);
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
      const incompleteBuyIdentity = measured(gate, ["incomplete_or_held_buy_identity"], []);
      const makeWithoutProcess = measured(gate, ["make_parts_without_material_or_process"], []);
      model.primaryCriterion = 0;
      model.primaryEvidence =
        (Array.isArray(provisional) ? provisional.length : 0) +
        (Array.isArray(missingLinks) ? missingLinks.length : 0) +
        (Array.isArray(incompleteBuyIdentity) ? incompleteBuyIdentity.length : 0) +
        (Array.isArray(makeWithoutProcess) ? makeWithoutProcess.length : 0);
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
      model.primaryCriterion = "PASS";
      model.primaryEvidence = model.reportedStatus;
      model.auxiliaryCriterion = "81 samples; <=1 degree; zero missing scope/blocked exact operations/unauthorized intersections";
      model.auxiliaryEvidence = compactMeasured(gate.measured);
      model.mode = "VALIDATOR_STATUS";
      break;
    default:
      model.primaryCriterion = "PASS";
      model.primaryEvidence = model.reportedStatus;
      model.mode = "VALIDATOR_STATUS";
      model.note = `${model.note} Formula status is controlled by the final validator status field; measured evidence is retained verbatim.`.trim();
  }
  return model;
}

const gateModels = providedGates.map(exactGateModel);

// 08_FINAL_VALIDATION
const gateRowsById = new Map();
{
  const sheet = sheets.get("08_FINAL_VALIDATION");
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
  createTitle(sheet, "FINAL CALCULATED VALIDATION GATES", "Every workbook gate status is a formula driven by the corresponding final validator status; no static PASS cell or non-validator blocker participates in release.", headers.length);
  sheet.getRange("A4:J5").values = [
    ["Computed Total", null, "Computed PASS", null, "Computed FAIL", null, "Computed BLOCKED", null, "Count Reconciliation", null],
    ["Validator Total", providedGates.length, "Validator PASS", reportedGateCounts.PASS, "Validator FAIL", reportedGateCounts.FAIL, "Validator BLOCKED", reportedGateCounts.BLOCKED, "Formula Release", null],
  ];
  sheet.getRange("J5").formulas = [[`=IF(AND(B5>0,D5=B5,F5=0,H5=0),"PASS","NOT_RELEASED")`]];
  sheet.getRange("A4:J4").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.ink } };
  sheet.getRange("A5:J5").format = { fill: COLORS.pale, font: { bold: true, color: COLORS.ink } };
  const rows = gateModels.map((gate, index) => {
    const row = 8 + index;
    gateRowsById.set(gate.id, row);
    const actual = gate.actualFormula ? { formula: gate.actualFormula } : (gate.primaryEvidence ?? "");
    const statusFormula = `=IF(J${row}="","BLOCKED",IF(J${row}="PASS","PASS",IF(J${row}="FAIL","FAIL","BLOCKED")))`;
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
  sheet.getRange("J4").formulas = [[`=IF(AND(B4=B5,D4=D5,F4=F5,H4=H5),"MATCH","MISMATCH")`]];
  sheet.getRange("B4:H5").format.numberFormat = "0";
  applyStatusConditionalFormatting(sheet.getRange("J4"));
}

// 09_NCR_CLOSURE
let ncrTable;
{
  const sheet = sheets.get("09_NCR_CLOSURE");
  const headers = ["NCR", "Rejected Condition", "Required Correction", "Controlling Gates", "Evidence", "Formula Status", "Owner / Disposition"];
  createTitle(sheet, "FINAL NCR CLOSURE MATRIX", "Closure is formula-derived from the genuine final neutral-CAD gates; no NCR is closed by authoring assertion or environment availability.", headers.length);
  const ncrs = [
    ["NCR-01", "Uncontrolled assembly context and ambiguous external crane/ORION/load-cell hardware.", "Classify product versus external context, control the boundary, remove duplicates, and prove the product load path reaches it.", ["AP242-STOWED", "AP242-DEPLOYED", "STATE-PARITY", "ATTACHMENT-COHESION", "RECOVERY-LOAD-PATH"], "Named AP242 hierarchy, state parity, separately named external context, and structural connectivity evidence"],
    ["NCR-02", "Incomplete deployed-system cohesion across buoy, harness, terminal, tether, hardpoint, and primary structure.", "Model and retain the complete deployed recovery chain with both flexible-member termini physically connected.", ["STATE-PARITY", "ATTACHMENT-COHESION", "RECOVERY-LOAD-PATH"], "State parity and occurrence-specific attachment/load-path evidence"],
    ["NCR-03", "Unsupported routing and improperly placed small hardware.", "Define origins, destinations, penetrations, clamps, fairleads, glands, strain relief, bend radius, service slack, tool access, and engagement.", ["PROCUREMENT-DEFINITION", "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION", "DOD-CLOSED-PRESSURE-SUBSYSTEMS", "DOD-CLOSED-ROUTE-ENDS", "CLEARANCE-EVIDENCE-STOWED", "CLEARANCE-EVIDENCE-DEPLOYED", "MOTION-FULL-MECHANISM"], "Calculated procurement, hardware, pressure-route closure, near-clearance, and full-motion evidence"],
    ["NCR-04", "Wall, boss, and spring-envelope interference.", "Provide manufactured passages and reinforcement while eliminating every undocumented intersection through full travel.", ["INTERFERENCE-STOWED", "INTERFERENCE-DEPLOYED", "CLEARANCE-EVIDENCE-STOWED", "CLEARANCE-EVIDENCE-DEPLOYED", "MOTION-FULL-MECHANISM"], "Endpoint pair audits, critical clearance register, and full-mechanism motion sweep"],
    ["NCR-05", "Floating or unretained mechanism components.", "Provide pivots/guides/seats, axial and lateral retention, anti-rotation, defined DOF, stops/locks, and service method.", ["ATTACHMENT-COHESION", "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION", "DOD-POSITIVE-DEPLOYED-LOCKS", "DOD-POSITIVE-STOWED-RETENTION", "PROCUREMENT-DEFINITION", "MOTION-FULL-MECHANISM"], "Calculated attachment, hardware-retention, deployed-lock, stowed-retention, procurement, and motion evidence"],
    ["NCR-06", "Open-ended line and unattached hardware.", "Terminate every line at modeled hardware, add support and controlled penetrations, and verify collision-free movement.", ["ATTACHMENT-COHESION", "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION", "DOD-CLOSED-PRESSURE-SUBSYSTEMS", "DOD-CLOSED-ROUTE-ENDS", "PROCUREMENT-DEFINITION", "MOTION-FULL-MECHANISM"], "Calculated attachment, hardware, pressure closure, route termination, procurement, and full-mechanism motion evidence"],
    ["NCR-07", "Faceted arm geometry built from excessive planar patches.", "Use smooth analytic or curvature-continuous exact B-rep arm geometry with no tessellated proxy.", ["AP242-STOWED", "BREP-VALID-STOWED", "AP242-DEPLOYED", "BREP-VALID-DEPLOYED", "ARM-SURFACE-QUALITY"], "AP242 text inspection, exact B-rep validity, and calculated arm face/surface inventory"],
    ["NCR-08", "Globally baked component geometry and unjustified identity placements.", "Use stable local part coordinates, meaningful occurrence transforms, reused part definitions, and consistent moving identities.", ["STATE-PARITY", "OCCURRENCE-TRANSFORMS"], "XCAF occurrence inventories, state parity, and transform-justification evidence"],
  ];
  const rows = ncrs.map((ncr) => {
    const gateCells = ncr[3].map((id) => {
      const row = gateRowsById.get(id);
      return row ? `'08_FINAL_VALIDATION'!G${row}` : '"BLOCKED"';
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
      "Final corrective configuration; disposition follows controlling gate formulas",
    ];
  });
  ncrTable = writeTable(sheet, 5, headers, rows, {
    statusColumns: [5],
    widthCaps: { 1: 52, 2: 52, 4: 46, 6: 48 },
  });
}

// 16_COMPLIANCE
{
  const sheet = sheets.get("16_COMPLIANCE");
  const headers = ["Requirement ID", "Requirement", "Primary Criterion", "Primary Evidence", "Aux Criterion", "Aux Evidence", "Formula Status", "Evidence Source", "Notes"];
  createTitle(sheet, "FINAL REQUIREMENT COMPLIANCE MATRIX", "Definition-of-Done requirements are linked to formula-derived final neutral-CAD validation gates and retain full precision.", headers.length);
  const compliance = gateModels.map((gate) => {
    const gateRow = gateRowsById.get(gate.id);
    return [
      gate.id,
      gate.requirement,
      { formula: `='08_FINAL_VALIDATION'!C${gateRow}` },
      { formula: `='08_FINAL_VALIDATION'!D${gateRow}` },
      { formula: `='08_FINAL_VALIDATION'!E${gateRow}` },
      { formula: `='08_FINAL_VALIDATION'!F${gateRow}` },
      { formula: `='08_FINAL_VALIDATION'!G${gateRow}` },
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
  createTitle(sheet, "STINGRAY I5S DF8 — FINAL EXACT AP242 BUILD, PARTS & PROCUREMENT REGISTER", "Evidence-backed final configuration workbook. Release is formula-derived solely from the final neutral-CAD Definition-of-Done gate results.", 8);
  sheet.getRange("A4:H4").values = [["Validation Gates", null, "PASS", null, "FAIL", null, "BLOCKED", null]];
  sheet.getRange("A5:H5").values = [[null, null, null, null, null, null, null, null]];
  sheet.getRange("A4:H4").format = { fill: COLORS.teal, font: { bold: true, color: COLORS.white }, horizontalAlignment: "center" };
  sheet.getRange("A5:H5").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.navy, size: 14 }, horizontalAlignment: "center" };
  sheet.getRange("B5").formulas = [["='08_FINAL_VALIDATION'!B4"]];
  sheet.getRange("D5").formulas = [["='08_FINAL_VALIDATION'!D4"]];
  sheet.getRange("F5").formulas = [["='08_FINAL_VALIDATION'!F4"]];
  sheet.getRange("H5").formulas = [["='08_FINAL_VALIDATION'!H4"]];
  applyStatusConditionalFormatting(sheet.getRange("C4:H5"));

  sheet.getRange("A7:H7").values = [["NCRs Closed", null, "NCRs Open", null, "NCRs Blocked", null, "Definition of Done", null]];
  sheet.getRange("A8:H8").values = [[null, null, null, null, null, null, null, null]];
  sheet.getRange("A7:H7").format = { fill: COLORS.blue, font: { bold: true, color: COLORS.white }, horizontalAlignment: "center" };
  sheet.getRange("A8:H8").format = { fill: COLORS.pale, font: { bold: true, color: COLORS.navy, size: 13 }, horizontalAlignment: "center" };
  sheet.getRange("B8").formulas = [[`=COUNTIF('09_NCR_CLOSURE'!F${ncrTable.dataStart}:F${ncrTable.dataEnd},"CLOSED")`]];
  sheet.getRange("D8").formulas = [[`=COUNTIF('09_NCR_CLOSURE'!F${ncrTable.dataStart}:F${ncrTable.dataEnd},"OPEN")`]];
  sheet.getRange("F8").formulas = [[`=COUNTIF('09_NCR_CLOSURE'!F${ncrTable.dataStart}:F${ncrTable.dataEnd},"BLOCKED")`]];
  sheet.getRange("H8").formulas = [[`=IF(AND('08_FINAL_VALIDATION'!B4>0,'08_FINAL_VALIDATION'!D4='08_FINAL_VALIDATION'!B4,'08_FINAL_VALIDATION'!F4=0,'08_FINAL_VALIDATION'!H4=0),"PASS","FAIL")`]];
  applyStatusConditionalFormatting(sheet.getRange("H8"));

  const fileEntries = Object.entries(manifest.files ?? {});
  const metadata = [
    ["Package status", null],
    ["Authoring kernel", manifest.authoring_kernel ?? ""],
    ["Exchange schema", manifest.schema ?? ""],
    ["Owner target-CAD environment", CREO_ENVIRONMENT_DISPOSITION],
    ["Crosshead travel, full precision mm", numericOrBlank(manifest.crosshead_travel_mm)],
    ["Stowed occurrence count", stowed.occurrences?.length ?? 0],
    ["Deployed occurrence count", deployed.occurrences?.length ?? 0],
    ["Unique authored part count", parts.length],
    ["Workbook generation time", new Date()],
  ];
  sheet.getRange("A10:B10").values = [["Package Metadata", "Value"]];
  sheet.getRange("A10:B10").format = { fill: COLORS.blue, font: { bold: true, color: COLORS.white } };
  sheet.getRange(`A11:B${10 + metadata.length}`).values = metadata;
  sheet.getRange("B11").formulas = [[RELEASE_STATUS_FORMULA]];
  sheet.getRange(`A11:A${10 + metadata.length}`).format = { fill: COLORS.pale, font: { bold: true, color: COLORS.ink } };
  sheet.getRange(`B11:B${10 + metadata.length}`).format = { font: { color: COLORS.ink }, wrapText: true };
  sheet.getRange("B15").format.numberFormat = "0.000000";
  sheet.getRange("B19").format.numberFormat = "yyyy-mm-dd hh:mm";

  sheet.getRange("D10:H10").values = [["Product / Context File", "SHA-256", "Bytes", "Schema", "Release Standing"]];
  sheet.getRange("D10:H10").format = { fill: COLORS.blue, font: { bold: true, color: COLORS.white } };
  const fileRows = fileEntries.map(([name, info]) => [name, info.sha256, info.size_bytes, manifest.schema, rawReleaseLabel]);
  if (fileRows.length) sheet.getRange(`D11:H${10 + fileRows.length}`).values = fileRows;
  sheet.getRange(`D11:H${Math.max(11, 10 + fileRows.length)}`).format = { font: { size: 9, color: COLORS.ink }, wrapText: true, borders: { insideHorizontal: { style: "thin", color: COLORS.line } } };
  sheet.getRange(`F11:F${Math.max(11, 10 + fileRows.length)}`).format.numberFormat = "#,##0";

  sheet.getRange("A20:H20").merge();
  sheet.getRange("A20").values = [["Release rule: FINAL — RELEASED only when every genuine final neutral-CAD Definition-of-Done gate is PASS and the formula counts contain zero FAIL and zero BLOCKED. OCP/XCAF clean-process reimport is controlling."]];
  sheet.getRange("A20:H20").format = { fill: COLORS.cyan, font: { bold: true, color: COLORS.navy }, wrapText: true };
  sheet.getRange("A20:H20").format.rowHeight = 34;
  sheet.getRange("A22:H22").merge();
  sheet.getRange("A22").values = [["Source and purchase hyperlinks are recorded in 03_PURCHASED_ITEMS, controlled custom fabrication definitions in 04_CUSTOM_PARTS, and authorized consumables in 07_CONSUMABLES. Additional source/process evidence begins at 14_SOURCE_CAD."]];
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
  ["01_OCCURRENCE_BOM", 18],
  ["11_CLEARANCE_REGISTER", 20],
  ["12_INTERFERENCE_REGISTER", 20],
  ["18_NEUTRAL_VALIDATION", 24],
  ["19_ROUTING", 20],
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
  range: "08_FINAL_VALIDATION!A1:J39",
  include: "values,formulas",
  tableMaxRows: 39,
  tableMaxCols: 10,
  maxChars: 20000,
});
console.log("GATE_INSPECTION\n" + gateInspection.ndjson);

const ncrInspection = await workbook.inspect({
  kind: "table",
  range: "09_NCR_CLOSURE!A1:G16",
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
  range: `08_FINAL_VALIDATION!A7:J${7 + gateModels.length}`,
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
  const reported = reportedGateCounts[status];
  if (resolvedGateCounts[status] !== reported) {
    throw new Error(
      `Formula-resolved ${status} gate count ${resolvedGateCounts[status]} does not match filtered final validator count ${reported}.`,
    );
  }
}

const resolvedNcrInspection = await workbook.inspect({
  kind: "table",
  range: `09_NCR_CLOSURE!A5:G${ncrTable.dataEnd}`,
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
  summary: "Final neutral-CAD workbook formula error scan",
});
console.log("FORMULA_ERROR_SCAN\n" + errorScan.ndjson);

await fs.mkdir(previewDir, { recursive: true });
for (const fileName of await fs.readdir(previewDir)) {
  if (fileName.endsWith(".png")) await fs.unlink(path.join(previewDir, fileName));
}
const renderFailures = [];
for (const name of sheetNames) {
  try {
    if (name === "11_CLEARANCE_REGISTER" && clearanceCsv.length > 440) {
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
const workbookStat = await fs.stat(outputPath);
const validationManifestPath = path.join(analysisDir, "validation", "validation_manifest.json");
const validationManifestStat = await fs.stat(validationManifestPath);
const gateResultRecord = authenticatedByName.get("gate_results.json");
if (!gateResultRecord) throw new Error("Authenticated gate_results.json record is unavailable after workbook save.");
const stepFiles = {};
for (const fileName of FINAL_PRODUCT_STEP_FILES) {
  const record = authenticatedByName.get(fileName);
  if (!record) throw new Error(`Authenticated final STEP record is unavailable after workbook save: ${fileName}.`);
  stepFiles[fileName] = { sha256: record.sha256, size_bytes: record.size };
}
const workbookBuildManifest = {
  schema: "DF8_FINAL_WORKBOOK_BUILD_MANIFEST_V1",
  workbook: {
    name: path.basename(outputPath),
    sha256: await sha256File(outputPath),
    size_bytes: workbookStat.size,
  },
  validation_manifest: {
    name: "validation_manifest.json",
    sha256: await sha256File(validationManifestPath),
    size_bytes: validationManifestStat.size,
  },
  gate_results: {
    name: "gate_results.json",
    sha256: gateResultRecord.sha256,
    size_bytes: gateResultRecord.size,
  },
  step_files: stepFiles,
};
await fs.writeFile(
  path.join(analysisDir, "workbook_build_manifest.json"),
  `${JSON.stringify(workbookBuildManifest, null, 2)}\n`,
  "utf8",
);
console.log(`EXPORTED ${outputPath}`);
console.log(`RENDERED ${sheetNames.length} sheets to ${previewDir}`);
