## 🧩 Ethernaut Level 14: Gatekeeper Two
### 🔒 Goal
Become the `entrant` by passing three tricky gates, each designed to block naive contract interaction.

---
### 🔍 Contract Summary
```solidity
function enter(bytes8 _gateKey) public gateOne gateTwo gateThree(_gateKey) returns (bool);
```
Three gate modifiers block this function:

🔐 Gate One
```solidity
require(msg.sender != tx.origin);
```
- Ensures you're calling from a contract, not an EOA.
- ✅ Solution: Call from an attacker contract.

🔐 Gate Two
```solidity
assembly {
    x := extcodesize(caller())
}
require(x == 0);
```
- `extcodesize(caller())` is 0 during constructor execution of a contract.
- ✅ Solution: Call `enter()` from the constructor of your attacking contract.

🔐 Gate Three
```solidity
require(uint64(bytes8(keccak256(abi.encodePacked(msg.sender)))) ^ uint64(_gateKey) == type(uint64).max);
```
- Use XOR to derive the _`gateKey`

---
### 🚀 Exploit Strategy
1. Write GatekeeperTwoAttack contract.
2. Inside the constructor:
- Compute gateKey using XOR method.
- Call gatekeeper.enter(gateKey);
3. Deploy the attacker from your wallet.

---
### Lessons Learned
- `extcodesize(address)` returns `0` for contracts under construction → don’t use it for EOA vs contract detection.
- Bitwise XOR is reversible and can be brute-forced or solved algebraically.
- Security through obscure arithmetic conditions rarely provides meaningful protection.
- Contracts should avoid gating logic based on caller type or code size — these can usually be bypassed.

---
### 🧠 Real-World Takeaways
#### 🔬 `extcodesize()` as a Defensive Tool
The `extcodesize()` opcode reveals the code size at a given address. It returns `0` during a contract's constructor, which has these real-world implications:
- Anti-Bot Protection: DApps check if msg.sender has no code — filtering bots that interact immediately after deployment.
- Flash Loan / MEV Defense: Prevent temporary contracts from manipulating state within one atomic transaction.
- Whitelist Enforcement: Primitive EOA detection (not foolproof) — by rejecting contracts.
- Constructor-only Initialization: Used in upgradable proxies to restrict critical logic to the constructor.
