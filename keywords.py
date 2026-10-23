"""Technical keywords in job descriptions, and a running tally of how many postings ask for each.

skills(text) -> the keywords one posting mentions. tally(jobs, ...) counts each job once (by link), keeps
all-time totals plus the last 30 days, and writes feed/keywords.csv: the skills most entry-level tech postings
want, for the "Resume keywords" tab in the job sheet.
"""
import csv
import io
import json
import re
from datetime import datetime, timedelta

# (keyword, category, pattern). Patterns are case-insensitive unless they start with (?-i).
KEYWORDS = [
    # Languages
    ('Python', 'Language', r'\bpython\b'), ('Java', 'Language', r'\bjava\b(?!\s*script)'),
    ('JavaScript', 'Language', r'\bjavascript\b|\bES6\b'), ('TypeScript', 'Language', r'\btypescript\b'),
    ('C++', 'Language', r'(?<![\w+])c\+\+'), ('C#', 'Language', r'(?<!\w)c#'), ('C', 'Language', r'(?-i)(?<![\w/+#.])C(?![\w+#])(?=\s*(,|/|and|or|\)|programming|language))'),
    ('Go', 'Language', r'\bgolang\b|(?-i:\bGo\b)(?=\s*(,|/|\)|and|or|programming|language|developer))'),
    ('Rust', 'Language', r'\brust\b'), ('Kotlin', 'Language', r'\bkotlin\b'), ('Swift', 'Language', r'\bswift\b'),
    ('Ruby', 'Language', r'\bruby\b'), ('PHP', 'Language', r'\bphp\b'), ('Scala', 'Language', r'\bscala\b'),
    ('R', 'Language', r'(?-i)(?<![\w&-])R(?![\w&-])(?=\s*(,|/|\)|and|or|programming|language|studio))'),
    ('MATLAB', 'Language', r'\bmatlab\b'), ('SQL', 'Language', r'\bsql\b'), ('Bash/Shell', 'Language', r'\bbash\b|shell script'),
    ('PowerShell', 'Language', r'\bpowershell\b'), ('HTML/CSS', 'Language', r'\bhtml5?\b|\bcss3?\b'),
    ('Dart', 'Language', r'\bdart\b'), ('Solidity', 'Language', r'\bsolidity\b'), ('VBA', 'Language', r'\bvba\b'),
    ('Verilog/VHDL', 'Language', r'\bverilog\b|\bvhdl\b'), ('Embedded C', 'Language', r'embedded c\b'),
    # Frameworks and libraries
    ('React', 'Framework', r'\breact(\.?js)?\b(?!\s*native)'), ('React Native', 'Framework', r'react native'),
    ('Angular', 'Framework', r'\bangular(js)?\b'), ('Vue', 'Framework', r'\bvue(\.?js)?\b'), ('Next.js', 'Framework', r'\bnext\.?js\b'),
    ('Node.js', 'Framework', r'\bnode(\.?js)?\b'), ('Express', 'Framework', r'express\.?js|node(\.?js)?\s*(/|,|and)\s*express'),
    ('Django', 'Framework', r'\bdjango\b'), ('Flask', 'Framework', r'\bflask\b'), ('FastAPI', 'Framework', r'\bfastapi\b'),
    ('Spring Boot', 'Framework', r'spring ?boot|spring (framework|mvc|cloud)'), ('.NET', 'Framework', r'\.net\b|\basp\.net\b|dotnet'),
    ('Ruby on Rails', 'Framework', r'\brails\b'), ('Laravel', 'Framework', r'\blaravel\b'), ('Flutter', 'Framework', r'\bflutter\b'),
    ('jQuery', 'Framework', r'\bjquery\b'), ('Tailwind', 'Framework', r'\btailwind\b'), ('GraphQL', 'Framework', r'\bgraphql\b'),
    ('REST APIs', 'Framework', r'\brest(ful)?\b( api)?|\bapis?\b'), ('gRPC', 'Framework', r'\bgrpc\b'),
    ('Redux', 'Framework', r'\bredux\b'), ('Unity', 'Framework', r'\bunity\b(?! of)'), ('Qt', 'Framework', r'(?-i)\bQt\b'),
    # Data, AI and ML
    ('Pandas', 'Data & AI', r'\bpandas\b'), ('NumPy', 'Data & AI', r'\bnumpy\b'), ('scikit-learn', 'Data & AI', r'scikit|sklearn'),
    ('TensorFlow', 'Data & AI', r'tensorflow'), ('PyTorch', 'Data & AI', r'pytorch'), ('Keras', 'Data & AI', r'\bkeras\b'),
    ('Machine learning', 'Data & AI', r'machine learning|\bml\b'), ('Deep learning', 'Data & AI', r'deep learning|neural net'),
    ('LLMs / GenAI', 'Data & AI', r'\bllms?\b|large language model|generative ai|gen ?ai\b|gpt|prompt engineering'),
    ('RAG', 'Data & AI', r'\brag\b|retrieval.augmented'), ('NLP', 'Data & AI', r'\bnlp\b|natural language processing'),
    ('Computer vision', 'Data & AI', r'computer vision|opencv'), ('LangChain', 'Data & AI', r'langchain|llamaindex'),
    ('Hugging Face', 'Data & AI', r'hugging ?face'), ('Spark', 'Data & AI', r'\bspark\b|pyspark'), ('Hadoop', 'Data & AI', r'\bhadoop\b'),
    ('Airflow', 'Data & AI', r'\bairflow\b'), ('dbt', 'Data & AI', r'(?-i)\bdbt\b'), ('Kafka', 'Data & AI', r'\bkafka\b'),
    ('ETL / data pipelines', 'Data & AI', r'\betl\b|\belt\b|data pipeline'), ('Databricks', 'Data & AI', r'databricks'),
    ('Snowflake', 'Data & AI', r'snowflake'), ('Power BI', 'Data & AI', r'power ?bi\b'), ('Tableau', 'Data & AI', r'\btableau\b'),
    ('Looker', 'Data & AI', r'\blooker\b'), ('Excel', 'Data & AI', r'\bexcel\b'), ('Statistics', 'Data & AI', r'statistic'),
    ('A/B testing', 'Data & AI', r'a/b test'), ('Data visualization', 'Data & AI', r'data visuali[sz]ation'),
    # Databases
    ('PostgreSQL', 'Database', r'postgres'), ('MySQL', 'Database', r'\bmysql\b'), ('SQL Server', 'Database', r'sql server|\bmssql\b|t-sql'),
    ('Oracle', 'Database', r'\boracle\b'), ('MongoDB', 'Database', r'mongo'), ('Redis', 'Database', r'\bredis\b'),
    ('DynamoDB', 'Database', r'dynamodb'), ('Elasticsearch', 'Database', r'elastic ?search|opensearch|\belk\b'),
    ('NoSQL', 'Database', r'\bnosql\b'), ('Vector databases', 'Database', r'vector (database|db|store)|pinecone|pgvector|weaviate|milvus|faiss'),
    ('BigQuery', 'Database', r'bigquery'), ('Cassandra', 'Database', r'cassandra'), ('SQLite', 'Database', r'sqlite'),
    # Cloud and DevOps
    ('AWS', 'Cloud & DevOps', r'\baws\b|amazon web services|\bec2\b|\bs3\b|lambda'), ('Azure', 'Cloud & DevOps', r'\bazure\b'),
    ('Google Cloud', 'Cloud & DevOps', r'\bgcp\b|google cloud'), ('Docker', 'Cloud & DevOps', r'\bdocker\b|containeri[sz]'),
    ('Kubernetes', 'Cloud & DevOps', r'kubernetes|\bk8s\b|\beks\b|\baks\b|\bgke\b'), ('Terraform', 'Cloud & DevOps', r'terraform'),
    ('Ansible', 'Cloud & DevOps', r'\bansible\b'), ('CI/CD', 'Cloud & DevOps', r'ci ?/ ?cd|continuous (integration|delivery|deployment)'),
    ('GitHub Actions', 'Cloud & DevOps', r'github actions'), ('Jenkins', 'Cloud & DevOps', r'jenkins'), ('GitLab', 'Cloud & DevOps', r'gitlab'),
    ('Git', 'Cloud & DevOps', r'\bgit\b|github|bitbucket'), ('Linux', 'Cloud & DevOps', r'\blinux\b|\bunix\b|ubuntu|red ?hat|rhel'),
    ('Microservices', 'Cloud & DevOps', r'micro-?services'), ('Serverless', 'Cloud & DevOps', r'serverless'),
    ('Infrastructure as code', 'Cloud & DevOps', r'infrastructure as code|\biac\b|cloudformation'),
    ('Monitoring', 'Cloud & DevOps', r'prometheus|grafana|datadog|splunk|new relic|observability'),
    ('Nginx', 'Cloud & DevOps', r'\bnginx\b'), ('Networking (TCP/IP, DNS)', 'Cloud & DevOps', r'tcp/ip|\bdns\b|\bdhcp\b|\blan\b|\bwan\b|\bvpn\b|routing|switching'),
    # Security
    ('Cybersecurity', 'Security', r'cyber ?security|information security|infosec'), ('SIEM', 'Security', r'\bsiem\b|sentinel|qradar'),
    ('SOC', 'Security', r'\bsoc\b|security operations'), ('Incident response', 'Security', r'incident response|\bdfir\b'),
    ('Vulnerability management', 'Security', r'vulnerabilit|nessus|qualys|rapid7'), ('Penetration testing', 'Security', r'penetration test|pen ?test|burp|metasploit'),
    ('IAM', 'Security', r'\biam\b|identity and access|okta|active directory|\bentra\b|\bsso\b|\bmfa\b'),
    ('Firewalls', 'Security', r'firewall|palo alto|fortinet|fortigate'), ('EDR', 'Security', r'\bedr\b|crowdstrike|defender|sentinelone'),
    ('NIST / ISO 27001', 'Security', r'\bnist\b|iso ?27001|soc ?2\b|\bpci\b|cis controls'), ('Threat intelligence', 'Security', r'threat (intel|hunt)|mitre'),
    ('Cloud security', 'Security', r'cloud security'), ('Encryption / PKI', 'Security', r'encryption|\bpki\b|\btls\b|\bssl\b'),
    # IT support
    ('Windows', 'IT support', r'\bwindows\b'), ('macOS', 'IT support', r'mac ?os|\bos x\b|\bmac\b'), ('Microsoft 365', 'IT support', r'office ?365|microsoft 365|\bm365\b|\bo365\b|exchange|sharepoint|intune'),
    ('Ticketing (ServiceNow, Jira)', 'IT support', r'servicenow|zendesk|freshdesk|ticketing|jira service'),
    ('Help desk / troubleshooting', 'IT support', r'help ?desk|service desk|troubleshoot'), ('Hardware setup', 'IT support', r'hardware|printers?|imaging'),
    ('Google Workspace', 'IT support', r'google workspace|g ?suite'), ('VMware / virtualization', 'IT support', r'vmware|hyper-v|virtuali[sz]ation'),
    # Practices and tools
    ('Agile / Scrum', 'Practice', r'\bagile\b|\bscrum\b|kanban'), ('Jira', 'Practice', r'\bjira\b'), ('Testing (unit, automated)', 'Practice', r'unit test|automated test|test automation|\btdd\b'),
    ('Selenium / Cypress', 'Practice', r'selenium|cypress|playwright'), ('Jest / PyTest', 'Practice', r'\bjest\b|pytest|junit|mocha'),
    ('Data structures & algorithms', 'Practice', r'data structures|algorithms'), ('Object-oriented programming', 'Practice', r'object.oriented|\boop\b'),
    ('System design', 'Practice', r'system design|distributed systems|scalab'), ('Figma', 'Practice', r'\bfigma\b'),
    ('Mobile (iOS / Android)', 'Practice', r'\bios\b|\bandroid\b'), ('SDLC', 'Practice', r'\bsdlc\b|software development life ?cycle'),
    ('Postman', 'Practice', r'\bpostman\b'), ('Salesforce', 'Practice', r'salesforce'), ('SAP', 'Practice', r'(?-i)\bSAP\b'),
    ('Embedded systems', 'Practice', r'embedded|firmware|microcontroller|\brtos\b'), ('Blockchain', 'Practice', r'blockchain|web3|smart contract'),
    # Certifications
    ('AWS certification', 'Certification', r'aws certified|aws certification'), ('Azure certification', 'Certification', r'az-\d{3}|azure (certified|certification|fundamentals)'),
    ('CompTIA A+', 'Certification', r'a\+ certif|comptia a\+'), ('CompTIA Network+', 'Certification', r'network\+'),
    ('CompTIA Security+', 'Certification', r'security\+'), ('CCNA', 'Certification', r'\bccna\b'), ('CISSP', 'Certification', r'\bcissp\b'),
    ('ITIL', 'Certification', r'\bitil\b'), ('Google cert (Data / IT / Cyber)', 'Certification', r'google (data analytics|it support|cybersecurity) (certificate|professional)'),
]
COMPILED = []
for name, cat, pat in KEYWORDS:
    flags = 0 if pat.startswith('(?-i)') else re.I
    COMPILED.append((name, cat, re.compile(pat[5:] if pat.startswith('(?-i)') else pat, flags)))
