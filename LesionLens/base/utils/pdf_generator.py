from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.core.files.base import ContentFile

def generate_html_pdf(context, template_path='pdf/diagnosis_report.html'):
    # PDF-safe inline CSS (do not use >, +, rem, etc.)
    pdf_css = """
    body {
        font-family: Helvetica, sans-serif;
        font-size: 14px;
        color: #333;
        padding: 30px;
    }
    .lesionlens-header {
        font-size: 22px;
        font-weight: bold;
        color: #3e4684;
        margin-bottom: 20px;
    }
    .section-subheading {
        font-weight: bold;
        font-size: 16px;
        margin-top: 20px;
        margin-bottom: 10px;
        color: #3e4684;
    }
    ul, ol {
        margin-left: 20px;
    }
    """

    context['css'] = pdf_css
    html = render_to_string(template_path, context)

    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)
    return ContentFile(buffer.getvalue())
