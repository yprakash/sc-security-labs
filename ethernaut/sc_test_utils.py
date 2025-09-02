import os

from dotenv import load_dotenv
import solcx
from web3 import Web3
from web3.contract import Contract
from web3.types import TxReceipt

tx_receipt_keys = ["cumulativeGasUsed", "effectiveGasPrice", "from", "gasUsed", "logs", "status",
                   "to", "transactionHash", "transactionIndex", "blockNumber", "contractAddress"]
load_dotenv(dotenv_path='.env')


def get_env(key, default=None, throw=True):
    # though configparser can Organize (configuration settings into sections/hierarchical),
    # all other ways are Not cloud-native and Less secure for sensitive data
    val = os.getenv(key, default)
    if val is None:
        if throw and default is None:
            raise RuntimeError(f'env variable "{key}" not found. Please check')
        val = default
    return val


provider_url = get_env('PROVIDER_URL', "http://127.0.0.1:8545")
print('Connecting to Ethereum node at', provider_url)
w3 = Web3(Web3.HTTPProvider(provider_url))


def compile_contract(source_code: str, version: str, contract_name: str = None):
    installed_solc_versions = [v.public for v in solcx.get_installed_solc_versions()]
    print('installed_solc_versions:', installed_solc_versions)
    if version not in installed_solc_versions:
        solcx.install_solc(version)
        print(f'Installed solc version as {version} not installed already')
    solcx.set_solc_version(version=version)

    compiled_sol = solcx.compile_source(source_code)
    if contract_name is None:
        contract_key = next(iter(compiled_sol))
    else:
        contract_key = f'<stdin>:{contract_name}'
    contract_interface = compiled_sol[contract_key]
    print(f'Compiled contract interface for contract {contract_key}')
    return contract_interface


def load_w3_contract(
        dir_name: str,  # Directory containing the Solidity file
        file_name: str = None,  # Solidity file name '.sol'
        contract_name: str = None,  # Contract name in the Solidity source code
        version: str = '0.8.29',  # Solidity version to use for compilation
        deployer_index: int = 0,  # Index of the account to use for deployment
        value = None,  # Value to send with the transaction
        constructor_args: list = None  # Constructor arguments for the contract
):
    """
    Loads a Solidity contract from the specified directory, compiles it,
    and deploys it to the local Ethereum node. Returns the deployed contract instance.
    """
    if not file_name:
        file_name = next((f for f in os.listdir(dir_name) if f.endswith('.sol')), None)
    if file_name:
        print(f'Loading contract {file_name} from dir {dir_name}')
    else:
        raise Exception(f"No Solidity files found in directory: {dir_name}")

    # if not contract_name: contract_name = file_name.split('.')[0]  # Assume contract name matches file name

    contract_path = os.path.join(dir_name, file_name)
    with open(contract_path, 'r') as file:
        contract_source = file.read()

    contract_interface = compile_contract(contract_source, version, contract_name)
    deployer = w3.eth.accounts[deployer_index]
    print(f'Deployer: {deployer} at index {deployer_index} among {len(w3.eth.accounts)} Available eth Accounts')
    # Assume the first account in the list is the deployer

    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    # transact_args = {'from': deployer, 'gas': 1000000, 'gasPrice': w3.to_wei('50', 'gwei')}
    transact_args = {'from': deployer}
    if value:
        transact_args['value'] = value
    if constructor_args:
        tx_hash = contract.constructor(*constructor_args).transact(transact_args)
    else:
        tx_hash = contract.constructor().transact(transact_args)

    tx_receipt: TxReceipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    # tx_values = {k: v for k, v in tx_receipt.items() if k in tx_receipt_keys}
    print(f'Deployed contract Transaction receipt: {minimal_tx(tx_receipt)}')
    deployed_contract: Contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=contract_interface['abi'])
    return deployed_contract


def minimal_tx(tx_receipt: TxReceipt):
    """
    Returns a minimal transaction receipt with only the relevant fields.
    """
    return {k: tx_receipt[k] for k in tx_receipt_keys}


def get_web3_instance():
    return w3
