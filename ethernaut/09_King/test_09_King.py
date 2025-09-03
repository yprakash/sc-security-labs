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
    yield w3, challenge_dir
    print(f"\nTearing down the module: {file_name}")

def test_exploit(setup_module):
    w3, challenge_dir = setup_module
    initial_prize = w3.to_wei(1, 'ether')
    hack_prize = w3.to_wei(2, 'ether')
    deployer_index = 0
    deployer = w3.eth.accounts[deployer_index]
    king_contract = load_w3_contract(challenge_dir, file_name='King.sol', version='0.8.0',
                                     value=initial_prize, deployer_index=deployer_index)
    print(f'King contract deployed with initial prize {king_contract.functions.prize().call()}')
    assert king_contract.functions._king().call() == deployer

    hack_contract = load_w3_contract(challenge_dir, file_name='AttackerKing.sol', version='0.8.0',
                                     value=hack_prize, deployer_index=1,
                                     constructor_args=[king_contract.address])
    print(f'Deployed hacking contract address {hack_contract.address}')
    assert king_contract.functions._king().call() != deployer
    assert king_contract.functions._king().call() == hack_contract.address
    print(f"Validated King ownership is changed")

    hack_prize = w3.to_wei(3, 'ether')
    with pytest.raises(ContractLogicError) as reverted:
        hack_contract = load_w3_contract(challenge_dir, file_name='AttackerKing.sol', version='0.8.0',
                                         value=hack_prize, deployer_index=2,
                                         constructor_args=[king_contract.address])
    assert ("Failed to send ether to become king"  # should be as same as revert message in AttackerKing.sol
            in str(reverted.value))
    print('Asserted even the revert:', reverted)
