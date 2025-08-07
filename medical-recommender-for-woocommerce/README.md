# 🏥 Medical Recommender for WooCommerce

Inteligentny system rekomendacji produktów medycznych, który integruje się ze sklepem WooCommerce i analizuje dane o produktach, wyświetlając użytkownikowi rekomendacje na podstawie jego zawodu lub problemu zdrowotnego.

## 📌 Status projektu

**Aktualny etap: Etap 3 - API serwera (Flask)** ✅

### Zrealizowane funkcjonalności:

#### ✅ **Etap 1 - Moduł rekomendacyjny (lokalny)**
- ✅ Wczytywanie produktów z pliku CSV
- ✅ System reguł rekomendacji (zawód/choroba → kategorie produktów)
- ✅ Logika rekomendacji z oceną pewności
- ✅ Interfejs wiersza poleceń (CLI)
- ✅ Pełne typowanie Python (type hints)
- ✅ Dokumentacja Google Style

#### ✅ **Etap 2 - Integracja z WooCommerce**
- ✅ Autoryzacja przez WooCommerce REST API v3
- ✅ Pobieranie produktów z `GET /wp-json/wc/v3/products`
- ✅ Mapowanie danych do formatu zgodnego z systemem rekomendacji
- ✅ Cache'owanie danych lokalnie (products.json)
- ✅ Konfiguracja przez zmienne środowiskowe (.env)
- ✅ Testy jednostkowe dla integracji WooCommerce

#### ✅ **Etap 3 - API serwera (Flask)**
- ✅ Flask aplikacja z CORS
- ✅ Endpoint `GET /recommend?input=<query>` - rekomendacje JSON
- ✅ Endpoint `GET /products` - lista produktów (z filtrowaniem i paginacją)
- ✅ Endpoint `GET /categories` - dostępne kategorie
- ✅ Endpoint `GET /` - health check
- ✅ Obsługa błędów HTTP (404, 405, 500)
- ✅ Walidacja parametrów zapytań
- ✅ Testy API endpoints

### Planowane etapy:
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

### Konfiguracja WooCommerce (opcjonalna)

1. **Skopiuj plik konfiguracyjny:**
```bash
cp env.example .env
```

2. **Edytuj `.env` i dodaj dane WooCommerce:**
```env
WOOCOMMERCE_URL=https://twoj-sklep.pl
WOOCOMMERCE_CONSUMER_KEY=ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WOOCOMMERCE_CONSUMER_SECRET=cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CACHE_DURATION=3600
MAX_PRODUCTS=100
```

3. **Wygeneruj klucze API w WooCommerce:**
   - Przejdź do: WooCommerce > Ustawienia > Zaawansowane > REST API
   - Kliknij "Dodaj klucz"
   - Ustaw uprawnienia: `read`
   - Skopiuj Consumer Key i Consumer Secret

### Uruchomienie

```bash
# Tryb interaktywny (z lokalnymi danymi)
python main.py

# Z konfiguracją WooCommerce
python main.py --env .env

# Pojedyncze zapytanie
python main.py --query "ratownik medyczny"

# Wymuszenie odświeżenia z WooCommerce
python main.py --env .env --refresh
```

## 🌐 API Serwera (Etap 3)

### Uruchamianie serwera

```bash
# Podstawowe uruchomienie
python server.py

# Z konfiguracją WooCommerce
python server.py --env .env

# Na konkretnym porcie
python server.py --port 8000

# Tryb debug
python server.py --debug
```

Serwer będzie dostępny domyślnie na: **http://localhost:5000**

### 📡 Dostępne endpointy

#### `GET /` - Health Check
Sprawdza status API i liczbę załadowanych produktów.

**Przykład:**
```bash
curl http://localhost:5000/
```

**Odpowiedź:**
```json
{
  "status": "healthy",
  "message": "Medical Product Recommender API",
  "version": "1.0.0",
  "products_count": 1050,
  "woocommerce_enabled": true,
  "cache_enabled": true
}
```

#### `GET /recommend` - Rekomendacje produktów
Generuje rekomendacje na podstawie zapytania użytkownika.

**Parametry:**
- `input` (wymagany) - zapytanie (zawód, choroba, itp.)
- `limit` (opcjonalny) - maksymalna liczba produktów (domyślnie: 10)
- `format` (opcjonalny) - format odpowiedzi: `json` lub `simple` (domyślnie: `json`)

**Przykłady:**
```bash
# Podstawowe zapytanie
curl "http://localhost:5000/recommend?input=cukrzyca"

# Z limitem produktów
curl "http://localhost:5000/recommend?input=ratownik medyczny&limit=5"

# Format uproszczony
curl "http://localhost:5000/recommend?input=higiena&format=simple"
```

