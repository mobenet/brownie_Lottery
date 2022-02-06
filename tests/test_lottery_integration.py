from scripts.deploy import deploy_lottery
from scripts.helpfulscripts import (
    LOCAL_BLOCKHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
)
from brownie import network, accounts
import pytest
from scripts.deploy import deploy_lottery
import time

# here we will use testnet!!!! rinkeby


def test_can_pink_winner():
    if network.show_active() in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    # we dont need to pretend to be a chainlink node as we are on an actual network. so we will wait
    # for the chainlink node to respond
    time.sleep(60)  # one minut
    assert lottery.recentwinner() == account
    assert lottery.balance() == 0
