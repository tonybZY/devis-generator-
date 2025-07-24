# models.py - Modèles améliorés avec factures et tous les champs
from dataclasses import dataclass, field
from typing import List

@dataclass
class DevisItem:
    description: str
    details: List[str] = field(default_factory=list)
    quantite: int = 1
    prix_unitaire: float = 0
    tva_taux: float = 20
    remise: float = 0
    
    @property
    def total_ht(self):
        return (self.quantite * self.prix_unitaire) - self.remise
    
    @property
    def montant_tva(self):
        return self.total_ht * (self.tva_taux / 100)
    
    @property
    def total_ttc(self):
        return self.total_ht + self.montant_tva

@dataclass
class Devis:
    # Champs OBLIGATOIRES (sans valeur par défaut) EN PREMIER
    numero: str
    date_emission: str
    date_expiration: str
    fournisseur_nom: str
    fournisseur_adresse: str
    fournisseur_ville: str
    fournisseur_email: str
    fournisseur_siret: str
    client_nom: str
    client_adresse: str
    client_ville: str
    client_siret: str
    client_tva: str
    
    # Champs OPTIONNELS (avec valeur par défaut) APRÈS
    fournisseur_telephone: str = ""
    client_telephone: str = ""
    client_email: str = ""
    banque_nom: str = "BNP Paribas"
    banque_iban: str = "FR76 3000 4008 2800 0123 4567 890"
    banque_bic: str = "BNPAFRPPXXX"
    conditions_paiement: str = "Paiement à 30 jours"
    penalites_retard: str = "En cas de retard de paiement, une pénalité de 3 fois le taux d'intérêt légal sera appliquée"
    texte_intro: str = ""
    texte_conclusion: str = "Nous restons à votre disposition pour toute information complémentaire."
    items: List[DevisItem] = field(default_factory=list)
    total_ht: float = 0
    total_tva: float = 0
    total_ttc: float = 0
    
    def calculate_totals(self):
        self.total_ht = sum(item.total_ht for item in self.items)
        self.total_tva = sum(item.montant_tva for item in self.items)
        self.total_ttc = self.total_ht + self.total_tva
    
    def to_dict(self):
        return {
            "numero": self.numero,
            "date_emission": self.date_emission,
            "date_expiration": self.date_expiration,
            "fournisseur": {
                "nom": self.fournisseur_nom,
                "adresse": self.fournisseur_adresse,
                "ville": self.fournisseur_ville,
                "email": self.fournisseur_email,
                "siret": self.fournisseur_siret,
                "telephone": self.fournisseur_telephone
            },
            "client": {
                "nom": self.client_nom,
                "adresse": self.client_adresse,
                "ville": self.client_ville,
                "siret": self.client_siret,
                "tva": self.client_tva,
                "telephone": self.client_telephone,
                "email": self.client_email
            },
            "banque": {
                "nom": self.banque_nom,
                "iban": self.banque_iban,
                "bic": self.banque_bic
            },
            "conditions": {
                "paiement": self.conditions_paiement,
                "penalites": self.penalites_retard
            },
            "items": [
                {
                    "description": item.description,
                    "details": item.details,
                    "quantite": item.quantite,
                    "prix_unitaire": item.prix_unitaire,
                    "tva_taux": item.tva_taux,
                    "remise": item.remise,
                    "total_ht": item.total_ht
                } for item in self.items
            ],
            "totaux": {
                "total_ht": self.total_ht,
                "total_tva": self.total_tva,
                "total_ttc": self.total_ttc
            }
        }

@dataclass
class Facture:
    """Modèle pour les factures - similaire au devis avec quelques différences"""
    # Champs OBLIGATOIRES EN PREMIER
    numero: str
    date_emission: str
    date_echeance: str
    fournisseur_nom: str
    fournisseur_adresse: str
    fournisseur_ville: str
    fournisseur_email: str
    fournisseur_siret: str
    client_nom: str
    client_adresse: str
    client_ville: str
    client_siret: str
    client_tva: str
    
    # Champs OPTIONNELS APRÈS
    fournisseur_telephone: str = ""
    client_telephone: str = ""
    client_email: str = ""
    banque_nom: str = "BNP Paribas"
    banque_iban: str = "FR76 3000 4008 2800 0123 4567 890"
    banque_bic: str = "BNPAFRPPXXX"
    conditions_paiement: str = "Paiement à réception"
    penalites_retard: str = "En cas de retard de paiement, une pénalité de 3 fois le taux d'intérêt légal sera appliquée"
    statut_paiement: str = "En attente"
    numero_commande: str = ""
    reference_devis: str = ""
    items: List[DevisItem] = field(default_factory=list)
    total_ht: float = 0
    total_tva: float = 0
    total_ttc: float = 0
    
    def calculate_totals(self):
        self.total_ht = sum(item.total_ht for item in self.items)
        self.total_tva = sum(item.montant_tva for item in self.items)
        self.total_ttc = self.total_ht + self.total_tva
    
    def to_dict(self):
        return {
            "numero": self.numero,
            "date_emission": self.date_emission,
            "date_echeance": self.date_echeance,
            "statut_paiement": self.statut_paiement,
            "numero_commande": self.numero_commande,
            "reference_devis": self.reference_devis,
            "fournisseur": {
                "nom": self.fournisseur_nom,
                "adresse": self.fournisseur_adresse,
                "ville": self.fournisseur_ville,
                "email": self.fournisseur_email,
                "siret": self.fournisseur_siret,
                "telephone": self.fournisseur_telephone
            },
            "client": {
                "nom": self.client_nom,
                "adresse": self.client_adresse,
                "ville": self.client_ville,
                "siret": self.client_siret,
                "tva": self.client_tva,
                "telephone": self.client_telephone,
                "email": self.client_email
            },
            "banque": {
                "nom": self.banque_nom,
                "iban": self.banque_iban,
                "bic": self.banque_bic
            },
            "conditions": {
                "paiement": self.conditions_paiement,
                "penalites": self.penalites_retard
            },
            "items": [
                {
                    "description": item.description,
                    "details": item.details,
                    "quantite": item.quantite,
                    "prix_unitaire": item.prix_unitaire,
                    "tva_taux": item.tva_taux,
                    "remise": item.remise,
                    "total_ht": item.total_ht
                } for item in self.items
            ],
            "totaux": {
                "total_ht": self.total_ht,
                "total_tva": self.total_tva,
                "total_ttc": self.total_ttc
            }
        }
