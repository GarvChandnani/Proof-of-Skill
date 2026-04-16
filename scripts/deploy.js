const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);

  // Deploy SkillNFT
  const SkillNFT = await hre.ethers.getContractFactory("SkillNFT");
  const skillNFT = await SkillNFT.deploy();
  await skillNFT.waitForDeployment();
  const nftAddress = await skillNFT.getAddress();
  console.log("SkillNFT deployed to:", nftAddress);

  // Deploy ReviewManager
  const ReviewManager = await hre.ethers.getContractFactory("ReviewManager");
  const reviewManager = await ReviewManager.deploy(nftAddress);
  await reviewManager.waitForDeployment();
  const managerAddress = await reviewManager.getAddress();
  console.log("ReviewManager deployed to:", managerAddress);

  // Transfer minting rights (setReviewManager) to ReviewManager
  const tx = await skillNFT.setReviewManager(managerAddress);
  await tx.wait();
  console.log("ReviewManager authorized to mint NFTs.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
