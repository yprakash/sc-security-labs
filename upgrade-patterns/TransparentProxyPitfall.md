### Transparent Proxy Pitfall
In the Transparent Proxy pattern, what happens if the **proxy admin** calls a function that exists in the implementation contract?  
The call is blocked — admin can only use admin functions

In the Transparent Proxy pattern, the proxy contract checks:
- If caller == admin:  
  → Only **admin functions** (`upgradeTo`, `changeAdmin`, etc.) are allowed.  
  → Any other function call from the admin **reverts** to prevent accidental state changes.
- If caller != admin:  
  → Call is delegated to the implementation contract.

This prevents the admin from unintentionally interacting with the proxy as if they were a user, which could corrupt state or cause logic errors.

**Real-world note**: This is why upgrade scripts must **impersonate a non-admin** address when testing user flows in a transparent proxy.
