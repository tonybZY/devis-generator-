# pdf_generator.py - Version avec design professionnel
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_JUSTIFY, TA_LEFT
import os

# Couleurs unifiées pour devis ET factures
COULEUR_PRINCIPALE = colors.HexColor('#2c3e50')  # Bleu foncé pour tout
COULEUR_SECONDAIRE = colors.HexColor('#34495e')  # Gris foncé
COULEUR_ACCENT = colors.HexColor('#3498db')      # Bleu plus clair pour accents
COULEUR_FOND = colors.HexColor('#ecf0f1')        # Gris clair
COULEUR_TEXTE = colors.HexColor('#2c3e50')       # Texte principal

class SimpleCanvas(canvas.Canvas):
    """Canvas simple pour ajouter le footer personnalisé"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.doc_info = {}
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for idx, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            self.draw_footer(idx + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_footer(self, page_num, total_pages):
        # Footer simple
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        
        # Nom entreprise à gauche
        self.drawString(2*cm, 1.5*cm, f"{self.doc_info.get('company_name', '')}, SAS")
        
        # Numéro de document et page à droite
        self.drawRightString(
            A4[0] - 2*cm, 
            1.5*cm, 
            f"{self.doc_info.get('doc_number', '')} · {page_num}/{total_pages}"
        )
        
        self.restoreState()

def create_styles():
    """Créer les styles personnalisés minimaux pour le document"""
    styles = getSampleStyleSheet()
    
    # Styles de base nécessaires
    styles.add(ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COULEUR_TEXTE,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=11,
        textColor=COULEUR_PRINCIPALE,
        fontName='Helvetica-Bold',
        spaceAfter=5
    ))
    
    styles.add(ParagraphStyle(
        'DetailStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#7f8c8d'),
        leftIndent=15,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        'MoneyStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COULEUR_PRINCIPALE,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT
    ))
    
    return styles

def generate_pdf_devis(devis):
    """Générer un PDF de devis avec le design demandé"""
    filename = os.path.join('generated', f'devis_{devis.numero}.pdf')
    
    # Configuration du document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=3*cm
    )
    
    styles = create_styles()
    elements = []
    
    # Titre simple
    title_style = ParagraphStyle('Title', fontSize=18, textColor=COULEUR_PRINCIPALE, 
                                fontName='Helvetica-Bold', spaceAfter=15)
    elements.append(Paragraph("Devis", title_style))
    
    # Informations du devis alignées
    info_style = ParagraphStyle('InfoStyle', fontSize=10, textColor=COULEUR_TEXTE)
    info_bold = ParagraphStyle('InfoBold', fontSize=10, textColor=COULEUR_TEXTE, fontName='Helvetica-Bold')
    
    # Table pour aligner les informations
    info_data = [
        [Paragraph("<b>Numéro de devis</b>", info_bold), Paragraph(devis.numero, info_style)],
        [Paragraph("<b>Date d'émission</b>", info_bold), Paragraph(devis.date_emission, info_style)],
        [Paragraph("<b>Date d'expiration</b>", info_bold), Paragraph(devis.date_expiration, info_style)]
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 15*mm))
    
    # Informations Fournisseur et Client en colonnes
    # Créer les cellules
    fournisseur_content = []
    fournisseur_content.append(Paragraph(f"<b>{devis.fournisseur_nom}</b>", info_bold))
    fournisseur_content.append(Paragraph(devis.fournisseur_adresse, info_style))
    fournisseur_content.append(Paragraph(devis.fournisseur_ville, info_style))
    fournisseur_content.append(Paragraph(devis.fournisseur_email, info_style))
    fournisseur_content.append(Paragraph(devis.fournisseur_siret, info_style))
    
    client_content = []
    client_content.append(Paragraph(f"<b>{devis.client_nom}</b>", info_bold))
    client_content.append(Paragraph(devis.client_adresse, info_style))
    client_content.append(Paragraph(devis.client_ville, info_style))
    if devis.client_email:
        client_content.append(Paragraph(devis.client_email, info_style))
    client_content.append(Paragraph(devis.client_siret, info_style))
    client_content.append(Paragraph(f"Numéro de TVA: {devis.client_tva}", info_style))
    
    # Table pour les deux colonnes
    company_table = Table([[fournisseur_content, client_content]], colWidths=[9*cm, 9*cm])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(company_table)
    elements.append(Spacer(1, 15*mm))
    
    # Texte d'introduction si présent
    if devis.texte_intro:
        intro_style = ParagraphStyle('IntroStyle', fontSize=10, textColor=COULEUR_TEXTE, alignment=TA_JUSTIFY)
        elements.append(Paragraph(devis.texte_intro, intro_style))
        elements.append(Spacer(1, 10*mm))
    
    # Tableau des articles avec en-tête noir
    items_data = []
    
    # En-tête du tableau
    headers = [
        Paragraph("<b>Description</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, fontName='Helvetica-Bold')),
        Paragraph("<b>Qté</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Prix unitaire</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold')),
        Paragraph("<b>TVA (%)</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Total HT</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
    ]
    items_data.append(headers)
    
    # Articles
    for item in devis.items:
        # Description avec détails
        desc_text = f"<b>{item.description}</b>"
        if item.details:
            desc_text += "<br/>" + "<br/>".join(item.details)
        
        items_data.append([
            Paragraph(desc_text, ParagraphStyle('ItemDesc', fontSize=9, textColor=COULEUR_TEXTE)),
            Paragraph(str(item.quantite), ParagraphStyle('ItemCenter', 
                fontSize=9, alignment=TA_CENTER)),
            Paragraph(f"{item.prix_unitaire:.2f} €", ParagraphStyle('ItemRight',
                fontSize=9, alignment=TA_RIGHT)),
            Paragraph(f"{item.tva_taux} %", ParagraphStyle('ItemCenter',
                fontSize=9, alignment=TA_CENTER)),
            Paragraph(f"{item.total_ht:.2f} €", ParagraphStyle('ItemRight',
                fontSize=9, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        ])
        
        # Ligne de remise si applicable
        if item.remise > 0:
            items_data.append([
                '', '', '',
                Paragraph("Remise", ParagraphStyle('Remise', fontSize=9, alignment=TA_RIGHT)),
                Paragraph(f"-{item.remise:.2f} €", ParagraphStyle('RemiseAmount',
                    fontSize=9, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
            ])
    
    # Créer le tableau
    col_widths = [9*cm, 1.5*cm, 3*cm, 2*cm, 3*cm]
    items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
    
    # Style du tableau
    table_style = [
        # En-tête noir
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Corps
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        
        # Bordures fines
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]
    
    items_table.setStyle(TableStyle(table_style))
    elements.append(items_table)
    elements.append(Spacer(1, 15*mm))
    
    # Totaux alignés à droite
    totals_data = [
        [Paragraph("Total HT", info_style), 
         Paragraph(f"{devis.total_ht:.2f} €", info_bold)],
        [Paragraph("Montant total de la TVA", info_style), 
         Paragraph(f"{devis.total_tva:.2f} €", info_bold)],
        [Paragraph("<b>Total TTC</b>", info_bold), 
         Paragraph(f"<b>{devis.total_ttc:.2f} €</b>", info_bold)]
    ]
    
    totals_table = Table(totals_data, colWidths=[13*cm, 4*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    elements.append(totals_table)
    elements.append(Spacer(1, 15*mm))
    
    # Conditions de paiement
    if devis.conditions_paiement:
        elements.append(Paragraph("<b>CONDITIONS DE PAIEMENT</b>", info_bold))
        elements.append(Paragraph(devis.conditions_paiement, info_style))
        elements.append(Spacer(1, 3*mm))
        if devis.penalites_retard:
            elements.append(Paragraph(devis.penalites_retard, ParagraphStyle('SmallText', 
                fontSize=8, textColor=colors.grey, fontName='Helvetica')))
        elements.append(Spacer(1, 10*mm))
    
    # Informations bancaires
    if devis.banque_nom:
        elements.append(Paragraph("<b>COORDONNÉES BANCAIRES</b>", info_bold))
        elements.append(Spacer(1, 3*mm))
        
        elements.append(Paragraph(f"<b>Banque:</b> {devis.banque_nom}", info_style))
        elements.append(Paragraph(f"<b>IBAN:</b> {devis.banque_iban}", info_style))
        elements.append(Paragraph(f"<b>BIC:</b> {devis.banque_bic}", info_style))
        
        elements.append(Spacer(1, 10*mm))
    
    # Texte de conclusion
    if devis.texte_conclusion:
        elements.append(Paragraph(devis.texte_conclusion, info_style))
        elements.append(Spacer(1, 10*mm))
    
    # Signature
    elements.append(Spacer(1, 15*mm))
    sig_data = [[
        Paragraph("", info_style),  # Colonne vide
        Paragraph("Bon pour accord<br/>Date et signature:", info_style)
    ]]
    
    sig_table = Table(sig_data, colWidths=[12*cm, 6*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(sig_table)
    
    # Construire le PDF avec footer personnalisé
    def build_with_canvas(canvas_obj, doc):
        canvas_obj.doc_info = {
            'company_name': devis.fournisseur_nom,
            'doc_number': devis.numero
        }
    
    doc.build(elements, canvasmaker=SimpleCanvas, onFirstPage=build_with_canvas)
    
    return filename

def generate_pdf_facture(facture):
    """Générer un PDF de facture avec le même design"""
    filename = os.path.join('generated', f'facture_{facture.numero}.pdf')
    
    # Configuration du document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=3*cm
    )
    
    styles = create_styles()
    elements = []
    
    # Titre simple
    title_style = ParagraphStyle('Title', fontSize=18, textColor=COULEUR_PRINCIPALE, 
                                fontName='Helvetica-Bold', spaceAfter=15)
    elements.append(Paragraph("Facture", title_style))
    
    # Informations de la facture alignées
    info_style = ParagraphStyle('InfoStyle', fontSize=10, textColor=COULEUR_TEXTE)
    info_bold = ParagraphStyle('InfoBold', fontSize=10, textColor=COULEUR_TEXTE, fontName='Helvetica-Bold')
    
    # Table pour aligner les informations
    info_data = [
        [Paragraph("<b>Numéro de facture</b>", info_bold), Paragraph(facture.numero, info_style)],
        [Paragraph("<b>Date d'émission</b>", info_bold), Paragraph(facture.date_emission, info_style)],
        [Paragraph("<b>Date d'échéance</b>", info_bold), Paragraph(facture.date_echeance, info_style)]
    ]
    
    # Ajouter le statut avec couleur
    statut_color = COULEUR_ACCENT
    if facture.statut_paiement == "En retard":
        statut_color = colors.HexColor('#e74c3c')
    elif facture.statut_paiement == "Payée":
        statut_color = colors.HexColor('#27ae60')
    
    info_data.append([
        Paragraph("<b>Statut</b>", info_bold),
        Paragraph(f"<font color='{statut_color}'><b>{facture.statut_paiement}</b></font>", info_style)
    ])
    
    # Ajouter les références si présentes
    if facture.numero_commande:
        info_data.append([
            Paragraph("<b>N° de commande</b>", info_bold),
            Paragraph(facture.numero_commande, info_style)
        ])
    if facture.reference_devis:
        info_data.append([
            Paragraph("<b>Réf. devis</b>", info_bold),
            Paragraph(facture.reference_devis, info_style)
        ])
    
    info_table = Table(info_data, colWidths=[5*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 15*mm))
    
    # Informations Fournisseur et Client en colonnes
    fournisseur_content = []
    fournisseur_content.append(Paragraph(f"<b>{facture.fournisseur_nom}</b>", info_bold))
    fournisseur_content.append(Paragraph(facture.fournisseur_adresse, info_style))
    fournisseur_content.append(Paragraph(facture.fournisseur_ville, info_style))
    fournisseur_content.append(Paragraph(facture.fournisseur_email, info_style))
    fournisseur_content.append(Paragraph(facture.fournisseur_siret, info_style))
    
    client_content = []
    client_content.append(Paragraph(f"<b>{facture.client_nom}</b>", info_bold))
    client_content.append(Paragraph(facture.client_adresse, info_style))
    client_content.append(Paragraph(facture.client_ville, info_style))
    if facture.client_email:
        client_content.append(Paragraph(facture.client_email, info_style))
    client_content.append(Paragraph(facture.client_siret, info_style))
    client_content.append(Paragraph(f"Numéro de TVA: {facture.client_tva}", info_style))
    
    # Table pour les deux colonnes
    company_table = Table([[fournisseur_content, client_content]], colWidths=[9*cm, 9*cm])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(company_table)
    elements.append(Spacer(1, 15*mm))
    
    # Tableau des articles avec en-tête noir
    items_data = []
    
    # En-tête du tableau
    headers = [
        Paragraph("<b>Description</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, fontName='Helvetica-Bold')),
        Paragraph("<b>Qté</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Prix unitaire</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold')),
        Paragraph("<b>TVA (%)</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Total HT</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
    ]
    items_data.append(headers)
    
    # Articles
    for item in facture.items:
        # Description avec détails
        desc_text = f"<b>{item.description}</b>"
        if item.details:
            desc_text += "<br/>" + "<br/>".join(item.details)
        
        items_data.append([
            Paragraph(desc_text, ParagraphStyle('ItemDesc', fontSize=9, textColor=COULEUR_TEXTE)),
            Paragraph(str(item.quantite), ParagraphStyle('ItemCenter', 
                fontSize=9, alignment=TA_CENTER)),
            Paragraph(f"{item.prix_unitaire:.2f} €", ParagraphStyle('ItemRight',
                fontSize=9, alignment=TA_RIGHT)),
            Paragraph(f"{item.tva_taux} %", ParagraphStyle('ItemCenter',
                fontSize=9, alignment=TA_CENTER)),
            Paragraph(f"{item.total_ht:.2f} €", ParagraphStyle('ItemRight',
                fontSize=9, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        ])
        
        # Ligne de remise si applicable
        if item.remise > 0:
            items_data.append([
                '', '', '',
                Paragraph("Remise", ParagraphStyle('Remise', fontSize=9, alignment=TA_RIGHT)),
                Paragraph(f"-{item.remise:.2f} €", ParagraphStyle('RemiseAmount',
                    fontSize=9, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
            ])
    
    # Créer le tableau
    col_widths = [9*cm, 1.5*cm, 3*cm, 2*cm, 3*cm]
    items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
    
    # Style du tableau
    table_style = [
        # En-tête noir
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Corps
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        
        # Bordures fines
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]
    
    items_table.setStyle(TableStyle(table_style))
    elements.append(items_table)
    elements.append(Spacer(1, 15*mm))
    
    # Totaux alignés à droite
    totals_data = [
        [Paragraph("Total HT", info_style), 
         Paragraph(f"{facture.total_ht:.2f} €", info_bold)],
        [Paragraph("Montant total de la TVA", info_style), 
         Paragraph(f"{facture.total_tva:.2f} €", info_bold)],
        [Paragraph("<b>Total TTC</b>", info_bold), 
         Paragraph(f"<b>{facture.total_ttc:.2f} €</b>", info_bold)]
    ]
    
    totals_table = Table(totals_data, colWidths=[13*cm, 4*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    elements.append(totals_table)
    elements.append(Spacer(1, 15*mm))
    
    # Conditions de paiement
    if facture.conditions_paiement:
        elements.append(Paragraph("<b>CONDITIONS DE PAIEMENT</b>", info_bold))
        elements.append(Paragraph(facture.conditions_paiement, info_style))
        elements.append(Spacer(1, 3*mm))
        if facture.penalites_retard:
            elements.append(Paragraph(facture.penalites_retard, ParagraphStyle('SmallText', 
                fontSize=8, textColor=colors.grey, fontName='Helvetica')))
        elements.append(Spacer(1, 10*mm))
    
    # Informations bancaires
    if facture.banque_nom:
        elements.append(Paragraph("<b>COORDONNÉES BANCAIRES POUR LE RÈGLEMENT</b>", info_bold))
        elements.append(Spacer(1, 3*mm))
        
        elements.append(Paragraph(f"<b>Banque:</b> {facture.banque_nom}", info_style))
        elements.append(Paragraph(f"<b>IBAN:</b> {facture.banque_iban}", info_style))
        elements.append(Paragraph(f"<b>BIC:</b> {facture.banque_bic}", info_style))
    
    # Mentions légales
    elements.append(Spacer(1, 10*mm))
    legal_text = """TVA sur les encaissements. En cas de retard de paiement, seront exigibles, conformément à l'article L441-10 du code de commerce, une indemnité calculée sur la base de trois fois le taux de l'intérêt légal en vigueur ainsi qu'une indemnité forfaitaire pour frais de recouvrement de 40 euros."""
    elements.append(Paragraph(legal_text, ParagraphStyle('LegalText', 
        fontSize=8, textColor=colors.grey, fontName='Helvetica', alignment=TA_JUSTIFY)))
    
    # Construire le PDF avec footer personnalisé
    def build_with_canvas(canvas_obj, doc):
        canvas_obj.doc_info = {
            'company_name': facture.fournisseur_nom,
            'doc_number': facture.numero
        }
    
    doc.build(elements, canvasmaker=SimpleCanvas, onFirstPage=build_with_canvas)
    
    return filename
