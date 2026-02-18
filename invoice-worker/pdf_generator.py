"""
PDF Generator
Generiše PDF fakturu na osnovu podataka o narudžbini koristeći reportlab
"""
import io
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

logger = logging.getLogger(__name__)


def generate_invoice_pdf(order_data):
    """
    Generiše PDF fakturu i vraća bytes.

    order_data: {
        'order_id': 1,
        'order_number': 'ORD-20260101-ABC123',
        'customer_id': 'CUST-001',
        'customer_name': 'Marko Markovic',
        'items': [
            {
                'product_code': 'PROD-001',
                'product_name': 'Laptop Dell XPS 15',
                'quantity': 2,
                'unit_price': 1299.99,
                'total_price': 2599.98
            }
        ],
        'total_price': 2599.98,
        'created_at': '2026-01-01T10:00:00'
    }
    """
    logger.info(f"Generating PDF for order {order_data['order_number']}")

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Normal'],
        fontSize=24,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=0
    )

    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#666666'),
        spaceAfter=0
    )

    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=8,
        fontName='Helvetica',
        textColor=colors.HexColor('#999999'),
        spaceAfter=2
    )

    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=0
    )

    elements = []

    header_data = [[
        Paragraph("FAKTURA", title_style),
        Paragraph(f"#{order_data['order_number']}", ParagraphStyle(
            'OrderNum',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#4a90e2'),
            alignment=TA_RIGHT
        ))
    ]]

    header_table = Table(header_data, colWidths=[9*cm, 8*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*cm))

    # Datum
    created_at = order_data.get('created_at', datetime.utcnow().isoformat())
    if isinstance(created_at, str):
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = dt.strftime('%d.%m.%Y %H:%M')
        except Exception:
            formatted_date = created_at
    else:
        formatted_date = datetime.utcnow().strftime('%d.%m.%Y %H:%M')

    elements.append(Paragraph(f"Datum: {formatted_date}", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=2,
                                color=colors.HexColor('#4a90e2')))
    elements.append(Spacer(1, 0.5*cm))

    customer_data = [[
        Table([
            [Paragraph("KUPAC", label_style)],
            [Paragraph(order_data['customer_name'], value_style)],
            [Paragraph(f"ID: {order_data['customer_id']}", subtitle_style)],
        ], colWidths=[8*cm]),
        Table([
            [Paragraph("STATUS", label_style)],
            [Paragraph("PLAĆENO", ParagraphStyle(
                'Status',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#27ae60')
            ))],
        ], colWidths=[8*cm])
    ]]

    customer_table = Table(customer_data, colWidths=[9*cm, 8*cm])
    customer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 0.8*cm))

    table_data = [[
        Paragraph('ŠIFRA', ParagraphStyle('th', parent=styles['Normal'],
                  fontSize=9, fontName='Helvetica-Bold',
                  textColor=colors.white)),
        Paragraph('NAZIV PROIZVODA', ParagraphStyle('th', parent=styles['Normal'],
                  fontSize=9, fontName='Helvetica-Bold',
                  textColor=colors.white)),
        Paragraph('KOL.', ParagraphStyle('th', parent=styles['Normal'],
                  fontSize=9, fontName='Helvetica-Bold',
                  textColor=colors.white, alignment=TA_CENTER)),
        Paragraph('JED. CENA', ParagraphStyle('th', parent=styles['Normal'],
                  fontSize=9, fontName='Helvetica-Bold',
                  textColor=colors.white, alignment=TA_RIGHT)),
        Paragraph('UKUPNO', ParagraphStyle('th', parent=styles['Normal'],
                  fontSize=9, fontName='Helvetica-Bold',
                  textColor=colors.white, alignment=TA_RIGHT)),
    ]]

    for i, item in enumerate(order_data['items']):
        row_style = ParagraphStyle(
            f'row_{i}',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            textColor=colors.HexColor('#1a1a2e')
        )
        table_data.append([
            Paragraph(item.get('product_code', ''), row_style),
            Paragraph(item.get('product_name', ''), row_style),
            Paragraph(str(item.get('quantity', 0)),
                      ParagraphStyle(f'rc_{i}', parent=row_style, alignment=TA_CENTER)),
            Paragraph(f"${float(item.get('unit_price', 0)):.2f}",
                      ParagraphStyle(f'rr_{i}', parent=row_style, alignment=TA_RIGHT)),
            Paragraph(f"${float(item.get('total_price', 0)):.2f}",
                      ParagraphStyle(f'rt_{i}', parent=row_style,
                                     fontName='Helvetica-Bold', alignment=TA_RIGHT)),
        ])

    col_widths = [2.5*cm, 6.5*cm, 1.5*cm, 2.5*cm, 2.5*cm]
    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    row_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]
    items_table.setStyle(TableStyle(row_styles))
    elements.append(items_table)
    elements.append(Spacer(1, 0.5*cm))

    total_data = [[
        '',
        Paragraph('UKUPNO ZA UPLATU:', ParagraphStyle(
            'TotalLabel',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a1a2e'),
            alignment=TA_RIGHT
        )),
        Paragraph(f"${float(order_data['total_price']):.2f}", ParagraphStyle(
            'TotalValue',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#4a90e2'),
            alignment=TA_RIGHT
        )),
    ]]

    total_table = Table(total_data, colWidths=[9*cm, 5*cm, 3*cm])
    total_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (1, 0), (-1, 0), 1, colors.HexColor('#dee2e6')),
    ]))
    elements.append(total_table)

    elements.append(Spacer(1, 1*cm))
    elements.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor('#dee2e6')))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph(
        "Hvala na poverenju! | Cloud Order System",
        ParagraphStyle('Footer', parent=styles['Normal'],
                       fontSize=8, textColor=colors.HexColor('#999999'),
                       alignment=TA_CENTER)
    ))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    logger.info(f"PDF generated successfully ({len(pdf_bytes)} bytes)")
    return pdf_bytes
