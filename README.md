# Who Has the Leverage? Orlando Home Sellers, Zip by Zip

A five-year analysis (2021 → 2026) of how much negotiating power home sellers have kept or lost across 20 Orlando-area zip codes, turned into a Tableau dashboard a realtor can open in a listing appointment.

**Dashboard:** [Seller's Market or Not? Orlando Housing Leverage by Zip Code](https://public.tableau.com/views/SellersMarketorNotOrlandoHousingLeveragebyZipCode/Dashboard1) (Tableau Public)
**Data:** Realtor.com inventory metrics + Redfin housing market data, by zip, 2016–2026

[![Dashboard preview: click to open the interactive version on Tableau Public](https://public.tableau.com/static/images/Se/SellersMarketorNotOrlandoHousingLeveragebyZipCode/Dashboard1/1.png)](https://public.tableau.com/views/SellersMarketorNotOrlandoHousingLeveragebyZipCode/Dashboard1)

_Click the image to open the interactive dashboard: pick a zip from the dropdown or click the map._

---



## Why I built this

My mentor, Jeanine A, is also a realtor gets the same questions every week:

- **Sellers:** *"What's my home worth, and how long will it take to sell?"*
- **Buyers:** *"Do I have room to negotiate?"*

The honest answer depends on the zip code, and the market around Orlando has changed a lot since the 2021–22 frenzy. National headlines don't help much when someone is standing in Winter Garden or Apopka. I wanted to give her a **data-backed, zip-level answer** she could use to:

- price sellers correctly in listing appointments,
- set expectations and negotiation strategy for buyers,
- decide which zips to prospect in, and
- feed her market-update content.

That became the research question:

> **Where in Orlando have sellers lost leverage since 2021, and where do they still have it?**



## What I learned

I kept a running [decision log](decision_log.md) through the project. These are the lessons that changed the analysis, not just the code:

1. **Define the metric from the question, not the other way round.** My first metric framework was a generic "seller's / balanced / buyer's market" label. It looked complete but couldn't test my hypotheses, which are all about *change compared with the metro*. I rebuilt it from a plain-language definition of seller leverage (competition, speed, price concessions), mapped each part to a column, and only then decided how to combine them.
2. **Check what a column actually measures.** Realtor.com's `price_reduced_share` is *not* price-reduced listings ÷ active listings: that formula matched in only 0.7% of rows. The gap tracked how fast listings turned over (correlation −0.84), which suggests a different denominator. Using my own ratio would have inflated the 2021–22 baseline and hidden part of the rise in price cuts.
3. **The baseline is a decision, and it can change the answer.** Mid-2022 looked like the obvious "peak" to compare against, but by Jun–Aug 2022 price cuts were already back to 2019 levels while days on market still looked hot: the market was mid-turn. Seasonality is large too (summer price cuts run about 15% above the yearly average), so I only ever compare the same calendar months: **Jun–Aug 2021 → Jun–Aug 2026**, with **Mar–May 2022 → Mar–May 2026** as a robustness check.
4. **Correlated metrics quietly over-weight a score.** The two days-on-market measures correlate 0.79, and months of supply tracks both. Averaging all five inputs equally would have made one underlying signal about 60% of the score. Averaging within each dimension first, then across dimensions, gives supply, speed and price leverage equal say.
5. **Decide what "different" means before looking.** A zip can drift several points from the metro just from normal variation. I measured that drift in a quiet pre-pandemic period (2017 → 2019) and wrote the thresholds down before calculating results, so the results couldn't move the goalposts.
6. **One data source wasn't enough.** Realtor.com only covers listings, so it can't say whether a market favors sellers: that needs sales (months of supply, sale-to-list ratio). Adding Redfin meant handling its rolling 3-month windows, which I matched by averaging Realtor.com over the same three months.
7. **Small data traps add up.** Redfin stores missing values as the text `"NA"`, so pandas reported zero nulls until I converted them. A zip with a blank name was silently dropped by my Florida filter (it turned out to be a PO-box zip I'd have excluded anyway, but I only found out by tracing it).



## Hypotheses

Written before the analysis, each with a rejection rule:


|        | Hypothesis                                                                                                                                                                                                              | Rejected if                                               |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| **H1** | **New construction hurt resale sellers most.** In 34787 (Winter Garden) and 32712 (Apopka), price cut share and days on market rose more than the metro, because builder incentives pull buyers away from resale homes. | Both zips' increases are at or below the metro's          |
| **H2** | **Windermere held up.** 34786's leverage score dropped less than the metro's, thanks to scarce lakefront and large-lot homes and less rate-sensitive buyers.                                                            | 34786's drop is at or above the metro's                   |
| **H3** | **Affordable zips held up better.** 34761 (Ocoee) and 32703 (Apopka) lost less leverage than the growth zips 34787 and 32712, because they face less new-construction competition.                                      | Their drop is the same as or larger than the growth zips' |




## Data


| Source                                                                                               | What it adds                                                                                        | Grain                                        |
| ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| [Realtor.com Research: Inventory Core Metrics, zip, history](https://www.realtor.com/research/data/) | Price cut share, days on market (listings), pending ratio, new listings, list price per sq ft       | Monthly, Jul 2016 – Aug 2026                 |
| [Redfin Data Center: Housing Market Tracker, zip](https://www.redfin.com/news/data-center/)          | Months of supply, days on market (sold homes), sale-to-list ratio, homes sold, sale price per sq ft | Rolling 3-month windows, Sep 2016 – Aug 2026 |


**Scope:** 20 residential zips in the Orlando area (all in Orange County), including Jeanine Alcime (My mentor who is also a realtor, who I kept in mind whilst doing this project) six focus zips: 34786, 34787, 34761, 32712, 32703 and 32801. The raw files are too large for GitHub (up to 830 MB); download them from the links above into `data/`.

## Methodology



### 1. Clean and filter

- Filtered both national files to Florida, then to the 20 zips. Zips are stored as text so they join correctly.
- Converted Redfin's `"NA"` strings to real nulls. All of the remaining gaps in the Orlando data belonged to one PO-box zip (32704), which I excluded.



### 2. Align and join the two sources

- Averaged each Realtor.com metric over the same three months as each Redfin window (e.g. Redfin "Aug 2026" = Realtor.com Jun–Aug 2026), per zip.
- Joined on zip + month. Every one of the 20 zips matched in every window of the study period: **2,400 rows** (20 zips × 120 windows).
- Checked Redfin's months of supply against inventory ÷ monthly sales: all rows within ±0.5 months.



### 3. Build a leverage score

Five inputs across three dimensions of my definition:


| Dimension          | Inputs                                                     | More seller leverage when… |
| ------------------ | ---------------------------------------------------------- | -------------------------- |
| **Supply**         | Months of supply (Redfin)                                  | lower                      |
| **Speed**          | Days on market: Realtor.com listings and Redfin sold homes | lower                      |
| **Price leverage** | Price cut share (Realtor.com), sale-to-list ratio (Redfin) | fewer cuts, higher ratio   |


- Each input is standardized against one fixed reference (every zip × window from Jun–Aug 2021 to Jun–Aug 2026), so a shift across the whole metro still shows up.
- Inputs are averaged within each dimension, then the three dimensions are averaged (⅓ each).
- **0** = the average Orlando zip in 2021–26; each point is one standard deviation; **higher = more seller leverage**.
- Robustness version: four inputs equally weighted. It correlates 0.98 with the main score.



### 4. Test the hypotheses

- **Change** = score now − score at baseline; **metro change** = median of the 20 zips' changes; **gap** = zip change − metro change.
- The direction of the gap decides each hypothesis. A gap larger than the 90th percentile of normal drift (measured 2017 → 2019) is flagged as unusually large.
- Every result is checked four ways: primary vs. robustness windows × two score versions. I also shifted each window by a month either way to see which results depend on the exact months chosen.



### 5. Realtor-facing outputs

For every zip:

- **Label:** Seller-favored / Balanced / Buyer-favored, by majority vote of months of supply (<4 / 4–6 / >6), days to sell (<30 / 30–60 / >60) and sale-to-list (≥99% / 95–99% / <95%).
- **Outlook:** Heating up / Steady / Cooling, from the past year's change in price cuts, pending sales and new-listing flow.
- **Confidence:** whether Realtor.com and Redfin agree on the direction.
- **Talking point:** one plain-English line for a client conversation.



## Findings



### The headline

**Every one of the 20 zips lost seller leverage since summer 2021, and 17 of them went from a seller's market to balanced.** What matters most for pricing a listing today is that the whole metro has shifted. Pricing to 2021 comps will overshoot.


| Orlando median                    | Summer 2021       | Summer 2026                                                             |
| --------------------------------- | ----------------- | ----------------------------------------------------------------------- |
| Listings with a price cut         | 8.5%              | 22%                                                                     |
| Days to sell (Redfin, sold homes) | 9.5               | 46                                                                      |
| Months of supply                  | 1.05              | 4.35                                                                    |
| Sale-to-list ratio                | 100.0%            | 97.6%                                                                   |
| Leverage score                    | +1.24             | −0.65                                                                   |
| Market label (zips)               | 20 Seller-favored | 17 Balanced · 2 Seller-favored (32817, 32826) · 1 Buyer-favored (32801) |


For context, summer 2019 scored +0.17: today's market is softer for sellers than before the pandemic, not just "back to normal".

### Hypotheses


|                                                  | Verdict                    | Why                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------ | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **H1** New construction hurt resale sellers most | **Not confirmed**          | Results were mixed and within normal variation. Price cuts rose about 1 point more than the metro in both zips in the primary comparison but less in the robustness comparison, and the days-on-market results split. Winter Garden and Apopka lost leverage at about the metro rate. |
| **H2** Windermere held up                        | **Rejected**               | 34786 lost slightly *more* than the metro in the primary comparison (gap −0.19) and about the same in the robustness one. Windermere tracked the metro.                                                                                                                               |
| **H3** Affordable zips held up better            | **Confirmed, modest size** | Ocoee and Apopka 32703 lost less than the growth zips in all four checks (by 0.23–0.45 SD), and lost less than the metro in all 18 shifted-window combinations, the most stable result in the analysis.                                                                               |


**The surprise:** how little the zips differ. The metro fell about 1.9 standard deviations, while most zip-to-zip gaps were within the range of normal drift. The zips that lost the most (32827 Lake Nona and 32832, about 2.5) and those that lost the least are real but small differences compared with the shared drop.

**One caution:** College Park (32804) looks like it "held up", but that's mostly because its summer-2021 baseline was unusually weak (27% of listings had price cuts that summer vs. 8.5% for the metro). In the robustness comparison it tracked the metro.

### Example talking point

> **34786 (Windermere):** Balanced today, down from Seller-favored in summer 2021; it lost about as much seller leverage as Orlando overall. Price cuts went from 8% to 20% of listings, and homes now take 51 days to sell (vs. 9). Past year: heating up. Caveat: the comparison depends on which months you pick.



## The dashboard

Built in Tableau Public on a background designed in Figma, at 1366 px wide so it fits a laptop screen without sideways scrolling.

- **Zip snapshot (left):** pick a zip from the dropdown, or click it on the map, to see its label, leverage rank, change vs. Orlando, price cuts, days to sell, pending ratio, a talking point, and trends against the metro.
- **Orlando overall (right):** a map of today's labels, the top 10 zips by leverage lost, and the metro trend in price cuts and days to sell since 2019.
- **Phone layout:** just the dropdown and the snapshot tiles, readable across a kitchen table.



## Limitations

- **Zips aren't neighborhoods.** 34786 includes both Windermere and part of Horizon West, so H2's "Horizon West is dragging it down" explanation can't be tested at this level.
- **All property types are combined.** Condo-heavy 32801 is compared with single-family-heavy zips.
- **Small samples are noisy.** 32801, 32805 and 32826 had fewer than 50 sales in some 3-month windows, and several zips' results change direction when a window shifts by one month.
- **Averaging three monthly medians only approximates a 3-month median** for the Realtor.com metrics.
- **The label cutoffs are conventions.** The 99% sale-to-list line is calibrated to Orlando's 2019 vs. 2021 data; the 95% floor and the days-on-market bands aren't validated (no zip in the data reached a buyer's market by those measures except 32801).
- **The "p90" threshold is descriptive**, not a test of statistical significance.



## Repository


| Path                                                                                                                                                                                                                                     | What it is                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `[analysis.ipynb](analysis.ipynb)`                                                                                                                                                                                                       | The full analysis: cleaning, EDA, join, score, hypothesis tests, checks, conclusions       |
| `[decision_log.md](decision_log.md)`                                                                                                                                                                                                     | Field notes: every methodology decision and why                                            |
| `[export_tableau.py](export_tableau.py)`                                                                                                                                                                                                 | Builds the two Tableau files from the notebook's saved outputs                             |
| `data/processed/`                                                                                                                                                                                                                        | Notebook outputs: joined panel, scores, changes vs. metro, realtor outputs, talking points |
| `data/tableau/`                                                                                                                                                                                                                          | The two files the dashboard uses                                                           |
| `[tableau_dashboard_guide.md](tableau_dashboard_guide.md)`, `[tableau_snapshot_sheets.md](tableau_snapshot_sheets.md)`, `[tableau_dashboard_build.md](tableau_dashboard_build.md)`, `[tableau_figma_layout.md](tableau_figma_layout.md)` | Step-by-step build notes for the worksheets, the Figma layout and the dashboard            |




### Reproduce it

1. Download the Realtor.com zip history file and the Redfin zip market tracker file (links under [Data](#data)) into `data/`.
2. Run `analysis.ipynb` top to bottom. It writes everything in `data/processed/`.
3. Run `python3 export_tableau.py` to write `data/tableau/`.
4. Open the Tableau workbook and refresh both data sources.

