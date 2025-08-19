## FAQs on Upgrade Proxy Patterns

A DeFi team uses a **Beacon Proxy** pattern for their vault contracts. During audit, you notice the Beacon itself is upgradeable. Which of the following is the **biggest risk**?

A) Users interacting with proxies might trigger admin functions by mistake.  
B) An attacker who gains Beacon admin rights can upgrade the implementation of **all proxies** at once.  
C) Storage collisions are more likely than with Transparent Proxies.  
D) Users can bypass the Beacon and directly call the implementation contract safely.

Answer: B ✅  
If the Beacon admin is compromised, the attacker can upgrade the Beacon → which instantly upgrades the implementation for all Beacon proxies pointing to it. That’s systemic risk.

---

A protocol migrates from Transparent Proxies to UUPS Proxies because they want to save gas. Which of the following is **FALSE**?

A) The UUPS proxy does not contain upgrade logic; it delegates `upgradeTo()` calls to the implementation.  
B) If the implementation’s `upgradeTo()` is left unprotected, anyone can upgrade the proxy.  
C) Transparent proxies are more gas-efficient than UUPS.  
D) UUPS proxies rely on ERC1822 `proxiableUUID()` for safety.

answer: C ✅  
This is the **trap**: Transparent proxies are **more expensive** (extra checks to prevent admin from accidentally calling implementation functions), whereas **UUPS is lighter/cheaper**. So saying Transparent is “more gas-efficient” is false.

---

Which of the following is a **shared risk** between Beacon and Transparent proxies, but **not UUPS**?

A) Centralized upgradeability: a single admin contract/role can modify upgrades.  
B) Implementation contracts can become bricked if `upgradeTo()` is not protected.  
C) All proxies pointing to the same implementation are exposed if the admin role is compromised.  
D) Malicious initialization logic in a new implementation can drain user funds.

answer: C ✅  
Both Beacon and Transparent rely on an **external admin** contract/role controlling upgrades. If compromised → mass damage.  
UUPS, on the other hand, puts `upgradeTo()` in the implementation — so the “shared admin role risk” doesn’t exist in the same way (its risk is unprotected `upgradeTo()`).

---
Spot the bug – What is the main security issue in this Beacon Proxy?
```solidity
interface IBeacon {
    function implementation() external view returns (address);
}
contract BeaconProxy {
    address public beacon;
    constructor(address _beacon) {
        beacon = _beacon;
    }
    fallback() external payable {
        address impl = IBeacon(beacon).implementation();
        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }
}
```
A. `beacon` is not immutable, meaning anyone can change the beacon and upgrade the proxy.  
B. The proxy trusts the beacon blindly; if the beacon is malicious, it can point to an attacker contract.  
C. Both A and B.  
D. No issue, this is a standard minimal BeaconProxy implementation.

answer: C ✅ Both problems exist here:
1. Beacon mutability (A):
   - `address public beacon;` is just a normal storage var.
   - No `immutable` keyword, no access control, no setter restrictions.
   - If anyone (or even the deployer) can change it later via some added function, attackers can redirect the proxy to their own beacon.
2. Trusting the beacon blindly (B):
   - Even if the beacon itself is upgradeable, this proxy never verifies what it returns.
   - A compromised/malicious beacon can point to an attacker implementation contract at any time.
   - That’s why **beacon upgrades need admin governance and strong access control**.

**Takeaway**: Beacon Proxy inherits the risks of both storage collision AND malicious beacon logic.

---
### Delegatecall Pitfall
What’s the manual discovery vulnerability in this minimal proxy?
```solidity
contract Proxy {
    address public implementation;
    fallback() external payable {
        (bool ok, ) = implementation.delegatecall(msg.data);
        require(ok, "fail");
    }
}
```
A. Storage slot collision between proxy and implementation.  
B. Anyone can upgrade implementation by reentering.  
C. Proxy admin is missing, so no one can upgrade implementation.  
D. Reverts are swallowed by delegatecall.
> A. Storage slot collision between proxy and implementation.
- The proxy stores `address public implementation`; at slot 0.
- When it forwards calls with `delegatecall`, the implementation contract will use the proxy’s storage.
- If the implementation contract also defines a variable at slot 0 (say `uint256 totalSupply`), writing to it will overwrite the proxy’s `implementation` address.
- That allows attackers to redirect execution to arbitrary contracts — effectively an **upgrade without upgrade logic**.

👉 This is a **classic delegatecall pitfall**. That’s why secure proxies use EIP-1967 storage slots (`keccak256("eip1967.proxy.implementation") - 1`) to isolate storage.

Why not C?
- Saying “no one can upgrade” isn’t true — the vulnerability is worse: the **implementation itself can overwrite the proxy’s state** during delegatecall.
- That makes the system upgradeable by accident, not immutable.

---
**References**:
- https://ethereum.stackexchange.com/a/161348
