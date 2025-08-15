### Subtle Gas Trap
Consider this loop in a staking contract:
```solidity
function distributeRewards(address[] calldata stakers, uint256 rewardPerUser) external {
    for (uint256 i = 0; i < stakers.length; i++) {
        balances[stakers[i]] += rewardPerUser;
    }
}
```
A dev suggests replacing the loop condition with:
```solidity
uint256 len = stakers.length;
for (uint256 i = 0; i < len; i++) {
    balances[stakers[i]] += rewardPerUser;
}
```
and claims it’s always a gas optimization in Solidity ≥0.8. Is it correct?

**No** — in calldata arrays, `length` access is already very cheap; caching only helps for memory arrays.
- In **calldata arrays**, `stakers.length` is **loaded from calldata, not storage** — that’s an **extremely cheap operation** (almost free compared to SLOAD).
- In Solidity ≥0.8, the compiler is already smart enough to optimize away repeated length lookups in simple loops over calldata arrays.
- Caching into `len` actually adds an extra **stack slot** and an **MSTORE** to memory in some cases, so it can **cost more gas**, not less.

**Real-world impact**:  
In storage arrays, caching `length` is a must-have optimization; in calldata arrays, the effect is negligible or even **negative**.
