/**
 * Google Apps Script — Solar Controller Data Logger
 * ═══════════════════════════════════════════════════════════════
 *
 * SETUP INSTRUCTIONS:
 *
 * 1. Go to https://sheets.google.com and create a new spreadsheet.
 *    Name it e.g. "Solar Controller Log".
 *
 * 2. Open the spreadsheet, then go to:
 *      Extensions → Apps Script
 *
 * 3. Paste this entire file into the editor, replacing any existing code.
 *
 * 4. Click the floppy disk icon to save (name the project anything).
 *
 * 5. Click "Deploy" → "New deployment":
 *      - Type: Web app
 *      - Execute as: Me
 *      - Who has access: Anyone   ← IMPORTANT
 *    Click "Deploy", authorise the permissions when prompted.
 *
 * 6. Copy the Web App URL that looks like:
 *      https://script.google.com/macros/s/AKfycb.../exec
 *    Paste it into GS_SCRIPT_URL in solar_controller.ino.
 *
 * NOTE: Every time you edit this script you must deploy a NEW version
 *       (Deploy → Manage deployments → edit → version: New version).
 * ═══════════════════════════════════════════════════════════════
 */

// Name of the sheet tab that receives raw data
var DATA_SHEET_NAME  = "Data";

// Name of the sheet tab that holds the auto-generated dashboard charts
var CHART_SHEET_NAME = "Dashboard";

// How many rows to keep (older rows are pruned automatically).
// Set 0 to keep everything.
var MAX_ROWS = 10000;

// ─────────────────────────────────────────────────────────────
//  doGet — called by ESP32 via HTTP GET
// ─────────────────────────────────────────────────────────────
function doGet(e) {
  try {
    var ss    = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = getOrCreateDataSheet(ss);

    // Parse parameters
    var datetime = e.parameter.datetime || new Date().toISOString();
    var boiler   = parseFloat(e.parameter.boiler  || 0);
    var panel1   = parseFloat(e.parameter.panel1  || 0);
    var panel2   = parseFloat(e.parameter.panel2  || 0);
    var lux      = parseFloat(e.parameter.lux     || 0);
    var relay    = parseInt(e.parameter.relay     || 0);

    // Append row
    sheet.appendRow([datetime, boiler, panel1, panel2, lux, relay]);

    // Prune old rows if limit set
    if (MAX_ROWS > 0) {
      var rows = sheet.getLastRow();
      if (rows > MAX_ROWS + 1) { // +1 for header
        sheet.deleteRows(2, rows - MAX_ROWS - 1);
      }
    }

    // Regenerate dashboard charts every 12th write (~1 hour at 5 min intervals)
    var writeCount = PropertiesService.getScriptProperties().getProperty("writeCount") || "0";
    writeCount = parseInt(writeCount) + 1;
    PropertiesService.getScriptProperties().setProperty("writeCount", writeCount.toString());
    if (writeCount % 12 === 0) {
      buildDashboard(ss, sheet);
    }

    return ContentService.createTextOutput("OK").setMimeType(ContentService.MimeType.TEXT);

  } catch (err) {
    return ContentService.createTextOutput("ERROR: " + err.toString())
                         .setMimeType(ContentService.MimeType.TEXT);
  }
}

// ─────────────────────────────────────────────────────────────
//  Setup: creates header row if sheet is fresh
// ─────────────────────────────────────────────────────────────
function getOrCreateDataSheet(ss) {
  var sheet = ss.getSheetByName(DATA_SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(DATA_SHEET_NAME);
  }
  // Add header row if empty
  if (sheet.getLastRow() === 0) {
    var header = ["Datetime", "Boiler (°C)", "Panel 1 (°C)", "Panel 2 (°C)", "Lux", "Relay (0/1)"];
    sheet.appendRow(header);
    sheet.getRange(1, 1, 1, header.length).setFontWeight("bold").setBackground("#4a86e8").setFontColor("#ffffff");
    sheet.setFrozenRows(1);
    sheet.setColumnWidth(1, 160); // wider datetime column
  }
  return sheet;
}

