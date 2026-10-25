# Rules

Five graded rules from the brief. Break one and the submission fails.

1. Product claims come only from inboxkit.com, and the page is linked.
   Every claim in copy carries a claim ID that resolves to a row in
   config/claims.md with a live URL.

2. No em dashes or en dashes anywhere in copy or the memo.
   Enforced by `make lint`, not by memory.

3. One ask per message. Every email ends with the single CTA question
   or with nothing. The LinkedIn connection note asks only to connect.

4. A working opt-out in every email. Plain body line plus the
   sequencer unsubscribe merge tag. A "no" reply is honoured by
   `python run.py suppress --add <email> --reason opt_out`.

5. Smartlead and Instantly are integrations, never targets.
   Nobody is attacked by name. The competitor comparison table on
   inboxkit.com is not used anywhere in copy.

One rule of my own:

6. Every fact about a prospect carries a source URL, or the cell
   reads "Not found". No inferred titles, no guessed emails,
   no signal without a dated link.

Nothing gets sent. This repo writes CSVs. It has no sequencer
credentials and no send path.
