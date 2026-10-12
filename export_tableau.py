"""Build the two Tableau files from the notebook's saved outputs.

Run from anywhere:
    python3 export_tableau.py

Reads (written by analysis.ipynb):
    data/processed/orlando_scores_monthly.csv   (Building the Leverage score)
    data/processed/score_changes_vs_metro.csv   (Measure change and test the hypotheses)
    data/processed/realtor_outputs.csv          (Realtor Facing Outputs)

Writes:
    data/tableau/tableau_zip_summary.csv   one row per zip: map, zip snapshot, bar chart
    data/tableau/tableau_monthly.csv       one row per zip x 3-month window, 2019 on: trend lines
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
PROCESSED = ROOT / 'data' / 'processed'
OUT = ROOT / 'data' / 'tableau'

FOCUS_ZIPS = ['34786', '34787', '34761', '32712', '32703', '32801']   # Jeanine's zips
BASE, NOW = pd.Period('2021-08', 'M'), pd.Period('2026-08', 'M')       # primary: Jun-Aug 2021 -> Jun-Aug 2026
MIN_HOMES_SOLD = 50                                                    # per 3-month window, same as the notebook's check 3


def load_inputs():
    scores = pd.read_csv(PROCESSED / 'orlando_scores_monthly.csv', dtype={'zip': str})
    scores['date'] = pd.PeriodIndex(scores['date'], freq='M')
    score_changes = pd.read_csv(PROCESSED / 'score_changes_vs_metro.csv', dtype={'zip': str})
    realtor_outputs = pd.read_csv(PROCESSED / 'realtor_outputs.csv', dtype={'zip': str}).set_index('zip')
    return scores, score_changes, realtor_outputs


def stability_checks(scores):
    """Low volume and fragility, as in the notebook's 'Check 3'."""
    score_by_window = scores.set_index(['date', 'zip'])['leverage_score']
    homes_sold = scores.set_index(['date', 'zip'])['rf_homes_sold']

    key_windows = [pd.Period(m, 'M') for m in ['2021-08', '2026-08', '2022-05', '2026-05']]
    min_sold = pd.concat([homes_sold.loc[w] for w in key_windows], axis=1).min(axis=1)

    def share_lost_less(base_labels, now_labels):
        lost_less = []
        for b in base_labels:
            for n in now_labels:
                change = score_by_window.loc[pd.Period(n, 'M')] - score_by_window.loc[pd.Period(b, 'M')]
                lost_less.append(change > change.median())
        return pd.concat(lost_less, axis=1).mean(axis=1)

    primary = share_lost_less(['2021-07', '2021-08', '2021-09'], ['2026-06', '2026-07', '2026-08'])
    robust = share_lost_less(['2022-04', '2022-05', '2022-06'], ['2026-04', '2026-05', '2026-06'])
    return pd.DataFrame({
        'low_volume': min_sold < MIN_HOMES_SOLD,
        'fragile': ~primary.isin([0, 1]) | ~robust.isin([0, 1]),
    })


def talking_point(zip_code, city, outputs, result, checks, then, latest):
    """Same wording as the notebook's talking points."""
    if not result['beyond_p90']:
        comparison = 'lost about as much seller leverage as Orlando overall'
    elif result['gap'] > 0:
        comparison = 'held up noticeably better than Orlando overall'
    else:
        comparison = 'lost noticeably more seller leverage than Orlando overall'

    notes = []
    if outputs['confidence'] == 'mixed':
        notes.append('Realtor.com and Redfin disagree on the past year')
    if checks['fragile']:
        notes.append('the comparison depends on which months you pick')
    if checks['low_volume']:
        notes.append('few sales, so numbers move a lot')
    confidence = 'Caveat: ' + '; '.join(notes) + '.' if notes else 'Both sources agree, and the result holds across comparisons.'

    return (f"{zip_code} ({city}): {outputs['label_now']} today, down from {outputs['label_2021']} in summer 2021; it {comparison}. "
            f"Price cuts went from {then['rdc_price_cut_pct']:.0f}% to {latest['rdc_price_cut_pct']:.0f}% of listings, "
            f"and homes now take {latest['rf_dom']:.0f} days to sell (vs. {then['rf_dom']:.0f}). "
            f"Past year: {outputs['outlook'].lower()}. {confidence}")