// ─────────────────────────────────────────────────────────────
//  buildDashboard — creates/updates charts in a separate tab
// ─────────────────────────────────────────────────────────────
function buildDashboard(ss, dataSheet) {
  // Get or create dashboard sheet
  var dash = ss.getSheetByName(CHART_SHEET_NAME);
  if (!dash) {
    dash = ss.insertSheet(CHART_SHEET_NAME);
  }

  // Remove all existing charts on the dashboard
  var existingCharts = dash.getCharts();
  for (var i = 0; i < existingCharts.length; i++) {
    dash.removeChart(existingCharts[i]);
  }

  var lastRow  = dataSheet.getLastRow();
  if (lastRow < 2) return; // no data yet

  var dataRange  = dataSheet.getRange(1, 1, lastRow, 6);
  var timeRange  = dataSheet.getRange(1, 1, lastRow, 1);
  var tempRange  = dataSheet.getRange(1, 1, lastRow, 4); // datetime + 3 temps
  var luxRange   = dataSheet.getRange(1, 1, lastRow, 1);
  var luxDataRange = dataSheet.getRange(1, 5, lastRow, 1);

  // ── Chart 1: Temperature history ──────────────────────────
  var tempChart = dash.newChart()
    .setChartType(Charts.ChartType.LINE)
    .addRange(dataSheet.getRange(1, 1, lastRow, 1))   // datetime
    .addRange(dataSheet.getRange(1, 2, lastRow, 1))   // boiler
    .addRange(dataSheet.getRange(1, 3, lastRow, 1))   // panel 1
    .addRange(dataSheet.getRange(1, 4, lastRow, 1))   // panel 2
    .setNumHeaders(1)
    .setOption("title", "Temperature History (°C)")
    .setOption("hAxis.title", "Time")
    .setOption("vAxis.title", "Temperature (°C)")
    .setOption("legend.position", "bottom")
    .setOption("colors", ["#e06666", "#ff9900", "#6aa84f"])
    .setOption("width", 700)
    .setOption("height", 350)
    .setPosition(1, 1, 0, 0)
    .build();
  dash.insertChart(tempChart);

  // ── Chart 2: Sunshine (lux) ───────────────────────────────
  var luxChart = dash.newChart()
    .setChartType(Charts.ChartType.AREA)
    .addRange(dataSheet.getRange(1, 1, lastRow, 1))   // datetime
    .addRange(dataSheet.getRange(1, 5, lastRow, 1))   // lux
    .setNumHeaders(1)
    .setOption("title", "Sunshine (lux)")
    .setOption("hAxis.title", "Time")
    .setOption("vAxis.title", "Illuminance (lux)")
    .setOption("colors", ["#f1c232"])
    .setOption("width", 700)
    .setOption("height", 250)
    .setPosition(22, 1, 0, 0)
    .build();
  dash.insertChart(luxChart);

  // ── Chart 3: Relay / heating state ────────────────────────
  var relayChart = dash.newChart()
    .setChartType(Charts.ChartType.STEPPED_AREA)
    .addRange(dataSheet.getRange(1, 1, lastRow, 1))   // datetime
    .addRange(dataSheet.getRange(1, 6, lastRow, 1))   // relay
    .setNumHeaders(1)
    .setOption("title", "Electric Heater State (1=ON, 0=OFF)")
    .setOption("hAxis.title", "Time")
    .setOption("vAxis.title", "Relay")
    .setOption("colors", ["#cc0000"])
    .setOption("vAxis.maxValue", 1.2)
    .setOption("vAxis.minValue", -0.2)
    .setOption("width", 700)
    .setOption("height", 200)
    .setPosition(38, 1, 0, 0)
    .build();
  dash.insertChart(relayChart);

  SpreadsheetApp.flush();
}

// ─────────────────────────────────────────────────────────────
//  Manual trigger — run this once from the editor to test setup
//  and pre-create the header row.
// ─────────────────────────────────────────────────────────────
function initialSetup() {
  var ss    = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = getOrCreateDataSheet(ss);
  Logger.log("Data sheet ready. Rows: " + sheet.getLastRow());

  // Insert a test row so charts have data to show
  sheet.appendRow(["2025-01-01 12:00:00", 45.5, 72.3, 68.1, 25000, 0]);
  sheet.appendRow(["2025-01-01 12:05:00", 46.0, 74.1, 70.5, 28000, 0]);
  buildDashboard(ss, sheet);
  Logger.log("Dashboard built. Check the 'Dashboard' tab.");
}
