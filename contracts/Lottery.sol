// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    using SafeMathChainlink for uint256; //this controls overflow
    mapping(address => uint256) public addressToAmount;
    address payable[] public players;
    uint256 public randomness;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethToUsdPriceFeed;
    address payable public recentwinner;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    event RequestedRandomness(bytes32 requestId);
    LOTTERY_STATE public lottery_state; //variable of lottery_state type

    // 0
    // 1
    // 2
    uint256 public fee;
    bytes32 public keyhash;

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntryFee = 50 * (10**18);
        ethToUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED; // or 1
        fee = _fee;
        keyhash = _keyhash;
    }

    function enter() public payable {
        // 50 dollars minimum
        require(lottery_state == LOTTERY_STATE.OPEN, "Lottery not started yet"); // you can only enter if someone has started it
        require(msg.value >= getEntranceFee(), "Not enough eth");
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethToUsdPriceFeed.latestRoundData(); //this is gonna have 8 decimals
        uint256 adjustedPrice = uint256(price) * 10**10; //so now it has 18 decimals
        // solidity does not work with decimals so we cannot do 50$/2.000$*eth
        // 50*10¹⁸ / 2000*10¹⁸
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }

    //this can only be called by the admin
    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Cannot start a new lottery yet"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee); // request/receive arch : in this first trans we will request the data, in a second callback chainlink contract is going to return the data to this contraact
        //in another function Fullfillrandomness
        emit RequestedRandomness(requestId);
    }

    //when we call endLottery function, we are calling to a chainlink, that is going to respond calling fulfillRandomness

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        //no one can call this function. the VRFCoordinator will call this function
        //override means that we are overriding the original declaration of the fulfillrandomness
        //the vrfconsumer has the function fulfillrandomness but has nothing layout. it is meant to be overwritten
        //what is gonna happen after we get the random number back
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You aren't there yet"
        );
        require(_randomness > 0, "random-not-found");

        uint256 indexOfWinner = _randomness % players.length; // 22%7
        recentwinner = players[indexOfWinner];
        recentwinner.transfer(address(this).balance);
        //reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}
