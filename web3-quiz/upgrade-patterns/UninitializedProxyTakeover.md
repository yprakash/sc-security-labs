### Classic delegatecall / initializer exploit (Parity-style)

You have a proxy that `delegatecall`s into a library/implementation. The implementation has an initializer:
```solidity
// Implementation (library-style logic)
contract VaultLogic {
    address public owner; // slot 0
    function init(address _owner) external {
        owner = _owner;
    }
    function withdraw(address to, uint256 amount) external {
        require(msg.sender == owner, "not owner");
        // ... send funds ...
    }
}

// Proxy (simplified)
contract VaultProxy {
    address public implementation; // stored safely (assume ERC-1967 slot)
    fallback() external payable {
        (bool ok, ) = implementation.delegatecall(msg.data);
        require(ok);
    }
}
```
How can an attacker exploit when the deployer **forgets to call** `init(...)` after pointing the proxy at `VaultLogic`? No other access control is present on `init`.

Call `init(attacker)` via the proxy to set `owner` **in the proxy’s storage**, then call `withdraw` and drain funds.  
Because the proxy uses `delegatecall`, `VaultLogic.init` writes to **the proxy’s storage**. With no initializer guard, an attacker can call `init(attacker)` via the proxy, set themselves as `owner`, then call `withdraw` and drain funds. This is the classic _uninitialized proxy/library takeover_.

**Audit takeaway**: Always protect initializers (`initializer`/`reinitializer`), and ensure they’re called exactly once during deployment.
