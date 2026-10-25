# Outbound to agencies about to scale sending

Saurabh Sharma, 25 Oct 2026

## The bet

Outbound and lead generation agencies of 5 to 50 people that
already run Smartlead or Instantly and posted an outbound, SDR or
deliverability role in the last 90 days.

Infrastructure gets bought when sending volume is about to change.
A live job post is the most public, dated, checkable proof that it
is about to. The techstack filter means InboxKit plugs into what
they already use, so the migration objection never comes up.


## Segment and signal

| Signal | Dated | Maps to a purchase | Verdict |
| --- | --- | --- | --- |
| Hiring outbound or SDR | Yes, dated URL | Strong: seats mean mailboxes | Primary |
| Runs Smartlead or Instantly | Yes | Strong: InboxKit integrates | Filter |

## Qualified demo

An agency, booked with whoever owns the infrastructure decision
(founder, Head of Growth, Head of Outbound, Head of Deliverability,
Ops lead), at 10k cold emails a month or higher. 10k is the second
band on your own demo form, not a number I invented. AEs and SDRs
are excluded by title at the contact step.

## The math, in your unit

| Stage | Base | Conservative | Assumption |
| --- | --- | --- | --- |
| Qualified demos | 15 | 15 | Target from the brief |
| Positive replies | 30 | 30 | Half of positives book |
| Positive reply rate | 1.5% | 0.8% | Base: 6% reply at AI Interview Agents, quarter positive. Conservative: your 2% floor, 40% positive |
| Contacts live, verified | 2,000 | 3,750 | 30 divided by the rate |
| Emails sent | 6,800 | 12,750 | 3.4 per contact over 4 steps, stopping on reply or bounce |
| EPP | 227 | 425 | Both under your 500 |
| Raw contacts sourced | 2,700 | 5,000 | 75% pass verification, catch-alls held back |
| Mailboxes needed | 14 | 26 | 20 sending days, 25 a day per mailbox |

The assumption I trust least is that half of positive replies book
a qualified demo. It is a clean number with nothing behind it.

## What the campaign costs to run on your own stack

14 to 26 mailboxes at $3.00 each (C01), plus warmup at $3 a mailbox
(C08), is $84 to $156 in month one, falling to $42 to $78 after
warmup ends. Annual billing takes the mailbox rate to $2.50 (C02).

https://www.inboxkit.com/pricing

## Offer and CTA

A 30 minute agency demo that sizes mailbox count for the volume
implied by their job post, prices it against Azure tenants, and
shows warmup on one of their own domains.

The Azure line is the one most agency founders miss. At $30 a
tenant for up to 100 mailboxes (C04), an agency sizing past 200
mailboxes pays near $0.30 each against $3.00 on the standard rate.

One ask per message, and it is always the same one: the 30 minutes
your own form books. https://www.inboxkit.com/demo

## Kill rule and review

Pause any campaign whose EPP passes 1,000 after 1,500 sends, twice
your target. Leading indicator ahead of that: positive reply rate
by signal type, once each has 100 or more sends.

Monday review comes out of report.py: numbers, top three learnings,
next three launches.

## One note on your figures

Three numbers appear at two values on your site. Inbox placement
reads 95 percent on the agency page and 90 percent plus on the
homepage. Integrations read 24 plus in the FAQ and 20 plus in the
comparison table. Setup reads 10 minutes, 20 minutes and 30 to 120
minutes in three places. Copy uses the lower figure each time and
links the page carrying it.
