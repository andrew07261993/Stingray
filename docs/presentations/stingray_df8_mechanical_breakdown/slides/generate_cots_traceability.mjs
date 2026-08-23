import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const packageRoot = path.resolve(here, "..");
const manifestPath = path.join(packageRoot, "manifests", "per_part_render_manifest.json");
const outputJsonPath = path.join(packageRoot, "manifests", "per_part_cots_traceability.json");
const outputCsvPath = path.join(packageRoot, "manifests", "per_part_cots_traceability.csv");
const validationPath = path.join(packageRoot, "manifests", "per_part_cots_traceability_validation.json");

const manifest = JSON.parse(await fs.readFile(manifestPath, "utf8"));

const cotsOverrides = {
  "GN-615.3-M3-KN-PFB": {
    vendor_catalog_part_number: "GN 615.3-M3-KN-PFB",
    catalog_source_url: "https://www.jwwinco.com/en-us/products/3.1-Indexing-locking-blocking-with-pins-and-ball-shaped-elements/Spring-plungers/GN-615.3-Steel-Stainless-Steel-Ball-Plungers-with-thread-locking-with-ball-with-internal-hexagon",
  },
  "GS-19-50-V4A-B8-B8": {
    vendor_catalog_part_number: "GS-19-50-V4A-B8-B8",
    catalog_source_url: "https://www.acecontrols.com/us/calculations/gas-spring-configurator.html",
  },
  "GS-19-50-V4A-B8-B8-ROD-CHILD": {
    vendor_catalog_part_number: "GS-19-50-V4A-B8-B8",
    parent_purchased_assembly_part_number: "GS-19-50-V4A-B8-B8",
    catalog_source_url: "https://www.acecontrols.com/us/calculations/gas-spring-configurator.html",
  },
  "HBD-15-25-AA-P": {
    vendor_catalog_part_number: "HBD-15-25-AA-P",
    catalog_source_url: "https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15/hbd-15-25.html",
  },
  "HBD-15-25-AA-P-ROD-CHILD": {
    vendor_catalog_part_number: "HBD-15-25-AA-P",
    parent_purchased_assembly_part_number: "HBD-15-25-AA-P",
    catalog_source_url: "https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15/hbd-15-25.html",
  },
  "HDP-3-8-A1": {
    vendor_catalog_part_number: "HDP-3-8-A1",
    catalog_source_url: "https://www.accu.co.uk/dowel-pins/72653-HDP-3-8-A1",
  },
  "HEC-10-A4": {
    vendor_catalog_part_number: "HEC-10-A4",
    catalog_source_url: "https://www.accu.co.uk/external-circlips/629101-HEC-10-A4",
  },
  "HTP-3-30-A1": {
    vendor_catalog_part_number: "HTP-3-30-A1",
    catalog_source_url: "https://www.accu.co.uk/taper-pins/389498-HTP-3-30-A1",
  },
  "LELAND-81121": {
    vendor_catalog_part_number: "81121",
    catalog_source_url: "https://www.lelandgas.com/product-page/81121-cartridge-small-x-xml-x-xxg-gas",
  },
  "ROTOR-CLIP-DC-4SS": {
    vendor_catalog_part_number: "DC-4SS",
    catalog_source_url: "https://www.rotorclip.com/product/dc-4/",
  },
  "SS-CHS2-1": {
    vendor_catalog_part_number: "SS-CHS2-1",
    catalog_source_url: "https://products.swagelok.com/en/c/fixed-pressure/p/SS-CHS2-1",
  },
  "SSCA-M3-8-A4-BL": {
    vendor_catalog_part_number: "SSCA-M3-8-A4-BL",
    catalog_source_url: "https://www.accu.co.uk/cap-head-captive-screws/779966-SSCA-M3-8-A4-BL",
  },
  "SSCF-M3-10-A4": {
    vendor_catalog_part_number: "SSCF-M3-10-A4",
    catalog_source_url: "https://www.accu.co.uk/us/socket-cap-head-screws/3975-SSCF-M3-10-A4",
  },
  "SSCF-M3-6-A4": {
    vendor_catalog_part_number: "SSCF-M3-6-A4",
    catalog_source_url: "https://www.accu.co.uk/metric-cap-head-screws/3973-SSCF-M3-6-A4",
  },
  "SSCL-M4-8-A4": {
    vendor_catalog_part_number: "SSCL-M4-8-A4",
    catalog_source_url: "https://www.accu.co.uk/low-head-cap-screws/8885-SSCL-M4-8-A4",
  },
  "SSK-M3-6-A4-P80": {
    vendor_catalog_part_number: "SSK-M3-6-A4-P80",
    catalog_source_url: "https://www.accu.co.uk/countersunk-socket-head-screws/795226-SSK-M3-6-A4-P80",
  },
  "V80040": {
    vendor_catalog_part_number: "V80040",
    catalog_source_url: "https://fluid-components.nordsonmedical.com/Resources/Orders/",
  },
};

