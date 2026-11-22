/**
 * Comprehensive Mobile Test Suite Runner
 */
const { execSync } = require("child_process");
const path = require("path");

console.log("============================================================");
console.log("RUNNING MEDICARE MOBILE APPLICATION TESTS");
console.log("============================================================\n");

try {
  execSync("node tests/equivalence.test.js", {
    cwd: __dirname + "/..",
    stdio: "inherit"
  });

  execSync("node tests/datasets.test.js", {
    cwd: __dirname + "/..",
    stdio: "inherit"
  });

  console.log("\n============================================================");
  console.log("ALL MOBILE TESTS COMPLETED SUCCESSFULLY");
  console.log("============================================================");
} catch (err) {
  console.error("Test execution failed:", err.message);
  process.exit(1);
}
