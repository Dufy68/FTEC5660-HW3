# FTEC5660 Homework 3: Fisher's 15-Point Investment Agent

Build a LangChain agent that researches a company with tools and applies the
framework from Philip Fisher's *Common Stocks and Uncommon Profits* (Part One,
Chapter 3 "What to buy: the fifteen points to look for in a common stock", and
Chapter 4 "What to buy: applying this to your own needs"). You choose 3 of
Fisher's 15 points and decide yourself what PASS means for each. For every
company your agent gives a PASS/FAIL verdict on your 3 points and a short
summary.

The companies are fictional, so the model cannot answer from memory. Unlike a
pile of reports, the evidence is spread over three sources, and your agent has
to go and get it with tools, the way Fisher's "scuttlebutt" method sends an
investor to talk to customers, competitors, suppliers and staff.

## Data and tools

`public_test/` has one folder per company. Your code receives four tools per
company (built by the provided code in `hw3.py`):

| Tool | What it gives you |
| --- | --- |
| `list_documents()` | the company's six documents and their dates |
| `read_document(name)` | one document: the 2025 letter to shareholders, four earnings calls (Q3 2025 to Q2 2026) and a news file (July 2025 to July 2026) |
| `sql_query(query)` | one read-only SQLite query on the company's database; at most 50 rows come back, so use `SUM`, `GROUP BY` and `WHERE` |
| `interview(role, topic)` | what one person says about the company; at most **10 interviews per company** |

The documents are what management says. Management's own claims (such as "we
have never cut research" or "our people are our greatest strength") are not
evidence on their own: check them against the database and the interviews.

**Database tables** (amounts in USD thousands; dates `YYYY-MM-DD`, months
`YYYY-MM`, quarters like `2025Q3`; the fiscal year is the calendar year):

