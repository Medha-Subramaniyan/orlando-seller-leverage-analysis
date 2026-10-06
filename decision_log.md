# Decision Log / Field Notes

## On defining core metrics

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

- [ ] baseline year: 2022 or 2023 (and check realtor.com `quality_flag`, which is 1 on ~40% of 2022–23 Orlando rows)
- [ ] definition of seller leverage (step 1)
- [ ] leverage score method (step 5) + why
- [ ] numeric threshold for "more/less than metro average" (step 7)
- [ ] keep label / confidence / outlook as a separate realtor-facing output, or drop it?



## Where I left off

- **brought in redfin data - need to clean and explore it before using it to calcualte any core metrics**



## Questions

- why are some like median_listing_price_yy or median_listing_price_mm tiny decimals? 
- is the august data folded in to the historical data?
- should i separate the redfin df into sub dfs (central fl, orl) or just excise the geographic data as necessary?

