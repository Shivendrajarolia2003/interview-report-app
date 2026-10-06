import os
import re
import html
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from config import REPORTS_DIR

def clean_markdown_for_reportlab(text):
    """
    Safely converts markdown bold/italic formatting into ReportLab HTML tags
    and escapes raw XML characters (&, <, >) to avoid parser errors.
    """
    # 1. Temporarily replace markdown bold/italic with placeholders
    bolds = []
    def save_bold(match):
        bolds.append(match.group(1))
        return f"___BOLD_PLACEHOLDER_{len(bolds)-1}___"
        
    italics = []
    def save_italic(match):
        italics.append(match.group(1))
        return f"___ITALIC_PLACEHOLDER_{len(italics)-1}___"
        
    # Save bold **text**
    text = re.sub(r'\*\*(.*?)\*\*', save_bold, text)
    # Save italic *text* or _text_
    text = re.sub(r'\*(.*?)\*', save_italic, text)
    text = re.sub(r'_(.*?)_', save_italic, text)
    
    # 2. Escape XML special chars safely
    text = html.escape(text)
    
    # 3. Restore bold & italic tags as ReportLab <b> and <i>
    for i, bold_content in enumerate(bolds):
        escaped_bold = html.escape(bold_content)
        text = text.replace(f"___BOLD_PLACEHOLDER_{i}___", f"<b>{escaped_bold}</b>")
        
    for i, italic_content in enumerate(italics):
        escaped_italic = html.escape(italic_content)
        text = text.replace(f"___ITALIC_PLACEHOLDER_{i}___", f"<i>{escaped_italic}</i>")
        
    return text

def create_pdf_report(student_name, report_markdown, output_filename=None):
    """
    Converts markdown report text into a sleek, professional PDF document using ReportLab.
    """
    if not output_filename:
        clean_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '_')).rstrip()
        clean_name = clean_name.replace(" ", "_")
        output_filename = f"{clean_name}_Interview_Report.pdf"
        
    pdf_path = REPORTS_DIR / output_filename
    
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=10
    )
    
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    story = []
    
    # Header Banner
    story.append(Paragraph(f"Company Confidential — Candidate Interview Feedback Report", ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#64748B'))))
    story.append(Paragraph(clean_markdown_for_reportlab(student_name), title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563EB'), spaceAfter=15))
    
    # Parse markdown lines into PDF flowables
    lines = report_markdown.split('\n')
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        if line_str.startswith('# '):
            continue # Title already added above
        elif line_str.startswith('### ') or line_str.startswith('## '):
            heading_text = line_str.replace('#', '').strip()
            formatted_heading = clean_markdown_for_reportlab(heading_text)
            story.append(Paragraph(formatted_heading, h2_style))
        elif line_str.startswith('- ') or line_str.startswith('* '):
            bullet_text = line_str[2:].strip()
            formatted_bullet = clean_markdown_for_reportlab(bullet_text)
            story.append(Paragraph(f"• {formatted_bullet}", bullet_style))
        elif line_str.startswith('> '):
            quote_text = line_str[2:].strip()
            formatted_quote = clean_markdown_for_reportlab(quote_text)
            story.append(Paragraph(f"<i>{formatted_quote}</i>", ParagraphStyle('Quote', parent=body_style, leftIndent=15, textColor=colors.HexColor('#475569'))))
        else:
            formatted_body = clean_markdown_for_reportlab(line_str)
            story.append(Paragraph(formatted_body, body_style))
            
    doc.build(story)
    return str(pdf_path)
