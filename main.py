import io
import re
import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pypdf

SLOWNIK = {
    "nagroda": 1.0,
    "laureat": 1.0,
    "laureatka": 1.0,
    "sukces": 0.9,
    "awans": 0.8,
    "wyróżnienie": 0.9,
    "stypendium": 0.8,
    "odkrycie": 0.9,

    "przyjęcie": 0.6,
    "absolwent": 0.5,
    "staż": 0.6,
    "praktyki": 0.5,
    "rozwój": 0.7,
    "nowoczesny": 0.5,
    "otwarty": 0.4,

    "odwołany": -0.8,
    "odwołane": -0.8,
    "zawieszony": -0.8,
    "zaległość": -0.7,
    "poprawkowy": -0.5,
    "warunkowy": -0.6,

    "awaria": -0.8,
    "przerwa": -0.5,
    "niedostępny": -0.6,
    "zamknięte": -0.5,
    "opóźnienie": -0.6,
    "błąd": -0.6,
    "problem": -0.5,
}


def wyciaganie_tekstu_z_pdf(plik_pdf):
    try:
        otwarty_pdf = pypdf.PdfReader(io.BytesIO(plik_pdf))
        tekst_koncowy=[]
        for strona in otwarty_pdf.pages:
            tekst = strona.extract_text()
            if tekst:
                tekst_koncowy.append(tekst)

        return " ".join(tekst_koncowy)
    except Exception as error:
        print(f"Nie udało się odczytać pliku: {error}")
        return ""


def wyciaganie_linkow(aktualny_adres, kod_html):
    drzewo_html = BeautifulSoup(kod_html, "html.parser")
    poprawne_linki = []
    for link in drzewo_html.find_all("a", href=True):
        surowy_link = link["href"].strip()
        pelny_adres = urljoin(aktualny_adres, surowy_link)
        czesci_adresu = urlparse(pelny_adres)
        if czesci_adresu.scheme in ("http", "https"):
            czysty_adres = pelny_adres.split("#")[0]
            poprawne_linki.append(czysty_adres)

    return poprawne_linki


def pobieranie_zawartosci_strony(adres_url):
    naglowki = {"User-Agent": "Mozilla/5.0"}
    szablon = urllib.request.Request(adres_url, headers=naglowki)
    niezweryfikowany_ssl = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(szablon, timeout=5, context=niezweryfikowany_ssl) as zapytanie_do_strony:
            typ = zapytanie_do_strony.headers.get("Content-Type", "")
            surowy_plik = zapytanie_do_strony.read()

            if "application/pdf" in typ or adres_url.lower().endswith(".pdf"):
                return wyciaganie_tekstu_z_pdf(surowy_plik)

            if "text/html" not in typ and "text/plain" not in typ:
                return None

            return surowy_plik.decode("utf-8", errors="replace")

    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as error:
        print(f"Błąd podczas łączenia ze stroną : {error}")
        return None


def analiza_slownika(tresc_strony, wagi: dict = None):
    wagi = SLOWNIK

    drzewo = BeautifulSoup(tresc_strony, "html.parser")
    czysty_tekst = drzewo.get_text()
    slowa = re.findall(r"\w+", czysty_tekst.lower())

    laczny_wynik = 0.0
    for slowo in slowa:
        if slowo in wagi:
            laczny_wynik += wagi[slowo]
    return round(laczny_wynik, 2)


def przetworz_strone(adres_url, action, pobierz_linki):
    tresc = pobieranie_zawartosci_strony(adres_url)
    if tresc is None:
        return adres_url, None, []

    wynik = action(tresc)
    nowe_linki = wyciaganie_linkow(adres_url, tresc) if pobierz_linki else []
    return adres_url, wynik, nowe_linki


def crawl(start_page, distance, action=analiza_slownika, max_workers=5):
    odwiedzone_strony = {start_page}
    adresy_do_sprawdzenia  = [start_page]
    wyniki = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for glebokosc in range(distance + 1):
            pobierz_linki = glebokosc < distance
            zadania = []
            for adres in adresy_do_sprawdzenia:
                zlecenie = executor.submit(przetworz_strone, adres, action, pobierz_linki)
                zadania.append(zlecenie)

            nowe_adresy = []
            for zadanie in as_completed(zadania):
                adres, wynik, linki = zadanie.result()
                if wynik is not None:
                    wyniki.append((adres, wynik))
                    print(f"{adres}  : {wynik}")

                for link in linki:
                    if link not in odwiedzone_strony:
                        odwiedzone_strony.add(link)
                        nowe_adresy.append(link)

            adresy_do_sprawdzenia  = nowe_adresy
            if not adresy_do_sprawdzenia :
                break

    return wyniki


adres_startowy = "https://ii.uni.wroc.pl/"
maksymalna_glebokosc = 1

rezultaty = crawl(adres_startowy, maksymalna_glebokosc)


