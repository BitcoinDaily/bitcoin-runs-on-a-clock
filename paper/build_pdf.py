"""
build_pdf.py — manuscript.md -> styled HTML (figures embedded after the references)
-> PDF via Edge headless. Run from PowerLaw/paper/: python build_pdf.py
"""
import base64
import os
import re
import subprocess
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
# Edge headless print-to-pdf silently broke (exit 0, no file) on 2026-06-11; Chrome verified
# working. Keep both as candidates, Chrome first.
BROWSERS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
EDGE = next(b for b in BROWSERS if os.path.exists(b))

# Order = order of first appearance in the text. Figure NUMBERS are assigned automatically from
# this order (see main()); in-text references use {{FIGREF:key}} tokens that resolve to the same
# numbers, so figures can be reordered or inserted without renumbering anything by hand.
FIGS = [
    ("figC_clock_alignment.png", "Every mature cycle top lands in the same narrow band on the "
     "halving clock: 525, 546, and 534 days after its halving, three cycles apart. The 2013 first "
     "cycle, still immature, peaked earlier at 371 days. This is the paper's central claim in one "
     "picture."),
    ("fig1_powerlaw.png", "Bitcoin price vs time since genesis with the causally fit "
     "power-law trend (top) and the convergence of the expanding-window exponent to 5.61 (bottom)."),
    ("figA_null_distribution.png", "The turn-timing null. Left: across 10,000 block-bootstrapped "
     "Bitcoin histories run through the identical mechanical turn rule, none clusters its three "
     "mature tops as tightly as the observed 21 days (zero under the deterministic construction; "
     "0.16% under the conservative selection-symmetric variant). Right: the same null reproduces "
     "the bottom cluster in 38% of histories, so bottom timing is largely intrinsic to the "
     "drawdown process, not the clock."),
    ("fig5_caller_timeline.png", "Every canonical indicator firing, 2011\u20132026. "
     "The top-callers (red) collectively marked every top through April 2021 and were all silent "
     "at the October 2025 top; bottom-callers (blue) still fired in 2022."),
    ("fig3_extremes_funnel.png", "The compression mechanism: every top-side per-cycle "
     "maximum declines monotonically; bottom-side minima end the era higher than they began, "
     "though not monotonically."),
    ("fig4_ic_decay.png", "Information coefficients per epoch (descriptive): fast price "
     "and on-chain signals decay or flip sign across cycles; the time-anchored and slowest "
     "trend-anchored signals hold direction."),
    ("fig6_maturation_crossover.png", "The maturation crossover: the power-law timing "
     "rule's Sharpe edge versus buy-and-hold improves monotonically across epochs and crosses "
     "positive in the current cycle on both BTC and ETH (the 2025\u201326 holdout is out of "
     "sample; suggestive, see Section 5.4)."),
    ("fig7_m2_vs_clock.png", "Liquidity turns versus the clock: M2-growth turning "
     "points miss Bitcoin tops by 67 to 253 days with mixed sign; the halving clock holds them "
     "to \u00b110 days."),
    ("figB_clock_placebo.png", "The four-year-clock placebo. The three mature tops cluster within "
     "21 days measured from the halving, versus 68 days from the US election cycle, 71 days from a "
     "typical random four-year clock, and 1,423 days from a fixed four-year calendar. None of "
     "2,000 random four-year clocks is as tight as the halving, so the regularity is specific to "
     "the halving event, not a generic four-year rhythm."),
    ("fig2_satoshi_clock_spiral.png", "The Satoshi Clock: Bitcoin's full history as a "
     "damped spiral. Angle = days since halving (CLOCK); radius = causal power-law deviation "
     "(SPRING). The three mature tops (triangles) all fall in the shaded 525\u2013546-day wedge, while "
     "their radius shrinks each cycle along the dashed inward arrow (SPRING +2.69 then +1.29 then "
     "+0.43). The grey loop is the immature first cycle (2013, top at 371 days). The amplitude is "
     "dying; the clock is not."),
    ("fig8_cycle_shape.png", "The clock governs the whole cycle, not just the turns. "
     "Left: each cycle's price path aligned by days since halving (cross-cycle correlation 0.72; "
     "random alignment 0.02). Right: average forward 90-day return by phase, flipping positive to "
     "negative at the mechanically dated top window (525\u2013546 days) and back near the bottom."),
]

