# Ethernaut Level 07 — Force

### Challenge
The goal is to make the `Force` contract’s balance greater than 0.  
Players must figure out a way to send Ether to a contract that **does not have a payable function**.

#### Vulnerable Logic
```solidity
contract Force {
    // No payable functions
}
```
### Vulnerability Explained
- Solidity contracts without `payable` functions **cannot receive Ether via normal transfers**.
- However, Ether can still be sent using `selfdestruct(address)` from another contract.
- Once `selfdestruct` is called on a contract that references `Force`, its balance increases even though it has no payable functions — bypassing typical restrictions.

### Key Insights
- A contract can always receive Ether via `selfdestruct`, regardless of its payable functions.
- `Force` demonstrates that contracts cannot fully block incoming Ether if another contract intentionally sends it.
- This pattern can be used both defensively (forcing a contract to hold Ether) or to test assumptions about balances.

### Lessons Learned
- Contracts should not assume they can block all incoming Ether.
- Always validate the **source of funds** if Ether balance matters for logic.
- `selfdestruct` can bypass typical payable restrictions.

> ⚠️ **Note**: `selfdestruct` is deprecated after Solidity 0.8.18 and may change behavior in future. It still works for force-sending Ether today, but do not rely on it in production.
