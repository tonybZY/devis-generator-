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
    title_style = ParagraphStyle('Title', fontSize=16, textColor=colors.black, 
                                fontName='Helvetica-Bold', spaceAfter=15)
    elements.append(Paragraph("Devis", title_style))
    
    # Informations du devis - style exact du modèle
    info_label_style = ParagraphStyle('InfoLabel', fontSize=10, textColor=colors.black, 
                                     fontName='Helvetica-Bold')
    info_value_style = ParagraphStyle('InfoValue', fontSize=10, textColor=colors.black)
    
    # Utiliser une table invisible pour l'alignement parfait
    info_data = [
        [Paragraph("Numéro de devis", info_label_style), 
         Paragraph(devis.numero, info_value_style)],
        [Paragraph("Date d'émission", info_label_style), 
         Paragraph(devis.date_emission, info_value_style)],
        [Paragraph("Date d'expiration", info_label_style), 
         Paragraph(devis.date_expiration, info_value_style)]
    ]
    
    # Table avec largeurs spécifiques pour correspondre au modèle
    info_table = Table(info_data, colWidths=[4.5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        # Pas de bordures
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        # Padding minimal
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20*mm))
    
    # Informations Fournisseur et Client - style exact du modèle
    company_label_style = ParagraphStyle('CompanyLabel', fontSize=10, textColor=colors.black, 
                                        fontName='Helvetica-Bold')
    company_info_style = ParagraphStyle('CompanyInfo', fontSize=10, textColor=colors.black)
    
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
        intro_style = ParagraphStyle('IntroStyle', fontSize=10, textColor=COULEUR_TEXTE, alignment=TA_JUSTIFY)
        elements.append(Paragraph(devis.texte_intro, intro_style))
        elements.append(Spacer(1, 10*mm))
    
    # Tableau des articles avec en-tête noir comme le modèle
    items_data = []
    
    # En-tête du tableau - exactement comme le modèle
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
            # Les détails sont dans une cellule séparée qui span toutes les colonnes
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
    
    # Style du tableau - exactement comme le modèle
    table_style = [
        # En-tête noir
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3436')),
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
        
        # Bordures grises fines comme le modèle
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
    title_style = ParagraphStyle('Title', fontSize=16, textColor=colors.black, 
                                fontName='Helvetica-Bold', spaceAfter=15)
    elements.append(Paragraph("Facture", title_style))
    
    # Informations de la facture - style exact du modèle
    info_label_style = ParagraphStyle('InfoLabel', fontSize=10, textColor=colors.black, 
                                     fontName='Helvetica-Bold')
    info_value_style = ParagraphStyle('InfoValue', fontSize=10, textColor=colors.black)
    
    # Construire les données d'info
    info_data = [
        [Paragraph("Numéro de facture", info_label_style), 
         Paragraph(facture.numero, info_value_style)],
        [Paragraph("Date d'émission", info_label_style), 
         Paragraph(facture.date_emission, info_value_style)],
        [Paragraph("Date d'échéance", info_label_style), 
         Paragraph(facture.date_echeance, info_value_style)]
    ]
    
    # Ajouter le statut avec couleur
    statut_color = COULEUR_ACCENT
    if facture.statut_paiement == "En retard":
        statut_color = colors.HexColor('#e74c3c')
    elif facture.statut_paiement == "Payée":
        statut_color = colors.HexColor('#27ae60')
    
    statut_style = ParagraphStyle('StatutStyle', fontSize=10, textColor=statut_color, 
                                 fontName='Helvetica-Bold')
    info_data.append([
        Paragraph("Statut", info_label_style),
        Paragraph(facture.statut_paiement, statut_style)
    ])
    
    # Ajouter les références si présentes
    if facture.numero_commande:
        info_data.append([
            Paragraph("N° de commande", info_label_style),
            Paragraph(facture.numero_commande, info_value_style)
        ])
    if facture.reference_devis:
        info_data.append([
            Paragraph("Réf. devis", info_label_style),
            Paragraph(facture.reference_devis, info_value_style)
        ])
    
    # Table invisible pour l'alignement
    info_table = Table(info_data, colWidths=[4.5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20*mm))
    
    # Informations Fournisseur et Client - style exact du modèle
    company_info_style = ParagraphStyle('CompanyInfo', fontSize=10, textColor=colors.black)
    
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
    elements.append(Spacer(1, 20*mm))
    
    # Tableau des articles - même style que devis
    items_data = []
    
    # En-tête
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
    
    # Style du tableau
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3436')),
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
