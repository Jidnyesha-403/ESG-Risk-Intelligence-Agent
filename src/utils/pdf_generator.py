import os
import re
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and render custom headers/footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Top Header
        self.drawString(54, 750, "🌱 ESG RISK INTELLIGENCE HUB")
        date_str = datetime.now().strftime("%B %d, %Y")
        self.drawRightString(612 - 54, 750, f"Generated: {date_str}")
        
        self.setStrokeColor(colors.HexColor("#00b09b"))
        self.setLineWidth(1)
        self.line(54, 742, 612 - 54, 742)
        
        # Bottom Footer
        self.setFont("Helvetica", 8)
        self.drawString(54, 36, "Confidential ESG Analysis Report | Powered by Multi-Agent RAG Architecture")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, page_text)
        
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 612 - 54, 48)
        
        self.restoreState()

def create_esg_pdf(company_name: str, agg_e: str, agg_s: str, agg_g: str, report_markdown: str) -> bytes:
    """
    Converts company metadata, risk scores, and Markdown report into a professionally styled PDF document.
    Returns raw PDF bytes for direct download in Streamlit or API outputs.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A202C"),
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#00796B"),
        spaceBefore=12,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceBefore=8,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=5
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        spaceAfter=3
    )
    
    story = []
    
    # Document Title
    story.append(Paragraph(f"ESG Risk Intelligence Report: {company_name}", title_style))
    story.append(Spacer(1, 4))
    
    # Dashboard Table Colors
    def get_bg_color(risk):
        r = str(risk).upper()
        if "LOW" in r: return colors.HexColor("#C6F6D5")
        if "MEDIUM" in r: return colors.HexColor("#FEEBC8")
        return colors.HexColor("#FED7D7")
        
    def get_text_color(risk):
        r = str(risk).upper()
        if "LOW" in r: return colors.HexColor("#22543D")
        if "MEDIUM" in r: return colors.HexColor("#742A2A")
        return colors.HexColor("#742A2A")
        
    dash_data = [
        [Paragraph("<b>ESG Dimension</b>", body_style), Paragraph("<b>Risk Level</b>", body_style), Paragraph("<b>Industry Benchmark Context</b>", body_style)],
        [Paragraph("Environmental (E)", body_style), Paragraph(f"<b>{agg_e.upper()}</b>", ParagraphStyle('E', parent=body_style, textColor=get_text_color(agg_e))), Paragraph("Industry Carbon & Resource Baselines", body_style)],
        [Paragraph("Social (S)", body_style), Paragraph(f"<b>{agg_s.upper()}</b>", ParagraphStyle('S', parent=body_style, textColor=get_text_color(agg_s))), Paragraph("Labor Standards & Human Rights Safety", body_style)],
        [Paragraph("Governance (G)", body_style), Paragraph(f"<b>{agg_g.upper()}</b>", ParagraphStyle('G', parent=body_style, textColor=get_text_color(agg_g))), Paragraph("Board Oversight & Audit Integrity", body_style)],
    ]
    
    t = Table(dash_data, colWidths=[130, 90, 284])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#1A202C")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (1,1), (1,1), get_bg_color(agg_e)),
        ('BACKGROUND', (1,2), (1,2), get_bg_color(agg_s)),
        ('BACKGROUND', (1,3), (1,3), get_bg_color(agg_g)),
    ]))
    
    story.append(t)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=10))
    
    # Process markdown body lines
    lines = report_markdown.split('\n')
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        # Skip table syntax if repeated from markdown
        if line_str.startswith('|') or ('---' in line_str and '|' in line):
            continue
        if "Executive Risk Score Dashboard" in line_str or "Aggregated Risk Score" in line_str:
            continue
            
        if line_str == '---':
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceBefore=6, spaceAfter=6))
            continue
            
        # Escape raw XML special characters (&, <, >) before inserting custom HTML tags
        formatted_line = line_str.replace('&', '&amp;')
        
        # Convert markdown links [Text](URL) -> <a href="URL" color="#0066CC"><u>Text</u></a>
        formatted_line = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2" color="#0066CC"><u>\1</u></a>',
            formatted_line
        )
        # Convert **bold** -> <b>bold</b>
        formatted_line = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', formatted_line)
        # Convert *italic* -> <i>italic</i>
        formatted_line = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', formatted_line)
        
        # Headers
        if line_str.startswith('# '):
            clean_hdr = re.sub(r'^\#\s*', '', formatted_line)
            if company_name.lower() not in clean_hdr.lower() or "report" not in clean_hdr.lower():
                story.append(Paragraph(clean_hdr, h1_style))
        elif line_str.startswith('## '):
            clean_hdr = re.sub(r'^\#\#\s*', '', formatted_line)
            story.append(Paragraph(clean_hdr, h1_style))
        elif line_str.startswith('### '):
            clean_hdr = re.sub(r'^\#\#\#\s*', '', formatted_line)
            story.append(Paragraph(clean_hdr, h2_style))
        elif line_str.startswith('- ') or line_str.startswith('* '):
            bullet_text = re.sub(r'^[\-\*]\s*', '', formatted_line)
            story.append(Paragraph(f"• {bullet_text}", bullet_style))
        elif re.match(r'^\d+\.\s', line_str):
            story.append(Paragraph(formatted_line, bullet_style))
        else:
            story.append(Paragraph(formatted_line, body_style))
            
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
