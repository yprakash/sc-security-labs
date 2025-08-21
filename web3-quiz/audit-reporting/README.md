# Audit Reporting in Solidity Security Reviews

## Why Audit Reporting Matters
In security reviews, the *findings themselves* are only half the story.  
The other half — how you **communicate** those findings — determines whether developers, stakeholders, and external users can understand and act on them.  

Audit reporting emphasizes:
- **Precision:** exact commit scope, reproduction steps, and intended vs actual behaviour.
- **Traceability:** linking every fix to a commit, PR, or test so downstream users can verify.
- **Severity Rationale:** impact × likelihood, not just “sounds scary.”
- **Actionability:** concrete remediation paths, not generic warnings.

A strong report is a *technical artifact* that doubles as both audit log and public trust document.

---

## Anatomy of a Finding

### 1. Title
Concise, descriptive, and **cause + effect oriented**.  
Bad: `Reentrancy`  
Good: `Reentrancy possible in ERC777 claim despite nonReentrant guard (state updated after external callback)`

### 2. Severity
Top audit firms (like Hashlock), uses this severity model:

- **Critical:** Permanent loss of all funds, trivial exploit, no user action required.  
- **High:** Significant financial loss, governance takeover, or DoS with high likelihood.  
- **Medium:** High impact but gated by low-probability conditions (e.g., governance parameter mis-set).  
- **Low:** Niche, informational, or mitigated by business logic.  
- **Informational:** Style, best practices, clarity issues.  

> Always justify severity with **Impact** (what’s at risk) and **Likelihood** (how feasible).

### 3. Description
Narrative of the issue. Includes root cause analysis, affected functions, and how the bug arises.

### 4. Impact
Quantifies **who loses what, and how much**.  
- “All stakers’ funds can be drained if attacker triggers callback before state update.”  
- “Funds are locked if governance sets fee > 100% (unlikely, but plausible).”

### 5. Likelihood
- **High:** No external dependency, trivial to exploit.  
- **Medium:** Exploitable, but requires parameter changes, governance actions, or off-chain coordination.  
- **Low:** Theoretical, requires unrealistic conditions.  

### 6. Reproduction / Proof of Concept
A clear step-by-step path:
- Environment: Solidity version, optimizer settings, commit hash.  
- Commands: `forge test -m test_repro_DoS --fork-url ...`  
- Output: revert trace, logs, or transaction simulation.  

This ensures findings are **verifiable by anyone**.

### 7. Intended vs Actual Behaviour
| Intended (per spec) | Actual (in code) |
|----------------------|------------------|
| Users withdraw instantly without reentrancy risk | ERC777 callback fires before state update, allowing recursive drain |

This table is deceptively powerful: it captures the **design contract** vs **code reality** without long prose.

### 8. Affected Scope
List contracts, functions, commits:
- Scope: Token.sol, Staking.sol
- Commit: a1b2c3d
- Compiler: 0.8.26, optimizer 200 runs
- Networks: Sepolia, Mainnet planned

### 9. Recommendations
Top audit firms prefers **pattern-level fixes**:
- Use Checks-Effects-Interactions (CEI).  
- Replace push with pull payments.  
- Add `initializer` guards in upgradeable proxies.  
- Explicit error handling on low-level calls.  
- Invariants & fuzzing to test assumptions.  

Avoid lazy advice like “just add `nonReentrant`.”

### 10. Status Lifecycle
Precise audit trails:
- **Open → Resolved (commit/PR ref) → Verified (auditor retest hash) → Closed**  

This matters for compliance, insurance, and investor confidence.

---

## Real-World Vulnerability Examples

1. **Upgradeable Proxy Uninitialized**  
   - *Impact:* Anyone can call `initialize` and seize ownership.  
   - *Severity:* Critical.  
   - *Title:* `Upgradeable proxy uninitialized — privilege hijack risk (owner can be claimed)`  
   - *Recommendation:* Use OpenZeppelin `initializer` pattern.  

2. **ERC777 Callback Reentrancy**  
   - *Impact:* Attacker drains all deposits by reentering before state update.  
   - *Severity:* Critical.  
   - *Recommendation:* Apply CEI, update balances before external calls, add reentrancy tests.  

3. **Governance-Conditional DoS**  
   - *Impact:* Funds locked if admin sets parameter incorrectly.  
   - *Severity:* Medium (impact high, likelihood low).  
   - *Lesson:* Severity is not just impact — always weight by plausibility.

---

## Key Takeaways
- Findings must be **actionable, reproducible, and traceable**.  
- Severity without **impact × likelihood** justification is meaningless.  
- Use the **Intended vs Actual Behaviour** table to cut through ambiguity.  
- Recommendations should teach **defensive coding patterns**, not one-liners.  
- Scope hygiene (commit hash, compiler, networks) = credibility.  

---

## Conclusion
Audit reporting isn’t just about finding bugs — it’s about:
- Demonstrating **rigor** (commit-level traceability).  
- Showing **threat modelling maturity** (impact vs likelihood framing).  
- Communicating **credibly to non-technical stakeholders** (clarity, status lifecycle).  
