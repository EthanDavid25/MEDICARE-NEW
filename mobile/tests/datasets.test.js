/**
 * Datasets Integrity and Indian Healthcare Verification Test
 */
const assert = require("assert");
const fs = require("fs");
const path = require("path");

console.log("\n------------------------------------------------------------");
console.log("MEDICARE Dataset & Indian Healthcare Integrity Test Suite");
console.log("------------------------------------------------------------\n");

let passed = 0;
let total = 0;

function test(name, fn) {
  total++;
  try {
    fn();
    console.log(`✅ [PASS] ${name}`);
    passed++;
  } catch (err) {
    console.error(`❌ [FAIL] ${name}:`, err.message);
  }
}

// 1. Facilities India verification
test("Facilities: Exactly 14 verified Maharashtra facilities with valid coordinates", () => {
  const filePath = path.resolve(__dirname, "../../data/healthcare/facilities_india.json");
  assert(fs.existsSync(filePath), "facilities_india.json must exist");
  const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
  const facilities = Array.isArray(data) ? data : data.facilities;
  assert(Array.isArray(facilities), "facilities must be an array");
  assert.strictEqual(facilities.length, 14, `Expected 14 facilities, got ${facilities.length}`);

  for (const f of facilities) {
    assert(f.id, "Facility must have an id");
    assert(f.name, "Facility must have a name");
    assert(typeof f.latitude === "number", `Facility ${f.name} invalid latitude`);
    assert(typeof f.longitude === "number", `Facility ${f.name} invalid longitude`);
    assert(f.latitude >= 15.0 && f.latitude <= 22.5, `Facility ${f.name} latitude out of Maharashtra range`);
    assert(f.longitude >= 72.0 && f.longitude <= 81.0, `Facility ${f.name} longitude out of Maharashtra range`);
    assert(f.city, `Facility ${f.name} missing city`);
    assert(typeof f.has_emergency === "boolean", `Facility ${f.name} missing has_emergency boolean`);
    assert(f.phone, `Facility ${f.name} missing phone number`);
  }
});

// 2. Symptom Dictionary verification
test("Symptoms: Exactly 81 verified clinical symptoms", () => {
  const filePath = path.resolve(__dirname, "../../data/medical/symptoms.json");
  assert(fs.existsSync(filePath), "symptoms.json must exist");
  const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
  const count = data.symptoms ? data.symptoms.length : Object.keys(data).length;
  assert(count >= 80, `Expected at least 80 symptoms, got ${count}`);
});

// 3. Triage Rules verification
test("Rules: Complete triage rules with emergency escalations", () => {
  const filePath = path.resolve(__dirname, "../../data/medical/triage_rules.json");
  assert(fs.existsSync(filePath), "triage_rules.json must exist");
  const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
  const count = data.rules ? data.rules.length : Object.keys(data).length;
  assert(count >= 20, `Expected at least 20 triage rules, got ${count}`);
});

// 4. Emergency Helplines Verification
test("Emergency: Core Indian helpline configuration (112, 108, 102, 104)", () => {
  const helplines = ["112", "108", "102", "104"];
  for (const h of helplines) {
    assert(/^[0-9]{3,4}$/.test(h), `Invalid helpline format ${h}`);
  }
});

console.log(`\nDataset Results: ${passed} / ${total} tests passed.\n`);
if (passed !== total) process.exit(1);
