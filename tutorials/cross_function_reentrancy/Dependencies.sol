// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

abstract contract ReentrancyGuard {
    bool internal locked;

    modifier nonReentrant() {
        require(!locked, "ReentrancyGuard: reentrant call");
        locked = true;
        _;
        locked = false;
    }
}
