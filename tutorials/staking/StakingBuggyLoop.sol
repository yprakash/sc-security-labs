// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title StakingBuggyLoop
 * @notice Demonstrates the classic "loop over stakers" reward distribution bug.
 * - Vulnerability: distributeRewards() loops over unbounded stakers[].
 *   Anyone can DoS by making stakers[] huge (dust stakes), making this function
 *   run out of gas and effectively freezing reward distribution.
 * - Secondary issues shown for learning:
 *   - Credits `amount` as-staked without measuring actual received (fee-on-transfer risk).
 *   - Uses push-payments inside loop (less safe than pull-claims).
 */
contract StakingBuggyLoop is Ownable {
    using SafeERC20 for IERC20;

    IERC20 public immutable stakingToken;
    IERC20 public immutable rewardToken;

    uint256 public totalStaked;
    mapping(address => uint256) public balances;
    address[] public stakers;               // unbounded list
    mapping(address => bool) public isStaker;

    constructor(IERC20 _staking, IERC20 _reward) {
        stakingToken = _staking;
        rewardToken  = _reward;
    }

    function stake(uint256 amount) external {
        require(amount > 0, "zero");
        // Not robust for fee-on-transfer tokens (credits 'amount' blindly)
        stakingToken.safeTransferFrom(msg.sender, address(this), amount);
        if (!isStaker[msg.sender]) {
            isStaker[msg.sender] = true;
            stakers.push(msg.sender);
        }
        balances[msg.sender] += amount;
        totalStaked += amount;
    }

    /**
     * @dev Unbounded loop DoS:
     *   - If stakers[] length is large, this will revert due to gas,
     *     making rewards undistributable (griefing).
     */
    function distributeRewards(uint256 rewardAmount) external onlyOwner {
        require(totalStaked > 0, "nothing staked");
        rewardToken.safeTransferFrom(msg.sender, address(this), rewardAmount);

        for (uint256 i = 0; i < stakers.length; i++) {
            address u = stakers[i];
            uint256 share = (rewardAmount * balances[u]) / totalStaked;
            if (share > 0) {
                rewardToken.safeTransfer(u, share); // push per-user in loop
            }
        }
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "insufficient");
        balances[msg.sender] -= amount;
        totalStaked -= amount;
        stakingToken.safeTransfer(msg.sender, amount);
    }

    // View helper
    function stakersCount() external view returns (uint256) {
        return stakers.length;
    }
}
