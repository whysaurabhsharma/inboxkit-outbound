# Scale

Labels: **measured** means observed in this run on 25 Oct 2026.
**Estimated** means derived from an assumption or from a published
price, which was read on 25 Oct 2026 and not paid.

## Spend on this run

Total spend: $0 (measured). Calls made: the public job board APIs of
Greenhouse, Lever, Ashby, Workable and Recruitee, which have no
price. Prospeo, Clay, Apify and BounceBan were not called (measured).

## Free tiers: what they covered, where they ran out

| Service | Free allowance | Used | Ran out |
| --- | --- | --- | --- |
| Job board APIs | No published limit | 6 boards in the live run, 27 names probed in 3 min 24 s (measured) | No; no request was refused (measured) |
| Prospeo | 75 to 100 credits a month, sources disagree (estimated) | 0 (measured) | Not reached |
| Clay | 100 data credits, 500 actions a month, no API (estimated) | 0 (measured) | Not reached |
| Apify | $5 a month (estimated) | $0 (measured) | Not reached |
| BounceBan | Single checks free (estimated) | 0 (measured) | Not reached |

No free tier ran out. The run stopped before any metered step:
2 accounts qualified (measured), and enrichment was not run.

## Cost per contact

Unmeasurable at this scale. Contacts produced: 0 (measured). Spend:
$0 (measured). $0 divided by 0 contacts has no value. The input that
decides it, the share of accounts for which Prospeo returns a
verified email, has not been observed, because Prospeo was not run.
Measuring it needs a sample of accounts; 2 is too few to give a rate.

## What 2,000 contacts would cost

Assumptions, none measured:

- A1: one contact per account.
- A2: Prospeo returns a verified email for 60% of accounts searched.
- A3: each account costs 1 Search Person credit (charged when it
  returns a person) and 1 Enrich Person credit when an email is
  found. These are Prospeo's published credit rules.

From these: 3,334 accounts searched (estimated) and 5,334 credits,
3,334 for search plus 2,000 for emails (estimated), which is 2.67
credits per contact (estimated).

| Provider | Role | Cost for 2,000 contacts |
| --- | --- | --- |
| Prospeo | Find person and verified email | $103 to $249 (estimated): Growth at $99 for 5,000 credits plus 334 credits at about $10 per 1,000, or Pro at $249 for 15,000 credits. Published prices; sources disagree |
| BounceBan | Catch-alls only | $0 to $34 (estimated): Prospeo is asked for verified emails only, so it returns no catch-alls; $34 buys the entry pack of 10,000 credits if a second source adds catch-alls |
| Clay | Alternative to Prospeo, not additive | $185 to $495 a month (estimated): Launch has 2,500 data credits, Growth 6,000. Assumes 2 data credits per email found, which Clay does not publish |
| Account sourcing | Find 3,334 qualifying agencies | Not estimated. No source that covers agencies of 5 to 50 people with headcount has been priced or tested |

Contacts only, Prospeo route: $103 to $283 (estimated), which is $0.05
to $0.14 per contact (estimated). This excludes account sourcing,
which has no estimate.

## Bottleneck

Accounts, not emails. Evidence from the sourcing run, all measured:

- 22 agency names probed; 8 had a board on any of the five platforms.
- 6 boards approved; 4 had no open jobs.
- 2 accounts had a dated qualifying post (Belkins, memoryBlue).
- 0 of those 2 could be confirmed inside the 5 to 50 size band,
  because boards do not publish headcount.

At the measured yield of 2 qualifying accounts per 26 names probed,
3,334 accounts would need 43,342 names probed and 91 hours of probing
at the measured rate (estimated, linear extrapolation). No list of
43,342 agency names exists to probe.

By contrast, the Prospeo free tier would cover 28 to 37 contacts a
month at 2.67 credits per contact (estimated), already more than the
2 accounts the boards produced (measured).

## Second bottleneck: headcount and techstack

No free source used in this run gives headcount or techstack for these
accounts. Evidence, all measured:

- 0 of 6 approved boards publish headcount.
- 0 of 2 live job posts name Smartlead or Instantly.
- leads.csv: `employee_count` and `techstack` read "Not found" in 39 of
  39 rows. The synthetic rows carry no invented value for either.

Effect, measured: the techstack points (25) and size points (15) never
apply, so the maximum score is 60 and tier A (70 or more) cannot be
reached. All 39 leads are tier B: 14 at 60, 25 at 45. The 5 to 50
size band cannot be applied as a filter, only stated.

What it would take to fill them:

- Headcount: a company data source that returns employee count per
  domain. Prospeo company data and Clay company enrichment are the
  candidates; neither was tested, and whether Prospeo returns headcount
  is not verified. Assuming 1 credit per company lookup (A4, not
  measured), 3,334 accounts need 3,334 credits (estimated). With the
  5,334 contact credits above that is 8,668 Prospeo credits, which fits
  Pro at $249 for 15,000 (estimated). This costs money: 3,334 lookups
  exceed every free tier listed above (estimated).
- Techstack: Smartlead and Instantly send from the sequencer's servers,
  so a website technology scan need not see them (assumption, not
  verified). Three routes: job post text naming the tool (free, found
  in 0 of 2 posts, measured); the agency's own pages or a sequencer
  partner listing naming it (free, read by hand per account, not
  priced in time); a paid technographic provider (costs money, not
  priced, and whether any detects these two tools is not verified).

Until both are filled, a tier reflects signal and title only.

## First change with a budget

Spend it on account sourcing before any email credits: run one paid
company search that filters by industry and by headcount 5 to 50 on a
sample of 100 accounts, and measure how many pass the ICP checks in
this repo. That rate, with a measured Prospeo hit rate on the same
sample, replaces A2 and the missing sourcing line above with measured
numbers. A search that returns headcount also fills the size field,
which addresses part of the second bottleneck.

## Price sources, read 25 Oct 2026

- Prospeo credit rules: https://prospeo.io/api-docs/enrich-person and
  https://prospeo.io/api-docs/search-person
- Prospeo plans: https://emelia.io/hub/prospeo-preise (Starter $49 for
  2,000, Growth $99 for 5,000, Pro $249 for 15,000; extra credits about
  $10 per 1,000, single source) and https://coldiq.com/blog/prospeo-pricing
  (different tiers)
- Clay: https://www.clay.com/pricing (free tier);
  https://crustdata.com/reviews/clay (Launch $185 for 2,500, Growth
  $495 for 6,000)
- Apify: https://apify.com/pricing
- BounceBan: https://tomba.io/blog/bounceban-pricing-reviews-pros-and-cons
  ($34 for 10,000)
