# Ethernaut Level Level 10 — Re-entrancy: The Recursive Trap 🔁

The contract in this level manages Ether balances and allows users to deposit and withdraw their funds. However, it contains a critical flaw in the `withdraw()` function that makes it vulnerable to a **re-entrancy attack**.

An attacker can exploit this to **drain all funds from the contract**, even if they only deposited a small amount.

### 💥 Vulnerability Explained
The contract sends Ether to the caller **before** updating their balance.  
If the caller is a contract with a fallback/receive function, it can recursively call `withdraw()` again while the original balance is still intact.  
This loop drains the contract’s funds until its balance is empty.

### Key Tricks / Insights
- Re-entrancy happens when **external calls** are made before internal state is secured.
- `call` forwards all remaining gas by default, enabling complex logic in the callee.
- The Checks-Effects-Interactions (**CEI**) pattern prevents this: update state before making external calls.

### Lessons Learned
- Always follow CEI: update balances first, then interact with external addresses.
- Consider using reentrancy guards (`nonReentrant` modifier from OpenZeppelin).
- Avoid assuming external calls will behave safely.
