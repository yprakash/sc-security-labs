// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract FeeOnTransferToken is ERC20 {
    address public feeRecipient;
    address public feePercentage;

    constructor(string memory name, string memory symbol, address _feeRecipient, uint256 _feePercentage) ERC20(name, symbol) {
        require(_feeRecipient != address(0), "Invalid fee recipient address");
        require(_feePercentage <= 10000, "Fee percentage must be between 0 and 10000"); // 10000 = 100%

        feeRecipient = _feeRecipient;
        feePercentage = _feePercentage;
    }

    function setFeeRecipient(address _feeRecipient) external {
        require(msg.sender == feeRecipient, "Only the current fee recipient can set a new recipient");
        require(_feeRecipient != address(0), "Invalid fee recipient address");
        feeRecipient = _feeRecipient;
    }

    function setFeePercentage(uint256 _feePercentage) external {
        require(msg.sender == feeRecipient, "Only the current fee recipient can set a new fee percentage");
        require(_feePercentage <= 10000, "Fee percentage must be between 0 and 10000"); // 10000 = 100%
        feePercentage = _feePercentage;
    }

    function _transfer(address sender, address recipient, uint256 amount) internal virtual override {
        require(sender != address(0), "Transfer from the zero address");
        require(recipient != address(0), "Transfer to the zero address");

        uint256 fee = (amount * feePercentage) / 10000; // Calculate the fee
        uint256 amountAfterFee = amount - fee; // Amount after deducting the fee

        super._transfer(sender, feeRecipient, fee); // Transfer the fee to the fee recipient
        super._transfer(sender, recipient, amountAfterFee); // Transfer the remaining amount to the recipient
    }
}
