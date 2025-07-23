from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
import os
from models import Devis, DevisItem
from pdf_generator import generate_pdf
from docx_generator import generate_docx

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'generated'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/devis', methods=['POST'])
def create_devis():
    """
    Créer un nouveau devis avec les données reçues
    """
    try:
        data = request.json
        
        # Créer l'objet devis
        devis = Devis(
            numero=data.get('numero', f"D-{datetime.now().year}-{str(uuid.uuid4())[:3]}"),
            date_emission=data.get('date_emission', datetime.now().strftime('%d/%m/%Y')),
            date_expiration=data.get('date_expiration', (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')),
            
            # Informations fournisseur
            fournisseur_nom=data.get('fournisseur_nom', 'Infinytia'),
            fournisseur_adresse=data.get('fournisseur_adresse', '61 Rue De Lyon'),
            fournisseur_ville=data.get('fournisseur_ville', '75012 Paris, FR'),
            fournisseur_email=data.get('fournisseur_email', 'contact@infinytia.com'),
            fournisseur_siret=data.get('fournisseur_siret', '93968736400017'),
            
            # Informations client
            client_nom=data.get('client_nom'),
            client_adresse=data.get('client_adresse'),
            client_ville=data.get('client_ville'),
            client_siret=data.get('client_siret'),
            client_tva=data.get('client_tva'),
            
            # Articles
            items=[]
        )
        
        # Ajouter les articles
        for item_data in data.get('items', []):
            item = DevisItem(
                description=item_data.get('description'),
                details=item_data.get('details', []),
                quantite=item_data.get('quantite', 1),
                prix_unitaire=item_data.get('prix_unitaire', 0),
                tva_taux=item_data.get('tva_taux', 20),
                remise=item_data.get('remise', 0)
            )
            devis.items.append(item)
        
        # Calculer les totaux
        devis.calculate_totals()
        
        # Format de sortie demandé
        output_format = data.get('format', 'pdf').lower()
        
        if output_format == 'pdf':
            filename = generate_pdf(devis)
            mimetype = 'application/pdf'
        elif output_format == 'docx':
            filename = generate_docx(devis)
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            return jsonify({"error": "Format non supporté. Utilisez 'pdf' ou 'docx'"}), 400
        
        # Retourner le fichier
        return send_file(
            filename,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f"devis_{devis.numero}.{output_format}"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/devis/preview', methods=['POST'])
def preview_devis():
    """
    Prévisualiser les données du devis sans générer de fichier
    """
    try:
        data = request.json
        
        # Créer l'objet devis
        devis = Devis(
            numero=data.get('numero', f"D-{datetime.now().year}-{str(uuid.uuid4())[:3]}"),
            date_emission=data.get('date_emission', datetime.now().strftime('%d/%m/%Y')),
            date_expiration=data.get('date_expiration', (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')),
            
            # Informations fournisseur
            fournisseur_nom=data.get('fournisseur_nom', 'Infinytia'),
            fournisseur_adresse=data.get('fournisseur_adresse', '61 Rue De Lyon'),
            fournisseur_ville=data.get('fournisseur_ville', '75012 Paris, FR'),
            fournisseur_email=data.get('fournisseur_email', 'contact@infinytia.com'),
            fournisseur_siret=data.get('fournisseur_siret', '93968736400017'),
            
            # Informations client
            client_nom=data.get('client_nom'),
            client_adresse=data.get('client_adresse'),
            client_ville=data.get('client_ville'),
            client_siret=data.get('client_siret'),
            client_tva=data.get('client_tva'),
            
            # Articles
            items=[]
        )
        
        # Ajouter les articles
        for item_data in data.get('items', []):
            item = DevisItem(
                description=item_data.get('description'),
                details=item_data.get('details', []),
                quantite=item_data.get('quantite', 1),
                prix_unitaire=item_data.get('prix_unitaire', 0),
                tva_taux=item_data.get('tva_taux', 20),
                remise=item_data.get('remise', 0)
            )
            devis.items.append(item)
        
        # Calculer les totaux
        devis.calculate_totals()
        
        return jsonify(devis.to_dict()), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
