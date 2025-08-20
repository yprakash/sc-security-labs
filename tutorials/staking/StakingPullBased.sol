// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title StakingPullBased
 * @notice Gas-scalable reward accounting using cumulative "accRewardPerShare".
 * - No loops over users; O(1) operations per user.
 * - Users "pull-claim" their rewards; the contract never loops to push.
 * - Handles fee-on-transfer staking tokens on deposit via delta measurement.
 * - Reentrancy-safe on mutating flows.
 *
 * Math:
 *   accRewardPerShare scaled by ACC (1e12).
 *   pending(user) = (user.amount * accRewardPerShare) / ACC - user.rewardDebt
 *
 * Flows:
 *   - fund()    : owner adds rewards, updates accRewardPerShare
 *   - stake()   : auto-claims pending, then increases amount & rewardDebt
 *   - withdraw(): auto-claims pending, then decreases amount & rewardDebt
 *   - claim()   : pull-claim pending rewards
 */
contract StakingPullBased is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable stakingToken;
    IERC20 public immutable rewardToken;

    uint256 public constant ACC = 1e12;

    uint256 public totalStaked;
    uint256 public accRewardPerShare; // cumulative rewards per staked token (scaled by ACC)

    struct UserInfo {
        uint256 amount;      // staked tokens
        uint256 rewardDebt;  // accounting checkpoint
    }

    mapping(address => UserInfo) public users;

    event Funded(uint256 amount, uint256 accRewardPerShare);
    event Staked(address indexed user, uint256 received, uint256 newAmount);
    event Withdrawn(address indexed user, uint256 amount);
    event Claimed(address indexed user, uint256 reward);

    constructor(IERC20 _staking, IERC20 _reward) {
        stakingToken = _staking;
        rewardToken  = _reward;
    }

    function pendingRewards(address user) public view returns (uint256) {
        UserInfo memory u = users[user];
        if (u.amount == 0) {
            return 0;
        }
        uint256 _acc = accRewardPerShare;
        // no implicit rewards here (no auto-compounding), all funding via fund()
        return (u.amount * _acc) / ACC - u.rewardDebt;
    }

    /**
     * @dev Owner or distributor adds rewards to be claimed by stakers.
     * No loops; we update a single global accumulator.
     */
    function fund(uint256 amount) external onlyOwner {
        require(amount > 0, "zero");
        require(totalStaked > 0, "nothing staked");
        rewardToken.safeTransferFrom(msg.sender, address(this), amount);
        accRewardPerShare += (amount * ACC) / totalStaked;
        emit Funded(amount, accRewardPerShare);
    }

    /**
     * @dev Stake with fee-on-transfer safety: credit exactly what arrived.
     * Auto-claims pending before changing stake amount.
     */
    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "zero");
        UserInfo storage u = users[msg.sender];

        // 1) Claim any pending rewards first
        _claim(msg.sender, u);

        // 2) Measure actual received (fee-on-transfer safe)
        uint256 beforeBal = stakingToken.balanceOf(address(this));
        stakingToken.safeTransferFrom(msg.sender, address(this), amount);
        uint256 received = stakingToken.balanceOf(address(this)) - beforeBal;
        require(received > 0, "nothing received");

        // 3) Update state
        u.amount += received;
        totalStaked += received;

        // 4) Set checkpoint
        u.rewardDebt = (u.amount * accRewardPerShare) / ACC;

        emit Staked(msg.sender, received, u.amount);
    }

    /**
     * @dev Withdraw staked tokens. Auto-claims pending first.
     */
    function withdraw(uint256 amount) external nonReentrant {
        UserInfo storage u = users[msg.sender];
        require(amount > 0 && u.amount >= amount, "bad amount");

        // 1) Claim pending rewards first
        _claim(msg.sender, u);

        // 2) Update stake
        u.amount -= amount;
        totalStaked -= amount;

        // 3) Update checkpoint
        u.rewardDebt = (u.amount * accRewardPerShare) / ACC;

        // 4) Transfer staked tokens out (note: if staking token charges fee on send,
        //     the user receives less than 'amount'—that’s token-specific behavior,
        //     not an accounting inconsistency on our side.)
        stakingToken.safeTransfer(msg.sender, amount);

        emit Withdrawn(msg.sender, amount);
    }

    /**
     * @dev Claim rewards without changing stake.
     */
    function claim() external nonReentrant {
        UserInfo storage u = users[msg.sender];
        _claim(msg.sender, u);
        // rewardDebt updated inside _claim
    }

    function _claim(address user, UserInfo storage u) internal {
        uint256 pending = 0;
        if (u.amount > 0) {
            uint256 accumulated = (u.amount * accRewardPerShare) / ACC;
            pending = accumulated - u.rewardDebt;
        }
        if (pending > 0) {
            // CEI: effects before interactions
            u.rewardDebt = (u.amount * accRewardPerShare) / ACC;
            rewardToken.safeTransfer(user, pending);
            emit Claimed(user, pending);
        } else {
            // keep rewardDebt consistent even if 0 pending
            u.rewardDebt = (u.amount * accRewardPerShare) / ACC;
        }
    }
}
