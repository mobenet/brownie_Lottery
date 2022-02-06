1. Users can enter lottery with ETH based on a USD fee
2. An admin will choose when the lottery is over
3. The lottery will select a random winner


As we have a admin the app is not fully decentralized. We could decentralize it using Chainlink keepers (so that the contract chooses itself when the lottery is over)


chainlink keepers

HOw do we want to test ?
1. 'mainnet-fork' -> because we are only working on some on chain contracts
2. 'development' with mocks
3. 'testnet'