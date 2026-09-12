import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def create_pdf(filename="GSC_GA4_Semrush_Integration_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = colors.HexColor("#1A365D")   # Deep Navy
    secondary_color = colors.HexColor("#2B6CB0") # Blue
    accent_color = colors.HexColor("#319795")    # Teal
    dark_text = colors.HexColor("#2D3748")       # Charcoal
    bg_light = colors.HexColor("#F7FAFC")        # Soft grey
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#718096"),
        alignment=TA_CENTER
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=secondary_color,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=dark_text
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=dark_text,
        leftIndent=15
    )

    code_style = ParagraphStyle(
        'CodeText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1A202C")
    )

    story = []

    # Title & Header
    story.append(Paragraph("SEO Audit Engine — API Integration Guide", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Complete Blueprint for Connecting Google Search Console, Google Analytics 4 & Semrush", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceBefore=4, spaceAfter=14))

    # Overview Box
    overview_text = (
        "<b>Executive Summary:</b> Is guide ki madad se aap apne <b>SEO Audit Engine</b> me real-time traffic, "
        "search queries, organic rankings, CTR, bounce rate aur backlinks data ko automatically pull kar sakte hain. "
        "Service Account architecture ke through bina baar-baar login kiye backend automated reports generate karega."
    )
    overview_table = Table([[Paragraph(overview_text, body_style)]], colWidths=[530])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BEE3F8")),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 14))

    # STEP 1
    story.append(Paragraph("1. Google Cloud Service Account Setup (Unified Key)", h1_style))
    story.append(Paragraph("Service Account ek automated bot identity hai jo backend scripts ko Google APIs secure access deti hai:", body_style))
    story.append(Spacer(1, 4))
    
    steps_gcp = [
        "1. <b>Google Cloud Console</b> (<font color='#2B6CB0'>console.cloud.google.com</font>) par jayein aur Project select/create karein.",
        "2. <b>APIs & Services &gt; Library</b> me jaakar <b>Google Search Console API</b> aur <b>Google Analytics Data API</b> dono ko <b>Enable</b> karein.",
        "3. <b>Credentials &gt; Create Credentials &gt; Service Account</b> par click karein. Name: <font color='#2B6CB0'><b>seo-engine-bot</b></font>.",
        "4. Service Account banne ke baad uspar click karein &gt; <b>Keys Tab</b> &gt; <b>Add Key &gt; Create new key (JSON)</b>.",
        "5. Ek JSON file download hogi (e.g. <b>credentials.json</b>). Iska email address note kar lein (e.g. <font color='#718096'>seo-engine-bot@project-id.iam.gserviceaccount.com</font>)."
    ]
    for s in steps_gcp:
        story.append(Paragraph(s, bullet_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 10))

    # STEP 2
    story.append(Paragraph("2. Google Search Console (GSC) Integration", h1_style))
    story.append(Paragraph("Service Account email ko GSC Property me add karke real search clicks aur query rankings fetch ki jati hain:", body_style))
    story.append(Spacer(1, 4))

    steps_gsc = [
        "1. <b>Google Search Console</b> (<font color='#2B6CB0'>search.google.com/search-console</font>) open karein.",
        "2. Left sidebar se apni website property (e.g. <font color='#2B6CB0'>https://gurupunvaanii.com/</font>) select karein.",
        "3. Left menu me <b>Settings &gt; Users and permissions</b> par jayein.",
        "4. <b>Add User</b> click karein, Service Account Email paste karein, Permission me <b>Full</b> ya <b>Restricted (Read-Only)</b> select karke add karein.",
        "5. <b>Data Capabilities:</b> Total Clicks, Search Impressions, CTR, Average Position, Top 1000 Queries, URL Indexing Status."
    ]
    for s in steps_gsc:
        story.append(Paragraph(s, bullet_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 10))

    # STEP 3
    story.append(Paragraph("3. Google Analytics 4 (GA4) Integration", h1_style))
    story.append(Paragraph("GA4 Data API se real traffic sources, user behavior aur conversions capture hoti hain:", body_style))
    story.append(Spacer(1, 4))

    steps_ga4 = [
        "1. <b>Google Analytics 4</b> (<font color='#2B6CB0'>analytics.google.com</font>) open karein.",
        "2. Bottom-left <b>Admin (Gear Icon) &gt; Property Settings &gt; Property Access Management</b> me jayein.",
        "3. <b>+ Icon &gt; Add users</b> par click karein aur wahi Service Account Email daal kar <b>Viewer</b> permission dein.",
        "4. <b>Property ID:</b> Admin &gt; Property Settings &gt; <b>Property Details</b> me jakar 9-digit numeric <b>Property ID</b> copy karein.",
        "5. <b>Data Capabilities:</b> Active Users, Sessions, Engagement Rate, Bounce Rate, Traffic Channels (Organic/Direct/Paid/Referral)."
    ]
    for s in steps_ga4:
        story.append(Paragraph(s, bullet_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 12))

    # STEP 4
    story.append(Paragraph("4. Semrush Integration (API Key / CSV Importer)", h1_style))
    story.append(Paragraph("Semrush se Domain Authority, Organic Competitors aur Backlink profile pull karne ke do tarike hain:", body_style))
    story.append(Spacer(1, 4))

    steps_sem = [
        "<b>Option A (Semrush API Key):</b> Semrush account &gt; Subscription &gt; API Key copy karke direct automated sync.",
        "<b>Option B (CSV / Export Sync):</b> Semrush Domain Overview & Keyword export file ko dashboard me drag-drop ya backend sync karna.",
        "<b>Data Capabilities:</b> Authority Score (AS), Referring Domains, Follow vs NoFollow Backlinks, Keyword Difficulty (KD%)."
    ]
    for s in steps_sem:
        story.append(Paragraph(s, bullet_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 12))

    # STEP 5 - Python Implementation Summary Table
    story.append(Paragraph("5. Data Pipeline & Python Libraries", h1_style))
    
    table_data = [
        [Paragraph("<b>Source</b>", body_style), Paragraph("<b>Python Library</b>", body_style), Paragraph("<b>Key Metrics Extracted</b>", body_style)],
        [
            Paragraph("<b>Google Search Console</b>", body_style),
            Paragraph("<font face='Courier'>google-api-python-client</font><br/><font face='Courier'>google-auth</font>", code_style),
            Paragraph("Clicks, Impressions, CTR, Position, Top Search Queries, Landing Pages", body_style)
        ],
        [
            Paragraph("<b>Google Analytics 4</b>", body_style),
            Paragraph("<font face='Courier'>google-analytics-data</font>", code_style),
            Paragraph("Active Users, Sessions, Channels (Organic, Social, Direct), Bounce Rate", body_style)
        ],
        [
            Paragraph("<b>Semrush / SEO</b>", body_style),
            Paragraph("<font face='Courier'>requests</font> / JSON parser", code_style),
            Paragraph("Domain Authority Score, Total Backlinks, Referring Domains, Organic Keywords", body_style)
        ]
    ]

    t = Table(table_data, colWidths=[130, 160, 240])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t)

    story.append(Spacer(1, 16))

    # Integration Checklist Box
    checklist_box = [
        [Paragraph("<b>⚡ Next Action to Connect in this Project:</b><br/>"
                   "1. Apni downloaded <b>service_account.json</b> file ko project folder me save karein.<br/>"
                   "2. Apna <b>GSC Site URL</b> (e.g. <i>https://gurupunvaanii.com/</i> ya <i>sc-domain:gurupunvaanii.com</i>) aur <b>GA4 Property ID</b> provide karein.<br/>"
                   "3. Hum live collector script run karke dashboard me live traffic graphs aur tables render kar denge!", body_style)]
    ]
    cb_table = Table(checklist_box, colWidths=[530])
    cb_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FFF4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#9AE6B4")),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(cb_table)

    doc.build(story)
    print(f"PDF generated successfully at: {os.path.abspath(filename)}")

if __name__ == "__main__":
    create_pdf()
