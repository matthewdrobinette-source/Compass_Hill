// Print an HTML file to PDF with headless Chromium (used by render_pdf.py).
// Usage: node tools/html_to_pdf.js <in.html> <out.pdf>
const { execSync } = require("child_process");
const path = require("path");

function loadPlaywright() {
  try {
    return require("playwright");
  } catch {
    const globalRoot = execSync("npm root -g").toString().trim();
    return require(path.join(globalRoot, "playwright"));
  }
}

(async () => {
  const [input, output] = process.argv.slice(2);
  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  const page = await browser.newPage();
  await page.goto("file://" + path.resolve(input), { waitUntil: "load" });
  await page.pdf({
    path: output,
    format: "Letter",
    preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: "<span></span>",
    footerTemplate:
      '<div style="font-family:DejaVu Serif,serif;font-size:7.5pt;color:#777;width:100%;' +
      'padding:0 0.55in;display:flex;justify-content:space-between">' +
      "<span>Compass Hill Estate — Master Property Plan · Rev. B</span>" +
      '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
  });
  await browser.close();
})();
