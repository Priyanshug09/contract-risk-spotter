# PRD: AI Contract Risk Spotter

## 1. Summary

IT agency owners sign vendor contracts they don't have time to read carefully, and existing AI tools hallucinate when asked to summarize legal risk. This PRD describes a web app that reads an uploaded contract PDF, flags risky clauses by severity, and backs every flag with an exact quote from the document — so the user can trust the output instead of double-checking it.

## 2. Contacts

| Name | Role | Comment |
|---|---|---|
| Priyanshu Gupta | Founder / Builder | Owns product, engineering, and ships the MVP solo this week |

*This is a one-person build. Add rows here if a designer, advisor, or early reviewer joins.*

## 3. Background

IT agency owners and project managers sign 10-20 vendor Master Service Agreements (MSAs) a month. These are often 50+ pages, written to favor the vendor, and contain clauses (liability caps, auto-renewal, IP assignment) that the signer is legally bound by but rarely has time to read in full.

General-purpose AI chatbots (ChatGPT and similar) can summarize a contract today, but they're known to hallucinate: inventing clause numbers, paraphrasing risks that aren't actually in the text, or missing risks that are. In legal contexts a hallucinated risk — or a missed one — is not a minor UX bug, it's a liability problem. That gap in trust is why most agency owners still read contracts manually or skip reading them entirely.

What's new: large context-window models (Claude Sonnet 4.6 and similar) can now ingest a full 50-page PDF directly and return structured, citation-grounded output reliably enough to build a product around — this wasn't practical with earlier-generation models.

## 4. Objective

**Objective:** Give IT agency owners a fast, trustworthy way to find the risky clauses in a vendor contract before they sign — without reading the whole document and without worrying the AI is making things up.

**Why it matters:** Every contract an agency owner signs without full review is a liability exposure they're carrying personally. A tool that surfaces real risk, provably grounded in the actual text, removes the trust barrier that keeps people from using AI for this today.

**Key Results (MVP, ship this week):**
- 100% of flagged risks include a `raw_quote` that is verbatim, locatable text from the source PDF (zero hallucinated citations).
- Median time from upload to full risk breakdown is under 60 seconds.
- The model returns valid, UI-parseable JSON on at least 95% of uploads without a crash.

*Note: these are quality/reliability targets for the MVP, not adoption or revenue metrics — there's no user base yet to measure those against.*

## 5. Market Segment(s)

**Who:** IT agency owners and project managers who personally sign vendor contracts — technical enough to run the business, but not lawyers, and without in-house legal review for every deal.

**Defining job, not demographic:** the job is "decide whether to sign this vendor contract, today, without legal counsel." Anyone doing that job — regardless of company size or industry — has the same underlying need.

**Constraints on this segment:**
- High contract volume (10-20/month) relative to time available — review has to be fast or it won't happen.
- No budget or workflow for routing every contract to a lawyer.
- Carries personal/business liability for clauses they didn't catch.

## 6. Value Proposition(s)

**Job to be done:** "Tell me what's dangerous in this contract before I sign it, and prove it so I don't have to re-read the whole thing to check you."

**What customers gain:**
- A risk breakdown in under a minute instead of an hour-plus manual read.
- Confidence to act on the AI's output because every flag is tied to an exact quote, not a paraphrase.

**Pains avoided:**
- Signing a contract with a hidden liability cap, forced auto-renewal, or IP assignment clause.
- The specific pain of *general* AI tools: confidently-stated risks that turn out to be invented or misquoted.

**Why this beats the alternative:** ChatGPT-style tools are faster than a lawyer but not trustworthy for this use case — they don't force themselves to quote the source. This product's core differentiator is the citation constraint described in Section 7.4: if the AI can't find the exact text, it isn't allowed to report the risk. That's a narrower promise than "summarize this contract," but it's one the user can actually verify in two clicks.

## 7. Solution

### 7.1 UX / User Flow

