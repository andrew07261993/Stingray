import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const here = path.dirname(fileURLToPath(import.meta.url));
const packageRoot = path.resolve(here, "..");
const repoRoot = path.resolve(packageRoot, "../../..");
const qaRoot = path.join(here, "qa");
const pptxPath = path.join(packageRoot, "STINGRAY_I5S_DF8_MECHANICAL_BREAKDOWN_PER_PART.pptx");
const manifestPath = path.join(packageRoot, "manifests", "per_part_render_manifest.json");
const factsPath = path.join(packageRoot, "source_notes", "source_facts.json");
const validationPath = path.join(packageRoot, "manifests", "per_part_render_validation.json");
const tmpDir = process.env.TMP_DIR || os.tmpdir();

const manifest = JSON.parse(await fs.readFile(manifestPath, "utf8"));
const facts = JSON.parse(await fs.readFile(factsPath, "utf8"));
const renderValidation = JSON.parse(await fs.readFile(validationPath, "utf8"));
const included = manifest.filter((row) => row.included === true && row.render_status === "RENDERED");

const W = 1280;
const H = 720;
const COLORS = {
  navy: "#10283A",
  navy2: "#173F57",
  blue: "#0C6E91",
  teal: "#008B8B",
  ink: "#162632",
  slate: "#4E5E69",
  muted: "#71808A",
  line: "#CBD4DA",
  panel: "#EEF2F4",
  panel2: "#F7F9FA",
  white: "#FFFFFF",
  amber: "#B66A00",
  red: "#A7342C",
  green: "#25724B",
};
const FONT = "Aptos";
const subsystemOrder = [
  "Body structure",
  "Water activation",
  "Gas / inflation path",
  "Arm deployment / activation",
  "Body ejection / buoy extraction",
  "Load path / recovery attachment",
];

function pos(left, top, width, height) {
  return { left, top, width, height };
}

function addText(slide, text, position, style = {}, name = undefined) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    ...(name ? { name } : {}),
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontFamily: FONT,
    fontSize: 22,
    color: COLORS.ink,
    ...style,
  };
  return shape;
}

function addRect(slide, position, fill, line = COLORS.line, radius = false, name = undefined) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    ...(name ? { name } : {}),
    position,
    fill,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : 1 },
    ...(radius ? { borderRadius: "rounded-xl" } : {}),
  });
}

function addPill(slide, text, left, top, fill = COLORS.navy2, width = 88) {
  addRect(slide, pos(left, top, width, 30), fill, "none", true);
  addText(slide, text, pos(left, top + 1, width, 26), {
    fontSize: 16,
    bold: true,
    color: COLORS.white,
    alignment: "center",
  });
}

function setNotes(slide, sources, presenter = "") {
  const lines = [];
  if (presenter) lines.push(presenter, "");
  lines.push("[Sources]", ...sources.map((source) => `- ${source}`));
  slide.speakerNotes.textFrame.setText(lines.join("\n"));
  slide.speakerNotes.setVisible(true);
}

function addFooter(slide, slideNumber, label = "STINGRAY I5-S DF8 | Engineering review") {
  addRect(slide, pos(72, 675, 1136, 1), COLORS.line, "none");
  addText(slide, label, pos(72, 683, 900, 22), { fontSize: 15, color: COLORS.muted });
  addText(slide, String(slideNumber).padStart(2, "0"), pos(1138, 683, 70, 22), {
    fontSize: 15,
    bold: true,
    color: COLORS.navy,
    alignment: "right",
  });
}

function addHeader(slide, title, eyebrow, slideNumber, accent = COLORS.blue, titleFontSize = 46) {
  slide.background.fill = COLORS.white;
  addText(slide, eyebrow.toUpperCase(), pos(72, 38, 760, 24), {
    fontSize: 16,
    bold: true,
    color: accent,
    characterSpacing: 1,
  });
  addText(slide, title, pos(72, 67, 1080, 58), {
    fontSize: titleFontSize,
    bold: true,
    color: COLORS.navy,
  });
  addRect(slide, pos(72, 124, 1136, 2), accent, "none");
  addFooter(slide, slideNumber);
}