CSS = """
@page { margin: 25mm 22mm; }
body { font-family: 'Georgia', 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.55;
       color: #111; max-width: 175mm; margin: 0 auto; }
h1 { font-size: 17pt; line-height: 1.25; margin-bottom: 4px; }
h2 { font-size: 13pt; margin-top: 22px; border-bottom: 1px solid #999; padding-bottom: 2px; }
h3 { font-size: 11.5pt; margin-top: 16px; }
/* never strand a heading (or its section divider) at the bottom of a page:
   keep it with the content that follows, and never split a heading across pages */
h1, h2, h3 { break-after: avoid; page-break-after: avoid;
             break-inside: avoid; page-break-inside: avoid; }
hr { break-after: avoid; page-break-after: avoid; }
p, li, table { orphans: 2; widows: 2; }
table { border-collapse: collapse; margin: 10px auto; font-size: 9.5pt;
        font-family: 'Segoe UI', Arial, sans-serif; }
th, td { border: 1px solid #bbb; padding: 3px 8px; text-align: center; }
th { background: #f0f0f0; }
blockquote { border-left: 3px solid #999; margin-left: 0; padding-left: 14px; color: #333; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f5f5f5; padding: 0 2px; }
.figure { page-break-inside: avoid; text-align: center; margin: 24px 0; }
.figure img { max-width: 100%; max-height: 230mm; }
.figure p { font-size: 9pt; font-style: italic; text-align: left; margin-top: 6px; }
hr { border: none; border-top: 1px solid #ccc; margin: 18px 0; }
"""


def main():
    md = open(os.path.join(HERE, "manuscript.md"), encoding="utf-8").read()
    body = markdown.markdown(md, extensions=["tables", "smarty"])

    # inject each figure inline at its [[FIG:key]] marker (placed at first mention in the text);
    # figure numbers are assigned automatically from FIGS order
    fignum = {fn.split("_")[0]: i + 1 for i, (fn, _) in enumerate(FIGS)}
    placed = 0
    leftovers = ""
    for fn, cap in FIGS:
        key = fn.split("_")[0]
        p = os.path.join(HERE, "figures", fn)
        b64 = base64.b64encode(open(p, "rb").read()).decode()
        cap_full = f"Figure {fignum[key]}. {cap}"
        div = (f'<div class="figure"><img src="data:image/png;base64,{b64}"/>'
               f"<p>{cap_full}</p></div>")
        marker_p = f"<p>[[FIG:{key}]]</p>"
        marker = f"[[FIG:{key}]]"
        if marker_p in body:
            body = body.replace(marker_p, div, 1)
            placed += 1
        elif marker in body:
            body = body.replace(marker, f"</p>{div}<p>", 1)
            placed += 1
        else:
            leftovers += div                         # fallback: append at end
    # resolve in-text {{FIGREF:key}} references to the same auto-assigned numbers
    unresolved = []
    for key, num in fignum.items():
        body = body.replace(f"{{{{FIGREF:{key}}}}}", f"Figure {num}")
    import re as _re2
    leftover_refs = _re2.findall(r"\{\{FIGREF:[^}]+\}\}", body)
    if leftover_refs:
        raise SystemExit(f"UNRESOLVED FIGURE REFERENCES: {set(leftover_refs)}")
    print(f"figures placed inline: {placed}/{len(FIGS)}")
    if leftovers:
        leftovers = "<hr/><h2>Additional Figures</h2>" + leftovers

    html = (f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<style>{CSS}</style></head><body>{body}{leftovers}</body></html>")
    html_path = os.path.join(HERE, "manuscript.html")
    open(html_path, "w", encoding="utf-8").write(html)
    print(f"HTML written ({len(html)/1e6:.1f} MB)")

    pdf_path = os.path.join(HERE, "Bitcoin_Runs_on_a_Clock_Molnar_2026_draft.pdf")
    import pathlib, tempfile, shutil, hashlib, zlib, re as _re
    # a stale PDF must never be able to satisfy the success check: remove it first
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    uri = pathlib.Path(html_path).as_uri()
    tmp_pdf = os.path.join(tempfile.gettempdir(), "manuscript_build.pdf")
    if os.path.exists(tmp_pdf):
        os.remove(tmp_pdf)
    r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={tmp_pdf}", uri],
                       capture_output=True, text=True, timeout=180)
    if not os.path.exists(tmp_pdf):
        print("browser stderr:", (r.stderr or "")[-800:])
        raise SystemExit("PDF NOT PRODUCED")
    shutil.move(tmp_pdf, pdf_path)
    # content certification: extract real text (browser PDFs use subset-font glyph IDs,
    # so raw stream grep finds nothing -- a proper extractor is required)
    from pypdf import PdfReader
    raw = open(pdf_path, "rb").read()
    reader = PdfReader(pdf_path)
    t = "".join(page.extract_text() or "" for page in reader.pages)
    sentinels = ["Provenance, stated precisely", "carry no weight whatsoever",
                 "most likely a peak", "statistical zero", "formal inference battery",
                 "eight parts", "126,296", "leave-one-cycle-out",
                 "after the next halving", "next-halving anchor",
                 "four-year-clock placebo", "governs the whole cycle",
                 "Mahmudov and Puell", "autocorrelation-robust (HAC)"]
    missing = [s for s in sentinels if s not in t]
    if missing:
        raise SystemExit(f"PDF BUILT BUT MISSING SENTINELS: {missing}")
    sha = hashlib.sha256(raw).hexdigest()[:12]
    print(f"PDF written and CONTENT-CERTIFIED -> {pdf_path}")
    print(f"  size {len(raw)/1e6:.1f} MB | sha256 {sha} | all {len(sentinels)} sentinels present")


if __name__ == "__main__":
    main()
