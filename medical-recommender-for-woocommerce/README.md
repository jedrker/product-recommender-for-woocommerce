# 🏥 Medical Recommender for WooCommerce

Inteligentny system rekomendacji produktów medycznych, który integruje się ze sklepem WooCommerce i analizuje dane o produktach, wyświetlając użytkownikowi rekomendacje na podstawie jego zawodu lub problemu zdrowotnego.

## 📌 Status projektu

**Aktualny etap: Etap 1 - Moduł rekomendacyjny (lokalny)** ✅

### Zrealizowane funkcjonalności (Etap 1):
- ✅ Wczytywanie produktów z pliku CSV
- ✅ System reguł rekomendacji (zawód/choroba → kategorie produktów)
- ✅ Logika rekomendacji z oceną pewności
- ✅ Interfejs wiersza poleceń (CLI)
- ✅ Pełne typowanie Python (type hints)
- ✅ Dokumentacja Google Style

### Planowane etapy:
- 🟨 **Etap 2**: Integracja z WooCommerce REST API
- 🟧 **Etap 3**: API serwera (Flask/FastAPI)
- 🟦 **Etap 4**: Frontend (HTML/JS)
- 🟥 **Etap 5**: Konfiguracja produkcyjna

## 🚀 Szybki start

### Instalacja

```bash
# Klonowanie repozytorium
git clone <repo-url>
cd medical-recommender-for-woocommerce

# Instalacja zależności
pip install -r requirements.txt
```

### Uruchomienie (tryb interaktywny)

```bash
python main.py
```

### Przykłady użycia

```bash
# Tryb interaktywny
python main.py

# Pojedyncze zapytanie
python main.py --query "ratownik medyczny"

# Wynik w formacie JSON
python main.py --query "cukrzyca" --json

# Szczegółowe logowanie
python main.py --query "lekarz" --verbose

# Własny plik z produktami
python main.py --products custom_products.csv
```

## 📊 Przykłady rekomendacji

### Zawód: Ratownik medyczny
```bash
python main.py --query "ratownik medyczny"
```
**Rekomenduje**: torby ratownicze, defibrylatory, sprzęt diagnostyczny, apteczki

### Choroba: Cukrzyca
```bash
python main.py --query "cukrzyca"
```
**Rekomenduje**: glukometry, paski testowe, lancety, insulin pen

### Zawód: Pielęgniarka
```bash
python main.py --query "pielęgniarka"
```
**Rekomenduje**: rękawice, maseczki, żele dezynfekujące, opatrunki

## 🏗️ Architektura

### Struktura katalogów
```
medical-recommender-for-woocommerce/
├── core/                    # Główna logika biznesowa
│   ├── __init__.py
│   ├── models.py           # Modele danych (Product, Recommendation)
│   ├── rules.py            # Reguły rekomendacji
│   └── recommender.py      # Silnik rekomendacji
├── data/                   # Dane produktów
│   └── products.csv        # Przykładowe produkty medyczne
├── tests/                  # Testy jednostkowe
├── utils/                  # Narzędzia pomocnicze
├── main.py                 # Punkt wejścia CLI
├── requirements.txt        # Zależności Python
└── README.md              # Ta dokumentacja
```

### Główne komponenty

#### 1. `core.models`
- **Product**: Model produktu (id, nazwa, kategoria, cena, opis)
- **Recommendation**: Wynik rekomendacji z oceną pewności
- **RecommendationRule**: Reguła mapująca słowa kluczowe na kategorie

#### 2. `core.rules`
- Zawiera mapowanie zawodów/chorób na kategorie produktów
- Obsługuje słowa kluczowe w języku polskim i angielskim
- System wagowania reguł według istotności

#### 3. `core.recommender`
- **MedicalRecommender**: Główny silnik rekomendacji
- Wczytuje produkty z CSV
- Dopasowuje reguły do zapytań użytkownika
- Generuje rekomendacje z oceną pewności

## 🔧 Format danych

### products.csv
```csv
id,name,category,price,description
1,"Torba medyczna basic","torby",199.99,"Podstawowa torba ratownicza"
2,"Stetoskop kardiologiczny","sprzet_diagnostyczny",450.00,"Profesjonalny stetoskop"
```

