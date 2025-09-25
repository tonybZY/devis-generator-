# pdf_generator.py - Version avec design professionnel, thèmes colorés et support logo
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_JUSTIFY, TA_LEFT
import os
import requests
from io import BytesIO

# Thèmes de couleurs disponibles
THEMES_COULEURS = {
    'bleu': {
        'principale': colors.HexColor('#2c3e50'),
        'secondaire': colors.HexColor('#34495e'), 
        'accent': colors.HexColor('#3498db'),
        'fond': colors.HexColor('#ecf0f1'),
        'header_bg': colors.HexColor('#2d3436')
    },
    'vert': {
        'principale': colors.HexColor('#27ae60'),
        'secondaire': colors.HexColor('#2d5016'), 
        'accent': colors.HexColor('#58d68d'),
        'fond': colors.HexColor('#e8f8f5'),
        'header_bg': colors.HexColor('#1e8449')
    },
    'rouge': {
        'principale': colors.HexColor('#e74c3c'),
        'secondaire': colors.HexColor('#922b21'), 
        'accent': colors.HexColor('#f1948a'),
        'fond': colors.HexColor('#fadbd8'),
        'header_bg': colors.HexColor('#c0392b')
    },
    'violet': {
        'principale': colors.HexColor('#9b59b6'),
        'secondaire': colors.HexColor('#6c3483'), 
        'accent': colors.HexColor('#d7bde2'),
        'fond': colors.HexColor('#f4ecf7'),
        'header_bg': colors.HexColor('#8e44ad')
    },
    'orange': {
        'principale': colors.HexColor('#e67e22'),
        'secondaire': colors.HexColor('#a04000'), 
        'accent': colors.HexColor('#f5b041'),
        'fond': colors.HexColor('#fdeaa7'),
        'header_bg': colors.HexColor('#d35400')
    },
    'noir': {
        'principale': colors.HexColor('#2c3e50'),
        'secondaire': colors.HexColor('#34495e'), 
        'accent': colors.HexColor('#95a5a6'),
        'fond': colors.HexColor('#ecf0f1'),
        'header_bg': colors.HexColor('#2c3e50')
    }
}

# Couleurs par défaut (pour compatibilité)
COULEUR_PRINCIPALE = colors.HexColor('#2c3e50')
COULEUR_SECONDAIRE = colors.HexColor('#34495e')
COULEUR_ACCENT = colors.HexColor('#3498db')
COULEUR_FOND = colors.HexColor('#ecf0f1')
COULEUR_TEXTE = colors.HexColor('#2c3e50')

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

def download_logo(logo_url):
    """Télécharger et traiter le logo depuis une URL"""
    if not logo_url:
        return None
    
    try:
        # Télécharger l'image avec un timeout
        response = requests.get(logo_url, timeout=10)
        if response.status_code == 200:
            img_data = BytesIO(response.content)
            logo = Image(img_data)
            
            # Redimensionner le logo (hauteur max 2.5cm)
            max_height = 2.5 * cm
            logo.drawHeight = max_height
            logo.drawWidth = max_height * logo.imageWidth / logo.imageHeight
            
            # Si le logo est trop large, le redimensionner par la largeur
            max_width = 4 * cm
            if logo.drawWidth > max_width:
                logo.drawWidth = max_width
                logo.drawHeight = max_width * logo.imageHeight / logo.imageWidth
            
            return logo
    except Exception as e:
        print(f"Erreur lors du téléchargement du logo: {e}")
        return None
    
    return None

def create_header_with_logo(logo_url, title, title_size=18):
    """Créer l'en-tête avec logo et titre"""
    logo = download_logo(logo_url)
    
    title_paragraph = Paragraph(title, ParagraphStyle('Title', 
        fontSize=title_size, textColor=colors.black, fontName='Helvetica-Bold', leftIndent=0))
    
    if logo:
        # MODIFICATION: Créer un tableau avec titre à gauche et logo à droite
        header_data = [[title_paragraph, logo]]  # Inverser l'ordre
        header_table = Table(header_data, colWidths=[14*cm, 4*cm])  # Inverser les largeurs
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # AJOUT: Aligner le logo à droite dans sa cellule
        ]))
        return header_table
    else:
        # Pas de logo, titre seul dans un tableau
        title_data = [[title_paragraph]]
        title_table = Table(title_data, colWidths=[18*cm])
        title_table.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        return title_table