async function imageBytes(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function addImage(slide, filePath, position, alt, fit = "contain") {
  return slide.images.add({
    blob: await imageBytes(filePath),
    contentType: "image/png",
    alt,
    fit,
    position,
  });
}

function bullets(items) {
  return items.map((item) => `• ${item}`).join("\n");
}

function addBulletBlock(slide, title, items, position, accent = COLORS.blue) {
  addText(slide, title, pos(position.left, position.top, position.width, 34), {
    fontSize: 25,
    bold: true,
    color: accent,
  });
  addText(slide, bullets(items), pos(position.left, position.top + 46, position.width, position.height - 46), {
    fontSize: 22,
    color: COLORS.ink,
    lineSpacing: 1.15,
  });
}

function addMetric(slide, value, label, left, top, width, accent = COLORS.blue, valueFontSize = 54) {
  addText(slide, value, pos(left, top, width, 66), {
    fontSize: valueFontSize,
    bold: true,
    color: accent,
  });
  addRect(slide, pos(left, top + 67, Math.min(width, 104), 3), accent, "none");
  addText(slide, label, pos(left, top + 82, width, 74), {
    fontSize: 21.5,
    color: COLORS.slate,
  });
}

function contextPath(stem) {
  return path.join(here, "context_views", stem);
}

function sourceRef(relative) {
  return `${relative} @ ${facts.source_commit_sha}`;
}

const presentation = Presentation.create({ slideSize: { width: W, height: H } });
let slideNumber = 0;

// 1 — title
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  slide.background.fill = COLORS.navy;
  addText(slide, "STINGRAY I5-S DF8", pos(72, 84, 535, 74), {
    fontSize: 54,
    bold: true,
    color: COLORS.white,
  });
  addText(slide, "Mechanical breakdown", pos(72, 171, 535, 58), {
    fontSize: 43,
    bold: true,
    color: "#A8D9E8",
  });
  addText(slide, "Deterministic per-part CAD render set", pos(72, 246, 520, 70), {
    fontSize: 25,
    color: "#D9E8EF",
  });
  addText(slide, "121 unique source definitions  •  116 rendered  •  exact B-rep geometry", pos(72, 545, 535, 58), {
    fontSize: 21.5,
    color: "#D9E8EF",
  });
  addRect(slide, pos(638, 0, 642, 720), COLORS.panel, "none");
  await addImage(slide, contextPath("AFTER_IMAGE_01_PRODUCT_BOUNDARY.png"), pos(655, 54, 595, 612), "Source-derived DF8 product boundary view");
  addText(slide, "SOURCE-BACKED ENGINEERING REVIEW", pos(72, 635, 480, 24), {
    fontSize: 16,
    bold: true,
    color: "#6FC2D8",
    characterSpacing: 1,
  });
  setNotes(slide, [
    sourceRef("work/r2_source/build_r2.py"),
    sourceRef("work/final_analysis/authoring_inventory_stowed.json"),
    "slides/context_views/AFTER_IMAGE_01_PRODUCT_BOUNDARY.png — deterministic source-derived assembly context view",
    "manifests/per_part_render_manifest.json — current unique-definition and render counts",
  ]);
}

// 2 — purpose / scope
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Purpose and scope", "Review basis", slideNumber);
  addMetric(slide, "121", "Unique authoritative PartDefs", 72, 168, 240);
  addMetric(slide, "116", "Included source-derived PNGs", 340, 168, 250, COLORS.teal);
  addMetric(slide, "5", "Standard-fastener exclusions", 618, 168, 250, COLORS.amber);
  addMetric(slide, "0", "O-ring exclusions", 896, 168, 240, COLORS.green);
  addBulletBlock(slide, "What this package proves", [
    "Every included tile resolves to one current exact PartDef B-rep.",
    "MAKE and BUY definitions are retained at their controlled source fidelity.",
    "The deck explains mechanism intent while keeping open validation items open.",
  ], pos(72, 390, 535, 220));
  addBulletBlock(slide, "What it does not claim", [
    "No AI-generated geometry, artist approximation, or screenshot substitution.",
    "No release authorization, physical qualification, or manufacturing sign-off.",
    "No completion claim beyond the accepted 0°–55° motion checkpoint.",
  ], pos(650, 390, 558, 220), COLORS.red);
  setNotes(slide, [
    "manifests/per_part_render_manifest.json",
    "manifests/per_part_render_validation.json",
    sourceRef("work/final_analysis/manual_inspection_checkpoint/CAD_INSPECTION_STATUS.txt"),
  ]);
}

