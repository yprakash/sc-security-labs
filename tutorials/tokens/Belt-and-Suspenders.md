# Belt-and-Suspenders Accounting

In finance, “belt-and-suspenders” means _extra redundancy for safety_.  In Solidity, this translates to:
- **Never trust** `amount` **arguments blindly**
- Check actual balances before/after transfers
- **Design share-based systems** where rebases or deflationary quirks don’t break math

**Example: Combined Defensive Pattern**
```solidity
function safeDeposit(uint256 amount) external {
    uint256 beforeBal = token.balanceOf(address(this));
    token.transferFrom(msg.sender, address(this), amount);
    uint256 afterBal = token.balanceOf(address(this));
    uint256 received = afterBal - beforeBal;

    uint256 pool = beforeBal; // tokens in pool before deposit
    uint256 mintShares = (totalShares == 0) ? received : (received * totalShares) / pool;

    shares[msg.sender] += mintShares;
    totalShares += mintShares;
}
```
- ✔ Handles fee-on-transfer (credits only received)
- ✔ Handles rebasing (tracks shares, not raw tokens)
- ✔ Resilient across weird ERC-20 implementations
