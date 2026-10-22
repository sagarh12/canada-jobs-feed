# canada-jobs-feed

A job feed for [Job Scout](https://github.com/nruppatel16/jobscout-feed) that covers **all of Canada except Quebec**, plus fully remote US jobs.
It collects tech, data, cybersecurity and IT jobs for students, new grads and people with up to a
year of experience, and publishes them as one JSON file that a Job Scout sheet reads.

It replaces the AI Ignite class feed for the "Tech & Data" field, which only searches Toronto.

## What it searches

| Source | How | Where |
| --- | --- | --- |
| Indeed Canada | [JobSpy](https://github.com/speedyapply/JobSpy) | Canada-wide, plus Toronto, Ottawa, Waterloo, Vancouver, Calgary, Edmonton, Winnipeg and Halifax |
| LinkedIn | JobSpy | Canada-wide (LinkedIn allows about 16 searches a run, so terms rotate between runs) |
| Indeed (United States) | JobSpy, "<term> remote" | **Fully remote US jobs only**: kept only if marked remote, and dropped if the title, location or description says hybrid, on-site or in-office |
| Job Bank (Government of Canada) | Its search pages, newest first | All provinces and territories |
| Employer career sites | Their RSS feeds (SAP SuccessFactors) | Scotiabank, Deloitte, EY, SAP, Rogers, Bell, TELUS, Hydro One, OPG, Toronto Hydro, Canada Post, Purolator, Bombardier, University of Toronto, Halton Region |
| Employer hiring systems | Their Workday boards, read newest first and narrowed to Canada | RBC (incl. early talent), TD, CIBC (incl. campus), BMO, Desjardins, Manulife, Sun Life (incl. campus), Intact, iA, Ontario Teachers', OMERS, HOOPP (incl. students), Interac, Moneris, Fidelity Canada, Mastercard, PwC, BDO, Raymond Chabot Grant Thornton, Thomson Reuters, NVIDIA, Salesforce, Intel, Cisco, Ciena, Autodesk, CDW, CAE, Canadian Tire, Enbridge, Cenovus |
| Employer job APIs | Their own careers-site search | KPMG Canada, Microsoft (Canada), IBM (Canada), OpenText |
| Tech companies | Greenhouse, Ashby, Lever and SmartRecruiters job boards (Canadian jobs, plus fully remote US jobs) | Wealthsimple, Cohere, 1Password, KOHO, Benevity, Jobber, Lightspeed, Thinkific, Float, Neo Financial, Top Hat, Trulioo, Clearco, Hopper, Miovision, Procurify, Visier, Geotab, D2L, Hootsuite, Tenstorrent, Ritual, Fellow, Diligent, StackAdapt, Flipp, PointClickCare, Wattpad, Wave, Achievers, Magnet Forensics, Wishpond, Ubisoft, Visa, Bosch, Adobe, HP, Lyft, Stripe, Databricks, Cloudflare, Datadog, Twilio, Okta, Instacart, Coinbase, Robinhood, Samsara, Pinterest, Dropbox, Affirm, Figma, Brex, Scale AI, Anthropic, Snowflake, Plaid, Notion, Ramp, OpenAI, Shakepay, Loopio, PolicyMe, Waabi, Faire, Sophos, GitLab, Mercury, Elastic, Tailscale, Grafana Labs, Braze, Cerebras, MongoDB, Asana, Toast, Reddit, Carta, Fivetran, Sentry, Chainguard, Honeycomb, PagerDuty, Vanta, CircleCI, ClickHouse, Nubank, Sanity, Lattice, Zscaler, Abnormal Security, Cribl, Gusto, Amplitude, NerdWallet, Temporal, Arcadia, Bitwarden, Collibra, Dataiku, Discord, Drata, Expel, Hex, Iterable, Kira, LaunchDarkly, Linear, Mixpanel, Monzo, Netlify, Perplexity, Pinecone, PlanetScale, Replit, Secureframe, SecurityScorecard, Semgrep, Sigma Computing, Snyk, Socket, Storyblok, Supabase, Tines, Tulip, Vercel, Webflow, Wiz, Zapier, Anyscale |
| Public sector (tech roles only) | SuccessFactors RSS; BC's job list | City of Toronto, BC Public Service |
| Automotive (tech roles only) | Workday; Oracle Recruiting for Ford | General Motors, Ford, Magna, Nissan Canada, BlackBerry / QNX |
| Utilities and energy (tech roles only) | Workday; SuccessFactors RSS | Hydro Ottawa, Bruce Power, Capital Power, ENMAX, IESO, TransAlta (plus Hydro One, OPG, Toronto Hydro, Enbridge above) |
| Health (tech roles only) | Workday | Hospitals: Sinai Health, Southlake, Oak Valley Health, CHEO, St. Joseph's Hamilton, Public Health Ontario. Pharma and medtech: McKesson, Medtronic, Roche, Pfizer, Johnson & Johnson, GSK, AstraZeneca, Sanofi, Baxter, Philips, Abbott, Stryker, Novartis |

Employer jobs come straight from the company's own hiring system, usually hours or days before
they show up on LinkedIn or Indeed. They aren't searched by keyword, so only titles that name tech
work (software, data, IT, cyber, cloud, QA…) or an early-career role (new grad, graduate, intern,
co-op, student, junior, campus, rotational…) in Canada are kept. Automotive, utility and health
employers are stricter: tech titles only (software, data, IT, cyber, cloud, embedded, informatics…),
so nursing, plant and pharmacy jobs stay out. To add an employer on Workday, add
its `(name, host, site)` from the board's address, `https://<host>.myworkdayjobs.com/<site>`, to
`WORKDAY` in `feed.py`.

Search terms: software developer, software engineer, data analyst, data engineer, business
intelligence analyst, IT support, help desk, cyber security analyst, SOC analyst, network
administrator, cloud engineer, QA analyst, new grad software, junior developer, software intern,
software developer co-op, data analyst intern, data science intern, IT co-op, cybersecurity intern,
computer science student, summer student technology, new graduate software engineer, entry level
data analyst, junior IT analyst, technical support analyst.

**Left out:**
- Jobs in Quebec (a job that also names a place outside Quebec, like "Montreal or Toronto", stays;
  "Montréal, QC (remote)" is still a Quebec job).
- Part-time jobs: by job type (Indeed, LinkedIn, Ashby, Lever, SmartRecruiters, Job Bank), by title, or
  by a description saying it's a part-time position. A job offered as full-time or part-time stays.
- Jobs that require French: French titles, Job Bank postings whose Languages field asks for French
  or both languages, and descriptions asking for French or bilingualism ("French is an asset" is fine).
- Senior, lead, manager and executive titles, unless the title is also a student or new-grad role
  ("Product Owner Co-op").

- Only jobs posted in the last **48 hours** are searched for and kept.
- Results are merged across runs, so a run where a board blocks the scraper doesn't empty the feed.
- The same job found on several boards is kept once (same company, title and city), with the
  employer's own link preferred over a job board's.
- Each run stops starting new searches after about 8 minutes. LinkedIn searches run one at a
  time and stop for the run after three failures in a row. City searches run in a random order, so
  over a day every city gets covered.

## Schedule

GitHub's own schedule runs far less often than asked when GitHub is busy (on 2026-10-15,
"every 30 minutes" ran about every 2 hours). So the workflow is started **every 10 minutes from
outside**, by a small Google Apps Script project (`trigger/trigger.gs`) that calls GitHub's API.
Each of those runs is in `auto` mode:
- a **full run** (job boards + employers, about 9 minutes) when the last full run was 28+ minutes ago;
- otherwise a **quick run** (employers' own boards only, about 1.5 minutes).

A GitHub schedule at :17 and :47 stays as a backup. You can also start a run from the **Actions**
tab with **Run workflow** (mode `auto`, `full` or `quick`). Each run commits the `feed/` folder
when it changes.

**Setting up the trigger** (once):
1. GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** →
   Generate new token. Repository access: **Only select repositories** → `canada-jobs-feed`.
   Permissions → Repository permissions → **Actions: Read and write** (nothing else). Pick an expiry.
2. [script.google.com](https://script.google.com) → **New project** → paste `trigger/trigger.gs` → save.
3. Project Settings (gear) → **Script properties** → add `GITHUB_TOKEN` = the token.
4. Choose `setUp` in the toolbar → **Run** → approve the permissions. It starts a run right away,
   then every 10 minutes. `stop` turns it off.

When the token expires, runs fall back to GitHub's own schedule: make a new token and replace the
script property.

**Health check:** if a source (Indeed, LinkedIn, Job Bank, employer sites, employer boards, tech
company boards) finds nothing 3 runs in a row, the run fails and GitHub emails you.

## Phone alerts

New internship, co-op and new-grad jobs (asking for 0–1 years, or not saying) are pushed to your
phone through [ntfy](https://ntfy.sh), up to 15 a run. The channel name is the repo secret
`NTFY_TOPIC`. To get them, install the ntfy app (iOS or Android) and subscribe to that channel name.
Anyone who knows the name can read it, so keep it private. Delete the secret to stop alerts.

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
      "country": "CA",
      "years": 1
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `posted` | `YYYY-MM-DD`, or a full ISO time when the board gives one |
| `source` | `Indeed`, `LinkedIn`, `Job Bank`, or `<Employer> careers` (for example `TD careers`, `KPMG careers`) |
| `country` | `CA`, or `US` for fully remote US jobs (their `location` is `Remote · United States`) |
| `apply` | Only when known (Indeed, LinkedIn): the employer's own application page, for example a Greenhouse or Workday link |
| `years` | The most years of experience the job asks for, or `null` if it names none. Read from the description (Indeed, KPMG, IBM and the RSS career sites) or Job Bank's Experience field. LinkedIn jobs are `null` here; the sheet reads LinkedIn pages itself. |

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