// 3 — system overview
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "System overview", "Architecture", slideNumber);
  await addImage(slide, contextPath("AFTER_IMAGE_02_DEPLOYED_COHESION.png"), pos(625, 148, 583, 494), "Source-derived deployed cohesion view");
  addBulletBlock(slide, "Integrated mechanical system", [
    "Slender 53.0 mm body envelope with forward penetrator, arm module, and aft ejection closure.",
    "Three 733.806 mm arms share one guided crosshead and paired root links at 0° / 120° / 240° clocking.",
    "Water activation initiates puncture and full-flow routing; spring-ejector hardware extracts the buoy package.",
    "Harness, tether, thimbles, pins, and hardpoint maintain a continuous recovery load path.",
  ], pos(72, 158, 505, 450));
  addText(slide, "Endpoint view: 80° deployed configuration", pos(666, 617, 500, 24), {
    fontSize: 16,
    bold: true,
    color: COLORS.muted,
    alignment: "right",
  });
  setNotes(slide, [
    sourceRef("work/final_analysis/authoring_manifest.json"),
    sourceRef("work/final_analysis/authoring_inventory_deployed.json"),
    "slides/context_views/AFTER_IMAGE_02_DEPLOYED_COHESION.png",
  ]);
}

// 4 — overall architecture
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Overall architecture", "Three zones + one load path", slideNumber);
  await addImage(slide, contextPath("AFTER_IMAGE_01_PRODUCT_BOUNDARY.png"), pos(72, 150, 612, 490), "Source-derived DF8 overall product boundary");
  const zones = [
    ["01", "Forward", "Nose, ballast, water inlet, trigger hardware, cartridge and booster collection."],
    ["02", "Arm module", "Structural rings/longerons, common crosshead, links, arms, actuator, damper and backup spring."],
    ["03", "Aft", "Full-flow terminal, spring ejector, follower, latch/sear, buoy, door and recovery termination."],
    ["→", "Recovery", "Buoy gores → harness bands/legs → terminal → tether/thimbles → rigid hardpoint."],
  ];
  zones.forEach((zone, i) => {
    const top = 155 + i * 119;
    addText(slide, zone[0], pos(724, top, 54, 44), { fontSize: 28, bold: true, color: COLORS.blue });
    addText(slide, zone[1], pos(790, top, 350, 34), { fontSize: 25, bold: true, color: COLORS.navy });
    addText(slide, zone[2], pos(790, top + 38, 418, 68), { fontSize: 18.5, color: COLORS.slate, lineSpacing: 1 });
    if (i < zones.length - 1) addRect(slide, pos(724, top + 108, 484, 1), COLORS.line, "none");
  });
  setNotes(slide, [
    sourceRef("work/r2_source/r2_hierarchy.py"),
    sourceRef("work/final_analysis/authoring_inventory_stowed.json"),
    "slides/context_views/AFTER_IMAGE_01_PRODUCT_BOUNDARY.png",
  ]);
}

