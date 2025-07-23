from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
import os

class NumberedCanvas(canvas.Canvas):
    """Canvas personnalisé pour ajouter numérotation et pied de page"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.company_name = "Infinytia, SAS"
        self.doc_number = ""

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        if self.doc_number:
            self.drawRightString(
                A4[0] - 2*cm,
                2*cm,
                f"{self.doc_number} · {self._pageNumber}/{page_count}"
            )
        self.drawString(2*cm, 2*cm, self.company_name)

def generate_pdf(devis):
    filename = os.path.join('generated', f'devis_{devis.numero}.pdf')
    
    # Configuration du document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=3*cm
    )
    
    # Styles personnalisés
    styles = getSampleStyleSheet()
    
    # Style pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    # Style pour les en-têtes
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#7f8c8d'),
        fontName='Helvetica'
    )
    
    # Style pour le texte normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica'
    )
    
    # Style pour les détails
    detail_style = ParagraphStyle(
        'Detail',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#7f8c8d'),
        leftIndent=10,
        fontName='Helvetica'
    )
    
    elements = []
    
    # Logo et titre
    logo_data = [
        [Paragraph("Devis", title_style), Paragraph("Infinytia", title_style)]
    ]
    logo_table = Table(logo_data, colWidths=[10*cm, 8*cm])
    logo_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(logo_table)
    elements.append(Spacer(1, 15))
    
    # Informations du devis
    info_data = [
        [Paragraph("<b>Numéro de devis</b>", header_style), Paragraph(devis.numero, normal_style)],
        [Paragraph("<b>Date d'émission</b>", header_style), Paragraph(devis.date_emission, normal_style)],
        [Paragraph("<b>Date d'expiration</b>", header_style), Paragraph(devis.date_expiration, normal_style)]
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 30))
    
    # Fournisseur et Client
    company_data = []
    
    # Nom des sociétés en gras
    company_data.append([
        Paragraph(f"<b>{devis.fournisseur_nom}</b>", normal_style),
        Paragraph(f"<b>{devis.client_nom}</b>", normal_style)
    ])
    
    # Adresses
    company_data.extend([
        [Paragraph(devis.fournisseur_adresse, normal_style), 
         Paragraph(devis.client_adresse, normal_style)],
        [Paragraph(devis.fournisseur_ville, normal_style), 
         Paragraph(devis.client_ville, normal_style)],
        [Paragraph(devis.fournisseur_email, normal_style), 
         Paragraph(devis.client_siret, normal_style)],
        [Paragraph(devis.fournisseur_siret, normal_style), 
         Paragraph(f"Numéro de TVA: {devis.client_tva}", normal_style)]
    ])
    
    company_table = Table(company_data, colWidths=[9*cm, 9*cm])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEAFTER', (0, 0), (0, -1), 1, colors.HexColor('#ecf0f1')),
        ('LEFTPADDING', (1, 0), (1, -1), 20),
    ]))
    
    elements.append(company_table)
    elements.append(Spacer(1, 40))
    
    # Tableau des articles
    items_data = []
    
    # En-tête du tableau avec style sombre
    headers = [
        Paragraph("<b>Description</b>", ParagraphStyle('TableHeader', textColor=colors.whitesmoke, fontSize=10)),
        Paragraph("<b>Qté</b>", ParagraphStyle('TableHeader', textColor=colors.whitesmoke, fontSize=10, alignment=TA_RIGHT)),
        Paragraph("<b>Prix unitaire</b>", ParagraphStyle('TableHeader', textColor=colors.whitesmoke, fontSize=10, alignment=TA_RIGHT)),
        Paragraph("<b>TVA (%)</b>", ParagraphStyle('TableHeader', textColor=colors.whitesmoke, fontSize=10, alignment=TA_RIGHT)),
        Paragraph("<b>Total HT</b>", ParagraphStyle('TableHeader', textColor=colors.whitesmoke, fontSize=10, alignment=TA_RIGHT))
    ]
    items_data.append(headers)
    
    # Articles
    for item in devis.items:
        # Ligne principale de l'article
        items_data.append([
            Paragraph(f"<b>{item.description}</b>", normal_style),
            Paragraph(str(item.quantite), normal_style),
            Paragraph(f"{item.prix_unitaire:.2f} €", normal_style),
            Paragraph(f"{item.tva_taux} %", normal_style),
            Paragraph(f"{item.total_ht:.2f} €", normal_style)
        ])
        
        # Détails de l'article
        if item.details:
            detail_text = "<br/>".join([f"• {detail}" for detail in item.details])
            items_data.append([
                Paragraph(detail_text, detail_style),
                '', '', '', ''
            ])
        
        # Remise si applicable
        if item.remise > 0:
            items_data.append([
                Paragraph("Remise", ParagraphStyle('Remise', 
                    parent=detail_style, 
                    textColor=colors.HexColor('#e74c3c'),
                    alignment=TA_RIGHT,
                    rightIndent=10
                )),
                '', '', '',
                Paragraph(f"-{item.remise:.2f} €", ParagraphStyle('RemiseAmount',
                    fontSize=9,
                    textColor=colors.HexColor('#e74c3c')
                ))
            ])
            items_data.append(['', '', '', '', ''])  # Ligne vide
    
    # Créer le tableau
    col_widths = [9*cm, 1.5*cm, 3*cm, 2*cm, 3*cm]
    items_table = Table(items_data, colWidths=col_widths)
    
    # Style du tableau
    table_style = [
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, 0), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Corps du tableau
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, 0), 1, colors.HexColor('#2c3e50')),
        
        # Lignes de séparation subtiles
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]
    
    items_table.setStyle(TableStyle(table_style))
    elements.append(items_table)
    elements.append(Spacer(1, 30))
    
    # Totaux avec style moderne
    totals_data = [
        [Paragraph("Total HT", normal_style), 
         Paragraph(f"{devis.total_ht:.2f} €", ParagraphStyle('Total', 
            parent=normal_style, 
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT
         ))],
        [Paragraph("Montant total de la TVA", normal_style), 
         Paragraph(f"{devis.total_tva:.2f} €", ParagraphStyle('Total',
            parent=normal_style,
            alignment=TA_RIGHT
         ))],
        [Paragraph("Total TTC", ParagraphStyle('TotalTTC',
            parent=normal_style,
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#2c3e50')
         )), 
         Paragraph(f"{devis.total_ttc:.2f} €", ParagraphStyle('TotalTTCAmount',
            parent=normal_style,
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_RIGHT
         ))]
    ]
    
    totals_table = Table(totals_data, colWidths=[12*cm, 4*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#2c3e50')),
        ('TOPPADDING', (0, -1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
    ]))
    
    elements.append(totals_table)
    
    # Construire le PDF avec le canvas personnalisé
    def build_with_canvas(canvas_obj, doc):
        canvas_obj.doc_number = devis.numero
    
    doc.build(elements, canvasmaker=NumberedCanvas, onFirstPage=build_with_canvas, onLaterPages=build_with_canvas)
    
    return filename
