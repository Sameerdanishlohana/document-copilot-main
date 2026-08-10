# Client brief — Driftwood Capital

## The client

**Driftwood Capital** is an independent investment research firm with ~40 analysts. They sell deep equity research to institutional clients (hedge funds, mutual funds, pension funds) under annual subscriptions ($50K–$500K+ per client), plus custom commissioned research and analyst calls.

They don't manage money themselves. Their product is research and access to their analysts.

## How Driftwood makes money

- Analysts each cover ~15 US public companies in a specific industry (semiconductors, retail, energy, etc.)
- They produce written research reports, financial models, and stock-level recommendations
- Asset-management clients pay for the reports and for the right to call the analyst with questions
- Reputation is everything — a single bad call dents the franchise

## How they add value

- Their clients (portfolio managers at funds) don't have the bandwidth to read every 10-K, 10-Q, earnings transcript, and industry filing for the companies they invest in
- Driftwood's analysts have already done that reading and turned it into actionable summaries
- The value is *condensation*: turning thousands of pages into a one-page thesis the PM can act on

## The problem

Every Driftwood analyst spends roughly **half of every week** doing source-document intake — opening SEC filings, scanning for the sections they care about (risk factors, MD&A, business segments), copy-pasting passages, comparing year-over-year. Only after that intake work can they produce any original analysis.

The intake work is:

- Boring
- Necessary (you can't analyze what you haven't read)
- Repetitive across analysts (multiple analysts read the same Apple 10-K every January)
- The biggest single drag on analyst output

Hiring more analysts doesn't fix it — the intake bottleneck scales linearly with coverage. They want to fix the bottleneck.

## What they want

An internal chatbot — call it **Document Copilot** — where any Driftwood analyst can:

- Ask questions in plain English about any filing in Driftwood's curated corpus
- Get a sourced answer that cites the specific filing and the specific page
- Trust the answer enough to base downstream analysis on it
- Use it from a browser, logged in with their Driftwood email address
- See their own past conversations

## Example analyst questions

The current sample corpus contains 10-K filings for Apple, Amazon, Alphabet, Microsoft, and NVIDIA across fiscal years 2021–2025. The bot should be able to handle questions like these with cited answers and underlying passages:

1. Across Apple's 2021–2025 10-Ks, how did the revenue mix between iPhone, Services, Mac, iPad, and Wearables change, and which category appears to have contributed most to any mix shift?
2. For Amazon, compare AWS operating income and margin against North America and International from 2021–2025. In which years did AWS appear to fund losses or weaker profitability elsewhere?
3. How did NVIDIA describe demand drivers, customer concentration, and supply constraints for its Data Center business from fiscal 2021 through fiscal 2025?
4. Across Microsoft's 2021–2025 filings, what changed in the way the company describes Azure, AI infrastructure, and cloud capacity constraints?
5. For Alphabet, how did Google Search, YouTube ads, Google Network, subscriptions/platforms/devices, and Google Cloud revenue trends differ across the available 10-Ks?
6. Which of the five companies added, removed, or materially changed risk-factor language related to AI, cloud infrastructure, export controls, supply chain concentration, or regulation between 2021 and 2025?
7. For Apple and NVIDIA, what do the filings say about supplier concentration or dependence on third-party manufacturing, and did the wording become more or less urgent over time?
8. Compare capital expenditures and purchase commitments for Microsoft, Alphabet, Amazon, and NVIDIA. What do the filings imply about the scale and timing of AI/cloud infrastructure investment?
9. For each company, summarize the most important geographic revenue exposures disclosed in the latest 10-K, then identify any year-over-year changes that could matter to an analyst.
10. If an analyst asks whether the filings prove that generative AI improved margins for any of these companies, what evidence exists in the corpus, and where should the bot refuse to infer beyond the filings?

## What "trust" means here

This is a research firm. Their entire business is being right. The bot must:

- **Never invent facts.** If the answer isn't in the corpus, it says so.
- **Always cite.** Every claim links to the source filing + page.
- **Show the underlying passage** so the analyst can verify in one click.

A wrong but confident answer is worse than no answer. Hallucinations kill the product.

## Constraints

- Corpus: SEC filings (10-Ks and 10-Qs) for S&P 500 companies, 2020–2025
- Source: SEC EDGAR (public domain)
- Users: ~40 Driftwood analysts, plus a few partners
- Login: Driftwood email addresses (no SSO required)
- Hosting: must run on a small/medium cloud footprint; Driftwood has no infra team

## Out of scope (explicitly)

- Trading recommendations or stock picks
- External data sources (no news, no social, no alternative data)
- Anything generating analysis not grounded in the corpus
- Multi-tenant / multi-client. This is Driftwood-internal only.
- Billing, plans, paywalls
- Mobile app

## Definition of done

The analyst pilot group (5 senior analysts) tries it for a week and reports it saves them at least 3 hours per analyst per week. If yes, Driftwood rolls it out firm-wide.
