# Ethernaut Challenges

### Overview
This section contains my end-to-end work on [Ethernaut](https://ethernaut.openzeppelin.com/), the smart contract security CTF game by OpenZeppelin.  
Each level demonstrates a distinct Solidity/EVM vulnerability — I’ve solved them all with a dual approach:
- **Exploit contracts** (`attack.sol`) written in Solidity
- **Automated interaction scripts** in Python
- **Foundry-based test suite** for reproducibility

The goal is not only to solve Ethernaut, but to document, automate, and test each vulnerability as if it were part of a professional audit process.

---

### Structure
sc-security-labs/ethernaut/  
├── 01_FallbackTrap/  
│ ├── Fallback.sol             # Actual contract by Ethernaut  
│ ├── attack.sol               # Exploit contract (if required)  
│ ├── test_01_FallbackTrap.py  # Python automation for deployment & interactions  
│ └── README.md                # Minimal blog-style explanation  
│  
├── 02_Fallout/  
│ ├── ...  
│  
├── test/  
│ ├── 01_FallbackTrap.t.sol # Foundry test per challenge  
│ ├── 02_Fallout.t.sol  
│ └── ...  
│  
├── script/ # Shared Foundry scripts (if needed)  
└── src/ # (Not used in this project)  

- **Level folders**  
  Each challenge folder contains:
  - `attack.sol` → Exploit contract (only where necessary).  
  - `script.py` → Automated Python script that deploys the exploit and interacts as the player.  
  - `README.md` → Minimal explanation of the vulnerability (no walkthrough).  

- **Global `test/` folder**  
  - One Foundry test (`.t.sol`) per level.  
  - Validates the exploit in a reproducible and automated way.  

---

### Approach
1. **Minimal Documentation**  
   Each challenge has a concise `README.md` that highlights:
   - The security concept demonstrated  
   - The vulnerable code snippet  
   - The essence of the vulnerability  
   - Lessons learned  

2. **Code + Automation**  
   Every exploit is backed by both Solidity and Python automation, demonstrating:
   - Low-level control of transactions/events (Python)  
   - Smart contract exploit design (Solidity)  
   - Modern testing methodology (Foundry)  

3. **Audit Mindset**  
   Instead of walkthroughs, I keep explanations minimal.  
   Reviewers can directly inspect the exploit contract, test, or automation script — the way an auditor would in real-world engagements.

---

### Why This Matters
For potential employers and clients, this folder shows:
- **Hands-on mastery of Ethereum security** through Ethernaut.  
- **Tooling versatility**: Foundry, Solidity, and Python (automation & scripting).  
- **Professional structure**: tests, scripts, and documentation organized like a real audit lab.  
- **Clarity**: Minimal explanations, with code/tests as the source of truth.

---

### Lessons Learned
- Solidity vulnerabilities are best understood with **working exploits + tests**.  
- Good documentation is concise: capture the essence, let the code speak.  
- Combining multiple toolchains (Foundry + Python) reflects real-world auditing practice.  

---

### References
- [Ethernaut – OpenZeppelin](https://ethernaut.openzeppelin.com/)  
- [Ethereum Smart Contract Best Practices](https://consensys.github.io/smart-contract-best-practices/)  
- [Foundry Book](https://book.getfoundry.sh/)  
- [Web3.py Documentation](https://web3py.readthedocs.io/)  