// 5 — operating sequence
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Mechanical operating sequence", "Source-defined order", slideNumber);
  const steps = [
    ["01", "Wet", "Water reaches the screened inlet and source-controlled bobbin housing."],
    ["02", "Release", "The water-sensitive trigger chain releases the puncture action."],
    ["03", "Open flow", "Cartridge puncture feeds the collection path, check valve and full-flow route."],
    ["04", "Deploy arms", "GS-19, HBD and backup spring act through the guided crosshead and link pairs."],
    ["05", "Eject buoy", "Latch/sear release lets the guided ejector spring drive the follower and open the captive door."],
    ["06", "Carry load", "Inflated buoy load transfers through harness, terminal, tether and rigid hardpoint."],
  ];
  // Connector rules are authored before nodes.
  addRect(slide, pos(112, 244, 1052, 4), COLORS.line, "none");
  addRect(slide, pos(112, 488, 1052, 4), COLORS.line, "none");
  steps.forEach((step, i) => {
    const row = i < 3 ? 0 : 1;
    const col = i % 3;
    const left = 72 + col * 378;
    const top = row === 0 ? 158 : 402;
    addRect(slide, pos(left + 25, top + 67, 40, 40), COLORS.blue, "none", true);
    addText(slide, step[0], pos(left + 25, top + 73, 40, 26), { fontSize: 16, bold: true, color: COLORS.white, alignment: "center" });
    addText(slide, step[1], pos(left + 82, top + 52, 265, 34), { fontSize: 25, bold: true, color: COLORS.navy });
    addText(slide, step[2], pos(left + 82, top + 88, 270, 105), { fontSize: 21.5, color: COLORS.slate });
  });
  setNotes(slide, [
    sourceRef("work/r2_source/build_r2.py"),
    sourceRef("work/final_analysis/authoring_inventory_stowed.json"),
    sourceRef("work/final_analysis/authoring_inventory_deployed.json"),
  ], "The endpoint CAD defines configuration and interfaces; this slide does not assert event timing or measured performance.");
}

// 6 — body structure
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Subassembly: body structure", "Mechanism support", slideNumber);
  await addImage(slide, contextPath("AFTER_IMAGE_05_ROOT_ROUTE_CLEARANCE.png"), pos(650, 154, 558, 470), "Source-derived root and route clearance view");
  addBulletBlock(slide, "How the structure works", [
    "Forward and aft titanium shells close the 53.0 mm normal body envelope around exact local apertures and hardpoints.",
    "Longerons and structural rings establish body stations, react actuator/spring loads, and carry deployment interfaces.",
    "Routed rings and local passages constrain gas/control lines without replacing their explicit termination definitions.",
    "The rigid stowed length is 2031.000 mm against a 2032 mm maximum.",
  ], pos(72, 160, 520, 435));
  setNotes(slide, [
    sourceRef("CURRENT_STATE.json"),
    sourceRef("work/final_analysis/authoring_manifest.json"),
    "slides/context_views/AFTER_IMAGE_05_ROOT_ROUTE_CLEARANCE.png",
  ]);
}

// 7 — water activation
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Subassembly: water activation", "Initiation chain", slideNumber, COLORS.teal);
  await addImage(slide, contextPath("AFTER_IMAGE_04_WATER_PORT.png"), pos(620, 150, 588, 490), "Source-derived water-port section");
  addBulletBlock(slide, "Mechanical function", [
    "A screened inlet admits water to the controlled trigger housing while preserving the body interface.",
    "The Halkey-Roberts V80040 bobbin is the source-controlled water-sensitive element represented in the model.",
    "Housing and cap locate the bobbin and transfer its release into the puncture/activation chain.",
    "The deck shows interface intent only; no wet-time, salinity, contamination, or environmental qualification is asserted.",
  ], pos(72, 160, 500, 425), COLORS.teal);
  setNotes(slide, [
    sourceRef("work/final_analysis/authoring_inventory_stowed.json"),
    sourceRef("work/r2_source/build_r2.py"),
    "slides/context_views/AFTER_IMAGE_04_WATER_PORT.png",
  ]);
}

