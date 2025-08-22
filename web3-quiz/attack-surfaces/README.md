# 🔓 Attack Surfaces in Solidity Smart Contracts

Attack surfaces define **where and how an attacker can interact with your smart contract**.  
For auditors, mapping these vectors is the **first step in threat modeling** before diving into code.  
This README distills key lessons from real-world exploits, tailored for security auditing.

## 1. Reentrancy Vectors
### What
When a contract makes an external call **before updating state**, an attacker can reenter the function and break invariants.

### Example
```solidity
function withdraw(uint amount) external {
    require(balances[msg.sender] >= amount, "low balance");
    (bool ok,) = msg.sender.call{value: amount}("");  // ❌ external call first
    require(ok, "send failed");
    balances[msg.sender] -= amount;
}
```
### Risk
- Attacker loops withdrawal calls before state updates.
- Famous case: The DAO (2016) – $60M drained.

### Defense
✅ Checks-Effects-Interactions pattern  
✅ ReentrancyGuard (nonReentrant)  
✅ Consider pull payments (withdrawal pattern).

## 2. External Calls & Callback Hooks
### What
ERC777 and ERC1155 introduce **hooks** (`tokensReceived`, `onERC1155Received`) that can trigger attacker logic.

### Risk
- A benign-looking `token.transferFrom()` → triggers attacker’s `tokensReceived()`.
- Can bypass invariants and create hidden reentrancy.

### Real Exploit
- **Uniswap V1 + ERC777** reentrancy incident (2019).

### Defense
- Don’t assume ERC20 semantics; **validate hooks** or block non-vanilla tokens.
- Use **pull mechanisms** (don’t push tokens directly).

## 3. Delegatecall and Context Confusion
### What
`delegatecall` executes external code in the caller’s storage context.

### Risk
- Library hijacking → attacker contract writes to storage of victim.
- Proxy patterns magnify this risk.

### Real Exploit
- Parity Multisig (2017): unprotected `delegatecall` to init function → $150M locked forever.

### Defense
- Only `delegatecall` to trusted libraries.
- Protect `initialize()` functions with `initializer` modifiers.

## 4. MEV and Ordering Risks
### What
Since miners (and validators) order transactions, **state assumptions about order are unreliable**.

### Examples
- Front-running: attacker copies your tx with higher gas.
- Sandwiching: attacker surrounds a victim’s trade.
- Back-running: attacker profits from state change after victim tx.

### Defense
- Commit–reveal schemes
- Use of private mempools (e.g., Flashbots)
- Slippage checks on DEX trades.

## 5. Gas Griefing and Denial of Service
### What
External calls propagate **all remaining gas** by default. Attackers can force OOG failures or manipulate refund logic.

Example
```solidity
(bool ok,) = addr.call(""); // forwards all gas
require(ok); // DoS risk if addr is malicious
```
### Defense
- Use `call{gas: 2300}` only when safe.
- Don’t rely on `transfer()` (EIP-1884 broke gas assumptions).
- Batch-processing: allow skipping bad entries instead of reverting whole loop.

## 6. Privilege Escalation
### What
When access control boundaries are weak or misconfigured, attackers escalate privileges.

### Common Pitfalls
- Using `tx.origin` for auth
- Unprotected `selfdestruct()`
- Upgradeable proxies with unprotected `upgradeTo()` or `initialize()`

### Real Exploits
- Audius (2022): unprotected re-init → attacker seized ownership.
- Multichain (2023): flawed MPC key management led to ~$120M loss.

### Defense
- Always restrict with `onlyOwner` or role-based access control.
- Ensure upgradeability uses **OpenZeppelin’s UUPS/Transparent Proxy with access control**.
- Lock initializer functions after first use.

## 7. Key Auditor Mindset
When auditing attack surfaces, always ask:
1. Where are the external calls?
2. What if they reenter?
3. Who controls this input?
4. Does MEV ordering break assumptions?
5. Could access control be bypassed through proxies or `delegatecall`s?

## 📌 Final Notes
Attack surfaces are not just “bugs” — they are **design flaws waiting to be exploited**.  
Strong auditors think like **adversaries**: _Where would I poke this contract if I wanted to drain it_?

Real-world auditing reports must **document each attack surface**, explain impact, and provide **defensive patterns**.