def create_styles(couleurs):
    """Créer les styles personnalisés avec les couleurs du thème"""
    styles = getSampleStyleSheet()
    
    # Styles de base nécessaires
    styles.add(ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=couleurs['principale'],
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=11,
        textColor=couleurs['principale'],
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
        textColor=couleurs['principale'],
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT
    ))
    
    return styles

def generate_pdf_devis(devis, theme='bleu'):
    """Générer un PDF de devis avec le thème de couleur choisi"""
    # Récupérer les couleurs du thème
    couleurs = THEMES_COULEURS.get(theme, THEMES_COULEURS['bleu'])
    
    filename = os.path.join('generated', f'devis_{devis.numero}_{theme}.pdf')
    
    # Configuration du document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=0.8*cm,
        bottomMargin=3*cm
    )
    
    styles = create_styles(couleurs)
    elements = []
    
    # En-tête avec logo et titre
    header_table = create_header_with_logo(devis.logo_url, "Devis", 18)
    elements.append(header_table)
    
    # Informations du devis - alignées en deux colonnes comme Fournisseur/Client
    left_column_data = """<b>Numéro de devis</b><br/>
<b>Date d'émission</b><br/>
<b>Date d'expiration</b>"""
    
    right_column_data = f"""{devis.numero}<br/>
{devis.date_emission}<br/>
{devis.date_expiration}"""
    
    # Utiliser des paragraphes avec line height
    left_style = ParagraphStyle('LeftColumn', fontSize=10, textColor=colors.black, 
                               fontName='Helvetica-Bold', leading=14, leftIndent=0, rightIndent=0)
    right_style = ParagraphStyle('RightColumn', fontSize=10, textColor=colors.black, 
                                leading=14, leftIndent=0, rightIndent=0)
    
    # Table invisible pour aligner les deux colonnes
    info_table = Table([[
        Paragraph(left_column_data, left_style),
        Paragraph(right_column_data, right_style)
    ]], colWidths=[9*cm, 9*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 10*mm))
    
    # Informations Fournisseur et Client
    company_info_style = ParagraphStyle('CompanyInfo', fontSize=10, textColor=colors.black, leftIndent=0, rightIndent=0)
    
    # Créer les contenus en une seule cellule par colonne
    fournisseur_text = f"""<b>{devis.fournisseur_nom}</b><br/>
{devis.fournisseur_adresse}<br/>
{devis.fournisseur_ville}<br/>
{devis.fournisseur_email}<br/>
{devis.fournisseur_siret}"""
    
    client_text = f"""<b>{devis.client_nom}</b><br/>
{devis.client_adresse}<br/>
{devis.client_ville}<br/>"""
    if devis.client_email:
        client_text += f"{devis.client_email}<br/>"
    client_text += f"""{devis.client_siret}<br/>
Numéro de TVA: {devis.client_tva}"""
    
    # Table invisible pour les deux colonnes
    company_data = [[
        Paragraph(fournisseur_text, company_info_style),
        Paragraph(client_text, company_info_style)
    ]]
    
    company_table = Table(company_data, colWidths=[9*cm, 9*cm])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(company_table)
    elements.append(Spacer(1, 15*mm))
    
    # Texte d'introduction si présent
    if devis.texte_intro:
        intro_style = ParagraphStyle('IntroStyle', fontSize=10, textColor=couleurs['principale'], alignment=TA_JUSTIFY)
        elements.append(Paragraph(devis.texte_intro, intro_style))
        elements.append(Spacer(1, 10*mm))
    
    # Tableau des articles avec en-tête coloré selon le thème
    items_data = []
    
    # En-tête du tableau avec la couleur du thème
    headers = [
        Paragraph("<b>Description</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, fontName='Helvetica-Bold')),
        Paragraph("<b>Qté</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Prix unitaire</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>TVA (%)</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Total HT</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
    ]
    items_data.append(headers)
    
    # Style pour les items
    item_desc_style = ParagraphStyle('ItemDesc', fontSize=9, textColor=colors.black)
    item_center_style = ParagraphStyle('ItemCenter', fontSize=9, textColor=colors.black, 
                                      alignment=TA_CENTER)
    item_right_style = ParagraphStyle('ItemRight', fontSize=9, textColor=colors.black, 
                                     alignment=TA_RIGHT)
    
    # Articles
    for item in devis.items:
        # Description principale en gras
        desc_text = f"<b>{item.description}</b>"
        
        # Si il y a des détails, les ajouter sur des lignes séparées
        if item.details:
            items_data.append([
                Paragraph(desc_text, item_desc_style),
                Paragraph(str(item.quantite), item_center_style),
                Paragraph(f"{item.prix_unitaire:.2f} €", item_right_style),
                Paragraph(f"{item.tva_taux} %", item_center_style),
                Paragraph(f"{item.total_ht:.2f} €", item_right_style)
            ])
            
            # Ajouter les détails sur une nouvelle ligne
            detail_text = "<br/>".join(item.details)
            items_data.append([
                Paragraph(detail_text, ParagraphStyle('DetailStyle', fontSize=9, 
                         textColor=colors.black, leftIndent=0)),
                '', '', '', ''
            ])
        else:
            # Pas de détails, juste la ligne principale
            items_data.append([
                Paragraph(desc_text, item_desc_style),
                Paragraph(str(item.quantite), item_center_style),
                Paragraph(f"{item.prix_unitaire:.2f} €", item_right_style),
                Paragraph(f"{item.tva_taux} %", item_center_style),
                Paragraph(f"{item.total_ht:.2f} €", item_right_style)
            ])
        
        # Ligne de remise si applicable
        if item.remise > 0:
            items_data.append([
                '', '', '', 
                Paragraph("Remise", item_right_style),
                Paragraph(f"-{item.remise:.2f} €", item_right_style)
            ])
    
    # Créer le tableau - largeurs exactes du modèle
    col_widths = [8.5*cm, 2*cm, 3*cm, 2.5*cm, 2.5*cm]
    items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
    
    # Style du tableau avec la couleur du thème pour l'en-tête
    table_style = [
        # En-tête avec couleur du thème
        ('BACKGROUND', (0, 0), (-1, 0), couleurs['header_bg']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Corps du tableau
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        
        # Alignements
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
        
        # Bordures grises fines
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#b2bec3')),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
    ]
    
    # Pour les lignes de détails, faire un span
    row_num = 1
    for item in devis.items:
        if item.details:
            # La ligne de détails doit span toutes les colonnes
            table_style.append(('SPAN', (0, row_num + 1), (-1, row_num + 1)))
            row_num += 2
        else:
            row_num += 1
        
        if item.remise > 0:
            row_num += 1
    
    items_table.setStyle(TableStyle(table_style))
    elements.append(items_table)
    elements.append(Spacer(1, 15*mm))
    
    # Totaux alignés à droite
    totals_style = ParagraphStyle('TotalsStyle', fontSize=10, textColor=colors.black)
    totals_bold = ParagraphStyle('TotalsBold', fontSize=10, textColor=colors.black, 
                                 fontName='Helvetica-Bold')
    
    totals_data = [
        [Paragraph("Total HT", totals_style), 
         Paragraph(f"{devis.total_ht:.2f} €", totals_bold)],
        [Paragraph("Montant total de la TVA", totals_style), 
         Paragraph(f"{devis.total_tva:.2f} €", totals_bold)],
        [Paragraph("<b>Total TTC</b>", totals_bold), 
         Paragraph(f"<b>{devis.total_ttc:.2f} €</b>", totals_bold)]
    ]
    
    totals_table = Table(totals_data, colWidths=[13*cm, 4*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        # Ligne sous le total TTC
        ('LINEBELOW', (0, 2), (-1, 2), 1, colors.black),
    ]))
    
    elements.append(totals_table)
    
    # Si il y a des conditions ou informations supplémentaires
    if devis.conditions_paiement or devis.banque_nom or devis.texte_conclusion:
        elements.append(Spacer(1, 15*mm))
    
    # Conditions de paiement
    if devis.conditions_paiement:
        cond_style = ParagraphStyle('CondStyle', fontSize=10, textColor=colors.black, 
                                   fontName='Helvetica-Bold')
        text_style = ParagraphStyle('TextStyle', fontSize=10, textColor=colors.black)
        
        elements.append(Paragraph("CONDITIONS DE PAIEMENT", cond_style))
        elements.append(Paragraph(devis.conditions_paiement, text_style))
        if devis.penalites_retard:
            elements.append(Spacer(1, 3*mm))
            elements.append(Paragraph(devis.penalites_retard, ParagraphStyle('SmallText', 
                fontSize=8, textColor=colors.grey, fontName='Helvetica')))
        elements.append(Spacer(1, 10*mm))
    
    # Informations bancaires
    if devis.banque_nom:
        bank_style = ParagraphStyle('BankStyle', fontSize=10, textColor=colors.black, 
                                   fontName='Helvetica-Bold')
        text_style = ParagraphStyle('TextStyle', fontSize=10, textColor=colors.black)
        
        elements.append(Paragraph("COORDONNÉES BANCAIRES", bank_style))
        elements.append(Spacer(1, 3*mm))
        
        elements.append(Paragraph(f"<b>Banque:</b> {devis.banque_nom}", text_style))
        elements.append(Paragraph(f"<b>IBAN:</b> {devis.banque_iban}", text_style))
        elements.append(Paragraph(f"<b>BIC:</b> {devis.banque_bic}", text_style))
        
        elements.append(Spacer(1, 10*mm))
    
    # Texte de conclusion
    if devis.texte_conclusion:
        text_style = ParagraphStyle('TextStyle', fontSize=10, textColor=colors.black)
        elements.append(Paragraph(devis.texte_conclusion, text_style))
        elements.append(Spacer(1, 10*mm))
    
    # Signature - seulement pour les devis
    elements.append(Spacer(1, 15*mm))
    sig_style = ParagraphStyle('SigStyle', fontSize=10, textColor=colors.black, 
                              alignment=TA_CENTER)
    
    sig_data = [[
        Paragraph("", sig_style),  # Colonne vide
        Paragraph("Bon pour accord<br/>Date et signature:", sig_style)
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

def generate_pdf_facture(facture, theme='bleu'):
    """Générer un PDF de facture avec le thème de couleur choisi"""
    # Récupérer les couleurs du thème
    couleurs = THEMES_COULEURS.get(theme, THEMES_COULEURS['bleu'])
    
    filename = os.path.join('generated', f'facture_{facture.numero}_{theme}.pdf')
    
    # Configuration du document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=0.8*cm,
        bottomMargin=3*cm
    )
    
    styles = create_styles(couleurs)
    elements = []
    
    # En-tête avec logo et titre
    header_table = create_header_with_logo(facture.logo_url, "Facture", 16)
    elements.append(header_table)
    
    # Informations de la facture - alignées en deux colonnes
    left_column_data = "<b>Numéro de facture</b><br/>"
    left_column_data += "<b>Date d'émission</b><br/>"
    left_column_data += "<b>Date d'échéance</b><br/>"
    left_column_data += "<b>Statut</b>"
    
    right_column_data = f"{facture.numero}<br/>"
    right_column_data += f"{facture.date_emission}<br/>"
    right_column_data += f"{facture.date_echeance}<br/>"
    
    # Statut avec couleur
    statut_color = couleurs['accent']
    if facture.statut_paiement == "En retard":
        statut_color = colors.HexColor('#e74c3c')
    elif facture.statut_paiement == "Payée":
        statut_color = colors.HexColor('#27ae60')
    
    right_column_data += f"<font color='{statut_color}'><b>{facture.statut_paiement}</b></font>"
    
    # Ajouter les références si présentes
    if facture.numero_commande:
        left_column_data += "<br/><b>N° de commande</b>"
        right_column_data += f"<br/>{facture.numero_commande}"
    if facture.reference_devis:
        left_column_data += "<br/><b>Réf. devis</b>"
        right_column_data += f"<br/>{facture.reference_devis}"
    
    # Utiliser des paragraphes avec line height
    left_style = ParagraphStyle('LeftColumn', fontSize=10, textColor=colors.black, 
                               fontName='Helvetica-Bold', leading=14, leftIndent=0, rightIndent=0)
    right_style = ParagraphStyle('RightColumn', fontSize=10, textColor=colors.black, 
                                leading=14, leftIndent=0, rightIndent=0)
    
    # Table invisible pour aligner les deux colonnes
    info_table = Table([[
        Paragraph(left_column_data, left_style),
        Paragraph(right_column_data, right_style)
    ]], colWidths=[9*cm, 9*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 10*mm))
    
    # Informations Fournisseur et Client
    company_info_style = ParagraphStyle('CompanyInfo', fontSize=10, textColor=colors.black, leftIndent=0, rightIndent=0)
    
    # Créer les contenus
    fournisseur_text = f"""<b>{facture.fournisseur_nom}</b><br/>
{facture.fournisseur_adresse}<br/>
{facture.fournisseur_ville}<br/>
{facture.fournisseur_email}<br/>
{facture.fournisseur_siret}"""
    
    client_text = f"""<b>{facture.client_nom}</b><br/>
{facture.client_adresse}<br/>
{facture.client_ville}<br/>"""
    if facture.client_email:
        client_text += f"{facture.client_email}<br/>"
    client_text += f"""{facture.client_siret}<br/>
Numéro de TVA: {facture.client_tva}"""
    
    # Table invisible pour les deux colonnes
    company_data = [[
        Paragraph(fournisseur_text, company_info_style),
        Paragraph(client_text, company_info_style)
    ]]
    
    company_table = Table(company_data, colWidths=[9*cm, 9*cm])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(company_table)
    elements.append(Spacer(1, 15*mm))
    
    # Tableau des articles - même style que devis
    items_data = []
    
    # En-tête avec couleur du thème
    headers = [
        Paragraph("<b>Description</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, fontName='Helvetica-Bold')),
        Paragraph("<b>Qté</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Prix unitaire</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>TVA (%)</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("<b>Total HT</b>", ParagraphStyle('TableHeader', 
            textColor=colors.white, fontSize=10, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
    ]
    items_data.append(headers)
    
    # Styles pour les items
    item_desc_style = ParagraphStyle('ItemDesc', fontSize=9, textColor=colors.black)
    item_center_style = ParagraphStyle('ItemCenter', fontSize=9, textColor=colors.black, 
                                      alignment=TA_CENTER)
    item_right_style = ParagraphStyle('ItemRight', fontSize=9, textColor=colors.black, 
                                     alignment=TA_RIGHT)
    
    # Articles
    for item in facture.items:
        desc_text = f"<b>{item.description}</b>"
        
        if item.details:
            items_data.append([
                Paragraph(desc_text, item_desc_style),
                Paragraph(str(item.quantite), item_center_style),
                Paragraph(f"{item.prix_unitaire:.2f} €", item_right_style),
                Paragraph(f"{item.tva_taux} %", item_center_style),
                Paragraph(f"{item.total_ht:.2f} €", item_right_style)
            ])
            
            detail_text = "<br/>".join(item.details)
            items_data.append([
                Paragraph(detail_text, ParagraphStyle('DetailStyle', fontSize=9, 
                         textColor=colors.black, leftIndent=0)),
                '', '', '', ''
            ])
        else:
            items_data.append([
                Paragraph(desc_text, item_desc_style),
                Paragraph(str(item.quantite), item_center_style),
                Paragraph(f"{item.prix_unitaire:.2f} €", item_right_style),
                Paragraph(f"{item.tva_taux} %", item_center_style),
                Paragraph(f"{item.total_ht:.2f} €", item_right_style)
            ])
        
        if item.remise > 0:
            items_data.append([
                '', '', '', 
                Paragraph("Remise", item_right_style),
                Paragraph(f"-{item.remise:.2f} €", item_right_style)
            ])
    
    # Créer le tableau
    col_widths = [8.5*cm, 2*cm, 3*cm, 2.5*cm, 2.5*cm]
    items_table = Table(items_data, colWidths=col_widths, repeatRows=1)
    
    # Style du tableau avec couleur du thème
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), couleurs['header_bg']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#b2bec3')),
        
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
    ]
    
    # Gérer les spans pour les détails
    row_num = 1
    for item in facture.items:
        if item.details:
            table_style.append(('SPAN', (0, row_num + 1), (-1, row_num + 1)))
            row_num += 2
        else:
            row_num += 1
        if item.remise > 0:
            row_num += 1
    
    items_table.setStyle(TableStyle(table_style))
    elements.append(items_table)
    elements.append(Spacer(1, 15*mm))
    
    # Totaux
    totals_style = ParagraphStyle('TotalsStyle', fontSize=10, textColor=colors.black)
    totals_bold = ParagraphStyle('TotalsBold', fontSize=10, textColor=colors.black, 
                                 fontName='Helvetica-Bold')
    
    totals_data = [
        [Paragraph("Total HT", totals_style), 
         Paragraph(f"{facture.total_ht:.2f} €", totals_bold)],
        [Paragraph("Montant total de la TVA", totals_style), 
         Paragraph(f"{facture.total_tva:.2f} €", totals_bold)],
        [Paragraph("<b>Total TTC</b>", totals_bold), 
         Paragraph(f"<b>{facture.total_ttc:.2f} €</b>", totals_bold)]
    ]
    
    totals_table = Table(totals_data, colWidths=[13*cm, 4*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        # Ligne sous le total TTC
        ('LINEBELOW', (0, 2), (-1, 2), 1, colors.black),
    ]))
    
    elements.append(totals_table)
    
    # Conditions et informations supplémentaires
    if facture.conditions_paiement or facture.banque_nom:
        elements.append(Spacer(1, 15*mm))
    
    # Conditions de paiement
    if facture.conditions_paiement:
        cond_style = ParagraphStyle('CondStyle', fontSize=10, textColor=colors.black, 
                                   fontName='Helvetica-Bold')
        text_style = ParagraphStyle('TextStyle', fontSize=10, textColor=colors.black)
        
        elements.append(Paragraph("CONDITIONS DE PAIEMENT", cond_style))
        elements.append(Paragraph(facture.conditions_paiement, text_style))
        if facture.penalites_retard:
            elements.append(Spacer(1, 3*mm))
            elements.append(Paragraph(facture.penalites_retard, ParagraphStyle('SmallText', 
                fontSize=8, textColor=colors.grey, fontName='Helvetica')))
        elements.append(Spacer(1, 10*mm))
    
    # Informations bancaires
    if facture.banque_nom:
        bank_style = ParagraphStyle('BankStyle', fontSize=10, textColor=colors.black, 
                                   fontName='Helvetica-Bold')
        text_style = ParagraphStyle('TextStyle', fontSize=10, textColor=colors.black)
        
        elements.append(Paragraph("COORDONNÉES BANCAIRES POUR LE RÈGLEMENT", bank_style))
        elements.append(Spacer(1, 3*mm))
        
        elements.append(Paragraph(f"<b>Banque:</b> {facture.banque_nom}", text_style))
        elements.append(Paragraph(f"<b>IBAN:</b> {facture.banque_iban}", text_style))
        elements.append(Paragraph(f"<b>BIC:</b> {facture.banque_bic}", text_style))
    
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
