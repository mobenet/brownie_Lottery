from tracemalloc import start
from brownie import network, config, Lottery
import time
from scripts.helpfulscripts import get_account, get_contract, fund_with_link

account = get_account(id="freecodecamp-account")


def deploy_lottery():
    # account = get_account(id="freecodecamp-account")
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify", False
        ),  # if no verify key , add false
    )
    print("deployed lottery")
    return lottery
    # if network.show_active() != "development":
    #    price_feed_address = config["networks"][network.show_active()][
    #        "price_feed_address"
    #   ]
    # else:
    # deploy mocks or fork ?


def start_lottery():
    # account = get_account(id="freecodecamp-account")
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("The lottery is started")


def enter_lottery():
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": get_account(), "value": value})
    tx.wait(1)
    print("You entered the lottery")


def end_lottery():
    # account = get_account(id="freecodecamp-account")
    lottery = Lottery[-1]
    # we first need some LINK token to call the endlottery
    # so first fund contract
    tx = fund_with_link(lottery.address, get_account(id="freecodecamp-account"))
    tx.wait(1)
    ending_trans = lottery.endLottery({"from": account})
    ending_trans.wait(1)
    # now we need to wait some blocks so that chainlink responds (callack function) to our fulfillrandomness func
    time.sleep(180)
    print(f"{lottery.recentwinner()} is the new winner")
    # there is no chainlink node to respond to the fuldillrandomness if we are in ganache


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