1. User opens the web app.
2. User uploads a contract PDF (50-page max).
3. App encodes the PDF and sends it to the Claude Sonnet 4.6 API with a fixed system prompt.
4. App parses the returned JSON.
5. UI shows a dashboard of flagged risks — High-risk items in red alert boxes, Medium-risk items styled distinctly but less urgently.
6. User clicks "View Raw Proof" on any flag to see the exact quoted sentence(s) from the contract.

### 7.2 Key Features

**Risk extraction engine**
The core feature. The LLM reads the uploaded contract and returns a structured JSON object per flagged risk: a plain-language risk summary, a severity tag (High/Medium), a page/paragraph citation, and a verbatim `raw_quote` from the source text.

**Risk dashboard**
Visual summary of all flagged risks, sorted by severity. High-risk items are visually isolated (red alert boxes) so the highest-stakes issues can't be missed in a skim.

**"View Raw Proof" verification**
One click surfaces the exact quoted text behind any flag, letting the user check the AI's claim against the source instantly rather than trusting it blindly.

**Risk tagging criteria**
- **High risk:** limits liability, forces auto-renewal, assigns IP to the vendor, lacks a clear exit clause.
- **Medium risk:** unusual tax indemnification, vague SLA references, unfair governing law.

### 7.3 Technology

Stack choice matters more than usual here because the failure mode (Section 7.4 Fail State) is a lawsuit, not a bad UX review. No shortcuts on the two components that touch grounding.

- **LLM — Claude Sonnet 4.6 via API.** Given the full PDF (base64-encoded) plus a strict system prompt. Chosen for its context window (large enough to comfortably hold a 50-page contract) and its track record on strict formatting and citation adherence, which is the property this whole product depends on.
- **PDF parser — LlamaParse or Unstructured.io, not PyPDF.** Basic PyPDF-style extraction mangles tables and destroys paragraph structure on real-world contracts. If the extracted text is garbled, the LLM is working from corrupted input and will hallucinate regardless of how good the prompt is — the parser is as load-bearing as the model for the anti-hallucination guarantee in Section 7.4.
- **Frontend — Streamlit.** Optimized for shipping this week, not for visual polish. This is a portfolio/proof-of-concept build, not a SaaS UI; Streamlit gets PDF upload and a JSON-driven dashboard working fast at the cost of design flexibility. Revisit if this moves beyond MVP.
- Output contract: structured JSON with required fields including `raw_quote`; malformed or missing-citation output should be treated as "no risk found" rather than displayed.

*Note on model naming: the source brief for this stack referenced "Claude 3.5 Sonnet." I've used Claude Sonnet 4.6 throughout this PRD per your earlier correction — flagging the discrepancy in case the 3.5 reference was intentional (e.g., copied from an older spec) rather than a slip.*

### 7.5 System Prompt (V1)

This is the actual prompt driving the grounding constraint in Section 7.4 — kept verbatim in the PRD so the engineering spec and the product spec don't drift apart.

```
You are a ruthless legal analyst specializing in IT agency contracts.

CONTEXT & CONSTRAINTS:
You will be provided with a legal document (maximum 50 pages).
You are strictly forbidden from using outside knowledge. If you cannot find the exact text in the document to support a claim, DO NOT OUTPUT IT. Zero hallucinations.

TASK:
1. Read the document and identify clauses that pose a risk to the IT agency.
2. If a clause limits liability, forces auto-renewal, assigns IP unfairly, or lacks a clear exit clause, tag it as [HIGH RISK].
3. If a clause is unusual, vague, or unfavorable but manageable, tag it as [MEDIUM RISK].
4. Every single bullet point MUST end with a citation formatted exactly like this: [Page X, Paragraph Y].

OUTPUT FORMAT:
- Output ONLY a bulleted list.
- Do not include introductions, conclusions, or conversational filler.
- Example format:
  - [HIGH RISK] The vendor limits total liability to the fees paid in the last month, exposing the agency to massive uncovered damages. [Page 12, Paragraph 3]
  - [MEDIUM RISK] The notice period for termination is 90 days, which is longer than standard. [Page 5, Paragraph 1]
```

