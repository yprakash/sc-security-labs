# 🛡️ Level 16: Preservation
### 🧠 TL;DR
Gain ownership of the Preservation contract by exploiting its delegatecall-based library system.

This challenge demonstrates how using `delegatecall` with untrusted libraries can allow attackers to overwrite your contract's storage layout — including ownership variables — through ABI signature collisions. By injecting a malicious library, the attacker rewires the contract to gain full control.

---
### 🔍 Challenge Overview
- Two library contracts are used via `delegatecall` to update timestamps.
- `delegatecall` executes code *in the context of the caller*, meaning storage layout must exactly match.
- `Preservation` stores the two library addresses and an `owner` address in its first three storage slots.

---
### 🚩 Vulnerability
The `Preservation` contract assumes that both libraries have a function `setTime(uint256)` which updates a timestamp. But:
```solidity
function setFirstTime(uint _timeStamp) public {
  timeZone1Library.delegatecall(abi.encodePacked(setTimeSignature, _timeStamp));
}
```
The `delegatecall` means the library's code will run in Preservation's context, writing to its own storage — specifically the first slot.

By passing in an address (as uint256) for the `_timeStamp`, the attacker tricks Preservation into writing to its timeZone1Library slot, replacing it with a malicious contract.

---
### ⚔️ Exploit Strategy
1. **Create a malicious contract** with a `setTime(uint256)` function that writes the value directly into slot `2`.
2. **Call `setFirstTime(malicious_contract_address)`**, tricking `delegatecall` to overwrite `timeZone1Library`.
3. **Call `setFirstTime(attacker_address)` again**, which routes through the malicious contract and sets `owner`.

---
### 🐍 Python Interactions (web3.py)
```python
# Step 1: Overwrite timeZone1Library
send_transaction_and_wait(preservation.functions.setFirstTime(malicious.address))

# Step 2: Use malicious library to take ownership
send_transaction_and_wait(preservation.functions.setFirstTime(attacker_address))

# Confirm
assert preservation.functions.owner().call() == attacker_address
```
---
### 🤯 Debugging Insight
> "I initially couldn’t understand how the contract’s address was changed first. I was confused that the second call worked while the first didn’t — until I realized the `delegatecall` actually replaces the library pointer, and only on the next call does the malicious logic execute in the same storage context."

This was a powerful realization about how `delegatecall` behaves when used with upgradable patterns or external libraries.

---
### 🧠 Takeaways
- Storage layout is critical when using `delegatecall`.
- Treat libraries as untrusted code unless they are immutable and under your control.
- Always separate logic and data when designing upgradable contracts.

---
### 🎯 Real-World Relevance
- This is a classic example of poor proxy design. We've seen similar bugs in:
- Early upgradable proxies before OpenZeppelin standardized storage patterns.
- DeFi protocols misusing external calls or unsafe upgrade mechanisms.