// 8 — gas / inflation
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Subassembly: gas / inflation path", "Pressure and control routing", slideNumber, COLORS.teal);
  await addImage(slide, contextPath("AFTER_IMAGE_09_ROUTE_AND_SEAR.png"), pos(632, 150, 576, 490), "Source-derived routed full-flow and sear context");
  addBulletBlock(slide, "Mechanical function", [
    "The Leland 81121 cartridge is punctured into a defined collection path; booster reservoirs provide distributed modeled gas volume.",
    "A check-valve branch enforces one-way flow before the direct full-flow valve and aft terminal manifold.",
    "Exact route definitions carry gas, pilot pressure, and Bowden control between named terminations and supports.",
    "Pressure continuity and engagement are modeled; proof, leakage, and flow-rate performance remain separate qualification activities.",
  ], pos(72, 160, 515, 445), COLORS.teal);
  setNotes(slide, [
    sourceRef("work/r2_source/build_r2.py"),
    sourceRef("work/final_analysis/authoring_inventory_stowed.json"),
    "slides/context_views/AFTER_IMAGE_09_ROUTE_AND_SEAR.png",
  ]);
}

// 9 — arm deployment
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Subassembly: arm deployment / activation", "Common powertrain", slideNumber);
  await addImage(slide, contextPath("AFTER_IMAGE_06_CROSSHEAD_RETENTION.png"), pos(624, 146, 584, 250), "Source-derived crosshead and retention view");
  await addImage(slide, contextPath("AFTER_IMAGE_08_ACTUATOR_SPRING.png"), pos(624, 408, 584, 240), "Source-derived actuator, damper and spring view");
  addBulletBlock(slide, "Mechanical function", [
    "The GS-19 powered stroke, HBD damping path, and guided backup spring converge on one six-clevis crosshead.",
    "Crosshead translation drives paired short links, converting axial motion into three synchronized arm-root rotations.",
    "Double-shear pivot stacks, guide shaft/spider, stop pads and fixed stops control alignment and endpoint geometry.",
    "Stow dogs retain transport position; spring-driven lock dogs engage the positive deployed stop interface at the 80° endpoint.",
    "The source closure law gives 15.055 mm crosshead travel, above the 15.050 mm minimum.",
  ], pos(72, 148, 515, 495));
  setNotes(slide, [
    sourceRef("work/r2_source/build_r2.py"),
    sourceRef("work/final_analysis/authoring_manifest.json"),
    "slides/context_views/AFTER_IMAGE_06_CROSSHEAD_RETENTION.png",
    "slides/context_views/AFTER_IMAGE_08_ACTUATOR_SPRING.png",
  ]);
}

// 10 — ejection
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Subassembly: body ejection / buoy extraction", "Later-phase mechanism", slideNumber, COLORS.amber);
  await addImage(slide, contextPath("AFTER_IMAGE_02_DEPLOYED_COHESION.png"), pos(630, 150, 578, 490), "Source-derived deployed buoy extraction context");
  addBulletBlock(slide, "Mechanical function", [
    "A captive latch/sear retains the follower and the stored energy of the guided long-stroke ejector spring.",
    "On release, the follower travels on anti-rotation rails and telescoping guide sleeves, pushing the buoy package aft.",
    "The low-force aft door rotates about its retained hinge pin and remains captive by lanyard.",
    "Eight source-defined gores form the 60 L buoy envelope; deployment geometry is modeled separately from the arm sweep.",
  ], pos(72, 160, 520, 445), COLORS.amber);
  setNotes(slide, [
    sourceRef("work/r2_source/build_r2.py"),
    sourceRef("work/final_analysis/authoring_inventory_deployed.json"),
    "slides/context_views/AFTER_IMAGE_02_DEPLOYED_COHESION.png",
  ]);
}

// 11 — recovery load path
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Subassembly: load path / recovery attachment", "Continuous structural chain", slideNumber, COLORS.green);
  await addImage(slide, contextPath("AFTER_IMAGE_03_TERMINAL_CHAIN.png"), pos(615, 150, 593, 490), "Source-derived terminal and recovery-chain context");
  addBulletBlock(slide, "Mechanical function", [
    "Two closed harness bands and four terminal legs collect the buoy membrane load into the structural terminal.",
    "Double-shear pins, external retainers and thimbles preserve named, serviceable connections at both tether ends.",
    "The HMPE recovery tether transfers load to the rigid aft hardpoint ring without relying on the door or follower as the terminal structure.",
    "CAD connectivity and attachment evidence are source-defined; physical proof load remains a separate validation activity.",
  ], pos(72, 160, 505, 440), COLORS.green);
  setNotes(slide, [
    sourceRef("work/r2_source/build_r2.py"),
    sourceRef("work/final_analysis/validation_cycle2/definition_of_done_audit.json"),
    "slides/context_views/AFTER_IMAGE_03_TERMINAL_CHAIN.png",
  ]);
}