**Odpowiedź (format json):**
```json
{
  "query": "cukrzyca",
  "confidence": 0.1,
  "reasoning": "Brak produktów w rekomendowanych kategoriach...",
  "count": 10,
  "products": [
    {
      "id": "123",
      "name": "Wziernik nosowy",
      "category": "narzedzia",
      "price": 45.00,
      "description": "Narzędzie laryngologiczne..."
    }
  ],
  "meta": {
    "total_products_available": 1050,
    "categories_available": 8,
    "woocommerce_enabled": true
  }
}
```

#### `GET /products` - Lista produktów
Zwraca listę dostępnych produktów z możliwością filtrowania i paginacji.

**Parametry:**
- `category` (opcjonalny) - filtruj według kategorii
- `limit` (opcjonalny) - liczba produktów na stronę (domyślnie: 50)
- `offset` (opcjonalny) - liczba produktów do pominięcia (domyślnie: 0)

**Przykłady:**
```bash
# Wszystkie produkty (pierwsze 50)
curl "http://localhost:5000/products"

# Produkty z kategorii higiena
curl "http://localhost:5000/products?category=higiena"

# Paginacja
curl "http://localhost:5000/products?limit=20&offset=40"
```

**Odpowiedź:**
```json
{
  "products": [
    {
      "id": "123",
      "name": "Rękawiczki nitrylowe",
      "category": "higiena",
      "price": 29.99,
      "description": "Rękawiczki bezpudrowe..."
    }
  ],
  "pagination": {
    "total": 1050,
    "limit": 50,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  },
  "meta": {
    "categories_available": ["higiena", "narzedzia", "opatrunki"],
    "woocommerce_enabled": true
  }
}
```

#### `GET /categories` - Dostępne kategorie
Zwraca listę wszystkich kategorii produktów z liczbą produktów w każdej.

**Przykład:**
```bash
curl "http://localhost:5000/categories"
```

**Odpowiedź:**
```json
{
  "categories": [
    {
      "name": "higiena",
      "product_count": 451
    },
    {
      "name": "narzedzia", 
      "product_count": 206
    }
  ],
  "total_categories": 8,
  "total_products": 1050
}
```

### 🔄 CORS

API automatycznie obsługuje CORS dla wszystkich origin (rozwój). W produkcji należy ograniczyć do konkretnych domen.

### ⚠️ Obsługa błędów

API zwraca standardowe kody HTTP i szczegółowe informacje o błędach:

- **400** - Błędne parametry
- **404** - Nieznaleziony endpoint
- **405** - Niedozwolona metoda HTTP
- **500** - Błąd wewnętrzny serwera
- **503** - Serwis niedostępny (recommender niezainicjalizowany)

**Przykład błędu:**
```json
{
  "error": "Missing required parameter 'input'",
  "code": "MISSING_PARAMETER",
  "example": "/recommend?input=cukrzyca"
}
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
│   └── recommender.py      # Silnik rekomendacji (rozszerzony o WooCommerce)
├── woo/                    # Integracja z WooCommerce
│   ├── __init__.py
│   ├── client.py           # Klient WooCommerce API
│   └── mapper.py           # Mapowanie danych WooCommerce
├── utils/                  # Narzędzia pomocnicze
│   ├── __init__.py
│   ├── config.py           # Zarządzanie konfiguracją (.env)
│   └── cache.py            # System cache'owania
├── data/                   # Dane produktów
│   ├── products.csv        # Przykładowe produkty medyczne
│   ├── products.json       # Cache produktów z WooCommerce
│   └── cache_metadata.json # Metadane cache
├── tests/                  # Testy jednostkowe
│   ├── test_models.py      # Testy modeli
│   ├── test_recommender.py # Testy silnika rekomendacji
│   └── test_woocommerce.py # Testy integracji WooCommerce
├── main.py                 # Punkt wejścia CLI (rozszerzony)
├── requirements.txt        # Zależności Python
├── env.example            # Przykład konfiguracji
└── README.md              # Ta dokumentacja
```

### Główne komponenty

#### 1. **core.recommender** (rozszerzony)
- **MedicalRecommender**: Główny silnik rekomendacji
- Obsługuje zarówno lokalne dane CSV jak i WooCommerce API
- Automatyczne cache'owanie produktów
- Testowanie połączenia z WooCommerce

#### 2. **woo.client**
- **WooCommerceClient**: Klient REST API WooCommerce
- Autoryzacja przez Consumer Key/Secret
- Paginacja produktów
- Obsługa błędów API

