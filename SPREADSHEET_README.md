# MIT Flyer Tracker Spreadsheet

## Files

- `mit_flyer_tracker_full.csv` - **NEW** comprehensive template with all 120 buildings and 86 stewards
- `mit_flyer_tracker.xlsx` - OLD template (smaller subset, can be deleted)
- `STEWARD_ASSIGNMENTS.md` - Breakdown of assignments by department

## What's in the New Template

✅ **120 MIT Buildings** - All academic, administrative, and public buildings (dorms excluded)
✅ **496 Posting Spots** - Bulletin boards across all floors
✅ **86 MIT GSU Stewards** - All assigned based on their departments
✅ **Department-Based Assignments** - Stewards matched to buildings in their departments
✅ **Clean Slate** - All spots set to "NO" (not posted) for fresh start
✅ **No Notes** - Ready for your team to fill in

## Buildings Included

- **Main Campus**: Buildings 1-76 (50+ buildings)
- **East Campus**: E1-E94 (25+ buildings)
- **North Campus**: N9-N57, NE18-NE103, NW10-NW98 (28+ buildings)
- **West Campus**: W2-WW15 (non-dorm buildings, 17+ buildings)

**Excluded**: Undergraduate dorms (W1, W4, W7, W51, W61, W70, W71, W79)

## Steward Assignments

All 86 MIT GSU stewards have been assigned to buildings based on their departments:

| Department | Stewards | Buildings |
|------------|----------|-----------|
| Bio | 13 | Koch Biology, Koch Institute, etc. |
| DMSE | 11 | Materials Science buildings |
| EECS | 7 | Stata Center, EECS labs, Computing |
| SHASS | 6 | Humanities buildings, Student Center |
| BE | 5 | Bioengineering buildings |
| Arch | 5 | Architecture buildings |
| ChemE | 4 | Chemical Engineering buildings |
| NSE | 4 | Nuclear Science buildings |
| IDSS | 4 | Data science buildings |
| AeroAstro | 3 | Aerospace buildings |
| Math | 3 | Mathematics building |
| MechE | 3 | Mechanical Engineering buildings |
| BCS | 3 | Brain & Cognitive Sciences |
| DUSP | 3 | Urban Planning buildings |
| Sloan | 3 | Management buildings |
| Chem | 2 | Chemistry buildings |
| CEE | 2 | Civil & Environmental |
| Physics | 2 | Physics buildings |
| HASTS | 2 | HASTS buildings |
| EAPS | 1 | Earth Sciences (Green Building) |

See `STEWARD_ASSIGNMENTS.md` for complete breakdown with individual steward assignments.

## How to Use

### Option 1: Import to Google Sheets (Recommended)

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. File → Import → Upload
4. Select `mit_flyer_tracker_full.csv`
5. Import settings:
   - Import location: "Replace spreadsheet"
   - Separator type: "Comma"
   - Convert text to numbers: NO (keep as text)
6. Click "Import data"
7. Rename the sheet tab to "Coverage Data"
8. Follow the setup instructions in the main README.md to publish as CSV

### Option 2: Convert to Excel

If you prefer Excel format:

1. Open the CSV in Excel or LibreOffice Calc
2. Select All (Ctrl+A)
3. Format cells:
   - Set "Bldg #" column to Text format (to preserve leading zeros)
   - Set other columns as needed
4. Save As → Excel Workbook (.xlsx)

### Option 3: Use CSV Directly

The CSV file works perfectly with the dashboard! You can:

1. Upload the CSV to Google Drive
2. Right-click → "Open with" → "Google Sheets"
3. It will automatically convert to Google Sheets format
4. Follow the publishing instructions in README.md

## Customizing Assignments

To modify steward assignments:

1. Open in Google Sheets (or Excel)
2. Use Find & Replace to swap steward names
3. Or manually edit the "Assigned To" column for specific spots
4. Keep the column structure unchanged for compatibility

## Testing the Dashboard

To test with sample data:

1. Import this CSV to Google Sheets
2. Manually set some "Posted" values to "YES"
3. Add random dates to "Date Posted" for posted spots
4. Publish as CSV following the README instructions
5. Load in the dashboard to see it in action

## Column Descriptions

- **Building**: Full building name (e.g., "Bldg 32 – Stata Center")
- **Bldg #**: Building number (e.g., "32", "E14")
- **Floor**: Floor number (1, 2, 3, etc.)
- **Spot Name**: Description of posting location
- **Spot Type**: Type of spot (all are "Bulletin Board")
- **Assigned To**: MIT GSU steward responsible for this spot
- **Posted**: "YES" or "NO" - whether flyer is currently posted
- **Date Posted**: Date when flyer was posted (YYYY-MM-DD format)
- **Notes**: Optional notes (access issues, board full, etc.)

## Questions?

- See main README.md for dashboard setup
- See BUILDINGS_LIST.md for complete building inventory
- See STEWARD_ASSIGNMENTS.md for detailed steward breakdown
- Contact MIT GSU for steward information: https://mitgsu.org/stewards