// 12 — mass properties
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Center of gravity / mass properties", "Current source calculation", slideNumber);
  const stowed = facts.mass_properties.stowed;
  const deployed = facts.mass_properties.deployed;
  const sCg = stowed.center_of_gravity_mm_in_master_frame;
  const dCg = deployed.center_of_gravity_mm_in_master_frame;
  addMetric(slide, `${stowed.system_mass_kg.toFixed(3)} kg`, "System mass", 72, 170, 250);
  addMetric(slide, `${facts.mass_reconciliation.source_derived_mass_reserve_kg.toFixed(3)} kg`, "Reserve to 18.14 kg limit", 350, 170, 270, COLORS.green);
  addMetric(slide, `${sCg.z.toFixed(1)} mm`, "STOWED CG — master Z", 650, 170, 245, COLORS.teal);
  addMetric(slide, `${dCg.z.toFixed(1)} mm`, "DEPLOYED CG — master Z", 930, 170, 250, COLORS.amber);
  addRect(slide, pos(72, 396, 1136, 1), COLORS.line, "none");
  addText(slide, "Computed CAD CG", pos(72, 426, 330, 34), { fontSize: 25, bold: true, color: COLORS.navy });
  addText(slide, `STOWED  X ${sCg.x.toFixed(3)}  |  Y ${sCg.y.toFixed(3)}  |  Z ${sCg.z.toFixed(3)} mm\nDEPLOYED X ${dCg.x.toFixed(3)}  |  Y ${dCg.y.toFixed(3)}  |  Z ${dCg.z.toFixed(3)} mm`, pos(72, 470, 550, 92), {
    fontSize: 23,
    color: COLORS.ink,
    bold: true,
  });
  addText(slide, "Method", pos(690, 426, 200, 34), { fontSize: 25, bold: true, color: COLORS.navy });
  addText(slide, `Mass-weighted global volume centroid of every current occurrence B-rep, using the validator’s committed mass precedence. CURRENT_STATE metadata is ${(facts.mass_reconciliation.absolute_difference_kg * 1000).toFixed(3)} g higher; exact source controls. CAD calculation only.`, pos(690, 470, 500, 126), {
    fontSize: 21.5,
    color: COLORS.slate,
  });
  setNotes(slide, [
    "source_notes/source_facts.json — regenerated exact-occurrence CG calculation",
    sourceRef("CURRENT_STATE.json"),
    sourceRef("work/final_analysis/authoring_inventory_stowed.json"),
    sourceRef("work/final_analysis/authoring_inventory_deployed.json"),
  ]);
}

