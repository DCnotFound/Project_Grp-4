# Turning the HDB project into a masters-level piece — what to change and why

## What's already strong (keep it, and say it explicitly in the deck)
- A real 3-schema Postgres design (`staging` → `core` → `analytics`), FK-normalized
  dimension tables (`town`, `flat_type`, `flat_model`), CHECK constraints, and an
  analytics view (`resale_enriched`) that the analysis code is required to query
  through — not read CSVs directly. That's a legitimate database-systems deliverable
  and a DBS-bank / PhD reviewer will recognize it as such. Don't let the deck bury it.

## What reads as undergraduate-level right now
The current `analysis.py` and the PPT are six independent `GROUP BY` queries, each
turned into one chart, each followed by a bullet list called **"Possible contributing
factors"** that admits — every single time — that town, flat type, floor area,
remaining lease, storey and building age are all entangled and the chart in front of
you can't separate them. That admission, repeated six times, is the tell: the project
is naming the confounding problem but never solving it. A masters-level version
solves it.

## The fix: one hedonic (multiple regression) model, run on your real data
I loaded your actual `hdb_resale.csv` + `hdb_property.csv` (240,807 transactions,
Jan 2017–Sep 2026, 26 towns, 99.999% address-matched) and fit the model your write-up
is implicitly asking for:

```
log(resale_price) ~ town + flat_type + floor_area_sqm + storey_midpoint
                    + remaining_lease_years + building_age_at_sale + year
```

**Naive (town only, i.e. what slide 10 currently shows): R² = 0.083**
**Full hedonic (controls added): R² = 0.907**

That jump is a slide by itself: town alone explains 8% of price variation;
once you control for what's actually *in* each town's transaction mix, the model
explains 91%. Most of what looked like geography in the bar chart is really
flat size, flat type, storey and vintage riding along with location.

### Town premium: naive vs. controlled (top 5, % vs baseline town)
| Town | Naive | Controlled |
|---|---|---|
| Bukit Timah | +66.2% | +34.6% |
| Bishan | +52.0% | +17.3% |
| Central Area | +40.7% | +30.4% |
| Bukit Merah | +31.5% | — |
| Queenstown | +31.3% | +17.1% |
| Marine Parade | — | +27.9% |

Central Area and Bukit Timah keep a real, large premium even after controlling for
everything else — that's a genuine location effect. Bishan and Queenstown's premiums
roughly halve — much of their apparent "expensiveness" is that they sell bigger,
higher-floor, newer-lease flats, not that the location itself commands as much as the
raw chart implies. That's a materially different, more defensible claim than slide 10's
"location is strongly associated with value."

### Controlled marginal effects (holding everything else fixed)
| Characteristic | Effect on price | p-value |
|---|---|---|
| +1 sqm floor area | +0.85% | <0.001 |
| +1 storey | +0.79% | <0.001 |
| +1 year remaining lease | +0.58% | <0.001 |
| +1 year building age | **−0.45%** | <0.001 |

The building-age result is the one that resolves your own slide 14 anomaly. Slide 14
shows some of the *oldest* buildings with high price/sqm and hand-waves it as a
"small-sample issue" possibly mixed with market-year timing. The controlled model
settles it: once transaction year is held fixed, building age has a clean,
monotonic, highly significant **negative** relationship with price. The naive chart's
"older = sometimes pricier" pattern is a market-year confound, exactly as your slide
already speculates — now proven rather than speculated.

## A quality-adjusted price index (upgrades slide 9)
Using the year fixed-effects from the same model, holding flat mix constant:

| Year | Quality-adjusted index | Raw median index (your current slide 9) |
|---|---|---|
| 2017 | 100.0 | 100.0 |
| 2019 | 98.6 | 97.6 |
| 2021 | 113.7 | 117.8 |
| 2023 | 135.7 | 134.1 |
| 2025 | 156.7 | 153.2 |
| 2026 (partial) | 157.1 | 153.7 |

The two track closely but not identically — in the 2020–2021 boom the raw median rose
faster than the quality-adjusted index, meaning part of that jump was buyers shifting
toward larger/better flats, not pure price appreciation. That's a genuinely more
careful answer to "how much did prices really rise" than a single median line.

## A second, genuinely new finding: the storey premium isn't one number
Rather than one citywide "higher floor = higher price" chart, I ran the storey→price
regression *per town* (Postgres has built-in `regr_slope`/`regr_r2` aggregates — this
is a real database-systems technique, not just a pandas trick):

- Clementi, Geylang, Ang Mo Kio, Central Area, Toa Payoh: **~150–161 SGD/sqm per storey**
- Sengkang, Sembawang: **~15–32 SGD/sqm per storey**

Older, more central towns show a 5–10x steeper storey premium than newer estate towns.
This is an interaction effect your single aggregate chart (slide 13) completely hides,
and it's an easy, visual second finding (small multiples or a sorted bar of slopes).

## What this changes about the deck (concrete, not just "do more stats")
1. Replace the six "Possible contributing factors" bullet lists — which are honest
   but ultimately just guesses — with the one regression table above, referenced from
   each relevant slide ("see hedonic model, slide X").
2. Add one slide: naive vs. controlled model, R² jump, and the "the town effect
   shrinks by up to half" finding. This is your single best slide.
3. Replace or supplement the raw median trend line with the quality-adjusted index.
4. Add the per-town storey-slope finding as a second genuinely new result.
5. Turn the building-age "small-sample issue" hand-wave into the resolved,
   statistically clean answer above.
6. On the database side: mention the materialized view + index you add for the
   model's feature set (`03_advanced_analysis.sql`), and cite an `EXPLAIN ANALYZE`
   before/after — a DB-systems grader will want to see a performance argument, not
   just a correctness one.

## Files
- `03_advanced_analysis.sql` — window functions (YoY growth via `LAG`, moving
  average), `ROLLUP` multi-dimensional summary, per-town `regr_slope`/`regr_r2`,
  a formalised small-sample flag replacing the "small-sample issue" hand-wave, and
  the materialized view + index for the model's feature set.
- `hedonic_regression_analysis.py` — drop-in replacement/addition to
  `src/analysis/analysis.py`, using your existing `dbconnection.py` and
  `analytics.resale_enriched` (via the new materialized view). Fits both models,
  prints the naive-vs-controlled comparison, and builds the quality-adjusted index.

## Before you run it
`hedonic_regression_analysis.py` queries `analytics.resale_model_features`, so run
`03_advanced_analysis.sql` against your Postgres instance first (it only *adds* a
materialized view + index — it doesn't touch `core` or the existing `resale_enriched`
view). You'll also need `pip install statsmodels` alongside your existing
`requirements.txt`.

All numbers above were computed by me directly on your actual `hdb_resale.csv` /
`hdb_property.csv` (via DuckDB, replicating your `core.resale_transaction` join
logic) so they should match closely once you re-run against your live Postgres
instance — treat them as a preview, not a substitute for re-running the SQL/Python
yourselves for the submission.
