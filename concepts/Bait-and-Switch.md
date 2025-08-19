## Governance & Upgradeability Risks

- Bait = show a harmless implementation, attract deposits/liquidity.
- Switch = later, use an `onlyOwner`/`onlyGovernance` function to change some critical parameter (or implementation address in upgradeable systems) **to drain funds or steal rewards**.

🔹 Example: Suppose we have a staking contract:
```solidity
contract Staking {
    IERC20 public rewardToken;
    uint256 public rewardRate;   // rewards per block
    address public owner;
    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }
    function setRewardRate(uint256 newRate) external onlyOwner {
        rewardRate = newRate;
    }
    function claimRewards() external {
        // gives msg.sender rewardRate tokens
        rewardToken.transfer(msg.sender, rewardRate);
    }
}
```
At first, `rewardRate = 1 token per block`.  
Users happily stake, thinking "this is sustainable".

👉 But the owner could later call:
```solidity
setRewardRate(1e24); // basically infinite
```
Now the owner (or a whitelisted address) can call `claimRewards()` and instantly drain the rewardToken reserves.  
This is a **governance rug pull** → the "bait" was sustainable rewards, the "switch" is malicious owner-controlled inflation.

---
### 🔹 More Severe: Upgradeable Contracts
With **Transparent/UUPS/Beacon proxies**, the bait-and-switch risk is bigger:
- Deploy a normal looking implementation.
- Attract TVL.
- Use `upgradeTo()` (onlyOwner controlled) to point to a new malicious implementation that has e.g.:
```solidity
function withdrawAll() external {
    payable(owner).transfer(address(this).balance);
}
```
Now all user funds are gone.  
This is exactly why **auditors flag “upgradeable + centralized admin”** as a governance-level issue.

---
### 🔹 Real-World Parallels
- 2021: A number of **yield farms and forks of Sushi** rugged users by upgrading reward logic or setting reward rates to drain reserves.
- 2022: Some projects did an “upgrade implementation” to one that included **stealth mint()** in ERC20s, inflating supply out of thin air.
---
### ✅ So when auditors say “bait-and-switch risk”:
- They don’t mean there’s a coding bug.
- They mean the **architecture gives the owner power** to change behavior in ways users don’t expect.
- Even if not currently exploited, it’s a **trust model problem**.