// 13 — analyses
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Analyses that drove the design", "Evidence hierarchy", slideNumber);
  const blocks = [
    ["Kinematics", "Closed-form arm/crosshead relation, 80° endpoint, 15.055 mm travel, and 1° motion-track definitions."],
    ["Force / rate control", "WP02 spring trade, force-versus-position, actuator choice and HBD damping concept informed the common powertrain."],
    ["Geometry integrity", "Endpoint B-rep validity, state parity, occurrence/BOM reconciliation, attachment and route topology checks."],
    ["Packaging / mass", "57.15 mm hard arm-module OD, 53.0 mm body target, 2032 mm rigid-length limit and 18.14 kg mass ceiling."],
  ];
  blocks.forEach((block, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const left = 72 + col * 578;
    const top = 158 + row * 238;
    addRect(slide, pos(left, top, 548, 205), row === 0 ? COLORS.panel2 : COLORS.panel, COLORS.line, false);
    addText(slide, block[0], pos(left + 28, top + 26, 490, 38), { fontSize: 27, bold: true, color: COLORS.blue });
    addText(slide, block[1], pos(left + 28, top + 79, 490, 100), { fontSize: 21.5, color: COLORS.slate });
  });
  addText(slide, "WP02 is retained as design-input history; current release claims are controlled by the final R2 source and validation state.", pos(72, 630, 1136, 30), {
    fontSize: 18,
    bold: true,
    color: COLORS.red,
    alignment: "center",
  });
  setNotes(slide, [
    sourceRef("work/input/wp02/STINGRAY_I5S_DF8_WP02_ARM_AND_POWERTRAIN/06_ENGINEERING_ANALYSIS/WP02_KINEMATIC_REGISTER.csv"),
    sourceRef("work/input/wp02/STINGRAY_I5S_DF8_WP02_ARM_AND_POWERTRAIN/06_ENGINEERING_ANALYSIS/WP02_SPRING_TRADE_AND_CORRECTION.csv"),
    sourceRef("work/input/wp02/STINGRAY_I5S_DF8_WP02_ARM_AND_POWERTRAIN/06_ENGINEERING_ANALYSIS/WP02_DYNAMIC_CASE_RESULTS.csv"),
    sourceRef("work/final_analysis/authoring_manifest.json"),
    sourceRef("work/final_analysis/state_parity_provenance_audit/state_parity_provenance_summary.json"),
  ]);
}

// 14 — status / limitations
{
  const slide = presentation.slides.add();
  slideNumber += 1;
  addHeader(slide, "Validation / current status / limitations", "Fail-closed release posture", slideNumber, COLORS.red);
  addMetric(slide, `${facts.validation.state_parity_occurrence_pass_count}/${facts.validation.state_parity_occurrence_count}`, "State-parity occurrences pass", 72, 165, 255, COLORS.green);
  addMetric(slide, "0°–55°", "Accepted automated checkpoint", 355, 165, 255, COLORS.teal);
  addMetric(slide, "56°–80°", "Not accepted as completed", 638, 165, 255, COLORS.amber);
  addMetric(slide, "NOT RELEASED", "Current package disposition", 920, 165, 265, COLORS.red, 36);
  addBulletBlock(slide, "What is current", [
    "Exact STOWED and DEPLOYED AP242 files and 121-definition authoring inventories are source-bound.",
    "All 116 requested PartDef renders pass filename, hash, size, format and manifest checks.",
    "State-parity provenance audit resolves all 279 rows.",
  ], pos(72, 400, 545, 220), COLORS.green);
  addBulletBlock(slide, "What remains open", [
    "Full 0°–80° motion acceptance; final validator stopped during post-merge schema checking.",
    "Physical/environmental qualification, calibrated damping performance and manufacturing qualification.",
    "Release gate computation and owner acceptance in the approved venue.",
  ], pos(660, 400, 548, 220), COLORS.red);
  setNotes(slide, [
    sourceRef("work/final_analysis/manual_inspection_checkpoint/CAD_INSPECTION_STATUS.txt"),
    sourceRef("work/final_analysis/state_parity_provenance_audit/state_parity_provenance_summary.json"),
    sourceRef("CURRENT_STATE.json"),
    "manifests/per_part_render_validation.json",
  ]);
}

