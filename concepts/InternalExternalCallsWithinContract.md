# Internal vs External Calls in Solidity
### Why `withdraw()` ≠ `this.withdraw()`
Smart contract developers often assume calling their own function is harmless. But the difference between `withdraw()` and `this.withdraw()` can open subtle attack surfaces, especially when access control or reentrancy is involved.

## 🔹 The Two Dispatch Paths
withdraw()
- Invokes the function _internally_.
- The same `msg` context is used. No new `msg.sender` or call context is created.
- Cheaper (no external message call).
- Bypasses visibility rules: `public` and `external` can be called internally as if they were internal.

this.withdraw()
- Forces a full **external CALL** via the EVM dispatcher.
- `msg.sender` becomes the contract itself (`address(this)`), not the original EOA.
- Executes access modifiers as if called externally.
- More expensive (extra call overhead, gas, possible reentrancy points).

```solidity
contract Vault {
    mapping(address => uint256) public balances;
    bool internal locked;
    modifier noReentrant() {
        require(!locked, "Reentrancy");
        locked = true;
        _;
        locked = false;
    }
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
    function withdraw() public noReentrant {
        uint256 amt = balances[msg.sender];
        balances[msg.sender] = 0;
        payable(msg.sender).transfer(amt);
    }
    function adminDrain() external {
        // Executes under the same modifier state.
        withdraw();
        // noReentrant modifier runs again with a fresh context.
        // If misconfigured, this can let contracts bypass modifiers or behave differently.
        this.withdraw();
    }
}
```
### 🔹 Real-World Risk
- Bypass Modifiers: An `onlyOwner` check may unintentionally pass when called as `this.fn()`, because `msg.sender` becomes the contract itself, which is often treated as a trusted entity.
- Reentrancy Windows: `this.withdraw()` re-enters the function with a fresh modifier stack, potentially undoing protection logic.
- Audit Finding Class: Misuse of `this.fn()` is often reported as “_Confused Contract Caller / Misconfigured Context_” issue.

### 🔹 Defense
1. Prefer Internal Calls when chaining functions (`withdraw()` instead of `this.withdraw()`).
2. Be explicit with `msg.sender` logic — don’t auto-trust `address(this)`.
3. Restrict dangerous entrypoints that can be re-invoked externally.
4. Audit Tip: Always check:
   - Are there any `this.fn()` calls?
   - Do they bypass `msg.sender` assumptions?
   - Do modifiers stack correctly?

### 🔹 Key Takeaway
- `withdraw()` → internal, safe, cheap.
- `this.withdraw()` → external, changes `msg.sender`, re-executes modifiers, can create privilege or reentrancy bugs.

👉 When auditing, every `this.fn()` should raise a red flag.