#### 3. **woo.mapper**
- **WooCommerceMapper**: Mapowanie danych
- Konwersja z formatu WooCommerce na wewnętrzne modele
- Mapowanie kategorii produktów
- Ekstrakcja cen i opisów

#### 4. **utils.config**
- **Config**: Zarządzanie konfiguracją
- Wczytywanie zmiennych środowiskowych z .env
- Walidacja konfiguracji
- Domyślne wartości

#### 5. **utils.cache**
- **ProductCache**: System cache'owania
- Zapisywanie/wczytywanie produktów w JSON
- Automatyczne wygasanie cache
- Metadane cache

## 🔧 Format danych

### products.csv (lokalne dane)
```csv
id,name,category,price,description
1,"Torba medyczna basic","torby",199.99,"Podstawowa torba ratownicza"
2,"Stetoskop kardiologiczny","sprzet_diagnostyczny",450.00,"Profesjonalny stetoskop"
```

### products.json (cache WooCommerce)
```json
[
  {
    "id": 123,
    "name": "Stetoskop Medical",
    "category": "sprzet_diagnostyczny",
    "price": 299.99,
    "description": "Profesjonalny stetoskop kardiologiczny"
  }
]
```

### .env (konfiguracja)
```env
WOOCOMMERCE_URL=https://twoj-sklep.pl
WOOCOMMERCE_CONSUMER_KEY=ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WOOCOMMERCE_CONSUMER_SECRET=cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CACHE_DURATION=3600
MAX_PRODUCTS=100
API_TIMEOUT=30
LOG_LEVEL=INFO
```

## 🧪 Testy

```bash
# Wszystkie testy
pytest

# Testy WooCommerce
pytest tests/test_woocommerce.py -v

# Testy z pokryciem kodu
pytest --cov=core --cov=woo --cov=utils

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

### Nowe metody WooCommerce

```python
from core.recommender import MedicalRecommender
from utils.config import Config

# Konfiguracja WooCommerce
config = Config(".env")
recommender = MedicalRecommender(config=config)

# Pobieranie produktów z WooCommerce
success = recommender.load_products_from_woocommerce()

# Wymuszenie odświeżenia
success = recommender.refresh_products()

# Testowanie połączenia
is_connected = recommender.test_woocommerce_connection()

# Informacje o cache
cache_info = recommender.get_cache_info()

# Informacje o sklepie
store_info = recommender.get_woocommerce_store_info()
```

## 🔄 Algorytm rekomendacji

1. **Źródło danych**: CSV (lokalne) lub WooCommerce API + cache
2. **Analiza zapytania**: Konwersja na małe litery, tokenizacja
3. **Dopasowanie reguł**: Wyszukiwanie pasujących słów kluczowych
4. **Obliczenie score'u**: Uwzględnienie wagi reguły i dokładności dopasowania
5. **Selekcja kategorii**: Wybór kategorii z najwyższymi score'ami
6. **Filtrowanie produktów**: Pobranie produktów z wybranych kategorii
7. **Sortowanie**: Według ceny (rosnąco)
8. **Ocena pewności**: Na podstawie jakości dopasowania reguł

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

### Informacje o WooCommerce
```bash
python main.py
# W trybie interaktywnym wpisz: woo
```

### Informacje o cache
```bash
python main.py
# W trybie interaktywnym wpisz: cache
```

### Odświeżenie produktów
```bash
python main.py
# W trybie interaktywnym wpisz: refresh
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

### Dodawanie nowych mapowań kategorii
Edytuj plik `woo/mapper.py` i dodaj nowe mapowanie w `CATEGORY_MAPPING`:

```python
"nowa_kategoria_woo": "wewnetrzna_kategoria",
```

### Konfiguracja cache
```python
# Zmiana czasu cache'owania (w sekundach)
CACHE_DURATION=7200  # 2 godziny

# Maksymalna liczba produktów
MAX_PRODUCTS=200
```

## 🤝 Konwencje kodu

- **Python 3.11+** z pełnym typowaniem
- **PEP8** + formatowanie przez `black`
- **Google Style** docstringi
- **pytest** do testów jednostkowych
- **Modułowość** - każda warstwa w oddzielnym folderze
- **Obsługa błędów** - szczegółowe logowanie i walidacja

## 📚 Następne kroki (Etap 3)

- [ ] API serwera Flask/FastAPI
- [ ] Endpointy REST API
- [ ] Middleware CORS
- [ ] Walidacja zapytań
- [ ] Dokumentacja API (Swagger/OpenAPI)

---

**Autor**: Medical Recommender Team  
**Licencja**: MIT  
**Status**: W rozwoju (Etap 2/5 ukończony) 