// 15+ — source-derived part definitions, two per slide for engineering readability.
for (const subsystem of subsystemOrder) {
  const rows = included
    .filter((row) => row.subsystem === subsystem)
    .sort((a, b) => a.part_number.localeCompare(b.part_number));
  const pageCount = Math.ceil(rows.length / 2);
  for (let page = 0; page < pageCount; page += 1) {
    const slide = presentation.slides.add();
    slideNumber += 1;
    const accent = subsystem.includes("Water") || subsystem.includes("Gas") ? COLORS.teal
      : subsystem.includes("ejection") ? COLORS.amber
      : subsystem.includes("Load") ? COLORS.green
      : COLORS.blue;
    const partPageTitle = `${subsystem} — Part definitions ${page + 1}/${pageCount}`;
    const partPageTitleFontSize = subsystem === "Body ejection / buoy extraction" && page >= 9 ? 40 : 46;
    addHeader(slide, partPageTitle, "Per-part exact B-rep", slideNumber, accent, partPageTitleFontSize);
    const pageRows = rows.slice(page * 2, page * 2 + 2);
    for (let slot = 0; slot < pageRows.length; slot += 1) {
      const row = pageRows[slot];
      const top = slot === 0 ? 148 : 405;
      if (slot === 1) addRect(slide, pos(72, 386, 1136, 1), COLORS.line, "none");
      const renderFile = path.resolve(repoRoot, row.render_png_path);
      await addImage(slide, renderFile, pos(72, top, 386, 224), `${row.part_number}: ${row.part_name}`);
      addPill(slide, row.classification, 486, top + 1, row.classification === "BUY" ? COLORS.teal : COLORS.navy2, 86);
      addPill(slide, row.geometry_state, 584, top + 1, COLORS.slate, 108);
      addText(slide, row.part_number, pos(486, top + 41, 696, 38), {
        fontSize: 26,
        bold: true,
        color: accent,
      });
      addText(slide, row.part_name, pos(486, top + 80, 696, 60), {
        fontSize: 23,
        bold: true,
        color: COLORS.navy,
      });
      addText(slide, row.function_summary, pos(486, top + 145, 696, 53), {
        fontSize: 21.5,
        color: COLORS.ink,
      });
      addText(slide, `${row.material}  •  ${row.occurrence_count} occurrence${row.occurrence_count === 1 ? "" : "s"}`, pos(486, top + 198, 722, 40), {
        fontSize: 16,
        color: COLORS.muted,
        lineSpacing: 0.9,
      });
    }
    setNotes(slide, pageRows.flatMap((row) => [
      `${row.part_number}: ${row.source_geometry_path}`,
      `${row.part_number}: ${row.render_png_path} (SHA-256 ${row.png_sha256})`,
    ]));
  }
}

if (slideNumber !== 73) {
  throw new Error(`Unexpected slide count ${slideNumber}; expected 73 for the current 116-part grouping.`);
}

await fs.mkdir(qaRoot, { recursive: true });
await fs.writeFile(
  path.join(tmpDir, "source-notes.txt"),
  `DF8 presentation sources\nSource commit: ${facts.source_commit_sha}\nManifest: ${manifestPath}\nFacts: ${factsPath}\n`,
  "utf8",
);

const inspection = await presentation.inspect({
  kind: "slide,textbox,shape,image,notes",
  maxChars: 2_000_000,
});
await fs.writeFile(path.join(qaRoot, "deck-inspection.ndjson"), inspection.ndjson, "utf8");

for (const [index, slide] of presentation.slides.items.entries()) {
  const stem = `slide-${String(index + 1).padStart(3, "0")}`;
  const png = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(qaRoot, `${stem}.png`), new Uint8Array(await png.arrayBuffer()));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(qaRoot, `${stem}.layout.json`), await layout.text(), "utf8");
}

const montage = await presentation.export({ format: "webp", montage: true, scale: 0.45 });
await fs.writeFile(path.join(qaRoot, "deck-montage.webp"), new Uint8Array(await montage.arrayBuffer()));

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(pptxPath);

const qaSummary = {
  schema: "STINGRAY_DF8_DECK_QA_V1",
  slide_count: slideNumber,
  included_part_render_count: included.length,
  render_manifest_validation_status: renderValidation.status,
  source_commit_sha: facts.source_commit_sha,
  pptx_path: path.relative(repoRoot, pptxPath).replaceAll("\\", "/"),
  rendered_slide_png_count: presentation.slides.items.length,
  layout_json_count: presentation.slides.items.length,
  inspection_path: path.relative(repoRoot, path.join(qaRoot, "deck-inspection.ndjson")).replaceAll("\\", "/"),
  montage_path: path.relative(repoRoot, path.join(qaRoot, "deck-montage.webp")).replaceAll("\\", "/"),
};
await fs.writeFile(
  path.join(packageRoot, "manifests", "deck_qa_summary.json"),
  `${JSON.stringify(qaSummary, null, 2)}\n`,
  "utf8",
);

console.log(JSON.stringify(qaSummary, null, 2));