| Table | Columns |
| --- | --- |
| `company` | name, industry |
| `industry_medians` | industry, revenue_growth_2y_pct, new_product_share_pct, new_product_sales_per_rd, operating_margin_pct (one row per industry; use the row for the company's own industry) |
| `orders` | order_id, order_date, product, customer, amount, note (about 3,000 to 4,000 orders from January 2023 to June 2026; revenue is the sum of order amounts) |
| `products` | product, launch_date |
| `monthly_costs` | month, cost_of_sales, selling_admin, research_development |
| `quarterly_cash` | quarter, operating_cash_flow, capex, cash_end |
| `capex_plan` | year, planned_capex (2026 to 2028) |
| `returns` | month, units_shipped, units_returned |
| `insider_trades` | trade_date, person, title, side (`buy` or `sell`), shares, price |

**Terms used in the data.**

| Term | Meaning |
| --- | --- |
| FY2025 | Fiscal year 2025. Here the fiscal year is the calendar year, so FY2025 is January to December 2025. |
| Quarter | Three months of the year: Q1 is January to March, Q2 April to June, Q3 July to September and Q4 October to December. The database writes `2025Q3`; the documents write "third quarter 2025". |
| Amounts | The database is in **USD thousands** (676,100 means US$676.1 million). The documents use USD millions. |
| Revenue | Money from sales: the sum of `amount` in `orders`. |
| Cost of sales | The cost of making the products that were sold. |
| Selling and admin | The cost of selling and of running the company (sales staff, offices, management). |
| R&D | Research and development spending, mainly on new products. |
| Operating margin | Operating profit as a share of revenue: (revenue − cost of sales − selling and admin − R&D) ÷ revenue. |
| Operating cash flow | Cash that the day-to-day business brings in during a quarter. |
| Cash at the end of a quarter | The cash the company holds on the last day of that quarter (`cash_end`). |
| Capex | Capital expenditure: spending on factories, machines and other long-term assets. `capex_plan` holds the planned capex for 2026 to 2028. |
| Return rate | Units returned ÷ units shipped, from the `returns` table. |
| Industry median | The middle value for companies in the same industry, from `industry_medians`. |
| Insider | A director or senior manager of the company. `insider_trades` lists the shares they bought (`buy`) or sold (`sell`). |
| Earnings call | A meeting each quarter where management presents the quarter's results to investors. Each call quotes that quarter's revenue. |

**Interviews.** Roles: `customer`, `current_employee`, `former_employee`,
`competitor`, `supplier`. Topics: `sales_team`, `working_conditions`,
`top_management`, `decision_making`, `competitive_edge`. Only some people know
about each topic; the others say they can't comment, and that answer still
uses up one interview.

| Topic | Who knows about it |
| --- | --- |
| `sales_team` | customer, competitor |
| `working_conditions` | current_employee, former_employee |
| `top_management` | former_employee, supplier |
| `decision_making` | supplier, customer |
| `competitive_edge` | competitor, customer |

People who know about a topic always agree with each other, so one good answer
is enough.

## Choose your 3 points and your rules

Pick any 3 of Fisher's 15 points and write them in `CHOSEN_POINTS` near the
top of `hw3.py`, e.g. `CHOSEN_POINTS = [1, 7, 15]`. The full questions are in
`FISHER_POINTS` in `hw3.py` and in the book.

| # | Fisher's point | Where the evidence is |
| --- | --- | --- |
| 1 | Market potential for sales growth | database |
| 2 | New products as current lines mature | database |
| 3 | Effective research and development | database |
| 4 | Above-average sales organization | interviews (`sales_team`) |
| 5 | Worthwhile profit margin | database |
| 6 | Maintaining or improving margins | database |
| 7 | Labour and personnel relations | interviews (`working_conditions`) |
| 8 | Executive relations | interviews (`top_management`) |
| 9 | Depth of management | interviews (`decision_making`) |
| 10 | Cost analysis and accounting controls | earnings calls, checked against the database |
| 11 | Advantage over competitors | interviews (`competitive_edge`) |
| 12 | Long-range outlook on profits | database |
| 13 | Growth without dilutive equity financing | database |
| 14 | Management talks freely about troubles | earnings calls, checked against the database |
| 15 | Management of unquestionable integrity | news file, checked against the database |

For each of your points, **you design the rule**: which evidence to use, what
to compute or whom to ask, and where the line between PASS and FAIL lies. PASS
means the company looks favourable on that point, as Fisher would see it.

We grade your verdicts against our own answer key. It uses one fixed rule per
point, which we do not publish, and the data never puts a company close to
the line of that rule, so a sensible reading of Fisher usually gives the same
answer. **Test your rules on the public answers**:
`public_test/ground_truth.json` gives the expected verdict on all 15 points
for each of the 20 public companies, and every point fails in 6 of them. If
your rule disagrees with the public answers, rethink it.

**Tip: calculate with tools, not in your head.** Do every sum, ratio and
comparison in SQL or Python, including the number of days between two dates
(SQLite's `julianday()` gives a date as a number of days).

## Student task

Fill in the three places in `hw3.py` marked `### YOUR CODE HERE`. You may add
imports, constants and helper functions above them, but do not change the
provided code below them:

- `CHOSEN_POINTS` lists your 3 points.
- `build_agent()` creates your model and anything else you need once.
- `analyze_companies(agent, companies)` receives
  `{company_folder: [list_documents, read_document, sql_query, interview]}`
  and returns, for every company,
  `{"points": {1: "PASS", 7: "FAIL", 15: "PASS"}, "summary": "..."}` (here with
  `CHOSEN_POINTS = [1, 7, 15]`).

Use the course techniques that fit your points: tool use for the database and
the interviews, planning which interviews to spend, routing each point to the
right source, prompt chaining, parallel calls, reflection to check your
answers, or a combination. Your code must read company data **only through
the four tools**; do not open `company.db` or `interviews.dat` yourself. Do
not hard-code folder names, company names or the public answers.

## Setup and public test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "DEEPSEEK_API_KEY=your_key_here" > .env
python3 hw3.py --data-folder public_test
```

Use your own DeepSeek API key (from https://platform.deepseek.com). The
required model is `deepseek-v4-flash`. We grade with our own key, so never put
a key in your code; `.env` must stay out of git.

The program creates `results.csv` with the columns `company`, `points`,
`points_correct`, `point_errors`, `interviews_used` and `summary`, and prints
the point score on your 3 points (the percentage after "balanced"). The point
score is the average of two shares: the share of truly passing verdicts that
you marked PASS and the share of truly failing verdicts that you marked FAIL.
For example, 90% and 60% give (90% + 60%) / 2 = 75%, and marking every point
PASS gives (100% + 0%) / 2 = 50%. Once `CHOSEN_POINTS` is set, the starter
runs before you add any API code (it returns no verdicts, so it scores 0%).

`public_test/ground_truth.json` gives the expected verdicts on all 15 points
for each public company. Grading uses a private set of about 20 unseen
companies with the same tools and the same answer key rules, but different
names and wording, and scores your 3 points only.

## Homework 3 solution

### My 3 points and rules

This implementation chooses points 4, 7 and 11. They cover customer-facing
execution, employee relations and competitive durability. Each has a directly
relevant interview source in the supplied tools. Fisher's questions below are
reproduced from `FISHER_POINTS` in the starter code (Part One, Chapter 3).

| Point | Why this point | PASS rule | Evidence |
| --- | --- | --- | --- |
| 4: sales organization | Sales quality determines whether a company can turn product potential into customer relationships. Fisher asks whether the company has an “above-average sales organization.” | PASS when the interview describes knowledgeable, proactive, consultative salespeople who understand customers and provide useful advice or support. FAIL for order-taking, price lists without advice, poor product knowledge or weak follow-up. | `interview(customer, sales_team)` |
| 7: labour and personnel relations | Employee treatment affects retention and the ability to execute consistently. Fisher asks about “outstanding labor and personnel relations.” | PASS when the interview describes fair treatment, constructive communication, training, safety or retention consistent with strong personnel relations. FAIL for intimidation, unsafe or unfair conditions, ignored concerns, excessive turnover or destructive labour relations. | `interview(current_employee, working_conditions)` |
| 11: competitive advantage | A profitable product is more valuable when rivals cannot easily replicate its advantage. | PASS for a concrete defensible advantage, such as proprietary technology, qualification barriers, embedded workflows, switching costs, exclusive access, network effects or difficult-to-copy expertise. FAIL for interchangeable products, easy copying, no durable differentiation or competition mainly on price. | `interview(competitor, competitive_edge)` |

The rules assess the full interview, including contrary evidence. They do not
require every listed positive example, and they do not use isolated sentiment
words. The homework states that knowledgeable interviewees agree, so one
informed source per point is sufficient for this dataset. This would be a weak
basis for an actual investment decision, where independent corroboration and
financial analysis would also be needed.

### Design

```mermaid
flowchart TD
    A[Company and supplied LangChain tools] --> B[Fixed interview plan]
    B --> C[Point 4: customer / sales_team]
    B --> D[Point 7: current_employee / working_conditions]
    B --> E[Point 11: competitor / competitive_edge]
    C --> F[Collected interview evidence]
    D --> F
    E --> F
    F --> G[LangChain prompt and deepseek-v4-flash in JSON mode]
    G --> H{Validate coverage, verdicts and exact quotes}
    H -->|Valid| I[Three verdicts and evidence-based summary]
    H -->|Invalid or API error| J{Attempts remaining?}
    J -->|Yes: reuse evidence| G
    J -->|No| K[Diagnostic entry with missing verdicts]
    I --> L[Unchanged runner writes results.csv]
    K --> L
```

The agent uses a fixed plan to route each point to a knowledgeable interviewee,
then calls the three interview tools once per company. A LangChain prompt/model/
JSON-parser chain applies the written rules using only those responses. Python
checks that the output covers each selected point exactly once, contains valid
PASS/FAIL verdicts, includes reasons and quotes the correct interview verbatim.
A failed response triggers up to two further model attempts without repeating
interviews. The summary is assembled from the validated verdicts, reasons and
quotes. Up to four companies run concurrently; individual company failures
produce diagnostic entries so the runner can still write its CSV. The model
has temperature zero, a 60-second request timeout, no implicit provider retries,
and a 90-second outer timeout per attempt. Interview text is explicitly treated
as evidence rather than instructions. Quote validation confirms provenance;
it does not independently prove that the model's interpretation is correct.

Only the supplied `interview` tool is needed for these chosen points. Company
database files, interview files and public answers are never read by the
student agent. No management claims or web search enter its company analysis.
The supplied tools, runner and scoring code are unchanged.

### Results

The first live public-test run on 10 November 2026 used `deepseek-v4-flash` and
returned all 60 requested verdicts correctly across 20 companies:

| Measure | Result |
| --- | --- |
| Point accuracy | 60 / 60 (100%) |
| Balanced point score | 100% |
| Correct PASS verdicts | 42 / 42 |
| Correct FAIL verdicts | 18 / 18 |
| Interviews per company | 3 |
| Disagreements with public answers | None |

A second live run from a fresh checkout, using the same installed Python
environment, also scored 60/60 with 100% balanced accuracy. The complete
per-company outputs are saved in `evaluation/public_run1.csv` and
`evaluation/public_run2.csv`.
No company-specific exceptions or public-label lookups were added. Public
accuracy does not establish performance on the unseen grading set, and
model outputs can vary even at temperature zero.

Four offline checks cover wrong-source quotes and duplicate points, retries
without spending additional interviews, isolation of a failed company, and
exhaustion of API retries. Run them from the repository root with:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

To reproduce the live evaluation, use Python 3.10 or newer and follow the setup
above, then run:

```bash
python hw3.py --data-folder public_test
```

Use the virtual environment's Python: some systems still map `python3` to an
older version. Keep `DEEPSEEK_API_KEY` in the ignored `.env` file or the process
environment. Missing credentials or exhausted retries produce missing verdicts
and diagnostic summaries, which count as incorrect; they are not replaced by
invented PASS/FAIL decisions.

Implementation references: [LangChain DeepSeek JSON-mode interface](https://reference.langchain.com/python/langchain-deepseek/chat_models/ChatDeepSeek/with_structured_output)
and [DeepSeek JSON output guide](https://api-docs.deepseek.com/guides/json_mode/).

## Task 2: Reflection

See [the reflection on AI sycophancy and AI psychosis](reflection.md), focusing
on evidence and independent judgment in FinTech agents.
