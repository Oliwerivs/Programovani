function sendPersonalizedEmails() {

  // ---------- CONFIG ----------
  const sheetName = "Sheet1";
  const emailColumn = "Email";       // Column header name
  const nameColumn = "Name";
  const conditionColumn = "Condition";  // Yes/No
  const numberColumn = "Value";      // numeric column
  const attachmentFileId = "YOUR_FILE_ID_HERE";  // Drive file ID
  const subject = "Your Personalized Report";

  // Email templates
  const shortText = (name, rows) =>
      `Hello ${name},\n\nHere are your values:\n` +
      rows.map(r => `• ${r.number}`).join("\n") +
      `\n\nRegards,\nYour Team`;

  const longText = (name, rows) =>
      `Hello ${name},\n\nThank you! Here is your extended data:\n` +
      rows.map(r => `• ${r.number}`).join("\n") +
      `\n\nThis is your longer explanation.\n\nRegards,\nYour Team`;

  // ---------- READ SHEET ----------
  const ss = SpreadsheetApp.getActive();
  const sheet = ss.getSheetByName(sheetName);
  const data = sheet.getDataRange().getValues();
  
  const headers = data.shift(); // first row (column names)
  
  const colIndex = name =>
    headers.indexOf(name) >= 0 ? headers.indexOf(name) : null;

  const emailIdx = colIndex(emailColumn);
  const nameIdx = colIndex(nameColumn);
  const condIdx = colIndex(conditionColumn);
  const numIdx = colIndex(numberColumn);

  if ([emailIdx, nameIdx, condIdx, numIdx].includes(null)) {
    throw new Error("One or more column names are incorrect.");
  }

  // ---------- GROUP ROWS BY EMAIL ----------
  const grouped = {};

  data.forEach(row => {
    const email = row[emailIdx];
    if (!email) return;

    if (!grouped[email]) {
      grouped[email] = {
        name: row[nameIdx],
        condition: row[condIdx],
        rows: []
      };
    }

    grouped[email].rows.push({
      number: row[numIdx]
    });
  });

  // ---------- SEND EMAILS ----------
  const file = DriveApp.getFileById(attachmentFileId);

  for (let email in grouped) {

    const entry = grouped[email];
    const name = entry.name;
    const condition = entry.condition;
    const rows = entry.rows;

    let body = "";
    let options = {};

    if (condition.toLowerCase() === "yes") {
      body = longText(name, rows);
      options = { attachments: [file] };
    } else {
      body = shortText(name, rows);
    }

    GmailApp.sendEmail(email, subject, body, options);
  }
}
