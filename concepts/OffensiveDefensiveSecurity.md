# Offensive vs Defensive Security in Smart Contracts
Smart contract security has two complementary sides:
- 🛠 **Defensive** security — building code that resists attack
- 🗡 **Offensive** security — thinking like an attacker to break assumptions

Both are essential. A good auditor (or developer) must **wear both hats**.

## 🔹 Offensive Security
> “If I were malicious, how would I break this?”

Offensive security is about adopting the mindset of an attacker.  
You deliberately look for ways to:
- Abuse assumptions
- Bypass intended logic
- Force edge cases
- Reorder transactions or calls

Example
```solidity
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount, "Not enough funds");
    (bool ok,) = msg.sender.call{value: amount}("");
    require(ok, "ETH transfer failed");
    balances[msg.sender] -= amount;
}
```
- Defensive developer’s view: Code checks balance, sends ETH, then updates.
- Offensive attacker’s view: Call reenters before `balances[msg.sender]` updates → withdraw twice.

## 🔹 Defensive Security
> “How do I make this unbreakable?”

Defensive security means anticipating attacks and writing code that **closes all doors before they’re tested**.

### Practices
- Checks-Effects-Interactions (CEI)
- Use `ReentrancyGuard`
- Explicit access controls
- Limit external calls & complexity
- Fail-safe defaults (e.g., pull over push payments)

#### Fixed Example
```solidity
function withdraw(uint256 amount) external nonReentrant {
    require(balances[msg.sender] >= amount, "Not enough funds");
    balances[msg.sender] -= amount;
    (bool ok,) = msg.sender.call{value: amount}("");
    require(ok, "ETH transfer failed");
}
```
## 🔹 The Feedback Loop
Offense and defense are **not opposites** — they **reinforce** each other:
- Offensive testing reveals weak spots.
- Defensive coding patterns strengthen them.
- Repeat until both perspectives converge.

## 🔹 Mindset Shift
- Offensive: **Exploit-driven** — “How can I profit / break invariants?”
- Defensive: **Invariant-driven** — “How do I guarantee correctness under all inputs?”

An auditor must **toggle between both lenses**.  
A developer should learn **offense to understand defense**.

## 📝 Conclusion
- 🗡 Offensive security = attacker’s perspective → find weak assumptions.
- 🛡 Defensive security = builder’s perspective → enforce invariants, reduce attack surface.
- ⚖️ Strong protocols come from **balancing both**.
