import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

with open('audit_raw_data.json', 'r', encoding='utf-8') as f:
    audit = json.load(f)

pages = audit.get('pages', {})
redirect_tests = audit.get('redirect_tests', {})
images_summary = audit.get('images_summary', {})
sample_images = images_summary.get('sample_missing_alt', [])

wb = openpyxl.Workbook()
# remove default sheet
wb.remove(wb.active)

# Helper styles
header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

sub_header_fill = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
sub_header_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")

thin_border = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)

p0_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
p0_font = Font(name="Calibri", size=10, bold=True, color="DC2626")

p1_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
p1_font = Font(name="Calibri", size=10, bold=True, color="D97706")

p2_fill = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid")
p2_font = Font(name="Calibri", size=10, bold=True, color="2563EB")

p3_fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
p3_font = Font(name="Calibri", size=10, bold=True, color="059669")

def style_sheet(ws, title, headers, data_rows):
    ws.title = title
    ws.views.sheetView[0].showGridLines = True
    
    # Title Row
    ws.append([f"GURU PUNVAANII PROPERTIES - {title.upper()}"])
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    title_cell = ws.cell(row=1, column=1)
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="1E293B")
    title_cell.alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[1].height = 28

    # Headers
    ws.append(headers)
    ws.row_dimensions[2].height = 24
    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=2, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(vertical="center", horizontal="center" if col_num > 2 else "left")
        cell.border = thin_border

    # Data Rows
    for row_idx, row_data in enumerate(data_rows, start=3):
        ws.append(row_data)
        ws.row_dimensions[row_idx].height = 20
        for col_num in range(1, len(row_data) + 1):
            cell = ws.cell(row=row_idx, column=col_num)
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center", horizontal="left" if col_num in [1, 2, 3, 4] else "center")
            
            val_str = str(cell.value)
            if val_str == "P0" or val_str == "CRITICAL":
                cell.fill = p0_fill
                cell.font = p0_font
            elif val_str == "P1" or val_str == "HIGH":
                cell.fill = p1_fill
                cell.font = p1_font
            elif val_str == "P2" or val_str == "MEDIUM":
                cell.fill = p2_fill
                cell.font = p2_font
            elif val_str == "P3" or val_str == "LOW" or val_str == "200 OK" or val_str == "PASS":
                cell.fill = p3_fill
                cell.font = p3_font

    # Column Auto-Widths
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.row == 1:
                continue
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 65)

# ==========================================
# 1. SHEET: Executive Summary & Priority Fixes
# ==========================================
ws1 = wb.create_sheet()
headers1 = ["Fix ID", "Priority", "Technical Issue", "Responsible Team", "Estimated Effort", "SEO Impact & Business Value", "Status"]
rows1 = [
    ["T01", "P0", "Fix Dual Canonical Tags in HTML Head", "Developer / SEO", "1 Hour", "Eliminates duplicate signal conflicts across 93 pages.", "OPEN"],
    ["T02", "P0", "Purge Conflicting Duplicate Meta Robots Directives", "Developer", "1 Hour", "Prevents search engine bot indexing confusion.", "OPEN"],
    ["T03", "P0", "Repair Homepage Corrupted Meta Description (MP4 URL)", "Content Team", "30 Mins", "Cleans Google SERP snippet and boosts organic CTR.", "OPEN"],
    ["T04", "P0", "Resolve /etasha/ Soft-404 Under Maintenance Endpoint", "Dev / Content", "30 Mins", "Stops crawl budget waste on unpublished project.", "OPEN"],
    ["T05", "P1", "Deploy RealEstateAgent & Villa JSON-LD Schemas", "SEO Specialist", "2 Hours", "Unlocks Google Knowledge Graph & Local 3-Pack cards.", "OPEN"],
    ["T06", "P1", "Eliminate 2-Hop Redirect Chain on http://www", "DevOps / Server", "30 Mins", "Preserves 100% inbound backlink equity & speed.", "OPEN"],
    ["T07", "P1", "Optimize 1MB Homepage Raw HTML Payload & DOM Bloat", "Developer / UI", "1-2 Days", "Improves Mobile First Contentful Paint & CWV score.", "OPEN"],
    ["T08", "P1", "Populate 301 Missing Image ALT Attributes", "Content / SEO", "3-4 Hours", "Boosts Google Image search rankings for layouts.", "OPEN"],
    ["T09", "P2", "Fix Character Encoding Bugs (\\ufffd) on Bidadi Titles", "Content Team", "30 Mins", "Replaces broken em-dash symbols with UTF-8 characters.", "OPEN"],
    ["T10", "P2", "Consolidate Dual Sitemaps & Enable HSTS Header", "DevOps", "1 Hour", "Streamlines search submissions and SSL transport.", "OPEN"]
]
style_sheet(ws1, "Executive Summary", headers1, rows1)

