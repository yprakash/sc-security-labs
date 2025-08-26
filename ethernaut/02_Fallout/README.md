# Challenge 02 - Fallout

This level demonstrates how a small typo in a constructor’s name can break the entire access control of a contract — letting any attacker become the owner. The inspiration comes from the real-world case of Rubixi, a Ponzi-like contract that accidentally allowed any user to hijack ownership due to a misnamed constructor.

📜 The Story

A new DeFi protocol launched with great fanfare. It had a "clever" twist on yield distribution — all built into a single contract. The developers added an owner role to control upgrades and withdrawals.

But they made a critical mistake: they misspelled the constructor.

Because of this:
- The contract did not assign ownership during deployment
- The “constructor” became a public function, callable by anyone
- One observant attacker saw this... and took over the contract forever.

This level simulates that failure — your job is to exploit it.

🧪 Your Goal
- Become the owner of the contract by exploiting the faulty constructor. Once you’re the owner, you win the level.

🧬 Skills You’ll Learn
- Legacy Solidity syntax & constructor patterns
- Misuse of access control
- Contract initialization bugs
- Real-world exploit modeling

⚠️ Make sure your foundry.toml is configured, as this level uses Solidity 0.6.0 to simulate based on older contract patterns (e.g., misnamed constructors).
```toml
solc_version = "0.6.0"
```
