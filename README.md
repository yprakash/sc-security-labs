# 🔐 Smart Contract Security Labs

[![Solidity](https://img.shields.io/badge/Solidity-0.8.x-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.13-yellow.svg)]()
[![Foundry](https://img.shields.io/badge/Foundry-Forge-green.svg)]()

**Smart Contract Security Labs** is a curated collection of hands-on projects, challenges, and educational resources focused on **Ethereum, DeFi, and Web3 security**.  

The **goal**: build a structured knowledge base and reproducible exploit labs that reflect both **practical security engineering** and **clear documentation**.  

👉 `sc-security-labs` is my **living Web3 security lab**.  

---
## 📂 Repository Structure
### 1. `audits/`
- Contains several subfolders, each simulating an **audit engagement** on a DeFi protocol or smart contract system.  
- Includes:
  - Vulnerability findings (documented in markdown).  
  - Proof-of-concept exploits (Solidity/Python).  
  - Tests verifying exploitability and fixes.  

👉 *Realistic audit-style case studies with reproducible examples.*  

---
### 2. [`concepts/`](./concepts/)
- Explanations of **DeFi primitives** and **security concepts**.  
- Each file focuses on a single topic (e.g., fee-on-transfer tokens, rebasing mechanics, access control pitfalls).  
- Written in a clear, blog-style format with definitions, examples, risks, and mitigations.  

👉 *Concise references for key blockchain security topics.*  

---
### 3. [`ethernaut/`](./ethernaut/)
- Full coverage of the [Ethernaut](https://ethernaut.openzeppelin.com/) smart contract CTF by OpenZeppelin.  
- Each level includes:
  - `attack.sol` → exploit contract (if required).  
  - `script.py` → Python automation for deployment/interaction.  
  - `test/LevelX.t.sol` → Foundry tests for reproducibility.  
  - `README.md` → minimal explanation of the vulnerability.  

👉 *Hands-on demonstration of core Solidity/EVM vulnerabilities.*  

---
### 4. `misc/`
- Collection of smaller experiments, notes, or snippets that don’t fit elsewhere.  
- Used as a scratchpad for exploratory research.  

---
### 5. [`tutorials/`](./tutorials/)
- Mini demo projects focused on specific vulnerabilities.  
- Each tutorial acts as a **self-contained lab** for teaching and testing a single security idea.  
- Example: [`cross_function_reentrancy/`](./tutorials/cross_function_reentrancy/) demonstrates **Cross-Function Reentrancy** using multiple interdependent contracts.  

👉 *Practical labs for deeper understanding of individual attack surfaces.*  

---
### 6. [`web3-quiz/`](./web3-quiz/)
- FAQs and exam-style questions in the Web3 security space.  
- Each Q&A has a **clear, concise answer** with real-world security context.  
- Built as a lightweight knowledge check and revision tool.  

👉 *Quick recall resource for interviews, certifications, and practice.*  

---
## 🌐 Purpose
This repository serves as:  
- A **security knowledge base** — organized and searchable.  
- A set of **reproducible exploit labs** — each with code, scripts, and tests.  
- A **long-term reference** — continuously updated as new vulnerabilities and practices evolve.  

---
## 🛡️ Highlights
- 📖 **Educational + Practical** — combines theory with reproducible exploits and defenses  
- ⚡ **Automation First** — exploits and solutions come with Python/Foundry test harnesses  
- 🔍 **Security Mindset** — focuses on real-world risks, not just academic examples  
- 🧩 **Composability** — each module builds toward a full-stack understanding of Web3 security

---
## 📌 Example Topics Covered
- Reentrancy, frontrunning & MEV  
- Integer overflows/underflows  
- Access control failures  
- Price oracle manipulation  
- Flash loan attacks  
- Upgradeable contract risks  
- Invariant & differential fuzzing  

---
## 📫 Connect
If you’re building in Web3 and value **security-driven development**, let’s connect.  

Feel free to contact me in case of any issues, or DM me on [LinkedIn](https://www.linkedin.com/in/yprakash/).  

If you’re hiring for protocol security or audit engineering — feel free to [reach out](mailto:yprakash.518@gmail.com).
