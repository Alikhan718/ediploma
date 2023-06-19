// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract NFTDiplomas is ERC721Enumerable, Ownable {
    struct DiplomaMetadata {
        string ipfsImageURI;
        string ipfsJsonURI;
    }

    mapping(uint256 => DiplomaMetadata) private _diplomaMetadata;

    constructor() ERC721("KBTU NFT Diplomas", "KBTUD") {}

    modifier onlyUnminted(uint256[] memory tokenIds) {
        for (uint256 i = 0; i < tokenIds.length; i++) {
            require(!_exists(tokenIds[i]), "Token already minted");
        }
        _;
    }

    function mintAllDiplomas(
        address recipient,
        uint256[] memory tokenIds,
        string[] memory imageURIs,
        string[] memory jsonURIs
    ) external onlyOwner onlyUnminted(tokenIds) {
        require(
            tokenIds.length == imageURIs.length && tokenIds.length == jsonURIs.length,
            "Input arrays length mismatch"
        );

        for (uint256 i = 0; i < tokenIds.length; i++) {
            _safeMint(recipient, tokenIds[i]);
            _setDiplomaMetadata(tokenIds[i], imageURIs[i], jsonURIs[i]);
        }
    }

    function _burn(uint256 tokenId) internal override {
        revert("Burning disabled for NFT Diplomas");
    }

    function transferFrom(address from, address to, uint256 tokenId) public virtual override(ERC721, IERC721) {
        revert("Transfer not allowed for NFT Diplomas");
    }

    function transfer(address to, uint256 tokenId) public virtual {
        revert("Transfer not allowed for NFT Diplomas");
    }

    function safeTransferFrom(address from, address to, uint256 tokenId) public virtual override(ERC721, IERC721) {
        revert("Transfer not allowed for NFT Diplomas");
    }

    function safeTransfer(address to, uint256 tokenId) public virtual {
        revert("Transfer not allowed for NFT Diplomas");
    }

    function getDiplomaMetadata(uint256 tokenId) public view returns (DiplomaMetadata memory) {
        require(_exists(tokenId), "Token does not exist");
        return _diplomaMetadata[tokenId];
    }

    function _setDiplomaMetadata(
        uint256 tokenId,
        string memory imageURI,
        string memory jsonURI
    ) internal {
        DiplomaMetadata memory metadata = DiplomaMetadata(imageURI, jsonURI);
        _diplomaMetadata[tokenId] = metadata;
    }
}