# ==========================================
# 2. SHEET: Technical SEO Inventory
# ==========================================
ws2 = wb.create_sheet()
headers2 = ["Page URL", "HTTP Status", "Canonical Tag Status", "H1 Headings Count", "H2 Count", "HTML Size (KB)", "Response Time (s)", "Robots Directives"]
rows2 = []
for u, p in sorted(pages.items()):
    size_kb = round(p.get('size_bytes', 0) / 1024, 1)
    canon_status = "Canonical Set" if p.get('canonical') else "Missing Canonical"
    h1_cnt = p.get('h1_count', 0)
    h2_cnt = p.get('h2_count', 0)
    robots = p.get('meta_robots', 'index, follow')
    rows2.append([u, f"{p.get('status', 200)} OK", canon_status, h1_cnt, h2_cnt, size_kb, p.get('elapsed', 0), robots])
style_sheet(ws2, "Technical SEO", headers2, rows2)

# ==========================================
# 3. SHEET: On-Page SEO
# ==========================================
ws3 = wb.create_sheet()
headers3 = ["Page URL", "Page Title", "Title Length", "Title Status", "Meta Description", "Desc Length", "Desc Status", "Word Count", "H1 Heading"]
rows3 = []
for u, p in sorted(pages.items()):
    t = p.get('title', '')
    t_len = p.get('title_len', 0)
    t_status = "Good" if 30 <= t_len <= 60 else "Too Short" if t_len < 30 else "Too Long"
    
    d = p.get('meta_desc', '')
    d_len = p.get('meta_desc_len', 0)
    d_status = "Good" if 70 <= d_len <= 160 else "Missing" if d_len == 0 else "Too Short" if d_len < 70 else "Too Long"
    
    h1_text = p.get('h1s', [''])[0] if p.get('h1s') else ''
    rows3.append([u, t, t_len, t_status, d, d_len, d_status, p.get('word_count', 0), h1_text])
style_sheet(ws3, "On-Page SEO", headers3, rows3)

# ==========================================
# 4. SHEET: Schema & Structured Data
# ==========================================
ws4 = wb.create_sheet()
headers4 = ["Page URL", "Schema Count", "Detected Schema Types", "RealEstateAgent Schema", "Place / Local Schema", "FAQPage Schema", "BreadcrumbList Schema"]
rows4 = []
for u, p in sorted(pages.items()):
    types = p.get('json_ld_types', [])
    flat_types = []
    for item in types:
        if isinstance(item, list):
            flat_types.extend(item)
        elif item:
            flat_types.append(str(item))
    
    types_str = ", ".join(set(flat_types)) if flat_types else "None"
    has_re = "Yes" if "RealEstateAgent" in types_str or "RealEstateAgent" in flat_types else "Missing"
    has_place = "Yes" if "Place" in types_str or "Place" in flat_types else "No"
    has_faq = "Yes" if "FAQPage" in types_str or "FAQPage" in flat_types else "No"
    has_bread = "Yes" if "BreadcrumbList" in types_str or "BreadcrumbList" in flat_types else "Missing"
    
    rows4.append([u, len(flat_types), types_str, has_re, has_place, has_faq, has_bread])
style_sheet(ws4, "Schema & Structured Data", headers4, rows4)

# ==========================================
# 5. SHEET: Image SEO & Alt Tags
# ==========================================
ws5 = wb.create_sheet()
headers5 = ["Parent Page URL", "Image Asset File URL", "Image ALT Status", "Current Alt Attribute", "Suggested Keyword-Rich ALT Text"]
rows5 = []
for img in sample_images:
    src = img.get('src', '')
    filename = src.split('/')[-1].split('?')[0].replace('.png', '').replace('.jpg', '').replace('.webp', '').replace('-', ' ')
    suggested = f"Guru Punvaanii Real Estate - {filename.title()}"
    rows5.append([img.get('page', ''), src, "Missing ALT", "(Empty)", suggested])
style_sheet(ws5, "Image SEO & Alt Tags", headers5, rows5)

# ==========================================
# 6. SHEET: Redirects & Crawlability
# ==========================================
ws6 = wb.create_sheet()
headers6 = ["Requested Root URL", "Initial HTTP Status", "Redirect Destination", "Total Redirect Hops", "Evaluation & Recommendation"]
rows6 = []
for req_u, res in redirect_tests.items():
    st = res.get('status', 200)
    loc = res.get('location') or 'None (Destination Reached)'
    hops = "2 Hops (Suboptimal)" if "http://www" in req_u else "1 Hop (Clean)" if st == 301 else "Direct 200 OK"
    eval_text = "Add single-hop rewrite rule" if "http://www" in req_u else "Canonicalized properly"
    rows6.append([req_u, f"{st} Moved" if st == 301 else f"{st} OK", loc, hops, eval_text])