const cotsRows = manifest.map((row) => {
  if (row.classification === "MAKE") {
    return {
      part_number: row.part_number,
      part_name: row.part_name,
      included_in_deck: row.included === true,
      cots_classification: "NOT_COTS_MAKE",
      vendor_or_manufacturer: "N/A — STINGRAY-controlled MAKE item",
      vendor_catalog_part_number: "N/A",
      parent_purchased_assembly_part_number: "N/A",
      catalog_identity_status: "N/A — MAKE",
      catalog_source_url: "N/A",
      vendor_serial_lot_or_heat_identifier: "N/A — MAKE PartDef",
      serial_lot_or_heat_verified: false,
      certificate_of_conformance_status: "N/A — supplier CoC does not apply to a MAKE PartDef",
      certificate_of_conformance_verified: false,
      certificate_evidence_reference: "N/A",
      receiving_release_disposition: "N/A — control with drawing, material certification, traveler, and build records",
    };
  }

  const override = cotsOverrides[row.part_number];
  if (!override) throw new Error(`Missing COTS catalog override for ${row.part_number}`);
  const isChild = Boolean(override.parent_purchased_assembly_part_number);
  return {
    part_number: row.part_number,
    part_name: row.part_name,
    included_in_deck: row.included === true,
    cots_classification: isChild ? "COTS_SUBCOMPONENT_CHILD" : "COTS_BUY",
    vendor_or_manufacturer: row.manufacturer,
    vendor_catalog_part_number: override.vendor_catalog_part_number,
    parent_purchased_assembly_part_number: override.parent_purchased_assembly_part_number || "N/A",
    catalog_identity_status: isChild
      ? "SOURCE-IDENTIFIED — geometry child governed by parent purchased assembly"
      : "SOURCE-IDENTIFIED — vendor/catalog identity recorded; delivered unit not inspected",
    catalog_source_url: override.catalog_source_url,
    vendor_serial_lot_or_heat_identifier: isChild
      ? "NOT PROVIDED — inherit from parent received assembly"
      : "NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving",
    serial_lot_or_heat_verified: false,
    certificate_of_conformance_status: isChild
      ? "NOT VERIFIED — inherit parent assembly CoC evidence"
      : "NOT VERIFIED — no delivered-unit supplier CoC is present in this package",
    certificate_of_conformance_verified: false,
    certificate_evidence_reference: "NONE IN PACKAGE",
    receiving_release_disposition: isChild
      ? "HOLD WITH PARENT — do not treat as a separately orderable line"
      : "HOLD — verify received item identity and retain supplier CoC before release",
  };
});

