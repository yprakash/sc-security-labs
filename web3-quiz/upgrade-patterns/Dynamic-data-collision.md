### Dynamic data collision (arrays/mappings across upgrades)
##### V1
```solidity
contract V1 {
    // slot 0
    struct User {
        uint256 balance;     // slot 0 (in struct)
        uint256[] deposits;  // slot 1 (in struct) → data at keccak(userSlot+1)
    }
    mapping(address => User) internal users; // slot 1
}
```
##### V2 (upgrade)
```solidity
contract V2 {
    struct User {
        uint256[] deposits;  // moved to top (was at struct slot 1)
        uint256 balance;     // moved down (was at struct slot 0)
    }
    mapping(address => User) internal users; // same mapping slot 1
}
```
After upgrading from **V1 → V2**, what’s the impact on previously stored users?

Catastrophic: `balance` and `deposits` **swap** struct positions; `deposits` data is read from the old `balance` slot and the array’s data pointer (keccak) changes — corrupting both fields.

- In storage, a `mapping` occupies a _single slot number_ (the mapping’s declared slot). For `users[key]`, the base slot for that entry is `keccak256(abi.encode(key, mappingSlot))`.
- In V1:
  - `User.balance` → stored at `base + 0`.
  - `User.deposits` → stored at `base + 1` (that slot holds the array’s length/pointer); the array elements live at `keccak256(base + 1)`.
- In V2 you swapped field order:
  - `User.deposits` → now `base + 0` (so Solidity will read the old `balance` value as the array’s length/pointer).
  - `User.balance` → now `base + 1` (so Solidity will read the old array length/pointer as the `balance`).

**Result**: previously stored data is **misinterpreted** — small lengths become balances, huge balances become array lengths/pointers → the contract will behave incorrectly and can read/write wildly wrong storage slots, corrupting state.

**Real-world note**: This exact class of bug has caused broken user balances and lost funds in upgrades where struct layouts were reordered. Always treat struct/field ordering as an invariant across upgrades.
