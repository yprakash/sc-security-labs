// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/ownership/Ownable.sol";

contract RebaseToken is ERC20, Ownable {
    uint256 public targetPrice;
    uint256 public rebaseInterval;
    uint256 public lastRebaseTime;

    event RebaseOccurred(uint256 currentPrice, uint256 newTotalSupply);

    constructor(string memory name, string memory symbol, uint256 _initialSupply, uint256 _targetPrice, uint256 _rebaseInterval) ERC20(name, symbol) {
        require(_targetPrice > 0, "Target price must be greater than zero");
        require(_rebaseInterval > 0, "Rebase interval must be greater than zero");

        targetPrice = _targetPrice;
        rebaseInterval = _rebaseInterval;
        lastRebaseTime = block.timestamp;
        _mint(msg.sender, _initialSupply * 10 ** decimals());
    }

    function rebase(uint256 currentPrice) external onlyOwner {
        require(block.timestamp >= lastRebaseTime + rebaseInterval, "Rebase not allowed yet");

        if (currentPrice == 0) {
            revert("Current price cannot be zero");
        }
        uint256 supplyAdjustment;

        if (currentPrice > targetPrice) {
            // Calculate the new total supply based on the current price
            supplyAdjustment = totalSupply() * (currentPrice - targetPrice) / targetPrice;
            _mint(address(this), supplyAdjustment); // Mint new tokens to maintain the target price
        } else if (currentPrice < targetPrice) {
            // Calculate the new total supply based on the current price
            supplyAdjustment = totalSupply() * (targetPrice - currentPrice) / targetPrice;
            _burn(address(this), supplyAdjustment); // Burn tokens to maintain the target price
        }

        lastRebaseTime = block.timestamp;
        emit RebaseOccurred(currentPrice, totalSupply());
    }
}
