# Bitcoin Runs on a Clock, Plain-English Walkthrough (for review)

A jargon-free guide to the paper, in the order the paper makes its points. Each part says
the same thing the real paper says, just simply, and flags the honest catches so you can
review exactly what is and isn't being claimed.

---

## The whole paper in 30 seconds

Every famous indicator people use to call Bitcoin tops and bottoms (Pi Cycle, MVRV, the Mayer
Multiple, the 200-week average, RSI) stopped working. They didn't fail by bad luck. They all
died for the **same reason**: Bitcoin's up-and-down swings get **smaller every cycle**, and these
indicators are basically lines drawn at a fixed height. As the swings shrink, they stop reaching
the line, so the indicator never fires.

But one thing did **not** shrink: the **timing**. Bitcoin's tops keep landing about 525 to 546
days after each "halving" (a scheduled event baked into Bitcoin's code). So the size of the move
is dying, but the clock is holding. The paper measures both, tests them hard against "it's just
luck," and stakes two future predictions.

**One line:** the amplitude is dying; the clock is not.

---

## 1. The puzzle (maps to: Introduction)

In October 2025, Bitcoin hit the highest price in its history. And **not one** of the famous
"the top is in" indicators fired. For ten years these things were near-perfect. Why did they all
go silent at the exact same moment?

The paper's answer: it wasn't luck or "this time is different." It was inevitable, and it's math.

---

## 2. What others have said (maps to: Related Work)

Other researchers noticed pieces of this: Bitcoin slowly becoming more "efficient" (harder to beat)
as it grows, and a "power law" idea that Bitcoin's price follows a curve based on its age. Two
famous models (Stock-to-Flow, the power law) had a flaw: they drew their trend line using the
whole history at once, which secretly lets the line peek at the future. This paper fixes that.

---

## 3. The data (maps to: Data)

- 15 years of daily Bitcoin prices, from **two independent sources that agree with each other**
  (so it's not one exchange's bad data).
- Plus Ethereum (to check the idea on a second coin) and some economic data (money supply,
  interest rates).
- The data was **frozen on a date**, so anyone can rerun the code and get the exact same numbers.
- "Tops" and "bottoms" are defined by a **fixed rule a computer applies** (a top = a new all-time
  high followed by at least a 45% crash), not by the authors hand-picking dates.

---

## 4. How we measured things (maps to: Methodology)

**The trend line (4.1).** We drew Bitcoin's long-term trend using **only past data at each point**,
never peeking ahead. The trend is "price grows as Bitcoin gets older," in a steady curved way. The
key number that describes the curve settled around **5.6** and stayed there, which tells us the
trend is real, not made up.

**The scoreboard (4.3).** For each indicator we gave it a score from −1 to +1 for how well it
predicts what price does over the next 1, 3, or 6 months. **0 means useless / coin-flip.**

> ⚠️ **The honest catch (and it's a big one).** We then tested whether our own "wins" were real by
> shuffling the data thousands of times. Result: the fancy statistics people normally use **don't
> hold up** at this small sample size, they cry "significant!" far too often. So we **threw out our
> own p-values** and refused to lean on them. We only trust patterns that show up the simple way:
> the direction never flips, and it repeats on a second data source and on Ethereum. This is the
> paper policing itself harder than a critic would.

**The luck test for the clock (4.5).** The tops landed 525 / 546 / 534 days after their halvings.
We asked: "could that tight grouping just be random?" We tested it two ways, a strict version and
a generous version that gives the "it's random" idea every benefit of the doubt, so nobody can
say we rigged it.

---

## 5. What we found (maps to: Results)

**5.1: The turns line up on the clock.** Tops cluster within about 2% of each other in
"days-after-halving" time. The odds of that happening by chance come out to roughly **1 in a
thousand to 1 in a million**, depending on how generous you are to the "it's random" theory.

**5.2: The indicators died in a clear order: precise → early → silent.**
- 2013 and 2017: they nailed the tops, sometimes to the day.
- 2021: a double top. They fired at the spring peak and **missed** the higher fall peak that
  actually ended the cycle (the first crack).
- 2025: **total silence.** Not one fired at the biggest top ever.
- Bonus: the 200-week average, the "Bitcoin always bottoms here" rule, failed in **both** directions
  (didn't touch it in 2018, smashed 34% below it in 2022).

**5.3: WHY they died (the heart of the paper).** Every cycle, the indicator's peak reading gets
smaller. MVRV peaked at 5.88, then 4.72, then 3.96, then **2.74**. The Mayer Multiple: 8.26 → 1.52.
These indicators are **lines at a fixed height**. As the waves shrink, they stop reaching the line.
The Pi Cycle indicator literally **can no longer reach its own trigger level**. So "it never missed
before" wasn't skill. It was the wave still being big enough to touch the line. Recalibrating
won't save you; you'd just be guessing at next cycle's size from the past.

**5.4: Fast indicators decay; the time-trend survives.** RSI (the everyman indicator) decays from
a useful score to basically zero, and some indicators even **flip** (start pointing the wrong way).
The only signal that keeps its direction across the recent cycles is the **time-based trend
deviation**. It also repeats on Ethereum.

> ⚠️ **Two honest catches here.** (1) We repeat that we do NOT trust our per-cycle "significance"
> numbers (see 4.3). (2) On the money question, there are two fair ways to measure "did timing
> beat just holding?":
> - **Cautious measure (reward vs. stress):** timing only starts winning *now*, in the latest cycle.
> - **Bolder measure (total money made):** a simple "sit in cash during the crash window" rule beat
>   just-holding in **all four cycles** and made about **53× more money**, mostly by dodging the big
>   crashes.
>
> These aren't contradictory, they measure different things (one punishes sitting in cash during a
> bull run; the other rewards dodging crashes). The paper reports **both** and refuses to call either
> a proven money-printer, because it's only 4 cycles.

**5.5: It works on Ethereum too.** A different coin, with a different trend curve, shows the same
pattern: fast price signals fade, the time-trend holds. So it's not a Bitcoin-only fluke.

**5.6: "But isn't it just the money printer / the economy?"** The most common objection. We checked
money supply (M2) and interest rates. They **flip which way they matter every cycle** and miss
Bitcoin's tops by hundreds of days. The clock holds to ~2%. The clincher: in 2024–2026 money was
**still expanding** while Bitcoin topped right on schedule and fell. The economy says "keep going";
the clock said "top." Price followed the clock.

> ⚠️ **Honest catch:** the economy moves on a roughly 4-year rhythm too, and with only 3–4 cycles we
> **can't 100% rule it out**. We show four different tests that all point to the clock, not proof.

**5.7: The "Satoshi Clock."** We describe Bitcoin's whole state with just two numbers:
- **CLOCK** = how many days since the last halving (where you are in the 4-year cycle).
- **SPRING** = how stretched price is above or below its trend line.

Plot these together and Bitcoin's history is a **spiral that gets smaller each loop** (the swings
dying) but **turns at the same place each time** (the clock holding). That picture is the whole
thesis in one image.

---

## 6. Why does the clock even work? (maps to: Discussion)

Two possible reasons, and **we deliberately don't pick one**:
1. **Real supply:** the halving cuts the new supply of Bitcoin in half on a fixed date, so the
   price reacts with a delay.
2. **Everyone's watching the same clock:** because the schedule is public and famous, people act
   around it, which makes it come true (self-fulfilling).

Either way, it's the **code** doing it, so the timing is knowable years ahead. Figuring out which
of the two reasons it is would be a future study.

---

## 7. What we are NOT claiming (maps to: Limitations): read this carefully

This is the most important part for your review. The paper is openly listing its own weak spots:
- **Only 3–4 cycles.** A tiny sample. We can't prove the halving *causes* the cycle.
- **We found the pattern looking backward.** The real test is the future predictions (Section 8).
- **Our fancy stats don't pass the strict test**, we say so out loud, and it sinks not just our
  numbers but everyone else's of that type.
- **We can't fully separate the economy** from the clock (both ~4-year rhythms).
- **Bottoms are weaker than tops**, the timing is much more reliable for tops.
- **The "53× / timing wins" result** depends on some choices and is heavily about dodging crashes;
  the honest, careful version of the edge is smaller.

If a critic attacks the paper, almost everything they'd say is **already written here by us first.**
That's the whole strategy.

---

## 8. The bets we're putting on the record (maps to: Predictions)

A real theory of timing should name dates **before** they happen:
1. **A bottom between about October 5 and November 16, 2026.** (We call this the *weaker* bet,
   because bottoms are less reliable.)
2. **A top 525–546 days after the next halving.** We give it as "days after the halving," **not** a
   fixed calendar date, because the halving's exact day isn't set yet (it drifts). At today's
   estimate that's roughly **late 2029**, which we'll sharpen as the halving gets close.

And the receipt: back in **January 2025**, the author publicly called an October 2025 top, nine
months early, using the old "18 months after halving" rule. The **timing was right** (top came in
October). The **price guess was wrong** (he said $150k–$200k; it hit ~$126k). That split, right on
*when*, wrong on *how much*, is literally the paper's whole point happening in real life.

---

## 9. The bottom line (maps to: Conclusion)

Every price-based way of reading Bitcoin's cycle is dying, in a measured, explainable way: the
swings shrink every cycle, so the indicators go quiet. The economy doesn't explain it either. The
one thing left standing is the clock written into Bitcoin's code in 2009. The amplitude is dying;
the clock is not. Bitcoin, at the end of the day, is code, and it keeps its own time.

---

### How to use this for your review

Read each numbered part above, then (if you want) flip to the matching section in the real PDF to
see the exact numbers and wording. If any point here doesn't match your understanding, or you'd
phrase a claim differently, that's exactly the kind of thing to flag before we send it.