CATEGORY = {name: cat for name, cat, _ in KEYWORDS}


def skills(text):
    """The technical keywords a job description mentions, in dictionary order."""
    text = text or ''
    return [name for name, _, rx in COMPILED if rx.search(text)]


def tally(jobs, state_path, csv_path, today=None, recent_days=30, keep_days=120):
    """Adds the jobs not counted yet (each link once) to the running tally and rewrites the CSV.
    state: {'seen': {link: 'YYYY-MM-DD'}, 'total': {kw: n}, 'jobs_total': n, 'daily': {date: {kw: n, '_jobs': n}}}"""
    today = today or datetime.utcnow().strftime('%Y-%m-%d')
    try:
        state = json.loads(state_path.read_text())
    except Exception:
        state = {}
    seen, total, daily = state.get('seen', {}), state.get('total', {}), state.get('daily', {})
    jobs_total, added = state.get('jobs_total', 0), 0
    for j in jobs:
        if not j.get('link') or j['link'] in seen or 'skills' not in j:
            continue
        seen[j['link']] = today
        jobs_total += 1
        added += 1
        day = daily.setdefault(today, {'_jobs': 0})
        day['_jobs'] += 1
        for kw in j['skills']:
            total[kw] = total.get(kw, 0) + 1
            day[kw] = day.get(kw, 0) + 1
    old = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=keep_days)).strftime('%Y-%m-%d')
    seen = {k: v for k, v in seen.items() if v >= old}  # links leave the feed long before this
    cut = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=recent_days)).strftime('%Y-%m-%d')
    week = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
    daily = {d: v for d, v in daily.items() if d >= old}
    recent, last7, recent_jobs = {}, {}, 0
    for d, v in daily.items():
        if d < cut:
            continue
        recent_jobs += v.get('_jobs', 0)
        for k, n in v.items():
            if k != '_jobs':
                recent[k] = recent.get(k, 0) + n
                if d >= week:
                    last7[k] = last7.get(k, 0) + n
    state_path.write_text(json.dumps({'seen': seen, 'total': total, 'jobs_total': jobs_total, 'daily': daily}, separators=(',', ':')))
    rows = sorted(total, key=lambda k: (-recent.get(k, 0), -total[k], k))
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(['Rank', 'Keyword', 'Category', f'% of postings (last {recent_days} days)', f'Postings (last {recent_days} days)',
                'Postings (last 7 days)', 'Postings (all time)', 'Updated'])
    for i, k in enumerate(rows, 1):
        share = f'{100 * recent.get(k, 0) / recent_jobs:.0f}%' if recent_jobs else ''
        w.writerow([i, k, CATEGORY.get(k, ''), share, recent.get(k, 0), last7.get(k, 0), total[k], today])
    w.writerow([])
    w.writerow(['', f'Based on {recent_jobs} postings in the last {recent_days} days ({jobs_total} all time)'])
    csv_path.write_text(out.getvalue())
    return added
