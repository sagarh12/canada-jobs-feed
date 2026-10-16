"""Checks for the feed's parsers and filters: python -m unittest test_years"""
import unittest

from feed import french_required, in_quebec_only, is_senior, jobbank_years, left_out, years_asked


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
            # phrasings without the word "experience"
            "2+ years developing web applications": 2,
            "Minimum 2 years in a software role": 2,
            "At least 3 years as a developer": 3,
            "We have been in business for over 10 years in Canada": None,
            "Founded 20 years ago": None,
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


class Filters(unittest.TestCase):
    def test_quebec(self):
        cases = {"Montreal, QC": True, "Montréal, Quebec, CA, H3B": True, "Laval": True, "Gatineau, QC, Canada": True,
                 "Saint-Laurent, Québec, CA": True, "Montreal or Toronto": False, "Toronto, ON": False,
                 "Remote · Canada": False, "Ottawa, ON": False, "Canada": False, "Vancouver, BC": False}
        for loc, quebec in cases.items():
            with self.subTest(loc=loc):
                self.assertEqual(in_quebec_only(loc), quebec)

    def test_french(self):
        cases = {
            "Bilingualism (English and French) is required.": True,
            "Fluency in French is mandatory for this role.": True,
            "You must be able to communicate in French with clients.": True,
            "French is an asset.": False,
            "Bilingual (English/French) is an asset": False,
            "Knowledge of French is considered a plus.": False,
            "This posting is also available in French.": False,
            "Strong English communication skills.": False,
            "Poste bilingue": True,
        }
        for text, french in cases.items():
            with self.subTest(text=text):
                self.assertEqual(french_required(text), french)

    def test_french_titles_and_senior(self):
        out = ["Stagiaire en développement logiciel", "Analyste de données junior", "Développeur(se) Java",
               "Technicien(ne) en informatique", "Ingénieur logiciel - finissant", "Staff Software Engineer",
               "Senior Data Analyst", "Software Engineer III"]
        keep = ["Product Owner Co-op", "Software Engineer Intern - Platform Architecture", "Data Analyst Intern",
                "Junior Developer", "IT Support Analyst", "Data Analyst II", "Senior Software Engineer Intern"]
        for t in out:
            with self.subTest(title=t):
                self.assertTrue(left_out({"title": t, "location": "Toronto, ON"}))
        for t in keep:
            with self.subTest(title=t):
                self.assertFalse(left_out({"title": t, "location": "Toronto, ON"}))
        self.assertFalse(is_senior("Lead Generation Intern"))


if __name__ == "__main__":
    unittest.main()
