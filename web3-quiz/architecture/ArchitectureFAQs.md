### Architecture — Access Control Layering
You are auditing a staking protocol. It uses an `onlyOwner` modifier on `setRewardRate(uint256 newRate)` function. The owner is a multisig controlled by the team.

Which of the following is the primary architectural concern?  
A. No issue — this is the standard pattern.  
B. Centralization risk — the team can arbitrarily change rewards, making staking economics unpredictable.  
C. Gas inefficiency — multisig interactions are more expensive than EOAs.  
D. Replay attack risk — multisigs are not secure against replays.
> Centralization risk
- Even though the function is access-controlled properly, the **architectural concern** is that the **team-controlled multisig** can arbitrarily change reward rates.
- This means stakers do not have **economic guarantees** — the protocol can **reduce or increase rewards at will**, which undermines trust and can even be used maliciously (e.g., bait-and-switch).
- This isn’t a Solidity-level bug, it’s a **governance/architecture-level risk** — exactly the kind of thing auditors should flag in reports.

Best practice:
- Define **clear governance processes** (DAO votes, timelocks) for critical parameter changes like reward rates, collateral ratios, or interest models.
- Otherwise, you expose users to **governance risk** (team abuse) instead of just technical risk.

---

### Architecture — Protocol Composability
A new DEX allows **flashloans** from its liquidity pools. The protocol assumes that as long as `totalSupply == reserve0 + reserve1`, the system is safe.  
What is the most critical design risk?  
A. Attackers can reenter flashloan functions to bypass repayment.  
B. The invariant check is too simplistic; it ignores token transfers with hooks (ERC777 / ERC1363) and other composability risks.  
C. Flashloans always introduce MEV risk regardless of invariants.  
D. The protocol is secure since flashloans require repayment within one transaction.
> B. The invariant check is too simplistic
- The protocol checks only `totalSupply == reserve0 + reserve1` to “validate” solvency, but this invariant is **too simplistic**.
- Why? Tokens with **transfer hooks** (like `ERC777` or malicious ERC20s) can execute arbitrary code during a transfer. That means:
  - Reserve balances may be manipulated mid-transaction.
  - Extra mint/burn logic can bypass assumptions.
- This is a composability risk — protocols must anticipate that any ERC20 token may not behave like a simple “balance = supply” model.

**Real-world tie-in**:
- Several hacks (e.g., **Uniswap integrations with ERC777**) demonstrated how reentrancy during token transfers breaks assumptions.
- That’s why secure DEXs like Uniswap V2/V3 use **carefully designed invariants** and **reentrancy guards**.

**Takeaway**: Never assume all ERC20s are “vanilla.” Invariants **must account for non-standard token behavior**.

---
### Architecture — Upgrade Pattern Trap

Consider this simplified Transparent Proxy pattern. What is the architectural flaw?
```solidity
contract Proxy {
    address public implementation;
    address public admin;
    function upgradeTo(address newImpl) external {
        require(msg.sender == admin, "Not admin");
        implementation = newImpl;
    }
    fallback() external payable {
        (bool ok, ) = implementation.delegatecall(msg.data);
        require(ok, "delegatecall failed");
    }
}
```
A. Implementation can call upgradeTo via delegatecall and seize upgradeability.  
B. Fallback does not forward msg.value, causing ETH to be locked.  
C. The proxy does not use storage slots defined by EIP-1967, creating upgrade collisions.  
D. Gas inefficiency — using delegatecall in fallback wastes gas.
> C. The proxy does not use storage slots defined by EIP-1967, creating upgrade collisions.
- In upgradeable proxies, storage layout collisions are a critical architectural risk.
- This proxy uses `implementation` and `admin`, variables occupy storage slots `0` and `1`.
- But — if the implementation contract **also** uses slot `0` for a state variable (say `uint256 totalSupply`), then after `delegatecall`, it will overwrite the proxy’s storage.