def build_zip_summary(scores, score_changes, realtor_outputs):
    changes = score_changes.set_index('zip')

    def pick(metric, comparison, column):
        return changes[(changes['metric'] == metric) & (changes['comparison'] == comparison)][column]

    by_window = scores.set_index(['date', 'zip'])
    then, latest = by_window.loc[BASE], by_window.loc[NOW]
    checks = stability_checks(scores)
    primary = changes[(changes['metric'] == 'leverage_score') & (changes['comparison'] == 'primary')]
    cities = scores.groupby('zip')['zip_name'].first().str.split(',').str[0].str.title()

    s = pd.DataFrame(index=realtor_outputs.index)
    s['city'] = cities
    s['state'] = 'FL'                  # geographic context so Tableau never guesses the country
    s['country'] = 'United States'
    s['is_focus'] = s.index.isin(FOCUS_ZIPS)
    s['label_2021'] = realtor_outputs['label_2021']
    s['label_now'] = realtor_outputs['label_now']
    s['score_2021'] = pick('leverage_score', 'primary', 'baseline')
    s['score_now'] = pick('leverage_score', 'primary', 'now')
    s['score_change'] = pick('leverage_score', 'primary', 'change')
    s['metro_score_change'] = pick('leverage_score', 'primary', 'metro_change')
    s['gap_vs_metro'] = pick('leverage_score', 'primary', 'gap')
    s['p90'] = pick('leverage_score', 'primary', 'p90')
    s['score_change_since_spring_2022'] = pick('leverage_score', 'robustness', 'change')
    s['leverage_lost'] = -s['score_change']
    s['rank_now'] = s['score_now'].rank(ascending=False).astype(int)         # 1 = most seller leverage today
    s['rank_lost'] = s['leverage_lost'].rank(ascending=False).astype(int)    # 1 = lost the most
    s['price_cut_pct_2021'] = then['rdc_price_cut_pct']
    s['price_cut_pct_now'] = latest['rdc_price_cut_pct']
    s['days_to_sell_2021'] = then['rf_dom']          # Redfin, sold homes
    s['days_to_sell_now'] = latest['rf_dom']
    s['listing_dom_now'] = latest['rdc_dom']         # Realtor.com, active listings
    s['pending_ratio_2021'] = then['rdc_pending_ratio']
    s['pending_ratio_now'] = latest['rdc_pending_ratio']
    s['months_supply_now'] = latest['rf_months_supply']
    s['sale_to_list_pct_now'] = latest['rf_sale_to_list_pct']
    for col in ['confidence', 'outlook', 'asking_ppsf_yoy_pct', 'sale_ppsf_yoy_pct', 'asking_outpacing_sales']:
        s[col] = realtor_outputs[col]
    s['low_volume'] = checks['low_volume']
    s['fragile'] = checks['fragile']
    s['talking_point'] = [talking_point(z, s.loc[z, 'city'], realtor_outputs.loc[z], primary.loc[z],
                                        checks.loc[z], then.loc[z], latest.loc[z]) for z in s.index]
    s.index.name = 'zip'
    return s


def build_monthly(scores, cities):
    monthly = scores[scores['date'] >= pd.Period('2019-01', 'M')].copy()
    monthly['window_end'] = monthly['date'].dt.to_timestamp()    # first day of the window's last month
    monthly['city'] = monthly['zip'].map(cities)
    monthly['state'] = 'FL'
    monthly['country'] = 'United States'
    monthly['is_focus'] = monthly['zip'].isin(FOCUS_ZIPS)
    monthly = monthly.rename(columns={'rdc_price_cut_pct': 'price_cut_pct', 'rf_dom': 'days_to_sell',
                                      'rdc_dom': 'listing_dom', 'rdc_pending_ratio': 'pending_ratio',
                                      'rf_months_supply': 'months_supply', 'rf_sale_to_list_pct': 'sale_to_list_pct'})
    trend_cols = ['leverage_score', 'price_cut_pct', 'days_to_sell', 'listing_dom',
                  'pending_ratio', 'months_supply', 'sale_to_list_pct']
    for col in trend_cols:   # metro median for that window, repeated on every zip's row
        monthly['metro_' + col] = monthly.groupby('date')[col].transform('median')
    return monthly[['zip', 'city', 'state', 'country', 'is_focus', 'window_end'] + trend_cols + ['metro_' + c for c in trend_cols]]


def main():
    scores, score_changes, realtor_outputs = load_inputs()
    zip_summary = build_zip_summary(scores, score_changes, realtor_outputs)
    monthly = build_monthly(scores, zip_summary['city'])

    OUT.mkdir(parents=True, exist_ok=True)
    zip_summary.round(2).reset_index().to_csv(OUT / 'tableau_zip_summary.csv', index=False)
    monthly.round(3).to_csv(OUT / 'tableau_monthly.csv', index=False)

    print(f'tableau_zip_summary.csv: {zip_summary.shape[0]} zips x {zip_summary.shape[1] + 1} columns')
    print(f'tableau_monthly.csv:     {monthly.shape[0]} rows, '
          f"{monthly['window_end'].min():%b %Y} to {monthly['window_end'].max():%b %Y}")
    print(f'saved to {OUT}')


if __name__ == '__main__':
    main()
