# Ethernaut Level 09 — King 👑
### Challenge
The goal is to permanently lock the `King` contract so no one else can become the new king.  
Normally, the throne can be taken by sending more Ether than the current prize, but the contract forwards Ether back to the previous king — which introduces a flaw.  
This level demonstrates a critical Denial of Service **(DoS)** vulnerability involving unexpected `revert` behavior in `payable` fallback contexts.

---
### Vulnerable Logic
```solidity
function _claimThrone() public payable {
    require(msg.value >= prize);
    payable(king).transfer(msg.value);  // risky transfer
    king = msg.sender;
    prize = msg.value;
}
```
---
### ⚔️ Vulnerability Insight
The contract assumes the previous king can **receive Ether** via `.transfer()`.

This is dangerous because:
- If the new king is a **contract with no `receive()` function** or an intentional `revert()` in receive() function, the entire transaction fails
- This **breaks the contract's logic** permanently (Denial of Service)
---

### 🧨 Exploit Summary
1. Deploy an **attack contract** with no `receive()` or one that `revert()`s on fallback.
2. Send Ether to the King contract to become the new king.
3. When anyone/any contract later tries to send Ether back to the attacker, it reverts.
4. No one else can ever claim kingship — the game is **DoS'd forever**.

---
#### Solidity's rules for handling Ether transfers to contracts are as follows:
1. If the call specifies a function signature that exists in the receiving contract, that function is executed.
2. If the call has no data (as in a simple Ether transfer via .transfer() or .send()), the receiving contract's receive() function (if it exists and is payable) is executed.
3. If there is no receive() function, but there is a payable fallback function, the fallback function is executed.
4. If none of the above conditions are met, the Ether transfer will fail, and the transaction will revert.

---
### ✍️ Key Takeaways
- Solidity’s `.transfer()` and `.send()` are **not safe** if recipients can revert or exceed gas limits.
- Contracts must **gracefully handle failed Ether sends**, especially in reward/payout flows.
- **Pull-based payment patterns** are more secure than push-based transfers.
- This challenge highlights a classic DoS vector seen in real-world exploits.