👉 This is why **EIP-1967** mandates specific storage slots (`bytes32` values) for `implementation` and `admin` — reducing collision risk.
#### **Real-world tie-in**:
- Badly designed proxies without fixed storage slots have been exploited — implementations overwrote proxy ownership or upgrade slots.
- OpenZeppelin Proxy strictly follows EIP-1967 to prevent this.

---
### Architecture — Tokenomics & Security Overlap
A yield protocol distributes rewards via a function:
```solidity
function claimReward() external {
    uint256 reward = rewardBalance[msg.sender];
    require(reward > 0, "No reward");
    rewardBalance[msg.sender] = 0;
    IERC20(rewardToken).transfer(msg.sender, reward);
}
```
The system assumes this is safe because reentrancy is prevented by updating state before transfer. What’s the architectural-level risk that still remains?

A. No risk — this is fully secure.  
B. If rewardToken is malicious (ERC777-style), it can perform reentrancy elsewhere in the protocol.  
C. Users can grief the system by repeatedly calling with zero rewards.  
D. Gas griefing — large transfers may cause DoS.
> B. If rewardToken is malicious (ERC777-style), it can perform reentrancy elsewhere in the protocol.
- The function follows the Checks-Effects-Interactions (**CEI**) pattern, so direct reentrancy on `rewardBalance` is **prevented**.
- BUT — if `rewardToken` is a malicious ERC20/777, its `transfer` may **trigger callbacks** (via hooks).
  - That callback could call into **other functions of the protocol**, not just `claimReward`.
  - For example, it could stake, borrow, or manipulate accounting while inside the transfer.

👉 This is a **protocol-level composability risk**, not a line-of-code bug.

#### Real-world tie-in:
- The **Uniswap ERC777 issue** (2019) forced Uniswap and Compound to add reentrancy guards to protect against malicious tokens.
- Just updating balances first is **not enough** when you have cross-function interactions and arbitrary tokens.

#### Best practice:
- Always consider malicious ERC20/777 tokens.
- Use reentrancy guards even after CEI.
- Consider **whitelisting reward tokens** or wrapping ERC777s to neutralize hooks.

---
### Architecture — Governance Risk in Proxies

A DAO controls the proxy admin of a lending protocol. The DAO can upgrade the implementation contract through governance proposals. Which of the following is the **most realistic risk**?

A. No risk — DAOs are decentralized and can’t be exploited.  
B. If a malicious proposal passes (due to low voter turnout or governance attack), funds can be drained via a malicious upgrade.  
C. Governance upgrade paths are always protected by timelocks, so this is safe.  
D. The proxy’s storage layout will automatically prevent malicious upgrades.
> B. Even though the protocol uses a DAO-controlled proxy admin, governance is not inherently safe.

**Risks**:
- **Low voter turnout** → attacker with enough tokens can push malicious proposals.
- **Governance capture** (flashloan attacks, borrowed voting power) → attacker seizes upgrade control temporarily.
- **Social engineering / rushed votes** → users approve harmful upgrades.

**Key point**: Decentralized governance ≠ automatically secure. It just shifts the **trust assumption** from the team → token holders.

Real-world tie-ins:
- **Beanstalk (2022)** — attacker flashloaned voting power, passed a malicious governance proposal, drained $182M.
- **Compound** — governance proposals have accidentally bricked functionality in the past due to overlooked risks.

👉 Auditors must always note: governance upgrades = fund custody risk.

---
### Architecture — Cross-Contract Assumptions

A staking protocol integrates with an external price oracle to calculate rewards:
```solidity
function rewardAmount(address user) public view returns (uint256) {
    uint256 price = oracle.getPrice();
    return balances[user] * price / 1e18;
}
```
What’s the architectural risk?
> If the oracle is compromised or manipulated, rewards can be miscalculated, inflating or draining the system.
- Even though `rewardAmount` is a `view` function and does not change state, the **architecture still depends on the oracle’s integrity**.
- If the oracle is manipulated:
  - Rewards could be massively inflated, causing insolvency when users claim.
  - Rewards could be suppressed, unfairly reducing payouts.
- This is a **design-level trust assumption**, not a Solidity coding bug.

