// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SkillNFT is ERC721, Ownable {
    uint256 private _nextTokenId;

    struct SkillData {
        string skillName;
        string ipfsHash;
        uint256 timestamp;
    }

    mapping(uint256 => SkillData) public skillDetails;
    
    // Address of the ReviewManager contract allowed to mint
    address public reviewManager;

    constructor() ERC721("ProofOfSkill", "POSK") Ownable(msg.sender) {}

    function setReviewManager(address _reviewManager) external onlyOwner {
        reviewManager = _reviewManager;
    }

    modifier onlyReviewManager() {
        require(msg.sender == reviewManager, "Only ReviewManager can mint");
        _;
    }

    function mintSkillNFT(address to, string memory skillName, string memory ipfsHash) external onlyReviewManager {
        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        
        skillDetails[tokenId] = SkillData({
            skillName: skillName,
            ipfsHash: ipfsHash,
            timestamp: block.timestamp
        });
    }

    function getSkillData(uint256 tokenId) external view returns (SkillData memory) {
        return skillDetails[tokenId];
    }

    // Override _update to make the token Soulbound (non-transferable)
    // In OpenZeppelin 5.x, _update is responsible for all transfers, mints, and burns.
    function _update(address to, uint256 tokenId, address auth) internal virtual override returns (address) {
        address from = _ownerOf(tokenId);
        
        // Allow minting (from == address(0)) and burning (to == address(0))
        require(from == address(0) || to == address(0), "SkillNFT: Token is Soulbound and non-transferable");
        
        return super._update(to, tokenId, auth);
    }
}
