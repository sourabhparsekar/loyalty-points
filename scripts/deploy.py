from brownie import accounts, network, RewardToken, RewardNFT, KFCShop, config

def main():
    print(f"Deploying to {network.show_active()}...")

    # Load deployer account (you created this via `brownie accounts new deployer`)
    deployer = accounts.load("deployer")
    # deployer = accounts[0]  # For simplicity in local/test networks
    print(f"Deployer address: {deployer.address}")

    # 1. Deploy RewardToken (ERC20)
    print("Deploying RewardToken...")
    reward_token = RewardToken.deploy({"from": deployer})
    print(f"RewardToken deployed at: {reward_token.address}")

    # 2. Deploy RewardNFT (ERC721)
    print("Deploying RewardNFT...")
    reward_nft = RewardNFT.deploy({"from": deployer})
    print(f"RewardNFT deployed at: {reward_nft.address}")

    # 3. Deploy KFCShop (loyalty program contract)
    print("Deploying KFCShop...")
    shop = KFCShop.deploy(
        reward_token.address,  # Address of the RewardToken contract
        reward_nft.address,    # Address of the RewardNFT contract
        500,          # NFT threshold (e.g., 500 units in wei)
        {"from": deployer}
    )
    print(f"KFCShop deployed at: {shop.address}")

    # Transfer ownership of ERC20 + ERC721 to Shop (only owner can mint)
    reward_token.transferOwnership(shop.address, {"from": deployer})
    reward_nft.transferOwnership(shop.address, {"from": deployer})

    print("✅ Deployment complete!")
    return reward_token, reward_nft, shop
