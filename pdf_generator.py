# pdf_generator.py - Version avec design unifié et en-tête compact
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus.flowables import HRFlowable
import os

# Couleurs unifiées pour devis ET factures
COULEUR_PRINCIPALE = colors.HexColor('#2c3e50')  # Bleu foncé pour tout
COULEUR_SECONDAIRE = colors.HexColor('#34495e')  # Gris foncé
COULEUR_ACCENT = colors.HexColor('#3498db')      # Bleu plus clair pour accents
COULEUR_FOND = colors.HexColor('#ecf0f1')        # Gris clair
COULEUR_TEXTE = colors.HexColor('#2c3e50')       # Texte principal

class NumberedCanvas(canvas.Canvas):
    """Canvas personnalisé pour ajouter numérotation et pied de page"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.company_info = {}

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_footer(self, page_count):
        # Ligne de séparation
        self.setStrokeColor(COULEUR_FOND)
        self.setLineWidth(1)
        self.line(2*cm, 3*cm, A4[0] - 2*cm, 3*cm)
        
        # Informations de page
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.grey)
        
        # Numéro de page
        self.drawRightString(
            A4[0] - 2*cm,
            2*cm,
            f"Page {self._pageNumber}/{page_count}"
        )
        
        # Informations légales
        self.drawCentredString(
            A4[0] / 2,
            2*cm,
            f"{self.company_info.get('nom', '')} - SIRET: {self.company_info.get('siret', '')} - TVA: {self.company_info.get('tva', '')}"
        )
        
        # Email
        self.setFillColor(COULEUR_ACCENT)
        self.drawString(
            2*cm,
            2*cm,
            self.company_info.get('email', '')
        )

def create_styles():
    """Créer les styles personnalisés pour le document"""
    styles = getSampleStyleSheet()
    
    # Style pour le titre (DEVIS ou FACTURE)
    styles.add(ParagraphStyle(
        'DocumentTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=COULEUR_PRINCIPALE,
        spaceAfter=5,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    ))
    
    # Style pour le nom de l'entreprise (plus petit)
    styles.add(ParagraphStyle(
        'CompanyName',
        parent=styles['Normal'],
        fontSize=14,
        textColor=COULEUR_ACCENT,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT
    ))
    
    # Style pour les informations de section
    styles.add(ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=11,
        textColor=COULEUR_PRINCIPALE,
        fontName='Helvetica-Bold',
        spaceAfter=5
    ))
    
    # Style pour le texte normal
    styles.add(ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COULEUR_TEXTE,
        fontName='Helvetica'
    ))
    
    # Style pour les détails
    styles.add(ParagraphStyle(
        'DetailStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#7f8c8d'),
        leftIndent=15,
        fontName='Helvetica'
    ))
    
    # Style pour les montants
    styles.add(ParagraphStyle(
        'MoneyStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COULEUR_PRINCIPALE,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT
    ))
    
    # Style pour les informations bancaires
    styles.add(ParagraphStyle(
        'BankInfo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=COULEUR_TEXTE,
        fontName='Helvetica',
        borderWidth=1,
        borderColor=COULEUR_FOND,
        borderPadding=10,
        backColor=colors.HexColor('#f8f9fa')
    ))
    
    return styles

def create_header_table(doc_type, company_name):
    """Créer un en-tête compact avec titre à gauche et entreprise à droite"""
    styles = create_styles()
    
    # Créer une table pour l'en-tête
    header_data = [[
        Paragraph(doc_type, styles['DocumentTitle']),
        Paragraph(company_name.upper(), styles['CompanyName'])
    ]]
    
    header_table = Table(header_data, colWidths=[10*cm, 8*cm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, 0), 2, COULEUR_PRINCIPALE),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    
    return header_table

def generate_pdf_devis(devis):
    """Générer un PDF de devis avec design unifié"""
    filename = os.path.join('generated', f'devis_{devis.numero}.pdf')
    
    # Configuration du document avec moins de marge en haut
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1.5*cm,  # Réduit de 2cm à 1.5cm
        bottomMargin=4*cm
    )
    
    styles = create_styles()
    elements = []
    
    # En-tête compact
    elements.append(create_header_table("DEVIS", devis.fournisseur_nom))
    elements.append(Spacer(1, 8*mm))
    
    # Informations du devis dans un format plus compact
    info_data = [
        [Paragraph("<b>Numéro</b>", styles['SectionHeader']), 
         Paragraph(devis.numero, styles['CustomNormal']),
         Paragraph("<b>Date d'émission</b>", styles['SectionHeader']), 
         Paragraph(devis.date_emission, styles['CustomNormal'])],
        [Paragraph("<b>Validité</b>", styles['SectionHeader']), 
         Paragraph(devis.date_expiration, styles['CustomNormal']),
         "", ""]
    ]
    
    info_table = Table(info_data, colWidths=[3.5*cm, 5*cm, 4*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 1, COULEUR_FOND),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 12*mm))
    
    # Informations Fournisseur et Client côte à côte
    company_headers = [
        [Paragraph("<b>ÉMETTEUR</b>", ParagraphStyle('CompanyHeader', 
            fontSize=11, textColor=COULEUR_PRINCIPALE, fontName='Helvetica-Bold')),
         Paragraph("<b>CLIENT</b>", ParagraphStyle('CompanyHeader', 
            fontSize=11, textColor=COULEUR_PRINCIPALE, fontName='Helvetica-Bold'))]
    ]
    
    header_table = Table(company_headers, colWidths=[9*cm, 9*cm])
    header_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, COULEUR_PRINCIPALE),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(header_table)
    
    # Contenu des informations
    company_data = [
        [Paragraph(f"<b>{devis.fournisseur_nom}</b>", styles['CustomNormal']),
         Paragraph(f"<b>{devis.client_nom}</b>", styles['CustomNormal'])],
        [Paragraph(devis.fournisseur_adresse, styles['CustomNormal']), 
         Paragraph(devis.client_adresse, styles['CustomNormal'])],
        [Paragraph(devis.fournisseur_ville, styles['CustomNormal']), 
         Paragraph(devis.client_ville, styles['CustomNormal'])],
        [Paragraph(f"Email: {devis.fournisseur_email}", styles['CustomNormal']), 
         Paragraph(f"SIRET: {devis.client_siret}", styles['CustomNormal'])],
        [Paragraph(f"Tél: {devis.fournisseur_telephone}", styles['CustomNormal']), 
         Paragraph(f"N° TVA: {devis.client_tva}", styles['CustomNormal'])],
        [Paragraph(f"SIRET: {devis.fournisseur_siret}", styles['CustomNormal']), 
         Paragraph(f"Email: {devis.client_email}", styles['CustomNormal']) if devis.client_email else Paragraph("", styles['CustomNormal'])],
    ]
    
    company_table = Table(company_data, colWidths=[9*cm, 9*cm])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(company_table)
    elements.append(Spacer(1, 15*mm))
    
    # Texte d'introduction si présent
    if devis.texte_intro:
        intro_style = ParagraphStyle('IntroStyle', 
            parent=styles['CustomNormal'],
            fontSize=10,
            textColor=COULEUR_TEXTE,
            alignment=TA_JUSTIFY
        )
        elements.append(Paragraph(devis.texte_intro, intro_style))
        elements.append(Spacer(1, 8*mm))
    
    # Tableau des articles
    items_data = []
    
    # En-tête du tableau
    headers = [
        Paragraph("<b>Description</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, fontName='Helvetica-Bold')),
        Paragraph("<b>Qté</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Prix unitaire</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold')),
        Paragraph("<b>TVA</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Total HT</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
    ]
    items_data.append(headers)
    
    # Articles
    row_index = 0
    for item in devis.items:
        # Ligne principale
        items_data.append([
            Paragraph(f"<b>{item.description}</b>", styles['CustomNormal']),
            Paragraph(str(item.quantite), ParagraphStyle('ItemCenter', 
                parent=styles['CustomNormal'], alignment=TA_CENTER)),
            Paragraph(f"{item.prix_unitaire:.2f} €", styles['MoneyStyle']),
            Paragraph(f"{item.tva_taux}%", ParagraphStyle('ItemCenter', 
                parent=styles['CustomNormal'], alignment=TA_CENTER)),
            Paragraph(f"{item.total_ht:.2f} €", styles['MoneyStyle'])
        ])
        row_index += 1
        
        # Détails
        if item.details:
            detail_text = "<br/>".join([f"• {detail}" for detail in item.details])
            items_data.append([
                Paragraph(detail_text, styles['DetailStyle']),
                '', '', '', ''
            ])
            row_index += 1
        
        # Remise
        if item.remise > 0:
            items_data.append([
                '', '', '',
                Paragraph("Remise", ParagraphStyle('Remise', 
                    fontSize=9, textColor=COULEUR_ACCENT, alignment=TA_RIGHT)),
                Paragraph(f"-{item.remise:.2f} €", ParagraphStyle('RemiseAmount',
                    fontSize=9, textColor=COULEUR_ACCENT, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
            ])
            row_index += 1
    
    # Créer le tableau
    col_widths = [8.5*cm, 2*cm, 3*cm, 2*cm, 3*cm]
    items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
    
    # Style du tableau avec couleur unifiée
    table_style = [
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), COULEUR_PRINCIPALE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('ALIGN', (3, 0), (3, 0), 'CENTER'),
        ('ALIGN', (4, 0), (4, 0), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Corps
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Bordures
        ('BOX', (0, 0), (-1, -1), 1, COULEUR_FOND),
        ('INNERGRID', (0, 0), (-1, 0), 1, COULEUR_PRINCIPALE),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, COULEUR_FOND),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]
    
    # Alternance de couleurs
    for i in range(1, len(items_data)):
        if i % 2 == 0:
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa')))
    
    items_table.setStyle(TableStyle(table_style))
    elements.append(items_table)
    elements.append(Spacer(1, 12*mm))
    
    # Totaux
    totals_data = [
        [Paragraph("Total HT", styles['CustomNormal']), 
         Paragraph(f"{devis.total_ht:.2f} €", styles['MoneyStyle'])],
        [Paragraph("TVA (20%)", styles['CustomNormal']), 
         Paragraph(f"{devis.total_tva:.2f} €", styles['MoneyStyle'])],
        [Paragraph("<b>TOTAL TTC</b>", ParagraphStyle('TotalTTC',
            fontSize=14, textColor=colors.white, fontName='Helvetica-Bold')), 
         Paragraph(f"<b>{devis.total_ttc:.2f} €</b>", ParagraphStyle('TotalAmount',
            fontSize=14, textColor=colors.white, fontName='Helvetica-Bold', alignment=TA_RIGHT))]
    ]
    
    totals_table = Table(totals_data, colWidths=[12*cm, 4*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        
        # Lignes de séparation
        ('LINEABOVE', (0, 0), (-1, 0), 1, COULEUR_FOND),
        ('LINEABOVE', (0, -1), (-1, -1), 2, COULEUR_PRINCIPALE),
        
        # Style de la ligne total
        ('BACKGROUND', (0, -1), (-1, -1), COULEUR_PRINCIPALE),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('TOPPADDING', (0, -1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        
        # Padding général
        ('TOPPADDING', (0, 0), (-1, -2), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -2), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(totals_table)
    elements.append(Spacer(1, 15*mm))
    
    # Conditions de paiement
    elements.append(Paragraph("<b>CONDITIONS DE PAIEMENT</b>", styles['SectionHeader']))
    elements.append(Paragraph(devis.conditions_paiement, styles['CustomNormal']))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(devis.penalites_retard, ParagraphStyle('SmallText', 
        fontSize=8, textColor=colors.grey, fontName='Helvetica')))
    elements.append(Spacer(1, 12*mm))
    
    # Informations bancaires
    bank_title = Paragraph("<b>COORDONNÉES BANCAIRES</b>", styles['SectionHeader'])
    elements.append(bank_title)
    
    bank_data = [
        [Paragraph("<b>Banque:</b>", styles['CustomNormal']), 
         Paragraph(devis.banque_nom, styles['CustomNormal'])],
        [Paragraph("<b>IBAN:</b>", styles['CustomNormal']), 
         Paragraph(devis.banque_iban, styles['CustomNormal'])],
        [Paragraph("<b>BIC:</b>", styles['CustomNormal']), 
         Paragraph(devis.banque_bic, styles['CustomNormal'])]
    ]
    
    bank_table = Table(bank_data, colWidths=[3*cm, 13*cm])
    bank_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f4f8')),
        ('BOX', (0, 0), (-1, -1), 1, COULEUR_ACCENT),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(bank_table)
    
    # Texte de conclusion
    if devis.texte_conclusion:
        elements.append(Spacer(1, 12*mm))
        elements.append(Paragraph(devis.texte_conclusion, styles['CustomNormal']))
    
    # Signature
    elements.append(Spacer(1, 15*mm))
    signature_data = [
        ["", "Bon pour accord"],
        ["", "Date et signature:"],
        ["", ""],
        ["", "_______________________"]
    ]
    
    signature_table = Table(signature_data, colWidths=[10*cm, 6*cm])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (1, 0), (1, -1), 10),
        ('TOPPADDING', (1, 0), (1, -1), 3),
    ]))
    
    elements.append(signature_table)
    
    # Construire le PDF
    def build_with_canvas(canvas_obj, doc):
        canvas_obj.company_info = {
            'nom': devis.fournisseur_nom,
            'siret': devis.fournisseur_siret,
            'email': devis.fournisseur_email,
            'tva': f"FR{devis.fournisseur_siret[:9]}"
        }
    
    doc.build(elements, canvasmaker=NumberedCanvas, onFirstPage=build_with_canvas, onLaterPages=build_with_canvas)
    
    return filename

def generate_pdf_facture(facture):
    """Générer un PDF de facture avec le même design unifié"""
    filename = os.path.join('generated', f'facture_{facture.numero}.pdf')
    
    # Configuration du document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1.5*cm,  # Même marge réduite
        bottomMargin=4*cm
    )
    
    styles = create_styles()
    elements = []
    
    # En-tête compact (même style que devis)
    elements.append(create_header_table("FACTURE", facture.fournisseur_nom))
    elements.append(Spacer(1, 8*mm))
    
    # Informations de la facture (format compact)
    info_rows = []
    
    # Première ligne
    info_rows.append([
        Paragraph("<b>Numéro</b>", styles['SectionHeader']), 
        Paragraph(facture.numero, styles['CustomNormal']),
        Paragraph("<b>Date</b>", styles['SectionHeader']), 
        Paragraph(facture.date_emission, styles['CustomNormal'])
    ])
    
    # Deuxième ligne
    info_rows.append([
        Paragraph("<b>Échéance</b>", styles['SectionHeader']), 
        Paragraph(facture.date_echeance, styles['CustomNormal']),
        Paragraph("<b>Statut</b>", styles['SectionHeader']),
        Paragraph("", styles['CustomNormal'])  # Placeholder
    ])
    
    # Créer le paragraphe de statut avec la bonne couleur
    statut_color = COULEUR_ACCENT
    if facture.statut_paiement == "En retard":
        statut_color = colors.HexColor('#e74c3c')  # Rouge
    elif facture.statut_paiement == "Payée":
        statut_color = colors.HexColor('#27ae60')  # Vert
    
    # Remplacer le placeholder par le statut coloré
    info_rows[1][3] = Paragraph(f"<font color='{statut_color}'><b>{facture.statut_paiement}</b></font>", 
                                styles['CustomNormal'])
    
    # Ajouter les références si présentes
    if facture.numero_commande or facture.reference_devis:
        ref_row = []
        if facture.numero_commande:
            ref_row.extend([
                Paragraph("<b>Commande</b>", styles['SectionHeader']),
                Paragraph(facture.numero_commande, styles['CustomNormal'])
            ])
        if facture.reference_devis:
            ref_row.extend([
                Paragraph("<b>Réf. devis</b>", styles['SectionHeader']),
                Paragraph(facture.reference_devis, styles['CustomNormal'])
            ])
        # Compléter la ligne si nécessaire
        while len(ref_row) < 4:
            ref_row.extend(["", ""])
        info_rows.append(ref_row)
    
    info_table = Table(info_rows, colWidths=[3.5*cm, 5*cm, 4*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff5f5')),  # Légèrement rosé pour facture
        ('BOX', (0, 0), (-1, -1), 1, COULEUR_FOND),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 12*mm))
    
    # Informations Fournisseur et Client (même structure que devis)
    company_headers = [
        [Paragraph("<b>ÉMETTEUR</b>", ParagraphStyle('CompanyHeader', 
            fontSize=11, textColor=COULEUR_PRINCIPALE, fontName='Helvetica-Bold')),
         Paragraph("<b>CLIENT</b>", ParagraphStyle('CompanyHeader', 
            fontSize=11, textColor=COULEUR_PRINCIPALE, fontName='Helvetica-Bold'))]
    ]
    
    header_table = Table(company_headers, colWidths=[9*cm, 9*cm])
    header_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, COULEUR_PRINCIPALE),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(header_table)
    
    # Contenu des informations
    company_data = [
        [Paragraph(f"<b>{facture.fournisseur_nom}</b>", styles['CustomNormal']),
         Paragraph(f"<b>{facture.client_nom}</b>", styles['CustomNormal'])],
        [Paragraph(facture.fournisseur_adresse, styles['CustomNormal']), 
         Paragraph(facture.client_adresse, styles['CustomNormal'])],
        [Paragraph(facture.fournisseur_ville, styles['CustomNormal']), 
         Paragraph(facture.client_ville, styles['CustomNormal'])],
        [Paragraph(f"Email: {facture.fournisseur_email}", styles['CustomNormal']), 
         Paragraph(f"SIRET: {facture.client_siret}", styles['CustomNormal'])],
        [Paragraph(f"Tél: {facture.fournisseur_telephone}", styles['CustomNormal']), 
         Paragraph(f"N° TVA: {facture.client_tva}", styles['CustomNormal'])],
        [Paragraph(f"SIRET: {facture.fournisseur_siret}", styles['CustomNormal']), 
         Paragraph(f"Email: {facture.client_email}", styles['CustomNormal']) if facture.client_email else Paragraph("", styles['CustomNormal'])],
    ]
    
    company_table = Table(company_data, colWidths=[9*cm, 9*cm])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(company_table)
    elements.append(Spacer(1, 15*mm))
    
    # Tableau des articles (même structure et couleurs que devis)
    items_data = []
    
    # En-tête du tableau
    headers = [
        Paragraph("<b>Description</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, fontName='Helvetica-Bold')),
        Paragraph("<b>Qté</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Prix unitaire</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold')),
        Paragraph("<b>TVA</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Total HT</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
    ]
    items_data.append(headers)
    
    # Articles
    row_index = 0
    for item in facture.items:
        # Ligne principale
        items_data.append([
            Paragraph(f"<b>{item.description}</b>", styles['CustomNormal']),
            Paragraph(str(item.quantite), ParagraphStyle('ItemCenter', 
                parent=styles['CustomNormal'], alignment=TA_CENTER)),
            Paragraph(f"{item.prix_unitaire:.2f} €", styles['MoneyStyle']),
            Paragraph(f"{item.tva_taux}%", ParagraphStyle('ItemCenter', 
                parent=styles['CustomNormal'], alignment=TA_CENTER)),
            Paragraph(f"{item.total_ht:.2f} €", styles['MoneyStyle'])
        ])
        row_index += 1
        
        # Détails
        if item.details:
            detail_text = "<br/>".join([f"• {detail}" for detail in item.details])
            items_data.append([
                Paragraph(detail_text, styles['DetailStyle']),
                '', '', '', ''
            ])
            row_index += 1
        
        # Remise
        if item.remise > 0:
            items_data.append([
                '', '', '',
                Paragraph("Remise", ParagraphStyle('Remise', 
                    fontSize=9, textColor=COULEUR_ACCENT, alignment=TA_RIGHT)),
                Paragraph(f"-{item.remise:.2f} €", ParagraphStyle('RemiseAmount',
                    fontSize=9, textColor=COULEUR_ACCENT, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
            ])
            row_index += 1
    
    # Créer le tableau
    col_widths = [8.5*cm, 2*cm, 3*cm, 2*cm, 3*cm]
    items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
    
    # Style du tableau (même couleur que devis)
    table_style = [
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), COULEUR_PRINCIPALE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('ALIGN', (3, 0), (3, 0), 'CENTER'),
        ('ALIGN', (4, 0), (4, 0), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Corps
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Bordures
        ('BOX', (0, 0), (-1, -1), 1, COULEUR_FOND),
        ('INNERGRID', (0, 0), (-1, 0), 1, COULEUR_PRINCIPALE),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, COULEUR_FOND),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]
    
    # Alternance de couleurs (légèrement rosé pour facture)
    for i in range(1, len(items_data)):
        if i % 2 == 0:
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fff5f5')))
    
    items_table.setStyle(TableStyle(table_style))
    elements.append(items_table)
    elements.append(Spacer(1, 12*mm))
    
    # Totaux (même style que devis)
    totals_data = [
        [Paragraph("Total HT", styles['CustomNormal']), 
         Paragraph(f"{facture.total_ht:.2f} €", styles['MoneyStyle'])],
        [Paragraph("TVA (20%)", styles['CustomNormal']), 
         Paragraph(f"{facture.total_tva:.2f} €", styles['MoneyStyle'])],
        [Paragraph("<b>TOTAL TTC</b>", ParagraphStyle('TotalTTC',
            fontSize=14, textColor=colors.white, fontName='Helvetica-Bold')), 
         Paragraph(f"<b>{facture.total_ttc:.2f} €</b>", ParagraphStyle('TotalAmount',
            fontSize=14, textColor=colors.white, fontName='Helvetica-Bold', alignment=TA_RIGHT))]
    ]
    
    totals_table = Table(totals_data, colWidths=[12*cm, 4*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        
        # Lignes de séparation
        ('LINEABOVE', (0, 0), (-1, 0), 1, COULEUR_FOND),
        ('LINEABOVE', (0, -1), (-1, -1), 2, COULEUR_PRINCIPALE),
        
        # Style de la ligne total (même couleur que devis)
        ('BACKGROUND', (0, -1), (-1, -1), COULEUR_PRINCIPALE),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('TOPPADDING', (0, -1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        
        # Padding général
        ('TOPPADDING', (0, 0), (-1, -2), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -2), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(totals_table)
    elements.append(Spacer(1, 15*mm))
    
    # Conditions de paiement
    elements.append(Paragraph("<b>CONDITIONS DE PAIEMENT</b>", styles['SectionHeader']))
    elements.append(Paragraph(facture.conditions_paiement, styles['CustomNormal']))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(facture.penalites_retard, ParagraphStyle('SmallText', 
        fontSize=8, textColor=colors.grey, fontName='Helvetica')))
    elements.append(Spacer(1, 12*mm))
    
    # Informations bancaires
    bank_title = Paragraph("<b>COORDONNÉES BANCAIRES POUR LE RÈGLEMENT</b>", styles['SectionHeader'])
    elements.append(bank_title)
    
    bank_data = [
        [Paragraph("<b>Banque:</b>", styles['CustomNormal']), 
         Paragraph(facture.banque_nom, styles['CustomNormal'])],
        [Paragraph("<b>IBAN:</b>", styles['CustomNormal']), 
         Paragraph(facture.banque_iban, styles['CustomNormal'])],
        [Paragraph("<b>BIC:</b>", styles['CustomNormal']), 
         Paragraph(facture.banque_bic, styles['CustomNormal'])]
    ]
    
    bank_table = Table(bank_data, colWidths=[3*cm, 13*cm])
    bank_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffe8e8')),  # Légèrement rosé
        ('BOX', (0, 0), (-1, -1), 1, COULEUR_ACCENT),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(bank_table)
    
    # Mentions légales
    elements.append(Spacer(1, 12*mm))
    legal_text = """TVA sur les encaissements. En cas de retard de paiement, seront exigibles, conformément à l'article L441-10 du code de commerce, une indemnité calculée sur la base de trois fois le taux de l'intérêt légal en vigueur ainsi qu'une indemnité forfaitaire pour frais de recouvrement de 40 euros."""
    elements.append(Paragraph(legal_text, ParagraphStyle('LegalText', 
        fontSize=8, textColor=colors.grey, fontName='Helvetica', alignment=TA_JUSTIFY)))
    
    # Construire le PDF
    def build_with_canvas(canvas_obj, doc):
        canvas_obj.company_info = {
            'nom': facture.fournisseur_nom,
            'siret': facture.fournisseur_siret,
            'email': facture.fournisseur_email,
            'tva': f"FR{facture.fournisseur_siret[:9]}"
        }
    
    doc.build(elements, canvasmaker=NumberedCanvas, onFirstPage=build_with_canvas, onLaterPages=build_with_canvas)
    
    return filename
