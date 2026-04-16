// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./SkillNFT.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ReviewManager is Ownable {
    SkillNFT public skillNFT;

    struct Submission {
        uint256 id;
        address submitter;
        string skillCategory;
        string ipfsHash;
        uint256 totalScore;
        uint256 reviewCount;
        bool approved;
        bool finalized;
    }

    struct Review {
        address reviewer;
        uint8 score; // 1 to 5
    }

    uint256 public nextSubmissionId;
    mapping(uint256 => Submission) public submissions;
    mapping(uint256 => mapping(address => bool)) public hasReviewed;

    event SubmissionCreated(uint256 indexed id, address indexed submitter, string skillCategory);
    event Reviewed(uint256 indexed id, address indexed reviewer, uint8 score);
    event SubmissionApproved(uint256 indexed id, address indexed submitter, string skillCategory);
    event SubmissionRejected(uint256 indexed id);

    constructor(address _skillNFT) Ownable(msg.sender) {
        skillNFT = SkillNFT(_skillNFT);
    }

    function createSubmission(string memory skillCategory, string memory ipfsHash) external {
        uint256 subId = nextSubmissionId++;
        submissions[subId] = Submission({
            id: subId,
            submitter: msg.sender,
            skillCategory: skillCategory,
            ipfsHash: ipfsHash,
            totalScore: 0,
            reviewCount: 0,
            approved: false,
            finalized: false
        });
        emit SubmissionCreated(subId, msg.sender, skillCategory);
    }

    function submitReview(uint256 subId, uint8 score) external {
        require(subId < nextSubmissionId, "Invalid submission ID");
        require(score >= 1 && score <= 5, "Score must be between 1 and 5");
        require(!hasReviewed[subId][msg.sender], "Already reviewed");
        
        Submission storage sub = submissions[subId];
        require(!sub.finalized, "Submission already finalized");
        require(sub.submitter != msg.sender, "Cannot review own submission");

        hasReviewed[subId][msg.sender] = true;
        sub.totalScore += score;
        sub.reviewCount += 1;

        emit Reviewed(subId, msg.sender, score);

        // Consensus logic: required 3 reviews
        if (sub.reviewCount >= 3 && !sub.finalized) {
            _evaluateConsensus(subId);
        }
    }

    function _evaluateConsensus(uint256 subId) internal {
        Submission storage sub = submissions[subId];
        sub.finalized = true;

        // Multiply by 10 to keep precision (e.g. 3.5 = 35)
        uint256 avgScore = (sub.totalScore * 10) / sub.reviewCount;

        if (avgScore >= 35) {
            sub.approved = true;
            skillNFT.mintSkillNFT(sub.submitter, sub.skillCategory, sub.ipfsHash);
            emit SubmissionApproved(subId, sub.submitter, sub.skillCategory);
        } else {
            sub.approved = false;
            emit SubmissionRejected(subId);
        }
    }
}
