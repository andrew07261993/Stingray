import fs from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const artifactToolUrl = pathToFileURL(require.resolve("@oai/artifact-tool")).href;
const { Presentation, PresentationFile } = await import(artifactToolUrl);


const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const SOURCE = path.join(ROOT, "work", "short14_external_buoy", "inspection_views");
const OUT = path.join(ROOT, "work", "complete_product_definition", "08_EXECUTIVE");
const QA = path.join(OUT, "_qa");

const W = 1280;
const H = 720;
const C = {
  ink: "#000000",
  muted: "#475569",
  faint: "#EDEDED",
  rule: "#B8BCC4",
  blue: "#3D8DFF",
  cyan: "#6DCBF4",
  pale: "#EAF5FB",
  red: "#B42318",
  redPale: "#FEE4E2",
  green: "#137A4B",
  greenPale: "#E8F7EF",
  white: "#FFFFFF",
};
const FONT = "Arial";


async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}


async function readImageBlob(imagePath) {
  const bytes = await fs.readFile(imagePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}


function addText(slide, name, text, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontFamily: FONT,
    fontSize: 20,
    color: C.ink,
    ...style,
  };
  return shape;
}


function addPanel(slide, name, position, fill = C.faint, line = C.rule, radius = "rounded-xl") {
  return slide.shapes.add({
    geometry: "roundRect",
    name,
    position,
    fill,
    line: { style: "solid", fill: line, width: 1 },
    borderRadius: radius,
  });
}


function addRule(slide, name, left, top, width, fill = C.rule, weight = 1) {
  return slide.shapes.add({
    geometry: "rect",
    name,
    position: { left, top, width, height: weight },
    fill,
    line: { style: "solid", fill, width: 0 },
  });
}


function addTitle(slide, title, page, eyebrow = "STINGRAY DIGITAL PRODUCT DEFINITION") {
  addText(slide, `eyebrow-${page}`, eyebrow, { left: 42, top: 28, width: 750, height: 22 }, {
    fontSize: 12,
    bold: true,
    color: C.muted,
  });
  addText(slide, `title-${page}`, title, { left: 42, top: 58, width: 1160, height: 88 }, {
    fontSize: 39,
    bold: true,
    color: C.ink,
  });
  addRule(slide, `title-rule-${page}`, 42, 153, 1196, C.rule, 1);
}


function addFooter(slide, page, evidence) {
  addText(slide, `evidence-${page}`, evidence, { left: 42, top: 669, width: 1090, height: 24 }, {
    fontSize: 11,
    color: C.muted,
  });
  addText(slide, `page-${page}`, String(page), { left: 1182, top: 669, width: 56, height: 24 }, {
    fontSize: 11,
    bold: true,
    alignment: "right",
    color: C.muted,
  });
}


async function addImage(slide, name, fileName, position, alt, fit = "contain") {
  addPanel(slide, `${name}-backing`, position, C.white, C.rule);
  slide.images.add({
    blob: await readImageBlob(path.join(SOURCE, fileName)),
    contentType: "image/png",
    alt,
    fit,
    position,
    geometry: "roundRect",
    borderRadius: "rounded-xl",
  });
}


function addStatusBand(slide, name, text, left, top, width, kind = "fail") {
  const fill = kind === "pass" ? C.greenPale : kind === "neutral" ? C.pale : C.redPale;
  const color = kind === "pass" ? C.green : kind === "neutral" ? C.blue : C.red;
  addPanel(slide, `${name}-panel`, { left, top, width, height: 44 }, fill, color, "rounded-lg");
  addText(slide, `${name}-text`, text, { left: left + 14, top: top + 10, width: width - 28, height: 24 }, {
    fontSize: 16,
    bold: true,
    color,
    alignment: "center",
  });
}


function addMetric(slide, name, value, label, left, top, width, kind = "neutral") {
  const fill = kind === "pass" ? C.greenPale : kind === "fail" ? C.redPale : C.faint;
  const accent = kind === "pass" ? C.green : kind === "fail" ? C.red : C.blue;
  addPanel(slide, `${name}-panel`, { left, top, width, height: 178 }, fill, fill);
  addText(slide, `${name}-value`, value, { left: left + 20, top: top + 28, width: width - 40, height: 74 }, {
    fontSize: 48,
    bold: true,
    color: accent,
  });
  addText(slide, `${name}-label`, label, { left: left + 20, top: top + 108, width: width - 40, height: 54 }, {
    fontSize: 18,
    color: C.ink,
  });
}


