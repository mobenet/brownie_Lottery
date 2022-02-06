from os import link
from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
    interface,
)


LOCAL_BLOCKHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]


def get_account(index=None, id=None):
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id") -> brownie accounts list
    if index:
        return accounts[index]  # accounts[0]
    if id:
        return accounts.load(id)  # accounts brownie
    if (
        network.show_active() in LOCAL_BLOCKHAIN_ENVIRONMENTS
        or network.show_active()
        in FORKED_LOCAL_ENVIRONMENTS  # si la red es development o un mock, devuelve accounts[0]
    ):
        return accounts[0]
    return accounts.add(
        config["wallets"]["from_key"]
    )  # .env, y como default devuelve la account asociada a la private key (unica account "real")


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """This function will grab de contract addesses from the brownie config
    if defined, otherwise it will deploy a mock version of that contract
    and return that mock contract.

        Args:
            contract_name(string)

        returns:
            brownie.network.contract.ProjectContract: The most recently deployed version of
            this contract.
            MockV3Aggregator[-1]"""
    contract_type = contract_to_mock[contract_name]
    # for development networks
    if network.show_active() in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:  # len(MockV3Aggregator <= 0)
            deploy_mocks()
        contract = contract_type[-1]  # MockV3Aggregator[-1]
    else:  # now for testnets
        print("estas obtenint valor contract")
        contract_address = config["networks"][network.show_active()][contract_name]
        # abiz<<az
        # address
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_vale=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_vale, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1link
    account = account if account else get_account(id="freecodecamp-account")
    link_token = link_token if link_token else get_contract("link_token")
    print(
        f"before link, link_token = {link_token}, contract addres = {contract_address}, amount = {amount}"
    )
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # instead of doing this transfer, we can use Interfaces to interact with other contracts -> copy from chainlink mix the interface linktokensol
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund contract!")
    return tx
