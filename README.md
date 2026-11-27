# Wielowątkowy Web Crawler z analizą sentymentu

Skrypt w języku Python służący do przeszukiwania stron internetowych, do zadanej głębokości linków oraz wydźwięku ich treści na podstawie zdefiniowanego słownika wag.

## Funkcjonalności
* Wielowątkowość: Równoległe pobieranie i przetwarzanie stron przy użyciu 'ThreadPoolExecutor'.
* Obsługa wielu formatów: Automatyczne rozpoznawanie i wyciąganie tekstu zarówno ze stron HTML, jak i dokmentów PDF.
* Analiza sentymentu: Zliczanie punktów dla słów kluczowych o pozytywnym i negatywnym wydźwięku.
* Ochrona przed pętlami: Śledzenie odwiedzonych adresów URL, aby nie pobierać wielokrotnie tych samych podstron.

## Wymagania i instalacja

Projekt wymaga Pythona 3.x oraz biblioteki 'beautifulsoup4' i 'pypdf'

1.Sklonuj repozytorium:
 ```bash
   git clone https://github.com
   cd crawler
   ```

2.Zainstaluj wymagane biblioteki:
 ```bash
   pip install -r requirements.txt
   ```

## Uruchomienie

Uruchom główny skrypt:
```bash
python main.py
```

Domyślnie program analizuje adres zdefiniowany w zmiennej 'adres_startowy', do głębokości określonej w 'maksymalna_glebokosc' i wypisuje w konsoli wynik punktowy dla każdej odwiedzonej strony.
