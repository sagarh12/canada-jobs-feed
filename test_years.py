"""Checks for years_asked(): python -m unittest test_years"""
import unittest

from feed import jobbank_years, years_asked


class YearsAsked(unittest.TestCase):
    def test_descriptions(self):
        cases = {
            "3+ years of experience": 3,
            "Minimum of two (2) years related experience": 2,
            "1-2 years of experience": 1,
            "0-2 years of experience": 0,
            "Less than 2 years of experience": None,
            "Graduated within the last 2 years": None,
            "5+ years of professional software development": 5,
            "Experience: 4+ years": 4,
            "1 year of experience… 3 years experience is an asset": 1,
            "Our company has 25 years of experience": None,
            "Experience with React (2+ years preferred)": None,
            "minimum 2 yrs experience": 2,
        }
        for text, years in cases.items():
            with self.subTest(text=text):
                self.assertEqual(years_asked(text), years)

    def test_job_bank_field(self):
        cases = {"Will train": 0, "Experience an asset": 0, "Less than 1 year": 0, "7 months to less than 1 year": 0,
                 "1 year to less than 2 years": 1, "2 years to less than 3 years": 2, "5 years or more": 5, "": None}
        for text, years in cases.items():
            with self.subTest(text=text):
                self.assertEqual(jobbank_years(text), years)


if __name__ == "__main__":
    unittest.main()
