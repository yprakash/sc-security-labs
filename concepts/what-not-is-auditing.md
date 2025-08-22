# What Auditing Is Not
#### Avoiding Common Misconceptions in Smart Contract Security

Smart contract auditing is often misunderstood.  
A good auditor doesn’t just hunt for profitable hacks or guess an attacker’s incentives. Instead, the focus is on **protocol correctness** and whether the contract can maintain its **intended invariants**.  
This post highlights what auditing is not, with examples of common traps to avoid.

### 🔹 1. Auditing is not guessing attacker motives
An auditor’s role is to identify when the contract’s state can be broken — regardless of whether it’s “_economically rational_” for an attacker to exploit it.
- Wrong mindset:
  > “This bug costs the attacker gas, so it’s fine.”
- Correct mindset:
  > “This bug allows state to desynchronize from expectations. That’s a vulnerability.”

⚠️ Why this matters: Attacker incentives can change overnight (governance wars, sabotage, griefing). A protocol must be secure **even if attackers are irrational or willing to lose money**.

### 🔹 2. Auditing is not about speculation
You don’t need to predict who will attack, when, or why.  
Auditing asks: Can the contract be forced into an invalid state?  
If yes, then it’s a reportable issue.

### 🔹 3. Auditing is not only about “drain all funds”
High-severity bugs often involve theft.  
But state inconsistencies can also be catastrophic:
- Balance updates skipped or mis-ordered
- Locked funds (unwithdrawable)
- Governance rights accidentally inflated
- Accounting totals drifting from actual reserves

Even without an immediate exploit path, **broken invariants undermine trust**.

### 🔹 4. Auditing is not about ignoring “minor” issues
Sometimes, a bug seems low impact. Example:
- SWC-107: Reentrancy
  - It doesn’t matter if an attacker makes only a few wei profit.
  - What matters: the contract allowed state updates to be bypassed.

**State inconsistency = vulnerability**.  
Always report it.

---
### ✅ Quick Rule of Thumb
#### 👉 Correct:
“There’s a vulnerability because state can desync.”
#### ❌ Wrong:
“There’s no vulnerability because attacker loses money.”

### 🔹 5. Auditing is not about assumptions
- Don’t assume admins are benevolent.
- Don’t assume users will follow documentation.
- Don’t assume attackers need to make a profit.

Auditing is adversarial: **prove correctness against the worst-case inputs**.

### 🔹 6. Auditing is not one thing
Even after a code review, security requires:
- Fuzzing
- Formal verification
- Monitoring & alerting
- Testnets / audits before deployment
- Clear upgrade & kill-switch policies

Auditing is just one layer of defense.

### 📝 Takeaway
Auditing = checking invariants, state consistency, and correctness.  
It’s **not**:
- guessing motives
- speculating incentives
- ignoring “small” state bugs
- focusing only on direct profit hacks

When in doubt:
> If the state/invariants can break, report it.
