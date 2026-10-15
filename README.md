# canada-jobs-feed

A job feed for [Job Scout](https://github.com/nruppatel16/jobscout-feed) that covers **all of Canada**.
It collects tech, data, cybersecurity and IT jobs for students, new grads and people with up to a
year of experience, and publishes them as one JSON file that a Job Scout sheet reads.

It replaces the AI Ignite class feed for the "Tech & Data" field, which only searches Toronto.

## What it searches

| Source | How | Where |
| --- | --- | --- |
| Indeed Canada | [JobSpy](https://github.com/speedyapply/JobSpy) | Canada-wide, plus Toronto, Ottawa, Waterloo, Montreal, Vancouver, Calgary, Edmonton, Winnipeg and Halifax |
| LinkedIn | JobSpy | Same places |
| Job Bank (Government of Canada) | Its search pages, newest first | All provinces and territories |
| Employer career sites | Their RSS feeds (SAP SuccessFactors) | Rogers, Bell, TELUS, Hydro One, OPG, Toronto Hydro, Canada Post, Purolator, Bombardier, University of Toronto, Halton Region |

Search terms: software developer, software engineer, data analyst, data engineer, business
intelligence analyst, IT support, help desk, cyber security analyst, SOC analyst, network
administrator, cloud engineer, QA analyst, new grad software, junior developer.

- Only jobs posted in the last **48 hours** are searched for and kept.
- Results are merged across runs, so a run where a board blocks the scraper doesn't empty the feed.
- The same job found on several boards is kept once (same company, title and city).
- Senior, lead, manager and executive titles are dropped.
- Each run stops starting new searches after about 8 minutes. LinkedIn searches run one at a
  time and stop for the run after three failures in a row. City searches run in a random order, so
  over a day every city gets covered.

## Schedule

GitHub Actions runs `feed.py` every 30 minutes (`.github/workflows/feed.yml`) and commits the
`feed/` folder when it changes. You can also start a run from the **Actions** tab with **Run workflow**.

The repo is public because Actions minutes are free and unlimited for public repos.

## The feed

`https://raw.githubusercontent.com/sagarh12/canada-jobs-feed/main/feed/tech.json`

```json
{
  "updated": "2026-10-15T14:30:05+00:00",
  "jobs": [
    {
      "title": "Junior Data Analyst",
      "company": "Example Inc.",
      "location": "Calgary, AB",
      "posted": "2026-10-15",
      "link": "https://ca.indeed.com/viewjob?jk=...",
      "source": "Indeed",
      "years": 1
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `posted` | `YYYY-MM-DD`, or a full ISO time when the board gives one |
| `source` | `Indeed`, `LinkedIn`, `Job Bank`, or `<Employer> careers` (for example `Rogers careers`) |
| `years` | The most years of experience the job asks for, or `null` if it names none. Read from the description (Indeed) or Job Bank's Experience field. LinkedIn jobs are `null` here; the sheet reads LinkedIn pages itself. |

`years` uses the same rules as the sheet's experience check: "0-2 years" counts as 0, and
"less than 2 years", "graduated within 2 years" and "3 years preferred / an asset" don't count as
requirements. It matters most for Indeed, whose pages Google's servers can't open.

`feed/status.json` has the counts from the latest run.

## Pointing Job Scout at it

In the sheet, open **Extensions → Apps Script** and change `CLASS_FEED` to:

```js
const CLASS_FEED = 'https://raw.githubusercontent.com/sagarh12/canada-jobs-feed/main/feed/';
```

Keep the "Class job feed" setting on and the field set to "Tech & Data" (it reads `tech.json`).

## Running it yourself

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest test_years
.venv/bin/python feed.py
```
