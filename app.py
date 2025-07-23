# app.py - Version améliorée avec authentification et factures
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
import os
from functools import wraps
from models import Devis, DevisItem, Facture
from pdf_generator import generate_pdf_devis, generate_pdf_facture
from docx_generator import generate_docx_devis, generate_docx_facture

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'generated'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Clés API (à stocker dans des variables d'environnement en production)
API_KEY_1 = os.environ.get('API_KEY_1', 'your-secret-key-1-here')
API_KEY_2 = os.environ.get('API_KEY_2', 'your-secret-key-2-here')

def require_api_keys(f):
    """Décorateur pour vérifier les 2 clés API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérifier les headers
        key1 = request.headers.get('X-API-Key-1')
        key2 = request.headers.get('X-API-Key-2')
        
        if not key1 or not key2:
            return jsonify({"error": "Clés API manquantes"}), 401
        
        if key1 != API_KEY_1 or key2 != API_KEY_2:
            return jsonify({"error": "Clés API invalides"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/devis', methods=['POST'])
@require_api_keys
def create_devis():
    """Créer un nouveau devis avec les données reçues"""
    try:
        data = request.json
        
        # Créer l'objet devis avec toutes les options modifiables
        devis = Devis(
            numero=data.get('numero', f"D-{datetime.now().year}-{str(uuid.uuid4())[:3]}"),
            date_emission=data.get('date_emission', datetime.now().strftime('%d/%m/%Y')),
            date_expiration=data.get('date_expiration', (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')),
            
            # Informations fournisseur (tout modifiable)
            fournisseur_nom=data.get('fournisseur_nom', 'Infinytia'),
            fournisseur_adresse=data.get('fournisseur_adresse', '61 Rue De Lyon'),
            fournisseur_ville=data.get('fournisseur_ville', '75012 Paris, FR'),
            fournisseur_email=data.get('fournisseur_email', 'contact@infinytia.com'),
            fournisseur_siret=data.get('fournisseur_siret', '93968736400017'),
            fournisseur_telephone=data.get('fournisseur_telephone', '+33 1 23 45 67 89'),
            
            # Informations client
            client_nom=data.get('client_nom'),
            client_adresse=data.get('client_adresse'),
            client_ville=data.get('client_ville'),
            client_siret=data.get('client_siret'),
            client_tva=data.get('client_tva'),
            client_telephone=data.get('client_telephone', ''),
            client_email=data.get('client_email', ''),
            
            # Informations bancaires (modifiables)
            banque_nom=data.get('banque_nom', 'BNP Paribas'),
            banque_iban=data.get('banque_iban', 'FR76 3000 4008 2800 0123 4567 890'),
            banque_bic=data.get('banque_bic', 'BNPAFRPPXXX'),
            
            # Conditions de paiement
            conditions_paiement=data.get('conditions_paiement', 'Paiement à 30 jours'),
            penalites_retard=data.get('penalites_retard', 'En cas de retard de paiement, une pénalité de 3 fois le taux d\'intérêt légal sera appliquée'),
            
            # Texte personnalisé
            texte_intro=data.get('texte_intro', ''),
            texte_conclusion=data.get('texte_conclusion', 'Nous restons à votre disposition pour toute information complémentaire.'),
            
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
            filename = generate_pdf_devis(devis)
            mimetype = 'application/pdf'
        elif output_format == 'docx':
            filename = generate_docx_devis(devis)
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

@app.route('/api/facture', methods=['POST'])
@require_api_keys
def create_facture():
    """Créer une nouvelle facture avec les données reçues"""
    try:
        data = request.json
        
        # Créer l'objet facture
        facture = Facture(
            numero=data.get('numero', f"F-{datetime.now().year}-{str(uuid.uuid4())[:3]}"),
            date_emission=data.get('date_emission', datetime.now().strftime('%d/%m/%Y')),
            date_echeance=data.get('date_echeance', (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')),
            
            # Informations fournisseur
            fournisseur_nom=data.get('fournisseur_nom', 'Infinytia'),
            fournisseur_adresse=data.get('fournisseur_adresse', '61 Rue De Lyon'),
            fournisseur_ville=data.get('fournisseur_ville', '75012 Paris, FR'),
            fournisseur_email=data.get('fournisseur_email', 'contact@infinytia.com'),
            fournisseur_siret=data.get('fournisseur_siret', '93968736400017'),
            fournisseur_telephone=data.get('fournisseur_telephone', '+33 1 23 45 67 89'),
            
            # Informations client
            client_nom=data.get('client_nom'),
            client_adresse=data.get('client_adresse'),
            client_ville=data.get('client_ville'),
            client_siret=data.get('client_siret'),
            client_tva=data.get('client_tva'),
            client_telephone=data.get('client_telephone', ''),
            client_email=data.get('client_email', ''),
            
            # Informations bancaires
            banque_nom=data.get('banque_nom', 'BNP Paribas'),
            banque_iban=data.get('banque_iban', 'FR76 3000 4008 2800 0123 4567 890'),
            banque_bic=data.get('banque_bic', 'BNPAFRPPXXX'),
            
            # Conditions et statut
            conditions_paiement=data.get('conditions_paiement', 'Paiement à réception'),
            penalites_retard=data.get('penalites_retard', 'En cas de retard de paiement, une pénalité de 3 fois le taux d\'intérêt légal sera appliquée'),
            statut_paiement=data.get('statut_paiement', 'En attente'),
            
            # Références
            numero_commande=data.get('numero_commande', ''),
            reference_devis=data.get('reference_devis', ''),
            
            # Articles
            items=[]
        )
        
        # Ajouter les articles (même structure que devis)
        for item_data in data.get('items', []):
            item = DevisItem(
                description=item_data.get('description'),
                details=item_data.get('details', []),
                quantite=item_data.get('quantite', 1),
                prix_unitaire=item_data.get('prix_unitaire', 0),
                tva_taux=item_data.get('tva_taux', 20),
                remise=item_data.get('remise', 0)
            )
            facture.items.append(item)
        
        # Calculer les totaux
        facture.calculate_totals()
        
        # Format de sortie
        output_format = data.get('format', 'pdf').lower()
        
        if output_format == 'pdf':
            filename = generate_pdf_facture(facture)
            mimetype = 'application/pdf'
        elif output_format == 'docx':
            filename = generate_docx_facture(facture)
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            return jsonify({"error": "Format non supporté"}), 400
        
        return send_file(
            filename,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f"facture_{facture.numero}.{output_format}"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-auth', methods=['GET'])
@require_api_keys
def test_auth():
    """Endpoint pour tester l'authentification"""
    return jsonify({"message": "Authentification réussie!"}), 200

# Configuration pour Railway
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# Exemple de requête avec authentification :
"""
curl -X POST https://your-app.railway.app/api/devis \
  -H "Content-Type: application/json" \
  -H "X-API-Key-1: your-secret-key-1-here" \
  -H "X-API-Key-2: your-secret-key-2-here" \
  -d '{
    "client_nom": "CRINSTALLE",
    "client_adresse": "400 AVENUE GEORGES CLEMENCEAU",
    "client_ville": "84300 CAVAILLON, FR",
    "client_siret": "952170736",
    "client_tva": "FR57952170736",
    "banque_nom": "Crédit Agricole",
    "banque_iban": "FR76 1234 5678 9012 3456 7890 123",
    "banque_bic": "AGRIFRPP",
    "format": "pdf",
    "items": [
      {
        "description": "AGENT IA SLACK - GESTION DES ARMOIRES FIBRE",
        "details": [
          "Création de groupes Slack dédiés pour les équipes de techniciens",
          "Agent IA capable de retrouver les adresses des armoires",
          "Interface conversationnelle pour requêtes instantanées",
          "Base de données géolocalisée des armoires"
        ],
        "quantite": 1,
        "prix_unitaire": 900,
        "tva_taux": 20,
        "remise": 100
      }
    ]
  }'
"""
