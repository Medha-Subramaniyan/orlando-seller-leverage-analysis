# Decision Log / Field Notes

## On defining core metrics

### Price cut share: use realtor.com's `price_reduced_share` (not my own ratio)

- tested `price_reduced_count ÷ active_listing_count`: matches `price_reduced_share` in only **0.7%** of orlando rows. `÷ total_listing_count` doesn't match either
- `total_listing_count` ≈ active + pending (median diff 0, range −13 to +10, probably rounding)
- the gap between the two versions tracks turnover (`new_listing_count ÷ active_listing_count`): correlation **−0.84**. share ÷ my ratio was 0.26 in 2021 (turnover 1.16) vs. 0.59 in 2025 (turnover 0.33)
- **my read:** realtor.com probably divides by every listing active at any point in the month, not a typical day's count. that's inferred from the data, not documented. their docs only call it a share of active listings
- my own ratio is the one that mixes time frames (a month of price cuts ÷ a typical day's listings). it's most distorted in fast markets, so it would inflate the 2022 baseline and shrink H1's rise
- **dashboard wording:** "price cuts relative to listings on the market", not literally "% of listings that cut"
- price cut shares from different sources (redfin, zillow) are defined differently, so compare direction, not levels
- never mix this download with a realtor.com file downloaded before oct 2022 (methodology change)

### Baseline: Jun–Aug 2021 vs. Jun–Aug 2026 (primary), Mar–May 2022 vs. Mar–May 2026 (robustness)

- all 5 tier 1 metrics were at their best for sellers between jan and jul 2022 (metro median, 3-month windows)
- **primary: Jun–Aug 2021 → Jun–Aug 2026.** a 5-year analysis that ends with the latest data. jun–aug 2021 was still a hot market (price cut share 0.085, months of supply 1.05, sale-to-list ~100%) and has **0%** flagged rows
- **robustness: Mar–May 2022 → Mar–May 2026.** measures distance from the exact peak, same season. `quality_flag` 25% / 5%
  - if a zip's conclusion flips between the two, report it, don't hide it
- (first decided the other way round: mar–may 2022 primary. switched to make this a 5-year analysis; see the methodology checklist in the notebook)
- **context: Jun–Aug 2019** as the pre-pandemic reference, same season as the primary windows. not a hypothesis baseline
- **rejected: Jun–Aug 2022.** it was mid-turn: price cut share (0.188) and months of supply (2.2) were already back at 2019 levels while DOM and sale-to-list still looked hot. 45% flagged
- **rejected: 2023.** just after the rate shock, not a clear reference point. 55% flagged in mar–may
- seasonality is large (2016–19: jun–aug price cut share ~15% above the yearly avg, redfin DOM ~23% below), so always compare the same calendar months
- **todo:** update the research question (says "since 2023") and hypotheses (say "since 2022") to name these windows

| Window (metro median) | Price cut share | RDC DOM | Months of supply | Redfin DOM | Sale-to-list | `quality_flag` |
|---|---|---|---|---|---|---|
| Jun–Aug 2021 | 0.085 | 33 | 1.05 | 9.5 | 100.0% | 0% |
| Mar–May 2022 | 0.062 | 30 | 1.20 | 7 | 101.1% | 25% |
| Jun–Aug 2022 | 0.188 | 31 | 2.20 | 10 | 99.6% | 45% |
| Mar–May 2026 | 0.200 | 61 | 3.70 | 42.5 | 97.5% | 5% |
| Jun–Aug 2026 | 0.220 | 67.5 | 4.35 | 46 | 97.6% | 10% |

### Leverage score: average within each dimension, then across dimensions (option 1)

| Metric | Source | Dimension | More seller leverage → | Noise |
|---|---|---|---|---|
| `price_reduced_share` | realtor.com | price leverage | ↓ | 0.35 |
| `AVERAGE SALE TO LIST RATIO (%)` | redfin | price leverage | ↑ | 0.39 |
| `median_days_on_market` | realtor.com | speed | ↓ | 0.37 |
| `MEDIAN DAYS ON MARKET (DAYS)` | redfin | speed | ↓ | 0.44 |
| `MONTHS OF SUPPLY` | redfin | supply | ↓ | 0.32 |

- score = average of 3 dimensions (supply, speed, price leverage), each weighted ⅓. within a dimension, average its metrics
- each metric is standardized against a fixed reference period and flipped so that higher = more seller leverage
- **why:** all 5 move as expected at the 2022 peak. but the two DOMs correlate 0.79, and months of supply tracks both (0.69–0.75). averaging all 5 equally would give speed 40% and one underlying signal ~60%. averaging by dimension gives each part of my definition the same weight
- price cut share overlaps least with the others (0.43–0.56), so it adds the most independent information
- **robustness check:** option 2 (4 inputs, drop redfin DOM, equal weights)
- **H1 is tested on its raw metrics** (price cut share and DOM), not the score, since the score contains them. the score is for H2 and H3
- price trend ($/sq ft) isn't in the score. that's a deliberate scope choice: it's context for talking points
- noise = per-zip sd(month-to-month change) ÷ sd(level), median across zips. higher = noisier

### Leverage score: how it's built

- **flip:** months of supply, both DOMs and price cut share are multiplied by −1 (higher = worse for sellers). sale-to-list is **not** flipped (higher already = better for sellers). (the earlier plan said "flip sale-to-list", which only works if higher score = *less* leverage; we use higher = more)
- **reference:** every zip × window labeled 2021-08 through 2026-08 (jun–aug 2021 to jun–aug 2026) = 20 zips × 61 windows = 1,220 rows. the same fixed mean/SD are applied to every window, including 2019

| Input | Reference mean | Reference SD |
|---|---|---|
| months of supply | 3.10 | 1.75 |
| realtor.com DOM | 53.7 | 16.6 |
| redfin DOM | 30.7 | 17.9 |
| price cut share (%) | 18.5 | 6.98 |
| sale-to-list (%) | 98.03 | 1.53 |

- 0 = the average zip-window in the study period; +1 = 1 SD more seller leverage
- **checks:** every flipped input correlates positively with the score (0.64–0.89). main score and option 2 correlate 0.98. metro median score: mar–may 2022 1.41, jun–aug 2021 1.24, jun–aug 2019 0.17, mar–may 2026 −0.40, jun–aug 2026 −0.65
- outputs: `data/processed/orlando_scores_monthly.csv`, `data/processed/orlando_scores_windows.csv`

## On building the joined data

- **realtor.com 3-month averages:** each month M = average of M−2, M−1, M for the same zip, labeled M (same span as the redfin window labeled M). windows with fewer than 3 months are left empty, so each zip's first 2 months (jul, aug 2016) are blank
  - checked: matches pandas `rolling(3)`, and a hand average (34786, jun–aug 2021)
  - averaging 3 monthly medians/shares only approximates a true 3-month median/share (limitation)
- **join:** zip + `date`, outer join first. each of the 20 zips: 120 `both`, 2 `left_only` (jul/aug 2016, no redfin window), 0 `right_only`. no mismatches inside jun 2021–aug 2026
  - **kept only `both` rows** → 2,400 rows = 20 zips × 120 windows (sep 2016–aug 2026)
- **months of supply check:** `INVENTORY ÷ (HOMES SOLD ÷ 3)` vs. redfin's column. **verified, with a small consistent gap**: 89% within ±0.1 (rounding), 100% within ±0.5, max 0.25. my version runs slightly lower (median −0.04), probably because redfin measures inventory or sales slightly differently. consistent, so it doesn't affect changes. use redfin's own column for labels
- **counts:** `rdc_new_listings_mo_avg` is a monthly average. redfin `NEW LISTINGS` / `HOMES SOLD` are 3-month totals (~3× larger). compare direction across sources, not levels
- **scale: everything in percent.** realtor.com price cut share ×100 to match redfin's % columns, the label benchmarks (99% / 95%), and client wording. `rdc_pending_ratio` stays a ratio (can exceed 1)
- **names:** `rdc_` = realtor.com 3-month average, `rf_` = redfin 3-month window
- **outputs:** `data/processed/orlando_panel_monthly.csv` (all zip × windows) and `data/processed/orlando_panel_windows.csv` (the 5 comparison windows, 20 rows each, no tier 1 nulls). reload with `dtype={'zip': str}` and convert `date` back to a monthly period

## On sub-data frames from the realtor.com data

- originally wanted to filter down to florida, central fl, and orlando so I could do different levels of comparison - this resulted in 6 dataframes! 3 for the current(ish) month of august and 3 for historical 
  - **I beleive the august data is folded into the historical but i need to check. If it is that would mean i can discard the "august" data and just excise it from the historical data**

## On Realtor.com data richness

- doesnt have some of the heavy hitting metrics that are necessary to say "buyer-favored", "seller favored" or "balanced" as its just inventory data 
- bringin in redfin housing market tracker daya 
  - note this is also rolling data not monthly data



## On how to work w Redfin data

- its still 111406 rows when filtered down to florida data!!
- .isna() was returning 0's becuase the nulls are "NA" strings , not NaN
  - `redfin = redfin.replace('NA', pd.NA)`



### Decisions still open

- [x] baseline: jun–aug 2021 primary, mar–may 2022 robustness (see "On defining core metrics")
- the remaining items below are decided in the notebook's "Methodology Decision Checklist" cell
- [x] price cut share definition: realtor.com's `price_reduced_share`
- [ ] definition of seller leverage (step 1)
- [x] leverage score method: average within dimensions, then across (option 1)
- [ ] reference period for standardizing the score (e.g. the baseline window's metro distribution)
- [ ] mar–may 2019 as a "normal market" reference for talking points? (suggested, not decided)
- [ ] numeric threshold for "more/less than metro average" (step 7)
- [ ] keep label / confidence / outlook as a separate realtor-facing output, or drop it?



## Where I left off

- **brought in redfin data - need to clean and explore it before using it to calcualte any core metrics**



## Questions

- why are some like median_listing_price_yy or median_listing_price_mm tiny decimals? 
- is the august data folded in to the historical data?
- should i separate the redfin df into sub dfs (central fl, orl) or just excise the geographic data as necessary?

