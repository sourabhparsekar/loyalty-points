// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Importing the ERC721 standard implementation from OpenZeppelin.
// This provides the basic functionality of an ERC721 token, such as ownership and transfer of unique tokens.
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

// Importing the Ownable contract from OpenZeppelin.
// This provides functionality to restrict certain actions to the contract owner.
import "@openzeppelin/contracts/access/Ownable.sol";

// The RewardNFT contract inherits from ERC721 and Ownable.
// ERC721 provides the standard functionality for non-fungible tokens (NFTs), and Ownable allows for owner-restricted actions.
contract RewardNFT is ERC721, Ownable {
    // A public variable to keep track of the next token ID to be minted.
    // This ensures that each token has a unique ID.
    uint256 public nextTokenId;

    // Constructor function that is executed when the contract is deployed.
    // It initializes the NFT with a name ("KFCVoucher") and symbol ("KFCV").
    constructor() ERC721("KFCVoucher", "KFCV") {}

    // The `mintTo` function allows the owner of the contract to mint a new NFT.
    // This function is restricted to the owner using the `onlyOwner` modifier from the Ownable contract.
    // Parameters:
    // - `to`: The address to which the newly minted NFT will be sent.
    // Returns:
    // - The unique ID of the newly minted NFT.
    function mintTo(address to) external onlyOwner returns (uint256) {
        // Increment the `nextTokenId` to generate a new unique token ID.
        uint256 id = ++nextTokenId;

        // Mint the new NFT to the specified address using the `_safeMint` function.
        // `_safeMint` ensures that the recipient address can handle ERC721 tokens.
        _safeMint(to, id);

        // Return the ID of the newly minted NFT.
        return id;
    }
}