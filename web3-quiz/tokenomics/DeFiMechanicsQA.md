## DeFi and tokenomics mechanics — stablecoins, bonding curves, staking flows

### DeFi Mechanics — Stablecoin Collateralization
A protocol issues a stablecoin `sUSD` backed 1:1 by ETH. Users deposit ETH and mint equal value of `sUSD` using an oracle price feed.  
What’s the **primary DeFi risk** here?
```solidity
function mint(uint256 ethAmount) external payable {
    require(msg.value == ethAmount, "Mismatch");
    uint256 usdValue = ethAmount * ethPrice / 1e18;
    sUSD.mint(msg.sender, usdValue);
}
```
A. ETH price volatility could cause insolvency if ETH price drops.  
B. The protocol may miscalculate decimals in the ethPrice.  
C. Reentrancy in mint function.  
D. Users can mint without depositing collateral.
> A. ETH price volatility could cause insolvency if ETH price drops.
- The minting logic **does enforce collateral deposit**:
  - `require(msg.value == ethAmount)` ensures ETH is deposited.
  - `usdValue = ethAmount * ethPrice / 1e18` mints equivalent `sUSD`.
- So D is incorrect — you can’t mint without collateral.

👉 The real risk is **no over-collateralization**.
- If 1 ETH = $2000 at mint time, user deposits 1 ETH → mints 2000 sUSD.
- If ETH falls to $1500, that 1 ETH collateral now backs 2000 sUSD → protocol is **under-collateralized**.
- That’s why stablecoin systems like DAI require **>100% collateral ratios (e.g., 150%)**, plus liquidation mechanics.

Other points:
- B (**decimals miscalc**) is a coding bug, but **not** the core _mechanics_ risk.
- C (**reentrancy**) isn’t relevant here — mint just mints ERC20s after accounting.

---
### Staking Flow

A staking contract allows users to deposit tokens and earn rewards. What’s the hidden vulnerability?
```solidity
function stake(uint256 amount) external {
    require(amount > 0, "Zero stake");
    stakingToken.transferFrom(msg.sender, address(this), amount);
    balances[msg.sender] += amount;
}
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount, "Not enough staked");
    balances[msg.sender] -= amount;
    require(stakingToken.transfer(msg.sender, amount));
}
```
❌ A. Missing ReentrancyGuard in withdraw.

❌ B. No reward mechanism implemented.
> This is true — the function is purely “stake/unstake” without rewards. But that’s not inherently a vulnerability; it might just be a design choice.

❌ C. Uses transfer instead of safeTransfer.
> ⚠️ Subtle. If `stakingToken` is a non-standard ERC20 that doesn’t return a boolean, `transfer` could silently succeed/fail. Best practice is `IERC20(stakingToken).safeTransfer` (OpenZeppelin SafeERC20). This is a security/**design risk**, though not the **hidden vulnerability**.

✅ D. Does not handle deflationary tokens correctly.
- the **most realistic risk**. Some ERC-20s (deflationary/rebasing tokens) **burn or skim fees** on transfer.

Example:
- User stakes 100 tokens.
- But the token burns 5% on transfer, so only 95 arrive.
- `balances[msg.sender] = 100`, but contract only holds 95.
- Later, user calls `withdraw(100)` → contract reverts or runs out of funds.

This creates accounting mismatch vulnerabilities.

### Auditor’s Checklist for Staking Contracts:
- Use `safeTransferFrom` and `safeTransfer` (to handle non-standard ERC20).
- Check actual received amount:
```solidity
uint256 before = stakingToken.balanceOf(address(this));
stakingToken.transferFrom(msg.sender, address(this), amount);
uint256 received = stakingToken.balanceOf(address(this)) - before;
balances[msg.sender] += received;
```
- Handle **rebasing tokens** (balances may change unexpectedly).

🔥 Trick: This bug (deflationary mismatch) has been exploited in **real DeFi staking pools** where attackers deposited tokens with transfer fees, then drained more than contract balance allowed.

---
### Stablecoin Mechanic
A protocol pegs its stablecoin at $1 by allowing users to mint against ETH collateral.  
**Mint rule**: Deposit ETH worth $150 → Mint 100 stablecoins.  
**Redeem rule**: Burn 100 stablecoins → Withdraw ETH worth $150.  
Which economic flaw exists?

A. System can be drained if ETH price rises.  
B. Peg cannot hold if ETH price falls.  
C. Redeemers get arbitrage profits at expense of system.  
D. No flaw, this is safe if collateralization ratio is 150%.
> B. Peg cannot hold if ETH price falls.
- The system **assumes ETH will always cover liabilities**. But ETH is volatile.
- If ETH price drops, the collateral ratio falls below 100%. Example:
  - User deposited $150 worth of ETH, minted 100 stablecoins.
  - ETH price halves → collateral worth $75.
  - 100 stablecoins still in circulation. Collateral can’t cover redemption.
- This is exactly what happened with **early overcollateralized stablecoin prototypes** (before MakerDAO integrated liquidations).

Notes for exam framing:
- Option A (ETH rises) → doesn’t break the system, it overcollateralizes more.
- Option C (arbitrage profit) → can happen, but the root vulnerability is insolvency risk when price falls.
- Option D is false, because 150% collateralization is only safe with liquidation enforcement. Without it, peg collapse risk exists.

---
### Staking Flow — subtle bug
Which is the **most critical risk** here if used with arbitrary ERC20 tokens?
```solidity
function stake(uint256 amount) external {
    stakingToken.transferFrom(msg.sender, address(this), amount);
    balances[msg.sender] += amount;
}
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount, "Insufficient");
    stakingToken.transfer(msg.sender, amount);
    balances[msg.sender] -= amount;
}
```
A. Missing reward mechanism, so no incentive to stake.  
B. Malicious ERC20 could reenter withdraw.  
C. Deflationary tokens break accounting → users can withdraw more than deposited.  
D. Gas griefing due to repeated storage writes.
> C. Deflationary tokens break accounting → users can withdraw more than deposited.
- In stake(), the contract **assumes** that `transferFrom` will move exact `amount`.
- But some ERC20 tokens are **deflationary** or have fees (e.g., transfer burns 2%).
  - Example: You call `stake(100)` with a fee-on-transfer token.
  - Only 98 tokens reach the contract, but `balances[msg.sender]` is increased by **100**.
- Later in `withdraw()`, the user can withdraw 100, even though only 98 were actually deposited. This makes the pool **insolvent**.

Why not B (reentrancy)?
- `transfer` in ERC20 is a normal token transfer, **not an external call** to attacker logic (unlike ERC777 hooks).
- So **ERC20 alone cannot reenter**. Reentrancy here would only be possible with ERC777 or a malicious token contract implementing callbacks.

👉 This is a common audit finding: “Incompatible with fee-on-transfer/deflationary tokens.”

---
