# Skill: qualify-account

Decide whether one company fits the ICP. Return JSON only.

## Input

A company record with: company, domain, employee_count, techstack,
signal_type, signal_date, signal_url, signal_text.

## Rules

1. Fit is true only when the signal is dated inside the lookback
   window and the URL is present.
2. Never infer a techstack that is not in the record.
3. If you cannot cite a URL from the record, evidence_url must be
   the string "Not found" and fit must be false.
4. reason is one sentence, no adjectives, naming the fact you used.
5. Output JSON only. No preamble, no markdown fences.

## Output shape

{"fit": true, "reason": "...", "evidence_url": "https://..."}

## Prompt

You are qualifying one company against an ICP for a cold email
campaign selling email infrastructure.

ICP: outbound and lead generation agencies of 5 to 50 people that
run Smartlead or Instantly and posted an outbound, SDR or
deliverability role in the last 90 days.

Company record follows. Decide fit. Cite the URL in the record that
proves the signal. If the record has no usable URL, return fit
false and evidence_url "Not found".

Return JSON only.

## Version

qualify-v1
