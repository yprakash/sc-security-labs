// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import {console, Test} from "forge-std/Test.sol";
import {Vault} from "../08_Vault/Vault.sol";

contract VaultTest is Test {
    Vault vault;

    function setUp() public {
        bytes32 pwd = "A very strong secret password :)";
        vault = new Vault(pwd);
    }

    function testVaultUnlock() public {
        // Make sure it's initially locked
        assertTrue(vault.locked(), "Vault should be locked initially");
        // Read the private password from storage slot 1
        bytes32 pwd = vm.load(address(vault), bytes32(uint256(1)));
        // Use the password to unlock the contract
        vault.unlock(pwd);
        // Now it should be unlocked
        assertFalse(vault.locked(), "Vault should be unlocked after using the correct password");
        console.log("Vault unlocked successfully");
    }
}