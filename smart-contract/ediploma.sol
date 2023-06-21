// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "smart-contract/ERC721.sol";
import "smart-contract/Counters.sol";

contract KBTUDiplomas is ERC721 {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    string private _diplomaBaseURI;
    mapping(uint256 => bool) private _burnedTokens;

    constructor() ERC721("KBTU Diplomas", "KBTD") {
        _diplomaBaseURI = "ipfs//:QmdhQBzET83Azvsv8kixWugwGMpY5zfeuFoQFZUCRWa7xU/";
    }

    function baseURI() internal view virtual returns (string memory) {
        return _diplomaBaseURI;
    }

    function setBaseURI(string memory baseURI) external {
        _diplomaBaseURI = baseURI;
    }

    function mintDiplomas(address owner, uint256 numberOfDiplomas) external {
        require(owner != address(0), "Invalid owner address");
        require(numberOfDiplomas > 0, "Number of diplomas must be greater than zero");

        for (uint256 i = 0; i < numberOfDiplomas; i++) {
            _tokenIdCounter.increment();
            uint256 newTokenId = _tokenIdCounter.current();
            _safeMint(owner, newTokenId);
        }
    }

    function burnDiploma(uint256 tokenId) external {
        require(_isApprovedOrOwner(_msgSender(), tokenId), "Caller is not the owner nor approved");
        require(!_burnedTokens[tokenId], "Diploma has already been burned");

        _burn(tokenId);
        _burnedTokens[tokenId] = true;
    }

    function _transfer(address from, address to, uint256 tokenId) internal override {
        require(!_exists(tokenId), "Token ID does not exist");
        require(from == address(0), "Diploma owner cannot be changed");

        super._transfer(from, to, tokenId);
    }
}
