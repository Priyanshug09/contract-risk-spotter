# Product Testing & Evaluation Strategy

## Project Context

As the AI Product Manager for this project, I designed manual evaluation test cases to validate the core product constraint:

> **Zero-tolerance for hallucinated legal-risk extraction.**

The goal is not just to check whether the AI can summarize a contract. The real test is whether the system can reliably identify legal risks, stay grounded in the source document, and avoid inventing issues that are not present.

---

## Core Evaluation Principle

For legal AI products, trust is the product.

The system must satisfy two critical requirements:

1. **Catch real risks**
   It must identify high-risk clauses even when they are buried deep inside long documents.

2. **Avoid hallucinated risks**
   It must not invent risks just to produce an output.

---

## Test Case 1: The Hidden Landmine

### Test Type

**Accuracy Test / False Negative Detection**

### Objective

Prove that the AI does not become “lazy” on long documents and maintains strict grounding throughout the full contract.

### Action

Upload a 30-page standard SaaS agreement, but manually insert a highly toxic clause on Page 28.

Example toxic clause:

> “Client assumes all liability for data breaches.”

### Expected Result

The app must:

* Flag the clause as **[HIGH RISK]**
* Explain why it is risky
* Provide a citation pointing exactly to **Page 28**
* Avoid vague references such as “somewhere in the agreement”

### Fail State

The test fails if:

* The app misses the clause
* The app flags it without a citation
* The citation points to the wrong page
* The explanation is generic or unsupported by the contract text

---

## Test Case 2: The Innocent NDA

### Test Type

**False Positive Test / Hallucination Detection**

### Objective

Prove that the AI does not hallucinate risks just to satisfy the user’s expectation of finding issues.

### Action

Upload a basic 2-page mutual Non-Disclosure Agreement that contains no unfair liability limits, aggressive indemnity terms, hidden auto-renewals, or one-sided termination clauses.

### Expected Result

The app should return either:

* An empty risk list, or
* A clear message such as:

> “No significant legal risks were found in this document.”

The app must not invent fake risks.

---

## Test Case 3: Garbage In, Graceful Out

### Test Type

**Resilience Test / Error Handling**

### Objective

Prove that the UI and backend handle unexpected user behavior without crashing.

### Action

Upload an unsupported or invalid file type instead of a PDF contract.

Examples:

* `.jpeg` image
* `.docx` Word document
* 1-page plain text file
* Empty file
* Corrupted PDF

### Expected Result

The app should not crash or show a white screen of death.

Instead, it should display a clear, user-friendly error message.

Example:

> “Invalid file type. Please upload a PDF contract.”

---

## Risk Evaluation Logic

| Risk Type           | Product Risk                              | Business Impact                           |
| ------------------- | ----------------------------------------- | ----------------------------------------- |
| False Negative      | The AI misses a real legal risk           | Lawsuit, financial exposure, broken trust |
| False Positive      | The AI invents a non-existent risk        | Loss of credibility and user confidence   |
| Poor Error Handling | The app crashes or gives unclear feedback | User frustration and enterprise rejection |

---

## Product Principle

In enterprise AI, the goal is not to produce more text.

The goal is to produce **grounded, verifiable, and decision-safe output**.

For legal-risk extraction, the cost of a false negative is a lawsuit.

The cost of a false positive is broken trust.

These tests prove whether the system is actually reliable.