const fields = [
  "part_number",
  "part_name",
  "included_in_deck",
  "cots_classification",
  "vendor_or_manufacturer",
  "vendor_catalog_part_number",
  "parent_purchased_assembly_part_number",
  "catalog_identity_status",
  "catalog_source_url",
  "vendor_serial_lot_or_heat_identifier",
  "serial_lot_or_heat_verified",
  "certificate_of_conformance_status",
  "certificate_of_conformance_verified",
  "certificate_evidence_reference",
  "receiving_release_disposition",
];
const csvEscape = (value) => `"${String(value).replaceAll('"', '""')}"`;
const csv = [fields.join(","), ...cotsRows.map((row) => fields.map((field) => csvEscape(row[field])).join(","))].join("\n");

const buyRows = cotsRows.filter((row) => row.cots_classification !== "NOT_COTS_MAKE");
const parentBuyRows = buyRows.filter((row) => row.cots_classification === "COTS_BUY");
const childBuyRows = buyRows.filter((row) => row.cots_classification === "COTS_SUBCOMPONENT_CHILD");
const includedBuyRows = buyRows.filter((row) => row.included_in_deck);
const childParentsValid = childBuyRows.every((row) => parentBuyRows.some((parent) => parent.part_number === row.parent_purchased_assembly_part_number));
const requiredFieldsComplete = cotsRows.every((row) => fields.every((field) => row[field] !== undefined && row[field] !== null && String(row[field]).length > 0));
const checks = {
  traceability_row_count_121: cotsRows.length === 121,
  make_row_count_104: cotsRows.filter((row) => row.cots_classification === "NOT_COTS_MAKE").length === 104,
  buy_definition_row_count_17: buyRows.length === 17,
  included_buy_definition_row_count_12: includedBuyRows.length === 12,
  excluded_buy_fastener_row_count_5: buyRows.filter((row) => !row.included_in_deck).length === 5,
  required_fields_complete: requiredFieldsComplete,
  child_parent_links_valid: childParentsValid,
  buy_catalog_fields_complete: buyRows.every((row) => row.vendor_or_manufacturer && row.vendor_catalog_part_number && row.catalog_source_url),
  no_unsubstantiated_serial_lot_verification: buyRows.every((row) => row.serial_lot_or_heat_verified === false),
  no_unsubstantiated_coc_verification: buyRows.every((row) => row.certificate_of_conformance_verified === false),
  all_buy_rows_fail_closed: buyRows.every((row) => row.receiving_release_disposition.startsWith("HOLD")),
};
const validation = {
  schema: "STINGRAY_DF8_COTS_TRACEABILITY_VALIDATION_V1",
  status: Object.values(checks).every(Boolean) ? "PASS" : "FAIL",
  evidence_review_date: "2026-08-23",
  scope_note: "PASS means the traceability schema is complete and fail-closed. It does not mean any received COTS unit or supplier CoC has been accepted.",
  counts: {
    catalog_rows: cotsRows.length,
    make_rows: cotsRows.filter((row) => row.cots_classification === "NOT_COTS_MAKE").length,
    buy_definition_rows: buyRows.length,
    included_buy_definition_rows: includedBuyRows.length,
    excluded_buy_fastener_rows: buyRows.filter((row) => !row.included_in_deck).length,
    buy_parent_purchase_lines: parentBuyRows.length,
    buy_subcomponent_child_rows: childBuyRows.length,
    buy_serial_lot_or_heat_verified: buyRows.filter((row) => row.serial_lot_or_heat_verified).length,
    buy_certificate_of_conformance_verified: buyRows.filter((row) => row.certificate_of_conformance_verified).length,
  },
  checks,
  release_disposition: "COTS RECEIVING EVIDENCE INCOMPLETE — NOT RELEASED",
};

await fs.writeFile(outputJsonPath, `${JSON.stringify(cotsRows, null, 2)}\n`, "utf8");
await fs.writeFile(outputCsvPath, `${csv}\n`, "utf8");
await fs.writeFile(validationPath, `${JSON.stringify(validation, null, 2)}\n`, "utf8");
console.log(JSON.stringify(validation, null, 2));
if (validation.status !== "PASS") process.exitCode = 1;
