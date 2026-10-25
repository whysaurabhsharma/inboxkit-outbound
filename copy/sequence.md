# Sequence

Segment and offer: config/segment.md. Claims: config/claims.md.
Merge fields: `{{first_name}}`, `{{signal_role}}`, `{{signal_date}}`,
`{{first_line}}` (from copy/first_lines.csv, approved rows only),
`{{unsubscribe_link}}` (replace with your sequencer's unsubscribe tag).

## Cadence

| Day | Channel | Step |
| --- | --- | --- |
| 1 | LinkedIn | Connection note |
| 2 | Email | Email 1 (variant A or B) |
| 4 | LinkedIn | Follow-up 1, only if the connection was accepted |
| 8 | Email | Email 2 |
| 10 | LinkedIn | Follow-up 2, only if the connection was accepted |
| 15 | Email | Email 3 |
| 19 | Email | Email 4 |

Rules:

- Never both channels on the same day. The grid above has no shared day.
- Any email reply stops both channels.
- A bounce stops everything, and the address goes to
  `python run.py suppress --add <email> --reason bounce`.
- A "no" by any channel is honoured with
  `python run.py suppress --add <email> --reason opt_out`.

## The CTA

Every email ends with this one question, word for word. It asks for
the 30 minutes their demo form books (inboxkit.com/demo):

> Worth 30 minutes to size and price the mailboxes?

## Opt-out line

Every email closes with:

> Reply no to stop. Unsubscribe: {{unsubscribe_link}}

## Email 1, variant A: speed

Subject: new sdr seat

{{first_line}}

That seat adds sending volume within four weeks, and needs mailboxes
and DNS first.

Mailbox orders complete in 30 to 120 minutes, with SPF, DKIM and DMARC
set automatically (C09, C10).

Worth 30 minutes to size and price the mailboxes?

Reply no to stop. Unsubscribe: {{unsubscribe_link}}

## Email 1, variant B: pain

Subject: warmup timing

{{first_line}}

Its mailboxes must carry volume within four weeks, starting cold.

Warmup takes 14 days to reach 40 sends a day, at $3 a mailbox monthly
(C07, C08), so it should start now.

Worth 30 minutes to size and price the mailboxes?

Reply no to stop. Unsubscribe: {{unsubscribe_link}}

## Email 2: case study

Pick the version by the account's `employee_count`. claims.md records
no headcount for the case study companies, so the match is by the
volume each one states: P02 states 80K emails a week, the lowest
volume stated among the case studies; P03 states rates, not volume,
so it cannot overshoot an agency of 5 to 20 people. P01 and P04 to P06
state volumes or mailbox counts above this segment and are not used.

### 5 to 20 people (P03)

Subject: reply and bounce rates

You posted a {{signal_role}} role on {{signal_date}}.

More seats means more volume over the next four weeks, spread across
more mailboxes.

OutreachBloom runs at an 11.5 percent reply rate and 0.6 percent
bounces on InboxKit (P03).

Worth 30 minutes to size and price the mailboxes?

Reply no to stop. Unsubscribe: {{unsubscribe_link}}

### 21 to 50 people (P02)

Subject: 80k a week

You posted a {{signal_role}} role on {{signal_date}}.

More seats means more volume over the next four weeks, spread across
more mailboxes.

The Growth Pro sends 80K emails a week on InboxKit at a 15.2 percent
reply rate (P02).

Worth 30 minutes to size and price the mailboxes?

Reply no to stop. Unsubscribe: {{unsubscribe_link}}

## Email 3: the money

Subject: mailbox pricing

You posted a {{signal_role}} role on {{signal_date}}.

If that seat adds mailboxes over the next four weeks, the rate per
mailbox decides what the added volume costs.

Azure tenants are $30 a month for up to 100 mailboxes, from $0.30 a
mailbox, against $3.00 a mailbox at the monthly rate (C04, C01).

Worth 30 minutes to size and price the mailboxes?

Reply no to stop. Unsubscribe: {{unsubscribe_link}}

## Email 4: last note

Two lines by design, so it departs from the four line skeleton: the
offer restated with the signal and its date, then the CTA. The offer
line invites a no without adding a second question.

Subject: last note

Last note on the {{signal_role}} role from {{signal_date}}: the call
sizes mailboxes for it and prices them two ways, and a no is a fine
answer.

Worth 30 minutes to size and price the mailboxes?

Reply no to stop. Unsubscribe: {{unsubscribe_link}}

## Claims used, with sources

| ID | Used in | Source |
| --- | --- | --- |
| C01 | Email 3 | https://www.inboxkit.com/pricing |
| C04 | Email 3 | https://www.inboxkit.com/pricing |
| C07 | Email 1B, LinkedIn follow-up 1 | https://www.inboxkit.com/ |
| C08 | Email 1B | https://www.inboxkit.com/ |
| C09 | Email 1A | https://www.inboxkit.com/ |
| C10 | Email 1A | https://www.inboxkit.com/ |
| P02 | Email 2, 21 to 50 people | https://www.inboxkit.com/case-studies/tgp-one-click-mailbox-automation-inboxkit |
| P03 | Email 2, 5 to 20 people | https://www.inboxkit.com/case-studies/outreachbloom-crackdown-switch-inboxkit |

## Why there are no links in the emails

The only link in any email body is the unsubscribe merge tag. Links
in a cold email raise spam filtering risk and tracking domains can
carry reputation from other senders. This buyer runs cold email for a
living and knows that, so a link in the first touch reads as a sender
who does not. Each claim's source sits in the table above instead,
where a reviewer can check it.
