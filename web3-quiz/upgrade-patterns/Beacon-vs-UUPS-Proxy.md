### 👉 Notes for UpgradeableBeacon proxies
Why does OpenZeppelin’s `UpgradeableBeacon` enforce `Address.isContract(newImplementation)` during upgrades?

To prevent an EOA (externally owned account) from being set as implementation.
- When upgrading a Beacon, the `upgradeTo(newImplementation)` call sets the implementation that all proxies will delegate to.
- If you set it to an **EOA** (externally owned account), proxies would try to `delegatecall` into an address with **no code**, which bricks them.
- To prevent this, OpenZeppelin enforces:
```solidity
require(Address.isContract(newImplementation), "not a contract");
```
So it’s specifically to **ensure the new implementation actually contains code**.

---

👉 Suppose you have 1000 Beacon proxies pointing to the same Beacon. The Beacon is upgraded to `ImplementationV2`.  
`ImplementationV2` introduces a new `initializeV2()` function that needs to be called once to set some new state variables.  
Who must call `initializeV2()`?

Each proxy must call it individually.
- In a **Beacon Proxy pattern**, each proxy stores its own **state variables**.
- The Beacon only stores a pointer to the implementation contract — **not the state**.
- When you upgrade the Beacon to `ImplementationV2`, all proxies start using the new logic, but **their storage remains untouched**.
- That means **each proxy must execute** `initializeV2()` **individually** to populate its new state variables.
- Calling `initializeV2()` on the Beacon itself is meaningless — the Beacon doesn’t hold user balances, owner state, or protocol config. Those live in each proxy’s storage.
- This is a subtle but critical interview/audit gotcha. Many devs think the Beacon holds state like a singleton, but in fact, it’s just the “logic registry.”

⚠️ **Real-world consequence**:
If only one proxy is initialized and others are not, their storage vars (like `owner`, `config`, `oracle`, etc.) may remain **zeroed**, opening up to **ownership takeovers** or **inconsistent protocol behavior** across proxies.

---

### Comparison
- Beacon Proxy
  - Upgradeability is centralized in the **Beacon contract**, which holds the implementation address.
  - Risk: If the Beacon admin is compromised, all proxies using that Beacon are at risk.
  - However, the implementation itself does not expose `upgradeTo()`.

- Transparent Proxy
  - Admin calls are separated from user calls.
  - Avoids the classic issue of users accidentally hitting admin functions.
  - But the proxy itself contains the upgrade logic, making it a **single point of risk** for upgrades.

- UUPS Proxy
  - The proxy is minimal — all upgrade logic lives in the **implementation contract**.
  - ⚠️ If a developer forgets to restrict `upgradeTo()` with something like `onlyProxy` or `onlyOwner`, _anyone can upgrade the contract_.
  - This is a common real-world **catastrophic bug** (several hacks exploited this exact mistake).

#### T/F statements:
- Beacon Proxies are safer than Transparent Proxies because only the Beacon admin can call `upgradeTo()`, and implementation contracts cannot be accidentally bricked. **FALSE**
- Transparent Proxies prevent storage collisions better than Beacon Proxies because the admin logic lives in the proxy itself. **FALSE**
- UUPS Proxies can be more dangerous than Transparent or Beacon Proxies if the `upgradeTo()` function in the implementation is left **unprotected**. **TRUE**  
  Even if you use OpenZeppelin’s implementations, you still need to apply them correctly. The UUPS pattern in particular is very risky if you misconfigure access control.

🔥 **Real-world reference**: In 2021, some projects using UUPS without proper `onlyProxy` modifiers were exploited because attackers could directly call `upgradeTo()` on the implementation.

---
