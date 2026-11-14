# Writing the cards

## Output file

Write a JSON array (UTF-8) to the path in your brief. Each element:

```json
{
  "text": "Omitted variable bias: if the omitted variable is positively correlated with both X and Y, the OLS slope is biased {{c1::upward}}.",
  "extra": "The coefficient picks up the omitted variable's effect on Y because it moves with X.",
  "tags": ["ch02_empirical_methods", "omitted_variable_bias"],
  "source": "ch_2.pdf p.31",
  "yield": "high",
  "figure": {"file": "ch_2.pdf", "page": 31}
}
```

- `text` (required): the cloze sentence.
- `extra` (optional): 1–2 sentences of explanation or intuition, shown on the back. Use it
  for the "why", and for supporting details that don't deserve their own card.
- `tags` (required): the first tag is exactly the chapter tag from your brief; the second
  tag is a snake_case subtopic. Don't use spaces.
- `source` (required): the slide page(s) the fact comes from.
- `yield` (required): high, medium or low. Rate it using `exam_focus.md`.
- `figure` (optional): include it when a diagram, graph or table on that slide is the
  thing to learn. The slide image is shown on the back. Use it sparingly, for at most
  about 1 card in 10. `file` is the exact source file name (PDF only).

## Cloze rules

1. **Plain text only.** Don't use HTML tags. Literal `<`, `>` and `&` are fine, because they
   are escaped at build time. Use `\n` for a line break if you really need one.
2. **One atomic fact per deletion.** Cloze the meaningful term, number, direction or
   mechanism, never filler words. Use 1–3 deletions per card.
3. **Choose cloze numbers on purpose.** Use c1, c2 and c3 for facts that should be tested on
   separate cards. Reuse a number only when the items must be recalled together, such as
   a short two-item list.
4. **Make the answer unambiguous from the context.** If several answers could fit, add a hint:
   `{{c1::positive::sign}}`.
5. **Keep cards short**, ideally 35 words or fewer on the front. Split a long idea into
   several cards instead of writing a wall of text.
6. **Math.** Prefer plain text and Unicode: `β₁`, `≥`, `Δ`, `ΣMRS = MRT`,
   `Y = β₀ + β₁X + u`. If you need MathJax, write `\( ... \)` and make sure `}}` never
   appears inside a cloze except as the cloze's own closing. Put a space between braces:
   `} }`.
7. **Facts come from the materials**, stated the way the lecture states them. Don't invent
   numbers, dates or findings. Intuition you add in `extra` must agree with the slides.
   If you derive a result the slides only imply, such as a comparative static, say so in
   `extra`.
8. **Slides that contradict themselves.** When a caption disagrees with its own table, or a
   formula has an obvious typo, follow the table or the corrected formula (instructor
   annotations count as evidence). Say so in `extra`, and mention it in your final report.

Good and bad examples:

- Bad, clozes filler: `The {{c1::model}} shows that rents fall with distance.`
- Bad, the answer can't be pinned down: `{{c1::Toronto}} is a large city.`
- Bad, a list of six things clozed as one deletion. Split it, or cloze the 2–3 that matter.
- Good, a mechanism: `Agglomeration raises productivity through {{c1::sharing}}, {{c2::matching}} and {{c3::learning}} (Duranton–Puga).`
- Good, practice: `Practice: β̂ = −0.2 with SE 0.05 gives a 95% CI of about {{c1::(−0.3, −0.1)}}, so the effect is {{c2::statistically significant::significant or not?}}.`

## What to cover and what to skip

Cover every substantive slide, to the extent your depth allows (see `exam_focus.md`):
definitions, mechanisms, models and their assumptions, formulas and how to apply them,
how to interpret results, studies (design + finding), worked examples, and policies with
their effects. Turn any assignment, quiz or discussion questions that appear in the
slides, with their answers, into cards, because these are the instructor's own questions.

Skip course admin, polls, "introduce yourself" prompts, video links with no content, and
decorative slides.

Don't duplicate facts within your files.

## Reading figures and image-only slides

Extracted text loses graphs, tables, equations and handwriting. For every page your brief
lists as sparse, and any page whose text mentions a figure, table or equation, render it
and look at it:

```
python <SKILL_DIR>/scripts/render_pages.py "<source.pdf>" "<your image dir>" --pages 4,9-12
```

Then open the printed PNG paths with the Read tool. Use `--zoom 2.5` for small print.
Don't skip this step: in lecture slides the key result is often only in the figure.

## Check your work

Before replying, validate your file(s):

```
python <SKILL_DIR>/scripts/validate_cards.py "<your cards file>" --source-dir "<lecture folder>" --depth <depth>
```

Fix every ERROR. Read the WARN lines and fix the ones that are real problems.
