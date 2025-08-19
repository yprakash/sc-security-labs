### Gas Optimization Backfire in Loops
A developer tries to optimize gas in this ERC20-like `transfer` loop by caching `array.length` into a local variable:
```solidity
function batchTransfer(address[] calldata recipients, uint256 amount) external {
    uint256 len = recipients.length;
    for (uint256 i = 0; i < len; ) {
        balances[msg.sender] -= amount;
        balances[recipients[i]] += amount;
        i++;
    }
}
```
They claim: “_Caching `len` saves gas compared to using `recipients.length` each iteration_.”  
Which is **true**, but **what subtle security problem** can this cause in certain scenarios?

If `recipients` comes from calldata, caching `len` is fine, but if it were from storage, an attacker could modify its length mid-loop via a reentrant call, causing missed iterations or out-of-bounds reads.

- In the current code, `recipients` is from **calldata**, so the length is immutable during execution.
- But if this loop iterated over a **storage array**, and the function made any external call inside the loop (directly or indirectly), an attacker could modify the array length mid-loop via reentrancy.
- Since `len` was cached at the start, the loop would run with **stale length data**, potentially:
  - Skipping newly added malicious elements, or
  - Accessing removed elements, leading to **out-of-bounds read/write**.

**Real-world parallel**:  
This is similar to how caching `totalSupply` in token loops can break when the supply changes mid-execution due to reentrancy or hooks — a logic bug rather than direct gas waste.
