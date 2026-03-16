# Setup Summary - MIT Flyer Coverage Dashboard

## What's Been Updated

### 1. ✅ Comprehensive MIT Buildings List
- **Expanded from ~70 to 150+ buildings**
- Added all academic, administrative, and laboratory buildings
- Excluded undergraduate dormitories as requested (W1, W4, W7, W51, W61, W70, W71, W79)
- Buildings organized by campus location:
  - Main Campus (numbered buildings: 1-76)
  - East Campus (E-prefix buildings)
  - North Campus (N-prefix buildings)
  - Northeast Campus (NE-prefix buildings)
  - Northwest Campus (NW-prefix buildings)
  - West Campus non-dorm buildings (W-prefix)

See `BUILDINGS_LIST.md` for the complete list.

### 2. ✅ Interactive Map Integration (Leaflet + OpenStreetMap)
- **Replaced static SVG map with interactive Leaflet.js map**
- **Uses OpenStreetMap** - completely free and open source
- **No API key required** - works immediately!
- Map is fully scrollable and zoomable
- Buildings shown as labeled markers with color-coded coverage status
- Markers are clickable to show detailed floor-by-floor breakdown
- Popup tooltips show building info and coverage stats

**Key Features:**
- Green markers: 80-100% coverage
- Yellow markers: 50-79% coverage
- Red markers: 0-49% coverage
- Selected buildings show enlarged, pulsing markers
- Click markers for popups with detailed stats
- Smooth animations and responsive design

### 3. ✅ GitHub Pages Setup
- Created `.nojekyll` file to prevent Jekyll processing
- Updated README with detailed GitHub Pages deployment instructions
- Added Google Maps API key setup instructions
- Included information about API restrictions and free tier limits

## Files Modified/Created

### New Files:
- `.nojekyll` - Prevents GitHub from processing site with Jekyll
- `buildings_data.js` - Standalone building data (for reference)
- `BUILDINGS_LIST.md` - Complete list of all buildings included
- `SETUP_SUMMARY.md` - This file

### Modified Files:
- `index.html` - Major updates:
  - Added Google Maps API script
  - Expanded BUILDING_COORDS from ~70 to 150+ buildings
  - Replaced SVG map rendering with Google Maps markers
  - Added map initialization logic
  - Updated CSS for Google Maps container
  - Made map scrollable and interactive

- `README.md` - Updated with:
  - Google Maps API key instructions
  - Expanded GitHub Pages deployment guide
  - Updated FAQ with Google Maps info
  - Notes about building coverage

## Next Steps for Deployment

### 1. Deploy to GitHub Pages
1. Create a new GitHub repository
2. Upload these files to the root:
   - `index.html`
   - `.nojekyll`
   - (optional) `README.md`, `BUILDINGS_LIST.md`
3. Go to Settings → Pages
4. Select "Deploy from a branch" → main → / (root)
5. Wait 1-2 minutes for deployment
6. Access your dashboard at `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`

### 2. Set Up Your Data
1. Create/publish your Google Sheet as CSV
2. Open your GitHub Pages URL
3. Paste the published CSV URL
4. Start tracking flyer coverage!

## Technical Notes

### Mapping Technology
- **Leaflet.js**: Open-source JavaScript library for interactive maps
- **OpenStreetMap**: Free, open-source map data
- **No API keys or billing required**
- **No usage limits** - use as much as you want!
- Active community support and regular updates

### Browser Compatibility
- Works in all modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Mobile responsive design

### Data Updates
- Dashboard pulls fresh data from Google Sheets on each refresh
- Google's published CSV updates within ~5 minutes of sheet edits
- Click "Refresh" button to pull latest data

## Building Data Sources

Building information compiled from official MIT sources:
- MIT Facilities Maps & Floor Plans
- MIT Campus Maps (whereis.mit.edu)
- MIT Capital Projects website
- MIT Buildings LibGuides
- SAH Archipedia (architectural history)
- Wikipedia articles on MIT campus

## Questions?

- See `README.md` for detailed setup instructions
- See `BUILDINGS_LIST.md` for complete building inventory
- For MIT building questions, check [whereis.mit.edu](https://whereis.mit.edu/)
- For Google Maps API help, see [Google Maps Platform Documentation](https://developers.google.com/maps/documentation/javascript)
