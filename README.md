# Quiz dla Ciebie — Streamlit

Aplikacja po polsku: własny obrazek na start, dedykacja po przejściu dalej, import pytań, cztery tryby i podsumowanie wyniku. W paczce jest 40 przykładowych pytań z dodawania. Zastąp je własnymi.

## Uruchomienie lokalnie

Wymagany Python 3.11 lub nowszy. W folderze aplikacji uruchom:

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Publikacja z GitHuba

1. Rozpakuj paczkę. Prześlij zawartość folderu `quiz-streamlit` do repozytorium GitHub, zachowując foldery `data`, `assets` oraz `.streamlit`.
2. Wejdź na https://share.streamlit.io/ i zaloguj się kontem GitHub.
3. Wybierz **Create app**, swoje repozytorium i gałąź. Wskaż plik **app.py**. W ustawieniach zaawansowanych wybierz Python 3.11 lub nowszy.
4. Kliknij **Deploy**. Streamlit udostępni adres aplikacji.

Instrukcja platformy: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

## Własne pytania

Otwórz `szablon_pytan.xlsx`. Arkusz **Dashboard** opisuje format; arkusz **Pytania** zawiera dane do importu. Usuń przykłady i wstaw własne pytania od wiersza 2. Nagłówki muszą pozostać w wierszu 1.

| Kolumna | Zawartość |
|---|---|
| pytanie | Treść pytania — wymagana |
| A, B | Co najmniej dwie odpowiedzi — wymagane |
| C, D | Dodatkowe odpowiedzi — opcjonalne |
| poprawna | Jedna litera A/B/C/D wskazująca istniejącą odpowiedź |
| wyjasnienie | Wyjaśnienie po odpowiedzi — opcjonalne |
| kategoria | Temat pytania — opcjonalny |

Każdy wiersz to jedno pytanie z jedną poprawną odpowiedzią. Aplikacja odrzuca niekompletne wiersze i podaje ich numery. Puste wiersze ignoruje. Poprawność merytoryczna odpowiedzi pochodzi z Twojego klucza — aplikacja nie zgaduje odpowiedzi.

### Wgranie w aplikacji

W panelu bocznym otwórz **Pytania i szablon**, wybierz plik Excel lub CSV i kliknij **Wczytaj plik**. Zmiana bazy rozpoczyna nową próbę. Plik dotyczy tylko bieżącej sesji przeglądarki.

### Wgranie na GitHubie

Zapisz własny Excel jako **data/pytania.xlsx** w tym samym repozytorium co aplikacja. Ten plik ma pierwszeństwo przed przykładowym CSV. Po wdrożeniu nowej wersji kliknij **Wczytaj ponownie pytania z repozytorium** lub rozpocznij nową sesję. Nie trzeba zmieniać kodu ani przesyłać pytań do asystenta. Plik w innym repozytorium nie jest pobierany automatycznie.

CSV powinien być zapisany jako UTF-8, z separatorem przecinek lub średnik i tymi samymi nagłówkami. W `quiz_config.json` możesz wskazać `data/pytania.csv` zamiast Excela.

## Obrazek i dedykacja

W **Wygląd i dedykacja** możesz zmienić tytuł, osobę, dedykację i obrazek dla swojej sesji. Pierwszy ekran to obrazek z panelem wyboru liczby pytań na jego tle. Dedykacja pojawia się po kliknięciu „Przejdź dalej”.

Aby te ustawienia zobaczył każdy odwiedzający, pobierz ustawienia przyciskiem w panelu i zastąp **quiz_config.json** na GitHubie. Obrazek dodaj jako **assets/start.png** albo zmień `image_file` na jego ścieżkę w folderze aplikacji. Wgrywanie w panelu nie zapisuje zmian do repozytorium. Każda osoba ma własny postęp; wynik nie jest trwale przechowywany. Można go pobrać jako CSV.

## Tryby i wynik

- **3 losowe pytania**, **15 losowych pytań** oraz **30 losowych pytań**: losowanie bez powtórzeń. Jeżeli pula jest mniejsza, aplikacja używa całej puli i informuje o tym.
- **Pełna pula**: wszystkie pytania w kolejności z pliku.

Tryb wybierasz bezpośrednio na obrazku na pierwszym ekranie. Po dedykacji kliknij „Zaczynam quiz”.

Po sprawdzeniu odpowiedzi nie można jej zmienić. Na końcu są liczby poprawnych i błędnych odpowiedzi, wynik procentowy i przegląd odpowiedzi. Możesz też powtórzyć wyłącznie pytania, w których był błąd.

## Sprawdzenie aplikacji

```sh
python -m unittest discover -s tests -v
```
