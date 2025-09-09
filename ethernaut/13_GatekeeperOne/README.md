# 🧩 Ethernaut Level 13: Gatekeeper One
### 🔒 Goal

The contract has three gate checks that must be passed in a single call to enter().  
Unlock the `entrant` variable by passing all three gate checks in a single transaction.

---
### 🚪 Gate Breakdown
#### 🛑 gateOne
```solidity
require(msg.sender != tx.origin);
```
- Prevents direct calls from EOA.
- ✅ Use a **contract** to make the call.
---

#### 🛑 gateTwo
```solidity
require(gasleft() % 8191 == 0);
```
- You must call the function with exactly the right **gas left** at the check.
- ✅ Bruteforce the right gas value by looping over options or adjusting manually.
- 🔒 It's a gate meant to frustrate, not to teach practical coding skills. :(
---

#### 🛑 gateThree
```solidity
require(
    uint32(uint64(_gateKey)) == uint16(uint64(_gateKey)) &&
    uint32(uint64(_gateKey)) != uint64(_gateKey) &&
    uint32(uint64(_gateKey)) == uint16(uint160(tx.origin))
);
```
Three conditions:
1. Lower 4 bytes == lower 2 bytes → middle 2 bytes must be 0
2. Lower 4 bytes ≠ full 8 bytes → upper 4 bytes must be non-zero
3. Lower 4 bytes == `uint16(uint160(tx.origin))` → derived from your EOA
---
### Simple Explanation
This challenge demonstrates how contracts can enforce access through unusual checks:
- Caller restrictions (`msg.sender != tx.origin`) ensure the function is invoked via a contract.
- Gas-dependent logic creates brittle conditions that attackers can brute-force.
- Bitwise tricks on inputs (like casting a `bytes8` to narrower types) can be used to design "puzzles" — but they’re not reliable access controls.

In real protocols, such patterns are security _anti-patterns_: they don’t provide true protection, just obscurity. Skilled attackers can always bypass them.

---
### 🧠 Exploit Strategy
1. Create and deploy an attack contract.
2. Inside it, construct a valid `_gateKey`.
3. Call `enter()` from your contract with a brute-forced gas value:
```solidity
gatekeeper.enter{gas: precise_gas}(crafted_key);
```
---
### 🧪 Lessons Learned
- **Gas brute-forcing**: Gas-based conditions are unreliable due to miner and EVM variance.
- `tx.origin` checks are insecure and discouraged.
- Bitwise casting should never be used as a “secret lock.”
- Real security must rely on cryptographic proofs or economic incentives, not puzzles.
