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
    numero: str
    date_emission: str
    date_expiration: str
    
    # Fournisseur
    fournisseur_nom: str
    fournisseur_adresse: str
    fournisseur_ville: str
    fournisseur_email: str
    fournisseur_siret: str
    
    # Client
    client_nom: str
    client_adresse: str
    client_ville: str
    client_siret: str
    client_tva: str
    
    # Articles
    items: List[DevisItem] = field(default_factory=list)
    
    # Totaux
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
                "siret": self.fournisseur_siret
            },
            "client": {
                "nom": self.client_nom,
                "adresse": self.client_adresse,
                "ville": self.client_ville,
                "siret": self.client_siret,
                "tva": self.client_tva
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
