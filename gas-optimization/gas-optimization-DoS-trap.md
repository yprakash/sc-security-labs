### Gas optimization + DoS trap
```solidity
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract GasDoS {
    mapping(address => bool) public isWhitelisted;
    address[] public whitelistArray;

    function add(address user) public {
        isWhitelisted[user] = true;
        whitelistArray.push(user);
    }

    function removeAll() public {
        for (uint256 i = 0; i < whitelistArray.length; i++) {
            isWhitelisted[whitelistArray[i]] = false;
        }
        delete whitelistArray;
    }
}
```
If the whitelist grows to **50,000 addresses**, what is the main problem with `removeAll()`?

It will become **un-callable** because the loop can exceed the block gas limit.  
- `removeAll()` loops through **every** address in `whitelistArray` and performs a storage write (`SSTORE`) per address.
- Each write costs ~5,000 gas (non-zero → zero), so at 50,000 entries:
```
50,000 × 5,000 = 250,000,000 gas
```
That’s **far above** the current block gas limit (~[45M](https://www.radom.com/insights/ethereum-elevates-block-gas-limit-to-45-million-advancing-its-scaling-efforts) on Ethereum mainnet).
- This means the function will **always revert** once the array grows too large — effectively bricking cleanup logic.

**Security angle**:  
This is a textbook **unbounded loop DoS vulnerability**.  
Attackers can spam enough entries into `whitelistArray` to make `removeAll()` permanently unusable — locking state and possibly halting protocol operation.

**Best practice**:
- Avoid unbounded loops in state-changing functions.
- Use patterns like **chunked processing** (remove N items at a time), or **mappings without enumeration** for constant-time cleanup.
