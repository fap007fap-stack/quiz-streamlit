"""Import, validation and random selection independent of the UI."""
from io import BytesIO
import random
import pandas as pd

LETTERS = "ABCD"
REQUIRED = {"pytanie", "A", "B", "poprawna"}


def load_questions(data: bytes, filename: str) -> list[dict]:
    try:
        if filename.lower().endswith(".xlsx"):
            frame = pd.read_excel(BytesIO(data), sheet_name="Pytania", dtype=str, keep_default_na=False)
        elif filename.lower().endswith(".csv"):
            frame = pd.read_csv(BytesIO(data), sep=None, engine="python", dtype=str, keep_default_na=False, encoding="utf-8-sig")
        else:
            raise ValueError("Wybierz plik .xlsx lub .csv.")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Nie udało się odczytać pliku. Sprawdź format i arkusz Pytania.") from exc
    frame.columns = [str(c).strip() for c in frame.columns]
    if frame.columns.duplicated().any():
        raise ValueError("Nagłówki kolumn nie mogą się powtarzać.")
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError("Brakuje kolumn: " + ", ".join(sorted(missing)))
    questions, errors = [], []
    for index, row in frame.iterrows():
        values = {str(k): str(v).strip() for k, v in row.items()}
        # Empty template rows are ignored; incomplete populated rows are rejected.
        if not any(values.values()):
            continue
        n = index + 2
        options = {key: values.get(key, "") for key in LETTERS if values.get(key, "")}
        correct = values["poprawna"].upper()
        if not values["pytanie"] or not values["A"] or not values["B"]:
            errors.append(f"Wiersz {n}: uzupełnij pytanie oraz odpowiedzi A i B.")
        elif correct not in options:
            errors.append(f"Wiersz {n}: poprawna musi wskazywać wypełnioną odpowiedź A, B, C lub D.")
        elif len(set(options.values())) != len(options):
            errors.append(f"Wiersz {n}: odpowiedzi nie mogą być identyczne.")
        else:
            questions.append({"pytanie": values["pytanie"], "options": options, "poprawna": correct,
                              "wyjasnienie": values.get("wyjasnienie", ""), "kategoria": values.get("kategoria", "")})
    if errors:
        raise ValueError("\n".join(errors[:12]) + (f"\nI jeszcze {len(errors)-12} błędów." if len(errors)>12 else ""))
    if not questions:
        raise ValueError("Plik nie zawiera żadnych pytań.")
    return questions


def select_questions(pool: list[dict], count: int | None) -> list[dict]:
    if count is None:
        return list(pool)
    if count < 1:
        raise ValueError("Liczba pytań musi wynosić co najmniej 1.")
    return random.sample(pool, min(count, len(pool)))
