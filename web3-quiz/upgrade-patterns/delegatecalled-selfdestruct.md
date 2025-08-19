#### Can a delegatecalled `selfdestruct` kill the proxy? (tricky, real risk)?
Assume the implementation contains a maintenance function:
```solidity
function emergencyShutdown() external {
    selfdestruct(payable(msg.sender));
}
```
This function is reachable via the proxy’s fallback. If someone triggers it through the **proxy**, what happens?

The proxy selfdestructs because `selfdestruct` executes in the caller’s (proxy’s) context under `delegatecall`.  
When `delegatecall` is used, the **code of the implementation runs in the storage + context of the proxy**.  
So if `emergencyShutdown()` is called via the proxy, the `selfdestruct` executes _in the proxy’s context_. That means:  
- The proxy contract is destroyed.
- All Ether in the proxy is sent to the attacker.
- The implementation contract remains untouched (since it was never the `CALLER`).

**Audit takeaway**:
- Never leave `selfdestruct` or **privileged opcodes** in implementations.
- Use upgrade-safe base contracts (like OpenZeppelin’s).
