### proxy implementation's storage collision even with ERC-1967 standard
```solidity
contract Proxy {
    // ERC-1967 standard implementation slot
    bytes32 private constant _IMPLEMENTATION_SLOT =
        0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;

    function _getImplementation() internal view returns (address impl) {
        bytes32 slot = _IMPLEMENTATION_SLOT;
        assembly {
            impl := sload(slot)
        }
    }
}

contract Vault {
    // developer forgot to reserve storage gap
    uint256 public balance;     // slot 0
    address public owner;       // slot 1
}
```
Scenario:  
A year later, Vault is upgraded to add a new variable at the top:
```solidity
contract VaultV2 {
    uint256 public totalDeposits;  // new slot 0
    uint256 public balance;        // now slot 1
    address public owner;          // now slot 2
}
```
What can happen when upgrading from Vault to VaultV2?  
Storage variables in VaultV2 will shift, corrupting `balance` and `owner`.
- ERC-1967 standard stores the implementation in a special hash-based slot, not slot 0.
- ERC-1967 only protects the **proxy’s internal bookkeeping slots** (like _`IMPLEMENTATION_SLOT`) from colliding with the implementation contract’s storage.
- It does **not** protect **between versions of your own implementation**.
- By adding `totalDeposits` at the **top**, you pushed all existing variables down one slot.

This means:
- `balance` becomes garbage (old value of `owner`)
- `owner` becomes garbage (whatever was in empty slot 2)

💡 **Rule**: When upgrading, never insert new variables in the middle or at the top of your state variables — only append to the end. Or **use a storage gap**.
