from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

def generate_docx(devis):
    filename = os.path.join('generated', f'devis_{devis.numero}.docx')
    doc = Document()
    
    # En-tête
    header = doc.add_heading('Devis', 0)
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # Informations du devis
    doc.add_paragraph(f'Numéro de devis: {devis.numero}')
    doc.add_paragraph(f'Date d\'émission: {devis.date_emission}')
    doc.add_paragraph(f'Date d\'expiration: {devis.date_expiration}')
    doc.add_paragraph()
    
    # Tableau fournisseur/client
    table = doc.add_table(rows=5, cols=2)
    table.style = 'Light Grid'
    
    # Fournisseur
    table.cell(0, 0).text = devis.fournisseur_nom
    table.cell(1, 0).text = devis.fournisseur_adresse
    table.cell(2, 0).text = devis.fournisseur_ville
    table.cell(3, 0).text = devis.fournisseur_email
    table.cell(4, 0).text = devis.fournisseur_siret
    
    # Client
    table.cell(0, 1).text = devis.client_nom
    table.cell(1, 1).text = devis.client_adresse
    table.cell(2, 1).text = devis.client_ville
    table.cell(3, 1).text = f'SIRET: {devis.client_siret}'
    table.cell(4, 1).text = f'TVA: {devis.client_tva}'
    
    doc.add_paragraph()
    
    # Articles
    items_table = doc.add_table(rows=1, cols=5)
    items_table.style = 'Table Grid'
    
    # En-têtes
    headers = ['Description', 'Qté', 'Prix unitaire', 'TVA (%)', 'Total HT']
    for i, header in enumerate(headers):
        items_table.cell(0, i).text = header
    
    # Articles
    for item in devis.items:
        row = items_table.add_row()
        row.cells[0].text = item.description
        row.cells[1].text = str(item.quantite)
        row.cells[2].text = f'{item.prix_unitaire:.2f} €'
        row.cells[3].text = f'{item.tva_taux} %'
        row.cells[4].text = f'{item.total_ht:.2f} €'
        
        # Détails
        for detail in item.details:
            detail_row = items_table.add_row()
            detail_row.cells[0].text = f'  - {detail}'
        
        # Remise
        if item.remise > 0:
            remise_row = items_table.add_row()
            remise_row.cells[0].text = '  Remise'
            remise_row.cells[4].text = f'-{item.remise:.2f} €'
    
    doc.add_paragraph()
    
    # Totaux
    doc.add_paragraph(f'Total HT: {devis.total_ht:.2f} €')
    doc.add_paragraph(f'Montant total de la TVA: {devis.total_tva:.2f} €')
    doc.add_paragraph(f'Total TTC: {devis.total_ttc:.2f} €')
    
    # Sauvegarder
    doc.save(filename)
    return filename
