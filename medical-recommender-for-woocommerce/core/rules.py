"""Business rules for medical product recommendations.

This module contains the mapping logic between user input (professions, health conditions)
and product categories that should be recommended.
"""

from typing import List
from core.models import RecommendationRule


def get_recommendation_rules() -> List[RecommendationRule]:
    """Get all recommendation rules for the system.
    
    Returns:
        List of RecommendationRule objects defining the recommendation logic
    """
    return [
        # Zawody medyczne - Ratownik medyczny / Paramedyk
        RecommendationRule(
            keywords=["ratownik", "paramedyk", "karetka", "pogotowie", "ambulans"],
            categories=["sprzet_ratowniczy", "torby", "sprzet_diagnostyczny", "apteczki"],
            weight=1.0,
            description="Sprzęt dla ratowników medycznych i zespołów pogotowia"
        ),
        
        # Zawody medyczne - Lekarz
        RecommendationRule(
            keywords=["lekarz", "doktor", "dr", "physician", "medyk"],
            categories=["sprzet_diagnostyczny", "torby", "narzedzia", "wyposazenie"],
            weight=1.0,
            description="Sprzęt diagnostyczny i narzędzia dla lekarzy"
        ),
        
        # Zawody medyczne - Pielęgniarka
        RecommendationRule(
            keywords=["pielęgniarka", "pielęgniarz", "nurse"],
            categories=["higiena", "materialy_jednorazowe", "opatrunki", "sprzet_diagnostyczny"],
            weight=0.9,
            description="Materiały jednorazowe i sprzęt dla pielęgniarek"
        ),
        
        # Zawody medyczne - Fizjoterapeuta
        RecommendationRule(
            keywords=["fizjoterapeuta", "rehabilitant", "physiotherapist"],
            categories=["ortopedia", "wyposazenie"],
            weight=0.8,
            description="Sprzęt ortopedyczny i rehabilitacyjny"
        ),
        
        # Choroby i stany - Cukrzyca
        RecommendationRule(
            keywords=["cukrzyca", "diabetes", "diabetyk", "insulina", "glukoza", "cukier"],
            categories=["diabetologia"],
            weight=1.0,
            description="Produkty do kontroli i leczenia cukrzycy"
        ),
        
        # Choroby i stany - Problemy kardiologiczne
        RecommendationRule(
            keywords=["serce", "kardiologia", "nadciśnienie", "ciśnienie", "arytmia", "cardio"],
            categories=["sprzet_diagnostyczny"],
            weight=0.9,
            description="Sprzęt do badań kardiologicznych i kontroli ciśnienia"
        ),
        
        # Choroby i stany - Problemy oddechowe
        RecommendationRule(
            keywords=["astma", "COPD", "oddychanie", "płuca", "spirometria", "kaszel"],
            categories=["sprzet_diagnostyczny"],
            weight=0.9,
            description="Sprzęt do badania funkcji oddechowych"
        ),
        
        # Urazy i opatrunki
        RecommendationRule(
            keywords=["rana", "uraz", "skaleczenie", "oparzenie", "bandaż", "opatrunek"],
            categories=["opatrunki", "materialy_jednorazowe"],
            weight=0.8,
            description="Materiały do opatrywania ran i urazów"
        ),
        
        # Higiena i profilaktyka
        RecommendationRule(
            keywords=["higiena", "dezynfekcja", "sterylizacja", "czystość", "profilaktyka"],
            categories=["higiena", "materialy_jednorazowe"],
            weight=0.7,
            description="Produkty higieniczne i do dezynfekcji"
        ),
        
        # Badania i diagnostyka
        RecommendationRule(
            keywords=["badanie", "diagnoza", "pomiar", "test", "kontrola", "monitoring"],
            categories=["sprzet_diagnostyczny"],
            weight=0.8,
            description="Sprzęt do badań i diagnostyki medycznej"
        ),
        
        # Pierwsza pomoc
        RecommendationRule(
            keywords=["pierwsza pomoc", "apteczka", "nagły wypadek", "ratownictwo"],
            categories=["apteczki", "opatrunki", "materialy_jednorazowe"],
            weight=0.9,
            description="Wyposażenie do udzielania pierwszej pomocy"
        ),
        
        # Ortopedia i rehabilitacja
        RecommendationRule(
            keywords=["kręgosłup", "stawy", "ortopedia", "rehabilitacja", "stabilizacja"],
            categories=["ortopedia"],
            weight=0.8,
            description="Sprzęt ortopedyczny i stabilizujący"
        ),
        
        # Specjalistyczne zawody - Dentysta
        RecommendationRule(
            keywords=["dentysta", "stomatolog", "zęby", "dental"],
            categories=["narzedzia", "higiena"],
            weight=0.7,
            description="Narzędzia i materiały stomatologiczne"
        ),
        
        # Ogólne słowa kluczowe - szpital
        RecommendationRule(
            keywords=["szpital", "klinika", "przychodnia", "gabinet"],
            categories=["sprzet_diagnostyczny", "higiena", "wyposazenie"],
            weight=0.6,
            description="Podstawowe wyposażenie placówek medycznych"
        ),
    ]


def get_categories_by_priority() -> List[str]:
    """Get product categories ordered by general importance/frequency of use.
    
    Returns:
        List of category names in priority order
    """
    return [
        "sprzet_diagnostyczny",
        "higiena", 
        "opatrunki",
        "materialy_jednorazowe",
        "torby",
        "apteczki",
        "diabetologia",
        "sprzet_ratowniczy",
        "narzedzia",
        "wyposazenie",
        "ortopedia",
    ]


def get_fallback_categories() -> List[str]:
    """Get fallback categories when no specific rules match.
    
    Returns:
        List of most general/useful category names
    """
    return [
        "sprzet_diagnostyczny",
        "higiena",
        "apteczki",
    ] 