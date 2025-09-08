# Obfuscation: Function Selector Tricks

### Overview
Solidity allows low-level calls using raw **function selectors** instead of explicit function names.  
This is often used in proxy/delegatecall patterns, but it can also be abused to **hide dangerous logic**.

Every Solidity function call is encoded as `function_selector + arguments`.  
The function selector is the first 4 bytes of the Keccak256 hash of the function signature.  
While this is normally abstracted away, some contracts **use raw selectors directly**.  
When the function name is replaced with only a hex value, the intent of the code is hidden.

---
### Example 1: Transparent Usage (Not Obfuscated)
```solidity
(bool success,) = target.call(
    abi.encodeWithSelector(bytes4(keccak256("pwn()")))
);
```
Here the selector is derived inline from `"pwn()"`.  
It’s verbose, any reader can see clearly that `pwn()` is being called.
This is not true obfuscation.

---
### Example 2: Hidden Selector (Obfuscated)
```solidity
bytes4 private constant SECRET = 0xa9059cbb;
function backdoor(address target, uint256 amount) external {
    (bool ok,) = token.call(
        abi.encodeWithSelector(SECRET, target, amount)
    );
    require(ok, "call failed");
}
```
What is `0xa9059cbb`?
- To the naked eye, it looks like a random hex.
- In reality, it’s the selector for `transfer(address,uint256)`.
- This means the function is secretly transferring tokens — a backdoor disguised behind an opaque constant.

---
### Example 3: Misleading Constant Names
```solidity
bytes4 private constant SAFE = 0x23b872dd; // actually transferFrom(address,address,uint256)
function rugPull(address from, address to, uint256 amount) external {
    (bool ok,) = token.call(
        abi.encodeWithSelector(SAFE, from, to, amount)
    );
    require(ok, "safe call failed");
}
```
The constant is named `SAFE`, but it’s actually the dangerous `transferFrom` function.  
A superficial review may assume this is harmless.

---
### Why It’s Obfuscation
- Readers see only hex values (e.g., `0xa9059cbb`) instead of readable function names.
- The real function is unknown, without computing the selector (e.g., via 4byte.directory ).
- Malicious contracts exploit this to **hide dangerous calls** under misleading constants.

---
### Legitimate Uses
- Proxy contracts forwarding arbitrary calls to implementations.
- Minimal proxy clones (EIP-1167).
- Gas-optimized meta-transaction relayers.
  - 👉 In these contexts, selector usage is expected and documented.

---
### Lessons Learned
- If you see hardcoded 4-byte constants, **always decode them**.
- Tools: `cast 4byte` (Foundry), 4byte.directory
- Be wary of misleading constant names (`SAFE`, `SECURE`, etc.).
- `delegatecall` combined with opaque selectors is especially dangerous — execution runs in the caller’s storage.

---
### References
- [Solidity Docs: ABI Encoding](https://docs.soliditylang.org/en/latest/abi-spec.html)
- [Selector Example](https://solidity-by-example.org/function-selector/)
- [SWC-112: Delegatecall to Untrusted Callee](https://swcregistry.io/docs/SWC-112/)
