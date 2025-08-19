# Understanding Insolvency Risk in DeFi

### What is Insolvency Risk?

Insolvency occurs when a protocol’s **liabilities exceed its assets**.  
In simpler terms: users believe their tokens are backed 1:1, but when everyone tries to withdraw, there isn’t enough collateral left to cover all claims.

This situation often arises in lending protocols, stablecoins, and liquidity pools when assumptions about pricing, collateralization, or liquidations fail.

---

### Common Causes of Insolvency

1. **Under-Collateralization**
   - If loans are issued with too little collateral, borrowers can default and leave the system short.
   - Example: collateral drops in value faster than the protocol can liquidate it.
2. **Price Oracle Manipulation**
   - Protocols rely on oracles to price assets.
   - If an attacker manipulates the oracle feed, they can borrow more than they should, draining reserves.
3. **Liquidity Mismatches**
   - Promising instant withdrawals while locking collateral in illiquid assets leads to insolvency when too many users exit at once.
4. **Protocol Design Flaws**
   - Poor liquidation logic, misconfigured collateral ratios, or flawed reward incentives can all leave reserves depleted.

---

### Real-World Cases of Insolvency

- **bZx Protocol (2020)**: Attackers manipulated the price oracle via Uniswap, inflating collateral values. They borrowed far more than they should, leaving bZx with bad debt that couldn’t be repaid.
- **Mango Markets (2022)**: An attacker manipulated the value of their MNGO collateral using perpetual futures on Mango itself.  
  With the inflated collateral, they borrowed ~$100M worth of assets, draining liquidity and rendering the protocol insolvent.
- **Venus Protocol (2021)**: The price of XVS (Venus governance token) spiked, allowing over-leveraging. When the price later crashed, liquidations were insufficient, leaving the protocol with ~$100M in bad debt.

---

### Why Insolvency is Dangerous

- **User Losses:** Depositors and lenders may be unable to withdraw funds.  
- **Contagion Risk:** Insolvent protocols can trigger chain reactions across DeFi (e.g., lending platforms, stablecoins, LP positions).  
- **Loss of Trust:** Even a temporary shortfall can destroy confidence, leading to bank-run-like behavior.

---

### How Protocols Try to Prevent Insolvency

- **Over-Collateralization:** Borrowers must deposit more collateral than they borrow.  
- **Robust Oracle Design:** Using decentralized oracles (e.g., Chainlink) instead of a single AMM price.  
- **Liquidation Mechanisms:** Automated auctions or incentivized liquidators to cover bad debt quickly.  
- **Insurance / Backstop Funds:** Reserve pools that absorb losses during black-swan events.  

---

### Key Takeaway  
Insolvency risk isn’t just a theoretical concern — it has already cost DeFi users **hundreds of millions of dollars**.  
Protocols that fail to anticipate market manipulation, collateral crashes, or liquidity mismatches can collapse overnight.

In DeFi, **solvency = survival**.