### Kategorie produktów
- `sprzet_diagnostyczny` - stetoskopy, ciśnieniomierze, termometry
- `torby` - torby medyczne, walizki ratownicze
- `higiena` - rękawice, maseczki, żele dezynfekujące
- `diabetologia` - glukometry, paski testowe, lancety
- `opatrunki` - gaza, bandaże, plastry
- `sprzet_ratowniczy` - defibrylatory, aspiratory
- `apteczki` - kompletne zestawy pierwszej pomocy
- `ortopedia` - kołnierze, stabilizatory
- `narzedzia` - nożyczki, pinzety chirurgiczne
- `materialy_jednorazowe` - strzykawki, igły
- `wyposazenie` - lampy, stoły badawcze

## 🧪 Testy

```bash
# Uruchomienie testów
pytest

# Testy z pokryciem kodu
pytest --cov=core

# Szczegółowe logowanie testów
pytest -v
```

## 🎯 API rekomendacji

### Metoda `recommend(query: str, max_products: int = 10)`

**Parametry:**
- `query`: Zapytanie użytkownika (zawód, choroba, słowo kluczowe)
- `max_products`: Maksymalna liczba rekomendowanych produktów

**Zwraca:** Obiekt `Recommendation` zawierający:
- `query`: Oryginalne zapytanie
- `products`: Lista rekomendowanych produktów
- `confidence`: Ocena pewności (0.0-1.0)
- `reasoning`: Uzasadnienie rekomendacji

**Przykład w kodzie:**
```python
from core.recommender import MedicalRecommender

recommender = MedicalRecommender()
recommendation = recommender.recommend("ratownik medyczny")

print(f"Pewność: {recommendation.confidence:.1%}")
for product in recommendation.products[:3]:
    print(f"- {product.name} ({product.price} PLN)")
```

## 🔄 Algorytm rekomendacji

1. **Analiza zapytania**: Konwersja na małe litery, tokenizacja
2. **Dopasowanie reguł**: Wyszukiwanie pasujących słów kluczowych
3. **Obliczenie score'u**: Uwzględnienie wagi reguły i dokładności dopasowania
4. **Selekcja kategorii**: Wybór kategorii z najwyższymi score'ami
5. **Filtrowanie produktów**: Pobranie produktów z wybranych kategorii
6. **Sortowanie**: Według ceny (rosnąco)
7. **Ocena pewności**: Na podstawie jakości dopasowania reguł

## 🐛 Debugowanie

### Włączenie szczegółowych logów
```bash
python main.py --verbose
```

### Sprawdzenie dostępnych kategorii
```bash
python main.py
# W trybie interaktywnym wpisz: categories
```

### Sprawdzenie statystyk systemu
```bash
python main.py
# W trybie interaktywnym wpisz: stats
```

## 📝 Rozwój

### Dodawanie nowych reguł
Edytuj plik `core/rules.py` i dodaj nową regułę do listy w `get_recommendation_rules()`:

```python
RecommendationRule(
    keywords=["nowe", "słowa", "kluczowe"],
    categories=["kategoria1", "kategoria2"],
    weight=0.8,
    description="Opis reguły"
)
```

### Dodawanie nowych produktów
Edytuj plik `data/products.csv` i dodaj nowe wiersze:

```csv
31,"Nowy produkt","kategoria",99.99,"Opis produktu"
```

## 🤝 Konwencje kodu

- **Python 3.11+** z pełnym typowaniem
- **PEP8** + formatowanie przez `black`
- **Google Style** docstringi
- **pytest** do testów jednostkowych
- **Modułowość** - każda warstwa w oddzielnym folderze

## 📚 Następne kroki (Etap 2)

- [ ] Integracja z WooCommerce REST API
- [ ] Pobieranie produktów z sklepu online
- [ ] Cache'owanie danych lokalnie
- [ ] Konfiguracja przez zmienne środowiskowe

---

**Autor**: Medical Recommender Team  
**Licencja**: MIT  
**Status**: W rozwoju (Etap 1/5 ukończony) 