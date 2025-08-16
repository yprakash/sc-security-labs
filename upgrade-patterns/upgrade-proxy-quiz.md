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
**References**:
- https://ethereum.stackexchange.com/a/161348
