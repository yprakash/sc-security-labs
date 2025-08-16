#### What’s the subtle issue with this code?
```solidity
contract Admin {
    address public admin;
    constructor() {
        admin = msg.sender;
    }
    function isAdmin() external view returns (bool) {
        return msg.sender == admin;
    }
    function changeAdmin(address newAdmin) external {
        require(isAdmin(), "not admin");
        admin = newAdmin;
    }
}
```
`isAdmin()` is external, but used internally → always returns **False** (since `msg.sender` becomes the contract).

- `changeAdmin()` calls `isAdmin()`. But `isAdmin()` is **declared** `external`.
- In Solidity, when you call an `external` function from _inside the contract_, it is actually compiled into a **message call** (`CALL`), not a direct internal jump.
- That means `msg.sender` inside `isAdmin()` is not the EOA who called `changeAdmin()`. Instead, it becomes the contract itself (`address(this)`), since the contract is calling itself.

So:
- If Alice calls `changeAdmin()`, `msg.sender` in `changeAdmin()` is Alice. ✅
- But when `changeAdmin()` calls `isAdmin()`, it executes as if the contract called `isAdmin()`.
- Inside `isAdmin()`, `msg.sender == address(this)` ≠ `admin`. ❌  
Result → `require(isAdmin())` **always fails**, making `changeAdmin()` permanently unusable.

👉 This is why the correct fix is to declare `isAdmin()` as `internal` (or use an internal modifier like `onlyAdmin`).

Best practice is:
- Use **modifiers** or **internal functions** for access control.
- Avoid calling `external` view functions for auth checks from inside the contract.
