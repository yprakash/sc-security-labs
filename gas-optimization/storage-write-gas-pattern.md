### Storage write gas pattern
If you set a storage variable from one **non-zero** value to another **different non-zero** value, what is gas cost in Solidity ≥0.8.0?  
**It costs ~5,000 gas.**

- **20,000 gas** is charged when setting a storage slot from [zero → non-zero](https://ethereum.stackexchange.com/a/99141) (first initialization).
- **~5,000 gas** is charged when changing a **non-zero → different non-zero** value (an update).
- **~4,800 gas refund** applies when going from **non-zero → zero** (post-EIP-3529).

**Security / gas note**:  
This distinction matters in DeFi accounting logic — protocols that frequently update non-zero values (like balances, reserves, or indexes) pay far less than ones that constantly reset to zero and reinitialize. Some vault protocols intentionally keep “dust” values to avoid the 20k cost of reinitialization.
