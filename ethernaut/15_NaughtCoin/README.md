# 🧩 Level 15: Naught Coin
### 🔒 Goal
Drain all your tokens from the contract despite a time lock that prevents transfers.

---
### 🚨 Vulnerability Insight
The `transfer()` function is locked by a `require()` until 10 years pass.

However, ERC20 also exposes `approve()` and `transferFrom()`, which are not restricted.

This is a classic mistake: modifying only `transfer()`, but forgetting other ways tokens can move.
```solidity
function transfer(address _to, uint256 _value) public lockTokens returns (bool) {
    super.transfer(_to, _value);
}
```
The `lockTokens` modifier blocks `transfer` for a period of time.  
However, `approve` and `transferFrom` are still available from the inherited ERC20 implementation.

---
### 🎯 Exploit Strategy
- Deploy an attacker contract (optional) or use an EOA.
- Call `approve(attacker, balance)` from your player wallet.
- Use `transferFrom(player, attacker, balance)` to drain all tokens bypassing the lock.

---
### 🔍 Real-World Relevance
This challenge highlights a common ERC20 oversight:
- Locking or blacklisting logic often only targets `transfer()`, ignoring `transferFrom()`.
- Real-world token contracts need to secure all token-moving mechanisms, including:
  - transfer()
  - transferFrom()
  - approve() + allowance flow
  - permit() (if using EIP-2612)