async function buildDeck() {
  await fs.mkdir(OUT, { recursive: true });
  await fs.mkdir(QA, { recursive: true });
  const deck = Presentation.create({ slideSize: { width: W, height: H } });

  // 1 - Cover: adapted from Codex Grid slide 08 (half text / half evidence image).
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addText(slide, "cover-eyebrow", "EXECUTIVE RELEASE STATUS | 26 AUGUST 2026", { left: 42, top: 38, width: 570, height: 28 }, {
      fontSize: 13,
      bold: true,
      color: C.muted,
    });
    addText(slide, "cover-title", "STINGRAY digital product definition", { left: 42, top: 105, width: 550, height: 154 }, {
      fontSize: 52,
      bold: true,
      color: C.ink,
    });
    addText(slide, "cover-claim", "The mechanism is digitally coherent. The inflation architecture is not releaseable.", { left: 42, top: 287, width: 540, height: 108 }, {
      fontSize: 25,
      color: C.ink,
    });
    addStatusBand(slide, "cover-status", "NOT RELEASED FOR FABRICATION OR FIELD USE", 42, 462, 540, "fail");
    addText(slide, "cover-config", "Frozen configuration: 1,675.4 mm rigid body | 355 mm arm pivot | external 60 L buoy pack", { left: 42, top: 544, width: 545, height: 78 }, {
      fontSize: 17,
      color: C.muted,
    });
    await addImage(slide, "cover-image", "08_SHORTENED_DEPLOYED_SYSTEM.png", { left: 650, top: 42, width: 588, height: 588 }, "CAD-derived deployed system with extended arms and inflated external buoy");
    addFooter(slide, 1, "Evidence: Release Index; Non-Release Exception Report");
  }

  // 2 - Purpose and two physical states.
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addTitle(slide, "A compact body deploys arms and an external recovery buoy", 2);
    addText(slide, "purpose-copy", "The system is intended to remain compact before use, deploy three arms, open an aft softgoods pack, and transfer recovery load through a dedicated tether path.", { left: 42, top: 178, width: 1196, height: 66 }, {
      fontSize: 21,
      color: C.ink,
    });
    await addImage(slide, "purpose-stowed", "07_SHORTENED_STOWED_SYSTEM.png", { left: 42, top: 274, width: 570, height: 318 }, "CAD-derived shortened STOWED system with closed external Cordura pack");
    await addImage(slide, "purpose-deployed", "08_SHORTENED_DEPLOYED_SYSTEM.png", { left: 668, top: 274, width: 570, height: 318 }, "CAD-derived DEPLOYED system with arms and inflated buoy");
    addText(slide, "purpose-stowed-label", "STOWED - 1,675.4 mm rigid length", { left: 58, top: 605, width: 510, height: 30 }, { fontSize: 18, bold: true });
    addText(slide, "purpose-deployed-label", "DEPLOYED - 80 degree arms, open pack", { left: 684, top: 605, width: 510, height: 30 }, { fontSize: 18, bold: true });
    addFooter(slide, 2, "Evidence: Technical Analysis Report sections 5-6; CAD views 07-08");
  }

  // 3 - Operating sequence.
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addTitle(slide, "Operation is a five-step chain - and every link must work", 3);
    const steps = [
      ["1", "STOWED", "Arms retained; pack closed"],
      ["2", "TRIGGER", "Water bobbin or manual pull"],
      ["3", "DEPLOY", "Crosshead moves; three arms rotate"],
      ["4", "OPEN", "Cordura flaps peel; buoy unfolds"],
      ["5", "RECOVER", "Buoy inflates; tether carries load"],
    ];
    const lefts = [42, 288, 534, 780, 1026];
    for (let i = 0; i < steps.length; i += 1) {
      const [number, label, copy] = steps[i];
      const left = lefts[i];
      addPanel(slide, `sequence-panel-${i}`, { left, top: 246, width: 212, height: 264 }, i === 4 ? C.redPale : C.faint, i === 4 ? C.red : C.rule);
      addText(slide, `sequence-number-${i}`, number, { left: left + 18, top: 265, width: 48, height: 48 }, { fontSize: 32, bold: true, color: i === 4 ? C.red : C.blue });
      addText(slide, `sequence-label-${i}`, label, { left: left + 18, top: 332, width: 176, height: 34 }, { fontSize: 20, bold: true });
      addText(slide, `sequence-copy-${i}`, copy, { left: left + 18, top: 390, width: 176, height: 92 }, { fontSize: 18, color: C.muted });
      if (i < steps.length - 1) {
        addText(slide, `sequence-arrow-${i}`, ">", { left: left + 216, top: 352, width: 26, height: 40 }, { fontSize: 28, bold: true, color: C.rule, alignment: "center" });
      }
    }
    addStatusBand(slide, "sequence-failure", "The chain stops at step 5: the selected cartridge cannot supply the modeled buoy volume.", 210, 553, 860, "fail");
    addFooter(slide, 3, "Evidence: Technical Analysis Report sections 2, 7-8; Pressure Topology");
  }

  // 4 - Architecture.
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addTitle(slide, "Three subsystems share one continuous mechanical load path", 4);
    await addImage(slide, "architecture-image", "02_CORRECTED_AXIAL_SIDE_SECTION.png", { left: 42, top: 180, width: 780, height: 430 }, "CAD-derived corrected axial side section showing forward ballast, arm module, shortened aft body, and external buoy pack");
    const items = [
      ["FORWARD BODY", "Penetrator and ballast establish the nose-side structural datum."],
      ["ARM POWERTRAIN", "Gas springs, dampers, common crosshead, links, and stops rotate three arms."],
      ["AFT RECOVERY", "Closed/open softgoods, inflator, buoy harness, hardpoint, and HMPE tether."],
    ];
    for (let i = 0; i < items.length; i += 1) {
      const top = 184 + i * 142;
      addText(slide, `architecture-label-${i}`, items[i][0], { left: 864, top, width: 340, height: 30 }, { fontSize: 18, bold: true, color: C.blue });
      addText(slide, `architecture-copy-${i}`, items[i][1], { left: 864, top: top + 38, width: 340, height: 82 }, { fontSize: 18, color: C.ink });
    }
    addFooter(slide, 4, "Evidence: Component Design-Basis Matrix; Source Package 05 design report");
  }

  // 5 - Digital evidence metrics (adapted from Codex Grid slide 19).
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addTitle(slide, "The frozen digital assembly is complete enough to audit rigorously", 5);
    addText(slide, "metrics-intro", "Every claim below is tied to the frozen AP242 masters and their authoring inventories.", { left: 42, top: 174, width: 1196, height: 44 }, { fontSize: 21, color: C.ink });
    addMetric(slide, "metric-occ", "180", "named occurrences in each endpoint state", 42, 252, 278, "pass");
    addMetric(slide, "metric-parts", "92", "unique part definitions", 346, 252, 278, "neutral");
    addMetric(slide, "metric-angles", "81", "modeled arm positions from 0 to 80 degrees", 650, 252, 278, "pass");
    addMetric(slide, "metric-pairs", "697,167", "full-motion exact pair rows", 954, 252, 284, "pass");
    addStatusBand(slide, "metrics-result", "ZERO unauthorized rigid overlaps | ZERO blocked Booleans | ZERO track/fit-register errors", 126, 493, 1028, "pass");
    addText(slide, "metrics-mass", "Mass: 10.583 kg | reserve to 18.14 kg limit: 7.557 kg | rigid length: 1,675.4 mm", { left: 160, top: 566, width: 960, height: 42 }, { fontSize: 21, bold: true, alignment: "center" });
    addFooter(slide, 5, "Evidence: Endpoint Validation Summary; Full Motion Exact Boolean Summary; Mass/CG/Inertia Report");
  }

  // 6 - State integrity and open-pack owner intent.
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addTitle(slide, "The open DEPLOYED pack is controlling intent, not a cleanup defect", 6);
    await addImage(slide, "state-closed", "09_CLOSED_CORDURA_BUOY_PACK.png", { left: 42, top: 182, width: 540, height: 430 }, "CAD-derived closed Cordura buoy pack in STOWED state");
    await addImage(slide, "state-open", "12_OPEN_PACK_INFLATED_BUOY_TETHER_LOAD_PATH.png", { left: 698, top: 182, width: 540, height: 430 }, "CAD-derived owner-intent open pack with inflated buoy and structural tether load path");
    addText(slide, "state-left", "STOWED - separate panels form the closed pack.", { left: 62, top: 622, width: 500, height: 30 }, { fontSize: 17, bold: true });
    addText(slide, "state-right", "DEPLOYED - flaps remain attached; tether bypasses Cordura and hook-and-loop.", { left: 718, top: 622, width: 500, height: 36 }, { fontSize: 17, bold: true });
    addFooter(slide, 6, "Evidence: Screenshot Closure Report images 10-11; CAD views 09 and 12");
  }

  // 7 - Motion result.
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addTitle(slide, "Digital mechanism motion passed every modeled position", 7);
    await addImage(slide, "motion-image", "04_FORWARD_BALLAST_CARRIER_ADJACENCY.png", { left: 42, top: 182, width: 640, height: 438 }, "CAD-derived detail of forward ballast, transition, carrier, and pivot adjacency");
    addMetric(slide, "motion-angle", "0-80°", "one-degree audit coverage", 724, 190, 230, "pass");
    addMetric(slide, "motion-travel", "15.055", "mm crosshead travel", 976, 190, 262, "pass");
    addText(slide, "motion-proof", "- 43,035 rows in the five-angle gate\n- 697,167 rows in the full sweep\n- closure residual: 2.49e-14 mm\n- no invalid or unclassified rigid interference", { left: 740, top: 405, width: 470, height: 176 }, { fontSize: 21, color: C.ink });
    addPanel(slide, "motion-limit-panel", { left: 724, top: 574, width: 514, height: 62 }, C.pale, C.blue, "rounded-lg");
    addText(slide, "motion-limit-text", "Digital PASS does not prove deployment time, loads,\nfatigue, or physical lock capacity.", { left: 738, top: 586, width: 486, height: 38 }, { fontSize: 15, bold: true, color: C.blue, alignment: "center" });
    addFooter(slide, 7, "Evidence: Technical Analysis Report section 5; validation/full_motion");
  }

  // 8 - Gas capacity fail.
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addTitle(slide, "The selected 12 g cartridge can supply only about 11% of the modeled buoy", 8, "CONTROLLING RELEASE FAILURE");
    addText(slide, "gas-explain", "An optimistic ideal-gas calculation already proves the mismatch. Real delivery would be lower because of cooling, residual gas, pressure drop, leakage, and required buoy pressure.", { left: 42, top: 176, width: 1196, height: 66 }, { fontSize: 21 });
    addText(slide, "gas-label-a", "Selected cartridge at 20 C", { left: 90, top: 298, width: 290, height: 32 }, { fontSize: 18, bold: true });
    addPanel(slide, "gas-bar-a-bg", { left: 90, top: 342, width: 1020, height: 64 }, C.faint, C.faint, "rounded-lg");
    addPanel(slide, "gas-bar-a", { left: 90, top: 342, width: 111.5, height: 64 }, C.red, C.red, "rounded-lg");
    addText(slide, "gas-value-a", "6.56 L", { left: 216, top: 354, width: 180, height: 36 }, { fontSize: 25, bold: true, color: C.red });
    addText(slide, "gas-label-b", "Modeled buoy nominal volume", { left: 90, top: 446, width: 330, height: 32 }, { fontSize: 18, bold: true });
    addPanel(slide, "gas-bar-b", { left: 90, top: 490, width: 1020, height: 64 }, C.blue, C.blue, "rounded-lg");
    addText(slide, "gas-value-b", "60.0 L", { left: 1120, top: 502, width: 100, height: 36 }, { fontSize: 25, bold: true, color: C.blue, alignment: "right" });
    addStatusBand(slide, "gas-fail", "FAIL: ideal lower-bound CO2 mass is 109.8 g, before real losses and overpressure.", 188, 594, 904, "fail");
    addFooter(slide, 8, "Evidence: Technical Analysis Report section 2; Stored Gas Independent Calculation");
  }

  // 9 - Inflator/pressure definition.
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addTitle(slide, "The pressure path is compact, but its exact installed interfaces are unresolved", 9);
    await addImage(slide, "pressure-image", "10_PACK_SECTION_INFLATOR_WATER_ACCESS.png", { left: 42, top: 180, width: 610, height: 450 }, "CAD-derived pack section showing Hydro 1F proxy and direct water-entry access");
    const rows = [
      ["KNOWN", "Leland 81121: 12 g CO2, 3/8-24 puncture cartridge", "pass"],
      ["KNOWN", "Hydro 1F family uses V80040 water-sensitive bobbin", "pass"],
      ["OPEN", "Exact Hydro suffix and matching thread configuration", "fail"],
      ["OPEN", "Vendor-exact geometry, flow curve, patch interface, leak result", "fail"],
    ];
    for (let i = 0; i < rows.length; i += 1) {
      const top = 190 + i * 104;
      const kind = rows[i][2];
      addStatusBand(slide, `pressure-status-${i}`, rows[i][0], 698, top, 112, kind);
      addText(slide, `pressure-copy-${i}`, rows[i][1], { left: 836, top: top + 8, width: 386, height: 70 }, { fontSize: 18, color: C.ink });
    }
    addText(slide, "pressure-topology", "Topology: cartridge -> Hydro 1F family inflator -> custom 60 L buoy patch. No separate hose, tube, regulator, gauge, or pneumatic cylinder remains in this configuration.", { left: 698, top: 604, width: 524, height: 54 }, { fontSize: 16, color: C.muted });
    addFooter(slide, 9, "Evidence: Pressure Topology; Port-to-Port Table; Pressure Ratings Matrix");
  }

  // 10 - Make/buy and manufacturing readiness.
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addTitle(slide, "The current configuration is custom-heavy and not fabrication-ready", 10);
    addMetric(slide, "make-buy", "79 MAKE", "custom definitions requiring released manufacturing control", 42, 190, 352, "fail");
    addMetric(slide, "buy-count", "13 BUY", "catalog or supplier-derived definitions", 430, 190, 352, "neutral");
    addMetric(slide, "part-export", "123", "AP242/BREP/render state definitions delivered", 818, 190, 420, "pass");
    addText(slide, "manufacturing-open", "Fabrication remains prohibited because the package does not contain approved dimensioned drawings, GD&T, tolerance stacks, process capability, torque/locking data, or validated tool access.", { left: 42, top: 424, width: 740, height: 118 }, { fontSize: 23, color: C.ink });
    addPanel(slide, "manufacturing-panel", { left: 836, top: 424, width: 402, height: 174 }, C.redPale, C.red);
    addText(slide, "manufacturing-panel-title", "COTS-first objective", { left: 858, top: 446, width: 354, height: 30 }, { fontSize: 20, bold: true, color: C.red });
    addText(slide, "manufacturing-panel-copy", "No complete, orderable commercial inflation module has passed geometry, interface, gas-capacity, and application gates.", { left: 858, top: 494, width: 354, height: 86 }, { fontSize: 19 });
    addStatusBand(slide, "manufacturing-status", "NO PURCHASE OR FABRICATION AUTHORIZED", 180, 592, 920, "fail");
    addFooter(slide, 10, "Evidence: Full BOM; Make/Buy Trade Study; Manufactured-Part Drawing Register");
  }

  // 11 - Critical risks and tests.
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addTitle(slide, "Release now depends on physical evidence and an architecture correction", 11);
    const items = [
      ["1", "Correct inflation architecture", "Select a complete cartridge/inflator/buoy combination that passes capacity and rated-interface gates."],
      ["2", "Define loads and release drawings", "Control mission, impact, proof, life, tolerance, torque, material, finish, and inspection requirements."],
      ["3", "Qualify the physical product", "Wet opening, inflation, leak, proof/burst, buoyancy/stability, dynamic, fatigue, corrosion, and assembly trials."],
    ];
    for (let i = 0; i < items.length; i += 1) {
      const top = 190 + i * 142;
      addText(slide, `risk-number-${i}`, items[i][0], { left: 66, top, width: 58, height: 64 }, { fontSize: 42, bold: true, color: C.red });
      addText(slide, `risk-title-${i}`, items[i][1], { left: 150, top: top + 2, width: 390, height: 38 }, { fontSize: 22, bold: true });
      addText(slide, `risk-copy-${i}`, items[i][2], { left: 150, top: top + 48, width: 470, height: 76 }, { fontSize: 18, color: C.muted });
      addRule(slide, `risk-rule-${i}`, 66, top + 128, 554, C.rule, 1);
    }
    addPanel(slide, "risk-test-panel", { left: 688, top: 190, width: 550, height: 410 }, C.faint, C.rule);
    addText(slide, "risk-test-title", "Minimum physical test families", { left: 716, top: 216, width: 494, height: 36 }, { fontSize: 23, bold: true });
    addText(slide, "risk-test-list", "- inflation architecture and cold/hot delivery\n- wet pack opening and extraction\n- buoy proof, burst, leak, lift, and stability\n- arm/lock/hardpoint/tether structural proof\n- dynamic deployment and handling/drop\n- fatigue, wear, corrosion, UV, humidity, storage\n- realistic assembly, service, reset, and inspection", { left: 716, top: 282, width: 472, height: 270 }, { fontSize: 20, color: C.ink });
    addFooter(slide, 11, "Evidence: Risk Register/FMEA; Physical Verification Plan");
  }

  // 12 - Release gates.
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addTitle(slide, "Digital pass; production release fails", 12);
    addPanel(slide, "gate-pass-panel", { left: 42, top: 186, width: 552, height: 422 }, C.greenPale, C.green);
    addText(slide, "gate-pass-title", "DIGITAL PASS", { left: 70, top: 214, width: 496, height: 44 }, { fontSize: 26, bold: true, color: C.green });
    addText(slide, "gate-pass-list", "- clean procedural build\n- 180 occurrences per state\n- hierarchy, occurrence identities, transforms, and valid solids preserved on reimport\n- nominal envelope and mass properties\n- endpoint exact-Boolean audit\n- five-angle audit\n- full 0-80 degree one-degree sweep", { left: 70, top: 286, width: 480, height: 286 }, { fontSize: 19, color: C.ink });
    addPanel(slide, "gate-fail-panel", { left: 644, top: 186, width: 594, height: 422 }, C.redPale, C.red);
    addText(slide, "gate-fail-title", "RELEASE FAIL", { left: 674, top: 214, width: 534, height: 44 }, { fontSize: 26, bold: true, color: C.red });
    addText(slide, "gate-fail-list", "- 12 g / 60 L gas-capacity mismatch\n- inflator suffix, exact geometry, ratings, and leak/flow unknown\n- proxy and developmental softgood envelopes\n- required load/strength/tolerance analyses incomplete\n- manufacturing drawings and work instructions absent\n- physical qualification absent\n- AP242 bytes not reproducible across identical builds\n- root assembly naming nonconformance remains open\n- required screenshots and newer attachment placeholders absent", { left: 674, top: 286, width: 520, height: 306 }, { fontSize: 18, color: C.ink });
    addFooter(slide, 12, "Evidence: Objective Release Gate Table; Non-Release Exception Report");
  }

  // 13 - Decision and next action.
  {
    const slide = deck.slides.add();
    slide.background.fill = C.white;
    addText(slide, "close-eyebrow", "DECISION", { left: 42, top: 42, width: 280, height: 28 }, { fontSize: 13, bold: true, color: C.muted });
    addText(slide, "close-title", "Do not release this configuration", { left: 42, top: 114, width: 850, height: 92 }, { fontSize: 50, bold: true });
    addText(slide, "close-copy", "Use the frozen digital package as a controlled engineering baseline. Correct the inflation architecture first; then define loads, complete manufacturing definition, qualify the physical product, and rerun independent review.", { left: 42, top: 242, width: 810, height: 134 }, { fontSize: 25, color: C.ink });
    addStatusBand(slide, "close-status", "AUTHORIZATION: ENGINEERING REVIEW ONLY", 42, 426, 630, "neutral");
    addText(slide, "close-prohibitions", "No fabrication. No purchase. No qualification acceptance. No field use. No merge to main.", { left: 42, top: 514, width: 760, height: 78 }, { fontSize: 22, bold: true, color: C.red });
    addPanel(slide, "close-panel", { left: 900, top: 114, width: 338, height: 478 }, C.faint, C.rule);
    addText(slide, "close-panel-title", "Next gate", { left: 930, top: 150, width: 278, height: 36 }, { fontSize: 23, bold: true, color: C.blue });
    addText(slide, "close-panel-copy", "Bring back one complete, orderable, source-supported inflation module and a controlled 60 L requirement. If none passes, stop with a measured architecture decision.", { left: 930, top: 218, width: 278, height: 222 }, { fontSize: 21, color: C.ink });
    addText(slide, "close-panel-proof", "Digital baseline retained:\n- STOWED / DEPLOYED AP242\n- 92 unique parts\n- 123 state definitions\n- full 81-position audit", { left: 930, top: 462, width: 278, height: 110 }, { fontSize: 17, color: C.muted });
    addFooter(slide, 13, "Evidence: Release Index; Make/Buy Trade Study; Physical Verification Plan");
  }

  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(path.join(QA, `${stem}.png`), await deck.export({ slide, format: "png", scale: 1 }));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(QA, `${stem}.layout.json`), await layout.text());
  }
  await writeBlob(path.join(QA, "deck-montage.webp"), await deck.export({ format: "webp", montage: true, scale: 1 }));
  const inspect = await deck.inspect({ kind: "slide,textbox,shape,image", maxChars: 50000 });
  await fs.writeFile(path.join(QA, "deck-inspect.ndjson"), inspect.ndjson);
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(path.join(OUT, "STINGRAY_EXECUTIVE_STAKEHOLDER_RELEASE_STATUS.pptx"));
}


buildDeck().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
