// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;


import "@openzeppelin/contracts/access/Ownable.sol";
import "./RewardToken.sol";
import "./RewardNFT.sol";

contract KFCShop is Ownable {
    RewardToken public rewardToken;
    RewardNFT public rewardNFT;

    // threshold for NFT reward (use same unit as sale price in wei converted from frontend units)
    uint256 public nftThreshold; // e.g., 500 * 1e18 if prices are in "units"


    event Purchase(address indexed buyer, uint256 amountWei, uint256 tokenReward, bool nftMinted, uint256 nftId);


    constructor(address _rewardToken, address _rewardNFT, uint256 _nftThreshold) {
        rewardToken = RewardToken(_rewardToken);
        rewardNFT = RewardNFT(_rewardNFT);
        nftThreshold = _nftThreshold;
    }

    /**
     * @notice Owner-only function to record a purchase for a buyer
     * @param buyer Address of the buyer
     * @param amount Amount of purchase in "units" (not payable)
     */
    function buyFor(address buyer, uint256 amount) external onlyOwner {
        require(buyer != address(0), "Invalid buyer address");
        require(amount > 0, "Amount must be > 0");

        // Reward tokens: 10% of purchase amount
        uint256 tokenReward = (amount * 10) / 100;
        rewardToken.mint(buyer, tokenReward * 1e18);

        // Mint NFT if amount exceeds threshold and record the NFT ID
        bool mintedNFT = false;
        uint256 nftId = 0;
        if (amount >= nftThreshold) {
            nftId = rewardNFT.mintTo(buyer);
            mintedNFT = true;
        }

        emit Purchase(buyer, amount, tokenReward, mintedNFT, nftId);

    }

    // owner can withdraw ERC20 tokens mistakenly sent to this contract
    function rescueERC20(address token, address to, uint256 amount) external onlyOwner {
        IERC20(token).transfer(to, amount);
    }
}