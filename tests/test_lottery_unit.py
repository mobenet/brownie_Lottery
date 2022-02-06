from brownie import Lottery, accounts, network, config, exceptions
from scripts.deploy import deploy_lottery, get_account
from web3 import Web3
import pytest
from scripts.helpfulscripts import (
    LOCAL_BLOCKHAIN_ENVIRONMENTS,
    fund_with_link,
    get_contract,
    get_account,
)

# from dotenv import load_dotenv

# load_dotenv()

# we only want to run this when we are on a LOCAL environment. SO we will add pytest. unit testing never outside local
def test_getEntranceFee():
    if network.show_active() not in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    account = accounts[0]
    lottery = deploy_lottery()
    # Act
    # 2,000 etch/usd  -> setted in mocks
    # usdEntryFee = 50
    # 2000/1 == 50/x    x = 0.025
    expected_entrance = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert expected_entrance == entrance_fee
    # assert lottery.getEntranceFee() < Web3.toWei(0.02, "ether")


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):  # cannot enter if not started
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_enter():
    if network.show_active() not in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    lottery.startLottery({"from": get_account(id="freecodecamp-account")})
    lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
    assert lottery.players(0) == get_account()


def test_can_end():
    if network.show_active() not in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    lottery.startLottery({"from": get_account(id="freecodecamp-account")})
    lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": get_account(id="freecodecamp-account")})
    assert lottery.lottery_state() == 2


def test_can_pick_winner():
    if network.show_active() not in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    lottery.startLottery({"from": get_account(id="freecodecamp-account")})
    lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=5), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # we need to do all that because now it is the VRFCoordinator that callsback our contract to give it a random number
    transaction = lottery.endLottery({"from": get_account(id="freecodecamp-account")})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": get_account()}
    )
    starting_balance_account = get_account().balance()
    balance_lottery = lottery.balance()
    # 777 % 3 = 0 -> our account will be the winner
    assert lottery.recentwinner() == get_account()
    assert lottery.balance() == 0
    assert get_account().balance() == starting_balance_account + balance_lottery