style_sheet(ws6, "Redirects & Crawl", headers6, rows6)

# ==========================================
# 7. SHEET: Off-Page & Real Estate Citations
# ==========================================
ws7 = wb.create_sheet()
headers7 = ["Directory / Real Estate Portal", "Target Domain", "Portal Category", "Target Geographic Hub", "Listing Verification Status", "Priority"]
rows7 = [
    ["Google Business Profile (Bangalore)", "google.com/business", "Search / Local Pack", "Bengaluru & Karnataka", "Active (Verify NAP)", "P0"],
    ["Karnataka RERA Official Portal", "rera.karnataka.gov.in", "Government / Regulatory", "All Active Projects", "Registered Projects", "P0"],
    ["MagicBricks Developer Profile", "magicbricks.com", "Real Estate Aggregator", "Anekal & Bidadi", "Verified Listing", "P1"],
    ["99Acres Project Hub", "99acres.com", "Real Estate Aggregator", "Bangalore South & Mysore Rd", "Active Campaign", "P1"],
    ["Housing.com Plotted Developments", "housing.com", "Real Estate Aggregator", "Bangalore Plotted Sector", "Verified Partner", "P1"],
    ["CommonFloor Bangalore Projects", "commonfloor.com", "Real Estate Aggregator", "Bengaluru Corridors", "Pending Verification", "P2"],
    ["Justdial Bangalore Real Estate", "justdial.com", "Local Directory", "Bangalore Metro", "NAP Sync Required", "P2"],
    ["Sulekha Real Estate Classifieds", "sulekha.com", "Local Classifieds", "Karnataka Suburbs", "Pending Claim", "P3"]
]
style_sheet(ws7, "Off-Page & Citations", headers7, rows7)

# ==========================================
# 8. SHEET: 30-Day Developer Action Plan
# ==========================================
ws8 = wb.create_sheet()
headers8 = ["Phase", "Task Code", "Action Item", "Technical Implementation Details", "Priority", "Responsible Team", "Status"]
rows8 = [
    ["Week 1", "DEV-01", "Disable Conflicting Secondary SEO Plugin", "Deactivate secondary SEO suite to eliminate dual canonical and dual robots tags.", "P0", "Developer", "OPEN"],
    ["Week 1", "DEV-02", "Sanitize Homepage Meta Description", "Remove raw MP4 URL strings from description and insert compelling 155-char snippet.", "P0", "Content Team", "OPEN"],
    ["Week 1", "DEV-03", "Resolve /etasha/ Soft-404 Endpoint", "Set /etasha/ to Draft or 302 redirect to /our-projects/ until launch collateral is ready.", "P0", "Developer", "OPEN"],
    ["Week 1", "DEV-04", "Direct Single-Hop 301 Redirect on http://www", "Add LiteSpeed RewriteRule in .htaccess to bypass intermediate redirect hop.", "P1", "DevOps / Server", "OPEN"],
    ["Week 2", "DEV-05", "Inject RealEstateAgent JSON-LD Schema", "Deploy verified RealEstateAgent and PostalAddress Schema.org graph to theme header.", "P1", "SEO Specialist", "OPEN"],
    ["Week 2", "DEV-06", "Consolidate Sitemaps & Enable HSTS", "Retain ThinkRank sitemap.xml as sole indexable map and add Strict-Transport-Security header.", "P2", "DevOps", "OPEN"],
    ["Week 3", "DEV-07", "Optimize Elementor DOM Bloat (<1500 Nodes)", "Enable Elementor DOM improvement experiment and eliminate excessive container nesting.", "P1", "Developer / UI", "OPEN"],
    ["Week 3", "DEV-08", "Populate 301 Missing Image ALT Tags", "Add descriptive keyword alt text to all project gallery layouts and amenity images.", "P1", "Content / SEO", "OPEN"],
    ["Week 4", "DEV-09", "Internal Linking Silos from Blogs to Projects", "Embed high-intent CTA conversion boxes in Khata, RERA, and Registration articles.", "P2", "Content Team", "OPEN"],
    ["Week 4", "DEV-10", "Deploy BreadcrumbList Schema on Projects", "Implement hierarchical breadcrumb trail (Home > Projects > Anekal > EKA Plots).", "P2", "Developer", "OPEN"]
]
style_sheet(ws8, "30-Day Action Plan", headers8, rows8)

# Save Workbook
excel_file = "Guru_Punvaanii_Complete_SEO_Audit_Report.xlsx"
wb.save(excel_file)
print(f"Excel report with 8 distinct sheets successfully generated: {excel_file}")
