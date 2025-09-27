// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Importing the ERC20 standard implementation from OpenZeppelin.
// This provides the basic functionality of an ERC20 token, such as transfers and balances.
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

// Importing the Ownable contract from OpenZeppelin.
// This provides functionality to restrict certain actions to the contract owner.
import "@openzeppelin/contracts/access/Ownable.sol";

// The RewardToken contract inherits from ERC20 and Ownable.
// ERC20 provides the standard token functionality, and Ownable allows for owner-restricted actions.
contract RewardToken is ERC20, Ownable {
    // Constructor function that is executed when the contract is deployed.
    // It initializes the token with a name ("KFCReward") and symbol ("KFC").
    // It also mints an initial supply of tokens to the deployer's address.
    constructor() ERC20("KFCReward", "KFC") {
        // Minting 1,000,000 tokens (adjusted for decimals) to the deployer's address.
        // The `decimals()` function (inherited from ERC20) returns the number of decimal places (default is 18).
        _mint(msg.sender, 1000000 * 10 ** decimals()); // Initial supply for distribution
    }

    // The `mint` function allows the owner of the contract to mint new tokens.
    // This function is restricted to the owner using the `onlyOwner` modifier from the Ownable contract.
    // Parameters:
    // - `to`: The address to which the newly minted tokens will be sent.
    // - `amount`: The number of tokens to mint (adjusted for decimals).
    function mint(address to, uint256 amount) external onlyOwner {
        // Minting the specified amount of tokens to the given address.
        _mint(to, amount);
    }
}