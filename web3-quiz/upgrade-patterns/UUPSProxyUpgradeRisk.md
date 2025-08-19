### Architecture — Upgradeability Risk

A DeFi lending protocol deploys a **UUPS Proxy** for its main contract. The `upgradeTo` function is protected with the `onlyOwner` modifier. The owner is an EOA (externally owned account).  
Which of the following best describes the architectural risk here?
> If the owner’s private key is compromised, the attacker can upgrade the implementation to a malicious contract and drain all funds.
- In a UUPS proxy pattern, the `upgradeTo` function directly controls the **implementation contract address**.
- If the **owner’s private key** (an EOA in this case) is compromised, the attacker can upgrade to a malicious implementation and gain full control of the protocol — leading to complete fund loss.
- This is a well-known **centralization risk** in upgradeable contracts. Real-world examples include:
  - **Parity Multisig Wallet** (2017) — a flawed upgrade pattern bricked ~$150M.
  - **Ronin Bridge (2022)** — attacker gained validator key majority, leading to >$600M theft.
- **Best practice**: Ownership of upgradeability should be behind a **multisig, timelock, or governance contract** — never a single EOA.
