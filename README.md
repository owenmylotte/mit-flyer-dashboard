# MIT Flyer Coverage Dashboard

A live dashboard for tracking flyer posting coverage across MIT campus buildings. Your team edits a Google Sheet; the dashboard pulls the latest data automatically with an interactive **OpenStreetMap** overlay.

## How It Works

```
Google Sheet (your team edits) → Published CSV URL → Dashboard with OpenStreetMap (read-only view)
```

- **Editors** use Google Sheets normally (share the sheet with your team)
- **Viewers** open the GitHub Pages link and see the latest data on an interactive map
- Nobody viewing the dashboard can edit the spreadsheet
- Map is fully scrollable and zoomable using **Leaflet.js** and **OpenStreetMap**
- **100% free and open source** - no API keys required!

---

## Setup (10 minutes)

### Step 1: Set up the Google Sheet

1. Upload the included `mit_flyer_tracker.xlsx` to Google Drive, or create a new Google Sheet with these columns in this exact order:

   | Building | Bldg # | Floor | Spot Name | Spot Type | Assigned To | Posted | Date Posted | Notes |
   |----------|--------|-------|-----------|-----------|-------------|--------|-------------|-------|

2. The **"Posted"** column should contain `YES` or `NO`.
3. Name the data sheet **"Coverage Data"** (the tab at the bottom).
4. Replace the sample data with your real buildings and posting spots.

### Step 2: Publish the sheet

1. Open the Google Sheet.
2. Go to **File → Share → Publish to web**.
3. In the first dropdown, select **"Coverage Data"** (not "Entire Document").
4. In the second dropdown, select **"Comma-separated values (.csv)"**.
5. Click **Publish** and confirm.
6. Copy the URL it gives you. It will look something like:
   ```
   https://docs.google.com/spreadsheets/d/e/2PACX-XXXXX/pub?gid=XXXXX&single=true&output=csv
   ```
7. Save this URL — you'll paste it into the dashboard on first launch.

### Step 3: Deploy to GitHub Pages

1. **Create a new GitHub repository**:
   - Go to [GitHub](https://github.com) and create a new repository
   - Name it something like `mit-flyer-dashboard`
   - Can be public or private (GitHub Pages works with both, but free accounts need public repos for Pages)

2. **Upload files to the repository**:
   - Upload `index.html` and `.nojekyll` to the repository root
   - You can do this via the GitHub web interface or using Git:
     ```bash
     git init
     git add index.html .nojekyll
     git commit -m "Initial commit"
     git branch -M main
     git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
     git push -u origin main
     ```

3. **Enable GitHub Pages**:
   - Go to your repository on GitHub
   - Click **Settings** → **Pages** (in the left sidebar)
   - Under "Source", select **"Deploy from a branch"**
   - Choose the **main** branch and **/ (root)** folder
   - Click **Save**

4. **Wait for deployment**:
   - GitHub will build and deploy your site (usually takes 1-2 minutes)
   - Once done, you'll see a green checkmark and your site URL
   - Your dashboard will be live at:
     ```
     https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/
     ```

**That's it!** No API keys needed - the map works immediately using OpenStreetMap.

### Step 4: Connect the dashboard

1. Open your GitHub Pages URL.
2. Paste the published CSV URL from Step 2.
3. Click **"Connect & Launch Dashboard"**.
4. The URL is saved in your browser — next time you visit, it loads automatically.

---

## Day-to-Day Usage

### For your team (editors):
- Open the Google Sheet and update the **Posted** column to `YES`/`NO`
- Add new rows for new posting spots
- Add notes about access issues, full boards, etc.

### For anyone viewing the dashboard:
- Open the GitHub Pages link
- Click **"↻ Refresh"** to pull the latest data
- Use filters to view by team member or missing flyers only
- Click buildings on the map to drill down floor-by-floor

---

## Adding New Buildings

1. Add rows to the Google Sheet with the new building info.
2. The dashboard will pick them up automatically on the next refresh.
3. **For map placement**: The dashboard now includes over 150 MIT buildings with coordinates. New buildings will appear in the list view and on the map if their building number is already in the coordinate database.

4. **To add a building not yet in the database**:
   - Find the `BUILDING_COORDS` object in the HTML file (around line 300)
   - Add an entry like:
     ```javascript
     "NEW_NUM": { lat: 42.XXXXX, lng: -71.XXXXX, name: "Building Name" },
     ```
   - You can find coordinates by searching for the building on Google Maps and right-clicking to get the lat/lng

---

## FAQ

**Can viewers edit the spreadsheet?**
No. The published CSV URL is read-only. Only people you've shared the Google Sheet with directly (via the normal Share button) can edit it.

**Is the data public?**
The published CSV URL is technically accessible to anyone who has it, but it's a long random URL that nobody would guess. The data is just building names and flyer statuses — nothing sensitive.

**Do I need to pay for maps or get an API key?**
No! The dashboard uses **Leaflet.js** with **OpenStreetMap**, which are completely free and open source. No API keys, no billing, no usage limits.

**What is OpenStreetMap?**
OpenStreetMap is a free, open-source map of the world, built by a community of mappers. It's like Wikipedia for maps. Learn more at [openstreetmap.org](https://www.openstreetmap.org).

**Can I unpublish later?**
Yes. Go to File → Share → Publish to web → click "Stop publishing". The dashboard will stop working until you republish.

**Can I use a private GitHub repo?**
For free GitHub accounts, you need a public repository to use GitHub Pages. With GitHub Pro, you can use private repositories, but the GitHub Pages site will still be publicly accessible (they just don't show the source code).

**How often does the published CSV update?**
Within a few minutes of any edit to the Google Sheet. It's not instant, but usually catches up within 5 minutes.

**Can I zoom and scroll the map?**
Yes! The map is fully interactive. You can scroll to zoom, drag to pan, click buildings for details, and even see popups with coverage stats.
