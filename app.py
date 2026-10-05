from pathlib import Path
from io import BytesIO
import csv
import json
import uuid
import base64
from io import StringIO
from PIL import Image, UnidentifiedImageError
import streamlit as st
from quiz_core import load_questions, select_questions

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Quiz dla Ciebie", page_icon="✨", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""<style>
.stApp {background: radial-gradient(ellipse at top right, #f2eaff 0, #faf9fe 48%, #fff 100%);}
.block-container {max-width: 850px; padding-top: 2.5rem; padding-bottom: 3rem;}
h1,h2,h3 {letter-spacing: -.035em;}
div.stButton>button[kind=primary] {border-radius: 12px; min-height: 46px;}
div[data-testid=stMetric] {background:white; padding:18px; border:1px solid #e8e2f1; border-radius:16px;}
div[data-testid=stForm] {background: #ffffffcc; border-radius: 18px;}
</style>""", unsafe_allow_html=True)


def local_file(path):
    candidate = (ROOT / path).resolve()
    if not candidate.is_relative_to(ROOT):
        raise ValueError("Ścieżka pliku musi znajdować się w katalogu aplikacji.")
    return candidate


def reset():
    for key in ["round", "answers", "index", "round_id"]:
        st.session_state.pop(key, None)
    st.session_state.page = "home"


def begin(pool, count):
    st.session_state["round"] = select_questions(pool, count)
    st.session_state.answers = []
    st.session_state.index = 0
    st.session_state.round_id = uuid.uuid4().hex
    st.session_state.page = "quiz"


if "settings" not in st.session_state:
    try:
        st.session_state.settings = json.loads((ROOT / "quiz_config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        st.error("Nie można odczytać quiz_config.json. Sprawdź plik konfiguracji.")
        st.stop()
if "page" not in st.session_state:
    st.session_state.page = "home"
cfg = st.session_state.settings

with st.sidebar:
    st.subheader("Twój quiz")
    st.caption("Ustawienia dotyczą tej sesji przeglądarki.")
    with st.expander("Pytania i szablon", expanded=st.session_state.page == "home"):
        upload = st.file_uploader("Wgraj pytania", type=["xlsx", "csv"], key="questions_upload")
        if st.button("Wczytaj plik", disabled=upload is None):
            try:
                new_pool = load_questions(upload.getvalue(), upload.name)
                st.session_state.pool = new_pool
                st.session_state.source = upload.name
                reset()
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
        if st.button("Wczytaj ponownie pytania z repozytorium"):
            st.session_state.pop("pool", None)
            reset()
            st.rerun()
        template = ROOT / "szablon_pytan.xlsx"
        if template.exists():
            st.download_button("Pobierz szablon Excel", template.read_bytes(), "szablon_pytan.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.caption("Excel: arkusz Pytania. CSV: nagłówki pytanie, A, B, C, D, poprawna, wyjasnienie, kategoria.")
    if st.session_state.page != "home" and st.button("Wróć na start", help="Kończy bieżącą próbę."):
        reset()
        st.rerun()

if "pool" not in st.session_state:
    try:
        primary = local_file(cfg.get("questions_file", "data/pytania.xlsx"))
        path = primary if primary.exists() else ROOT / "data/pytania.csv"
        st.session_state.pool = load_questions(path.read_bytes(), path.name)
        st.session_state.source = path.name
    except (OSError, ValueError) as exc:
        st.error(f"Nie udało się wczytać pytań: {exc}")
        st.info("Wgraj poprawny plik w panelu bocznym.")
        st.stop()
pool = st.session_state.pool
page = st.session_state.page

if page == "home":
    background = "linear-gradient(135deg, #4c1d95, #241a36)"
    try:
        image_data = st.session_state.get("picture")
        default_image = local_file(cfg.get("image_file", "assets/start.png"))
        if not image_data and default_image.exists():
            image_data = default_image.read_bytes()
        if image_data:
            with Image.open(BytesIO(image_data)) as img:
                mime = Image.MIME.get(img.format, "image/png")
            encoded = base64.b64encode(image_data).decode("ascii")
            background = f'url("data:{mime};base64,{encoded}")'
    except (ValueError, OSError, UnidentifiedImageError):
        st.warning("Nie można wyświetlić obrazka. Wgraj inny w panelu bocznym.")
    st.markdown(f"""<style>
    .block-container {{max-width: 1240px; padding-top: 1.5rem;}}
    .st-key-hero {{background-image:{background}; background-size:cover;
        background-position:center; border-radius:24px; overflow:hidden;
        padding:clamp(250px, 37vw, 460px) 24px 24px; box-shadow:0 18px 55px #32200b26;}}
    .st-key-hero_controls {{background:rgba(28,20,15,.84); backdrop-filter:blur(12px);
        padding:20px 24px; border-radius:18px; border:1px solid #ffffff33;}}
    .st-key-hero_controls h3, .st-key-hero_controls label,
    .st-key-hero_controls p {{color:#fff !important;}}
    .st-key-hero_controls div.stButton>button[kind=primary] {{background:#f3c67a;
        border-color:#f3c67a; color:#30200f; font-weight:700;}}
    .st-key-hero_controls div.stButton>button[kind=primary] p {{color:#30200f !important;}}
    @media(max-width:640px) {{.st-key-hero {{padding:250px 12px 12px; border-radius:16px;}}
        .st-key-hero_controls {{padding:16px;}}}}
    </style>""", unsafe_allow_html=True)
    with st.container(key="hero"):
        with st.container(key="hero_controls"):
            st.subheader("Ile pytań chcesz przećwiczyć?")
            mode = st.selectbox("Wybierz liczbę pytań", ["3 losowe pytania", "15 losowych pytań", "30 losowych pytań", "Pełna pula"], key="home_mode", label_visibility="collapsed")
            count = {"3 losowe pytania":3, "15 losowych pytań":15, "30 losowych pytań":30, "Pełna pula":None}[mode]
            actual = min(count, len(pool)) if count else len(pool)
            st.caption(f"W puli: {len(pool)} pytań. W tej próbie: {actual}.")
            if st.button("Przejdź dalej →", type="primary", use_container_width=True):
                st.session_state.selected_count = count
                st.session_state.selected_mode = mode
                begin(pool, count)
                st.rerun()

elif page == "quiz":
    questions = st.session_state["round"]
    i = st.session_state.index
    q = questions[i]
    answers = st.session_state.answers
    answered = len(answers) > i
    st.caption(f"PYTANIE {i+1} Z {len(questions)}")
    st.progress(i / len(questions))
    st.subheader(q["pytanie"])
    if q["kategoria"]:
        st.caption(q["kategoria"])
    with st.form(f"answer_{st.session_state.round_id}_{i}"):
        answer = st.radio("Twoja odpowiedź", list(q["options"]), index=list(q["options"]).index(answers[i]) if answered else None, key=f"choice_{st.session_state.round_id}_{i}",
                          format_func=lambda key: f"{key}. {q['options'][key]}", disabled=answered)
        submitted = st.form_submit_button("Sprawdź odpowiedź", type="primary", disabled=answered)
    if submitted and not answered:
        if answer is None:
            st.warning("Najpierw wybierz odpowiedź.")
        else:
            answers.append(answer)
            st.rerun()
    if answered:
        if answers[i] == q["poprawna"]:
            st.success("Poprawna odpowiedź!")
        else:
            st.error(f"Tym razem nie. Poprawna odpowiedź: {q['poprawna']}. {q['options'][q['poprawna']]}")
        if q["wyjasnienie"]:
            st.write(q["wyjasnienie"])
        if st.button("Zobacz wynik →" if i+1 == len(questions) else "Następne pytanie →", type="primary", use_container_width=True):
            if i+1 == len(questions):
                st.session_state.page = "result"
            else:
                st.session_state.index += 1
            st.rerun()

elif page == "result":
    questions, answers = st.session_state["round"], st.session_state.answers
    correct = sum(a == q["poprawna"] for q, a in zip(questions, answers))
    wrong = len(questions) - correct
    st.caption("QUIZ UKOŃCZONY")
    st.title("Twój wynik")
    cols = st.columns(3)
    cols[0].metric("Poprawne", correct)
    cols[1].metric("Niepoprawne", wrong)
    cols[2].metric("Skuteczność", f"{correct / len(questions):.0%}")
    mistakes = []
    rows = []
    for q, a in zip(questions, answers):
        ok = a == q["poprawna"]
        rows.append([q["pytanie"], q["options"][a], q["options"][q["poprawna"]], "TAK" if ok else "NIE"])
        if not ok:
            mistakes.append(q)
        with st.expander(("✓ " if ok else "✗ ") + q["pytanie"]):
            st.write(f"Twoja odpowiedź: {a}. {q['options'][a]}")
            st.write(f"Poprawna: {q['poprawna']}. {q['options'][q['poprawna']]}")
            if q["wyjasnienie"]:
                st.write(q["wyjasnienie"])
    output = StringIO()
    writer = csv.writer(output, delimiter=";")
    # Protect exported text against Excel formula interpretation.
    safe = lambda v: "'" + v if v.lstrip().startswith(("=", "+", "-", "@")) else v
    writer.writerow(["Pytanie", "Twoja odpowiedź", "Poprawna odpowiedź", "Poprawnie"])
    writer.writerows([[safe(str(v)) for v in row] for row in rows])
    st.download_button("Pobierz wynik CSV", output.getvalue().encode("utf-8-sig"), "wynik_quizu.csv", "text/csv")
    if mistakes and st.button("Powtórz tylko błędne pytania", use_container_width=True):
        begin(mistakes, None)
        st.rerun()
    if st.button("Wybierz nowy quiz", type="primary", use_container_width=True):
        reset()
        st.rerun()
