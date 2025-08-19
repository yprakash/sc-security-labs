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
