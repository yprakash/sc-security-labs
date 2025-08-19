### View function gas trap
```solidity
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract ViewTrap {
    uint256 public counter;

    function getDouble() public view returns (uint256) {
        return counter * 2;
    }
}
```
On mainnet, Alice calls `getDouble()` via **eth_call** from her frontend, and Bob calls `getDouble()` inside a regular transaction (i.e., from another contract). Then **Alice’s call costs 0 gas, but Bob’s call consumes gas**.

- `view` functions are only “free” when called **off-chain** via `eth_call` — this is a _local simulation_ that doesn’t alter the blockchain state.
- When a `view` function is invoked **inside a transaction** (e.g., from another contract), it **still executes on-chain** and consumes gas exactly like any other function.
- The `view` keyword only enforces at compile-time that the function cannot modify state — it does not change runtime execution cost.

**Security / gas note**:  
Developers assume calling a `view` function from within another contract was “free” — this misunderstanding led to a costly bug where the “cheap” lookup was actually in a loop, and gas costs ballooned, making the function callable only for small inputs before hitting block gas limits.
