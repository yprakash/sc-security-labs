### Storage gaps — subtle upgrade rule
```solidity
contract V1 {
    address public owner;        // slot 0
    uint256 public value;        // slot 1
    uint256[50] private __gap;   // reserve 50 slots
}
```
Later you deploy `V2` and want to add two new state variables:
```solidity
contract V2 {
    address public owner;        // slot 0
    uint256 public value;        // slot 1
    uint256 public newA;         // -> use from __gap
    uint256 public newB;         // -> use from __gap
    uint256[48] private __gap;   // shrunk to 48
}
```
Safe/Unsafe?  
Safe — shrinking the gap from 50 → 48 is harmless because you only used 2 slots.

[OpenZeppelin](https://docs.openzeppelin.com/upgrades-plugins/writing-upgradeable#storage-gaps) explicitly documents that a `__gap` is meant to _reserve_ slots and that when you add new state variables in a later version, you **reduce the gap by the number of slots you consumed**. So shrinking `uint256[50] __gap` → `uint256[48] __gap` after adding two variables at the end **is the intended, safe pattern**.

Why this is safe (concise):
- `__gap` just reserves N contiguous 32-byte storage slots at the end of the contract’s storage layout. Consuming two of them by declaring two new variables and reducing the gap by two keeps the overall slot assignments stable.

**Practical tips / audit checklist**:
- Always add new variables **only at the end** of the storage layout (or consume `__gap` slots).
- Use OpenZeppelin’s `validateUpgrade` / `upgradeProxy` checks before upgrading — they will flag layout issues.
- Be careful with inheritance: changing base contract order or adding variables in a base can shift slots for children.
- Consider more robust namespaced layouts (ERC-7201) for complex systems that need stronger guarantees.
- Also keep in mind that your variables may be packed tightly depending on their type. Size should be reduced by the no.of extra slots consumed (not by the no.of extra variables introduced) See https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html
