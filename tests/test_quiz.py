from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quiz_core import load_questions, select_questions
from streamlit.testing.v1 import AppTest


class ImportTests(unittest.TestCase):
    def test_excel_and_csv_agree(self):
        excel = load_questions((ROOT / 'szablon_pytan.xlsx').read_bytes(), 'test.xlsx')
        csv = load_questions((ROOT / 'data/pytania.csv').read_bytes(), 'test.csv')
        self.assertEqual(excel, csv)
        self.assertEqual(len(excel), 40)

    def test_validation_and_blanks(self):
        good = b'pytanie;A;B;poprawna\nTest?;0;1;a\n;;;\n'
        self.assertEqual(load_questions(good, 'a.csv')[0]['poprawna'], 'A')
        for bad in [b'pytanie;A;B;poprawna\nTest?;0;1;D',
                    b'pytanie;A;B;poprawna\nTest?;;1;B',
                    b'pytanie;A;B;poprawna\nTest?;1;1;A',
                    b'pytanie;A;B;poprawna\n;;;']:
            with self.assertRaises(ValueError):
                load_questions(bad, 'test.csv')

    def test_sampling_modes(self):
        pool = load_questions((ROOT / 'data/pytania.csv').read_bytes(), 'test.csv')
        for count in [1, 15, 30, 40, 50]:
            sampled = select_questions(pool, count)
            self.assertEqual(len(sampled), min(count, 40))
            self.assertEqual(len({q['pytanie'] for q in sampled}), len(sampled))
        self.assertEqual(select_questions(pool, None), pool)


class FlowTests(unittest.TestCase):
    def click(self, at, label):
        next(b for b in at.button if b.label == label).click().run()
        self.assertFalse(at.exception, str(at.exception))

    def new_app(self, mode='3 losowe pytania'):
        at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=20).run()
        self.assertFalse(at.exception)
        at.selectbox[0].set_value(mode).run()
        self.click(at, 'Przejdź dalej →')
        return at

    def test_complete_quiz_and_retry(self):
        at = self.new_app()
        self.click(at, 'Zaczynam quiz →')
        self.click(at, 'Sprawdź odpowiedź')
        self.assertEqual(len(at.session_state.answers), 0)
        for i in range(3):
            q = at.session_state['round'][i]
            choice = q['poprawna'] if i < 2 else next(k for k in q['options'] if k != q['poprawna'])
            at.radio[0].set_value(choice)
            self.click(at, 'Sprawdź odpowiedź')
            self.assertTrue(next(b for b in at.button if b.label == 'Sprawdź odpowiedź').disabled)
            self.click(at, 'Następne pytanie →' if i < 2 else 'Zobacz wynik →')
        self.assertEqual([m.value for m in at.metric], ['2','1','67%'])
        self.click(at, 'Powtórz tylko błędne pytania')
        self.assertEqual(len(at.session_state['round']), 1)
        self.assertEqual(at.session_state.answers, [])
        self.click(at, 'Wróć na start')
        self.assertEqual(at.session_state.page, 'home')

    def test_all_mode_sizes_and_dedication(self):
        for mode, count in [('3 losowe pytania',3), ('15 losowych pytań',15), ('30 losowych pytań',30), ('Pełna pula',40)]:
            at = self.new_app(mode)
            self.click(at, 'Zaczynam quiz →')
            self.assertEqual(len(at.session_state['round']), count)


if __name__ == '__main__':
    unittest.main()