Real-world tie-in:  
- **Synthetix oracle incident (2019)** — bot exploited a faulty price feed, draining **~37M sETH** in minutes.
- **Harvest Finance hack (2020)** — price manipulation of Curve LP tokens drained **$34M**.

👉 Lesson: Auditors must **always flag external dependencies** like oracles, even inside view functions.

---
### Architecture — Hidden Upgrade Vector
You are auditing a protocol where the team claims: “_Our contracts are immutable — no upgrade functions exist._”  
But you find the following snippet in one of the contracts:
```solidity
function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
    IERC20(token).transfer(msg.sender, amount);
}
```
What’s the architectural-level risk here?
> This acts as a hidden upgrade vector because the owner can drain protocol funds at any time.
- The team markets the contracts as **immutable**, but this `emergencyWithdraw` effectively gives the **owner unilateral custody**.
- This is a “**hidden upgrade vector**” — not an upgrade in code structure, but in _practical control_.
- Users may believe the protocol is decentralized/immutable, but in reality, the **owner can rugpull** anytime.

**Real-world tie-in**:
- Many “rug pulls” use exactly this pattern: hiding behind “_admin-only emergency functions_”.
- Auditors must highlight that such functions **invalidate immutability claims** and represent **centralization risk**.

👉 Best practice:
- If emergency withdrawals are needed, use **timelocks + multisig + DAO approval**.
- Otherwise, call it what it is: **upgradeable / admin-controlled** protocol.

---
### Cross-function reentrancy

A protocol allows users to deposit ETH. Later, withdrawals are handled with:
```solidity
function deposit() external payable {
    balances[msg.sender] += msg.value;
}
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount, "Not enough balance");
    balances[msg.sender] -= amount;
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok, "ETH transfer failed");
}
```
Architecturally, what is the biggest design-level risk?  
A. Reentrancy attack on `withdraw`.  
B. ETH can get stuck if user is a contract without a payable fallback.  
C. Users may DOS the system by consuming all gas during `call`.  
D. The protocol lacks a way to pause withdrawals in emergencies.
> A. Reentrancy attack on withdraw.

At first glance, this looks **CEI-safe** — state updated before external call. But here’s the subtle trap:
- Because `balances` is updated **before the external call**, a malicious contract cannot directly double-withdraw in this function.
- BUT the reentrancy risk appears **if there are other functions** that depend on `balances[msg.sender]`.
  - Example: attacker calls `withdraw` → reenters another function like `deposit`, `claimReward`, or governance voting that relies on `balances`.
  - This is known as **cross-function reentrancy**.

**Why not B**?
- Sending ETH with `call{value: amount}("")` works even if the receiver contract has no payable function — it simply reverts if not payable.
- But since the protocol checks ok, that error is already handled.
- The _real_ systemic risk is _reentrancy_, not ETH lockup.

**Real-world tie-in**:
- TheDAO hack (2016) → classic reentrancy.
- bZx reentrancy exploit (2020) → cross-function reentrancy through ERC20 callbacks.

---

### Architecture — Multi-Contract Systems

A yield aggregator has the following design:
- Vault contract: accepts user deposits, issues shares.
- Strategy contracts: move funds into external protocols (Aave, Compound, Curve).
- Vault can upgrade to new strategies via `setStrategy(address newStrat)` controlled by the team multisig.

What’s the main architectural risk here?
> The team multisig can replace the strategy with a malicious one and drain funds.

- The **vault/strategy pattern** is common in Yearn-style yield aggregators.
- But because the vault lets a **team-controlled multisig** call `setStrategy()`, the multisig can swap in a **malicious strategy** at any time.
- That means the system is not really decentralized — **custody risk** is concentrated in the multisig.

#### Real-world tie-in:
- **Pickle Finance exploit (2020)** — strategy contracts were compromised, leading to ~$20M loss.
- **BadgerDAO attack (2021)** — injected malicious contracts into the frontend, tricking users into approvals.
- Even without an exploit, this is a **rug pull vector** disguised as “upgradeability.”

👉 Best practice:
- Guard strategy changes with **DAO votes + timelock**.
- Or require **user opt-in** to new strategies.
