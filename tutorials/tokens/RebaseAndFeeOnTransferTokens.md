# Fee on Transfer Tokens

Fee-on-transfer tokens are ERC-20 tokens that deduct a fee whenever they are transferred. This fee could be used for various purposes, such as burning a percentage of the tokens, redirecting a portion of each transaction to a specific wallet (e.g., for development, marketing, or redistribution to holders), or other utility-specific mechanisms.

Example: ./FeeOnTransferToken.sol

In this example, every time a transfer occurs, a fee is calculated and deducted before sending the remaining amount to the recipient.

Real-World Example: Reflect Finance (RFI)  
[RFI](https://etherscan.io/token/0xa1afffe3f4d611d252010e3eaf6f4d77088b0cd7#code) is a real-world example of a fee-on-transfer token. Every time an RFI token is transferred, a fee (typically 1%) is deducted from the transaction amount. This fee is then distributed among existing token holders, creating an automatic yield for holders based on transaction volume.

# Rebase Tokens

Rebase tokens adjust their total supply algorithmically, either increasing or decreasing the balance of all token holders simultaneously. The goal is typically to maintain a peg or target price by expanding or contracting the total supply in response to market conditions.

Example: ./RebaseToken.sol

Real-World Example: Ampleforth (AMPL)  
[AMPL](https://etherscan.io/address/0xd0e3f82ab04b983c05263cf3bf52481fbaa435b1#code) is a well-known rebase token that automatically adjusts its supply to target a price of $1 per AMPL. The rebase function changes the total supply based on the current market price, expanding or contracting the supply to bring the price closer to the target.

## Security Issues and Problems
### Slippage and Liquidity Issues
Many DeFi protocols, particularly Automated Market Makers (AMMs) like Uniswap and Sushiswap, assume that the amount of tokens sent equals the amount received. With fee-on-transfer tokens, this assumption breaks down, leading to higher-than-expected slippage and potential transaction failures.

### Breaking ERC-20 Assumptions
Protocols and smart contracts often rely on the standard ERC-20 behavior: that `balanceOf` returns a consistent value and that `transfer` and `transferFrom` result in equal amounts being sent and received. Fee-on-transfer tokens violate this assumption, which can cause smart contracts to malfunction.

### Incorrect Balances with Rebase Tokens
DeFi protocols typically assume that token balances remain static unless explicitly modified. However, with rebase tokens, balances can automatically adjust due to rebase events. This can cause significant issues:

- Over-Redemption: A protocol might allow users to withdraw more tokens than are available if it doesn’t account for a negative rebase.
- Under-Collateralization: In lending scenarios, a negative rebase could reduce collateral value, leading to under-collateralized loans and potential insolvency.
- Inaccurate Rewards: Staking protocols might distribute rewards based on the original staked amount, not accounting for changes due to rebase events.

### Front-Running Risks
Rebase tokens can be vulnerable to front-running attacks. Malicious actors might attempt to exploit predictable rebase events to profit from the expected supply changes, employing complex trading strategies to manipulate the market.

## Conclusion
While fee-on-transfer and rebase tokens offer innovative features, they also introduce significant complexities and security risks that must be carefully managed. Developers must account for these issues when integrating such tokens into DeFi protocols, ensuring that assumptions about token behavior align with the actual mechanics of these advanced ERC-20 tokens.
