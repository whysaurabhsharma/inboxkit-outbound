# Skill: first-line

Write one opening line for a cold email. Return the line only.

## Input

A contact record with: first_name, company, signal_type,
signal_date, signal_url, signal_text.

## Rules

1. Under 25 words.
2. State the dated fact and its date. Nothing else.
3. No adjective about them or about us. Not impressive, not
   exciting, not great.
4. No em dash, no en dash. Hyphens are fine.
5. No product claim. The line is about them, not about us.
6. No question. The ask comes later in the email.
7. No flattery opener. Never start with I noticed, I saw,
   congrats, love what, hope this finds.
8. If the record has no signal_url, return exactly: Not found
9. Never say a role is open, still open, currently open, or has been
   open since a date, and never say they are still hiring. A post date
   shows when the role was published, not that it is still open. Only
   say it if the record has a role_open_checked_on field, the date
   someone confirmed the post was live.

## Good

You posted an SDR role on 14 October and your site runs Smartlead.

Acme posted three outbound roles on 2 October.

## Bad

I noticed you are hiring, congrats on the growth. (flattery, no date)

Exciting to see Acme scaling the outbound team. (adjective)

Saw your job post and thought InboxKit could help. (product claim)

Your SDR role has been open since 14 October. (unsourced: a post date
does not show the role is still open)

## Prompt

Write the first line of a cold email to the contact below.

The reader runs a cold email agency and deletes forty of these a
day. The line earns the second line only if it states a dated fact
about them that they can check.

Follow every rule above. Return the line only, no quotes, no
preamble.

## Version

first-line-v2
