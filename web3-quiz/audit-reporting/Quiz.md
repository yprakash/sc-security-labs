## FAQs

You identified a bug that can lock user funds only if a governance timelock executes a specific parameter change that is unlikely but plausible. Best severity framing?  
A. Critical (loss of funds possible)  
B. High (impact high, likelihood high)  
C. Medium (impact high, likelihood low; document conditional path)  
D. Low (governance risk is out of scope)
> C
- Impact is high (funds locked), but likelihood depends on governance execution. That’s textbook _Medium_: “**high impact, low likelihood**.” Marking it “Critical” would dilute credibility.

A good “Impact” section should primarily:  
A. Describe how hard the bug is to exploit  
B. Quantify what assets/roles could be harmed and maximum plausible loss under stated assumptions  
C. Explain the root cause line-by-line  
D. List all tools used
> B
- Impact = **what can go wrong, who loses what, and how much**. Not just exploit difficulty (likelihood).

Which reproduction section is strongest?  
A. “Run tests; it fails.”  
B. “Use Foundry: `forge test -m test_repro_DoS` on commit X; env: Solidity 0.8.23; results: revert at L142 with error Y; tx trace attached.”  
C. “Likely reproducible, didn’t try.”  
D. “Slither flagged it.”  
> B
- Precise reproduction details are key: test name, commit hash, env, tx trace. It is advised to include **commit + PoC instructions**.

Choosing a title for a reentrancy issue in a claim function guarded by `nonReentrant`, but state updates occur after an external ERC777 callback:  
A. “Reentrancy”  
B. “Potential reentrancy due to ERC777 hooks despite `nonReentrant` (state update after external callback)”  
C. “Callback ordering”  
D. “Gas griefing”
> B
- The title must pinpoint **why** nonReentrant fails (ERC777 hooks allow reentrancy before state update). Clear, specific, not generic.

When is “Acknowledged / Won’t Fix” acceptable for High severity in reporting?  
A. Always, if the team signs off  
B. Only if mitigated by out-of-band controls and clearly justified; otherwise High should be **Resolved** before mainnet  
C. Never  
D. When a bug bounty is active  
> B
- High severity “Won’t Fix” is only acceptable if offset by **external guarantees** (multisig control, off-chain process). Otherwise Highs must be fixed pre-mainnet.

For MEV-related risks (e.g., sandwichable swap function), the report should include:  
A. A general statement that MEV exists  
B. A concrete attack path with miner/validator ordering assumptions, profit calculus, and mitigations (e.g., TWAP, commit-reveal, off-chain RFQ, private mempool)  
C. A link to Flashbots docs only  
D. “Use `nonReentrant`”  
> B
- Always concrete MEV analysis is expected: sandwich example, profit calculation, mitigations. “MEV exists” is not enough.

Two distinct functions share the same root cause (unchecked external call return leading to state desync). Best reporting approach?  
A. Separate findings for each function with duplicated text  
B. One root-cause finding listing all affected functions/paths under “Affected Scope,” with per-path notes  
C. One finding for the worst function, ignore others  
D. Put it in Gas Optimizations  
> B
- Best practice: one root-cause finding, list all functions under “Affected Scope.” Avoid duplicate tickets.

Which Status lifecycle wording is most precise for audit trails?  
A. Open → Fixed → Closed  
B. Identified → Pending Review → Done  
C. Open → Resolved (commit/tag PR#) → Verified (auditor retest hash/notes) → Closed  
D. Found → Patched  
> C
- Precise lifecycle = Open → Resolved (commit ref) → Verified (auditor retest) → Closed. This preserves traceability for regulators and users.

A report includes an “Intended vs Actual Behaviour” table. What belongs under Intended?  
A. What the code currently does on testnet  
B. The protocol’s documented design/spec claim for the function  
C. The auditor’s opinion of best practice  
D. The optimizer’s expected outcome  
> B
- Intended = protocol spec/design docs. Actual = observed code behaviour. This table highlights mismatches and avoids assumptions.

Subtle: Slither flags `tx.origin` in a function restricted to EOAs by business design (EOA-only staking). No value transfers depend on it; downstream calls are guarded. Best classification?  
A. High — always dangerous  
B. Medium — could allow phishing  
C. Low/Informational with design justification + recommend `msg.sender` pattern and explicit EOA-check alternative (e.g., `extcodesize`) and phishing caveat  
D. Not a finding  
> C
- `tx.origin` is usually dangerous (**phishing**), but here, business logic restricts EOAs. Report as **Low/Informational**: acknowledge risk, suggest safer patterns.

What must be present when assigning Critical severity?  
A. Potential permanent loss of all funds with trivial exploit; no user action needed  
B. Any revert in production  
C. A failing test  
D. A gas inefficiency leading to higher fees  
> A
- Critical = _loss of all user funds with trivial exploitation_. Reverts or gas inefficiencies don’t qualify.

An upgradeable proxy lacks an `initializer` guard and ownership is set in constructor of the logic contract. The cleanest report title?  
A. “Constructor misuse”  
B. “Upgradeable proxy uninitialized — privilege hijack risk (owner can be claimed)”  
C. “Upgrades issue”  
D. “Access control nit”  
> B
- “Upgradeable proxy uninitialized — privilege hijack risk” is the industry-standard phrasing. Constructor misuse is secondary.

In the Recommendations section for a reentrancy-prone withdraw, the most auditor-useful guidance is:  
A. “Add `nonReentrant`.”  
B. “Use checks-effects-interactions OR pull pattern; move state updates before external calls; prefer `call` with explicit error handling; add reentrancy tests/invariants.”  
C. “Use `transfer` to limit gas.”  
D. “Use more comments.”  
> B
- pattern-level remediation (CEI, pull payments, reentrancy tests). “Just add nonReentrant” is lazy.

Scope hygiene: which is best for traceability?  
A. “Audited repo.”  
B. “Scope: contracts `X.sol`,`Y.sol`; commit `abc1234`; compiler 0.8.26; settings (optimizer 200 runs); networks (Sepolia/Mainnet); exclusions listed.”  
C. “Everything in /contracts.”  
D. “The dApp.”  
> B
- Scope must include contracts, commit hash, compiler version/settings, networks.

Which report template is best suited for a single vulnerability?  
A. Title, Code Snippet, Fix PR Link  
B. Title, Severity (with rationale), Description, Impact, Likelihood, Repro Steps/PoC, Affected Scope (files/commits), Recommendations, Status, References/Notes  
C. Title, CWE ID, CVSS, Fix  
D. Title, Risk, Proof
> B
- Full structure: severity rationale, description, impact, likelihood, reproduction, scope, recs, status, refs. Not just CWE or PoC.