**Open question this raises:** Section 4/7.2 of this PRD specifies structured JSON output (with a `raw_quote` field) as the contract between the LLM and the UI, but this prompt specifies a plain bulleted-list output instead. Those two are not the same format — a bulleted list with inline citations is easier to get right on the first try, but the UI's "View Raw Proof" feature and severity-based dashboard rendering (Section 7.2) assume parseable JSON fields, not free text. Before building the UI, decide which one is actually V1: either adapt this prompt to emit JSON (riskier — JSON-formatting compliance under a 50-page input is a separate failure mode worth testing), or adapt the UI to parse this bulleted format (simpler, but means giving up structured fields like a dedicated `raw_quote` key unless you parse it out of each bullet). I'd lean toward keeping the prompt's plain-bullet format for V1 since it's simpler and the citation is already inline — but that's a call worth making deliberately, not by default.

### 7.4 Assumptions — the "1%" constraint: grounding & anti-hallucination

**Fail state:** the AI hallucinates a clause that isn't there, or — worse — misses a real hidden liability clause. The user, trusting the tool, signs the contract anyway. Result: a catastrophic lawsuit or financial loss for the agency, caused or enabled by this product. Every design choice in this section exists to make that fail state as unlikely as a prompt and parsing pipeline can make it.

This is the load-bearing engineering assumption of the whole product, so it's worth stating plainly rather than burying it as a feature:

- **Zero-tolerance policy:** the LLM is not allowed to use outside knowledge — only what's in the uploaded document.
- **Forced citation:** the system prompt requires a `[Page X, Paragraph Y]` citation on every flagged risk.
- **Proof mechanism:** the JSON schema requires a `raw_quote` field. If the model cannot locate exact source text for a risk, it must not output that risk at all — silence is preferred over an unverifiable claim.

**This is an assumption, not a guarantee.** Prompt-level constraints reduce hallucination risk but don't mathematically eliminate it — Claude Sonnet 4.6 can still occasionally produce a paraphrased or slightly-off quote despite instructions to the contrary. I haven't validated this against a test set of real contracts yet, so "100% of flagged risks have a verifiable raw_quote" (Section 8 / Key Results) should be treated as the target the system is designed to hit, validated by a manual spot-check process, not a property that's proven by the prompt alone. Before relying on this for real contract decisions, it's worth running a validation pass: pull a sample of flagged risks, manually confirm the quote appears verbatim in the source PDF, and track the failure rate.

A second open assumption: the product assumes IT agency owners will trust an AI tool with confidential vendor contracts. That's plausible given the time pressure they're under, but it's unvalidated — worth a quick gut-check with a few target users before investing past the MVP.

## 8. Release

**Scope for V1 (this week):**
- PDF upload, single contract, max 50 pages.
- Risk extraction with High/Medium tagging per Section 7.2 criteria.
- Dashboard with red alert boxes for High risk.
- "View Raw Proof" raw-quote verification.
- No login/authentication — single-session, stateless use.

**Explicitly out of scope for V1:**
- User authentication / login.
- Contract redlining or automated editing.
- Word document (.docx) support — PDF only.
- Comparing two contracts against each other.

**Why this scope:** the goal this week is to prove the grounding mechanism works end-to-end on a real contract, not to build a multi-tenant SaaS product. Anything that doesn't directly test "can we extract risk with a verifiable quote" is deferred.

**After V1, in rough priority order (not committed, not dated):**
1. Validate the zero-hallucination claim against a real test set (see Section 7.4) before showing this to any actual prospective user.
2. .docx support, since many MSAs circulate as Word docs before being signed as PDF.
3. Contract-to-contract comparison.
4. Authentication, if this moves from a personal tool toward something other people log into.
