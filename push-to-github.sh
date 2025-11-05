#!/bin/bash

# Investment Research Assistant - GitHub Setup Script
# This script helps you push the project to GitHub

set -e  # Exit on error

echo "🚀 Investment Research Assistant - GitHub Setup"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "${RED}❌ Error: Run this script from the investment-research-assistant directory${NC}"
    exit 1
fi

echo "${BLUE}📋 Step 1: Checking prerequisites...${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "${RED}❌ Git not found. Please install Git first${NC}"
    exit 1
fi
echo "✅ Git $(git --version | cut -d' ' -f3)"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo ""
    echo "${BLUE}📦 Step 2: Initializing Git repository...${NC}"
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already initialized"
fi

echo ""
echo "${BLUE}📝 Step 3: Checking repository status...${NC}"

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "Found uncommitted changes. Adding files..."
    git add .
    
    echo ""
    echo "${YELLOW}Enter commit message (or press Enter for default):${NC}"
    read -r commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="Initial commit: Investment Research Assistant with RAG pipeline

- FastAPI backend with RAG service
- Next.js frontend with professional chat interface  
- Pinecone vector database integration
- Document listing and download functionality
- Source citations with relevance scores"
    fi
    
    git commit -m "$commit_msg"
    echo "✅ Changes committed"
else
    echo "✅ No uncommitted changes"
fi

echo ""
echo "${BLUE}🔗 Step 4: Setting up GitHub remote...${NC}"

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    current_remote=$(git remote get-url origin)
    echo "⚠️  Remote 'origin' already exists: ${current_remote}"
    echo ""
    echo "${YELLOW}Do you want to update it? (y/n):${NC}"
    read -r update_remote
    if [ "$update_remote" = "y" ] || [ "$update_remote" = "Y" ]; then
        git remote remove origin
    else
        echo "Keeping existing remote"
        echo ""
        echo "${GREEN}✨ Setup complete!${NC}"
        echo ""
        echo "To push to GitHub:"
        echo "  ${BLUE}git push -u origin main${NC}"
        exit 0
    fi
fi

echo ""
echo "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}📌 IMPORTANT: Create GitHub Repository First${NC}"
echo "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1. Go to: ${BLUE}https://github.com/new${NC}"
echo ""
echo "2. Repository name: ${GREEN}investment-research-assistant${NC}"
echo "   (or choose your own name)"
echo ""
echo "3. Description: ${GREEN}AI-powered RAG system for analyzing financial documents${NC}"
echo ""
echo "4. Set visibility: ${GREEN}Public${NC} (recommended for portfolio)"
echo "   or Private if you prefer"
echo ""
echo "5. ${RED}DO NOT${NC} initialize with README, .gitignore, or license"
echo "   (we already have these files)"
echo ""
echo "6. Click ${GREEN}'Create repository'${NC}"
echo ""
echo "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "${YELLOW}After creating the repository, enter your GitHub username:${NC}"
read -r github_username

if [ -z "$github_username" ]; then
    echo "${RED}❌ Username cannot be empty${NC}"
    exit 1
fi

echo ""
echo "${YELLOW}Enter your repository name (default: investment-research-assistant):${NC}"
read -r repo_name

if [ -z "$repo_name" ]; then
    repo_name="investment-research-assistant"
fi

# Set default branch to main
git branch -M main 2>/dev/null || true

# Add remote
repo_url="https://github.com/${github_username}/${repo_name}.git"
echo ""
echo "${BLUE}🔗 Adding remote: ${repo_url}${NC}"
git remote add origin "$repo_url"

echo ""
echo "${BLUE}📤 Step 5: Pushing to GitHub...${NC}"
echo ""
echo "${YELLOW}This will push your code to GitHub. Continue? (y/n):${NC}"
read -r confirm_push

if [ "$confirm_push" != "y" ] && [ "$confirm_push" != "Y" ]; then
    echo "${YELLOW}Push cancelled. You can push manually later with:${NC}"
    echo "  ${BLUE}git push -u origin main${NC}"
    exit 0
fi

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
if git push -u origin main; then
    echo ""
    echo "${GREEN}✨ Successfully pushed to GitHub!${NC}"
    echo ""
    echo "Your repository is now available at:"
    echo "  ${BLUE}https://github.com/${github_username}/${repo_name}${NC}"
    echo ""
    echo "${GREEN}🎉 All done!${NC}"
else
    echo ""
    echo "${RED}❌ Push failed. Common issues:${NC}"
    echo ""
    echo "1. Authentication required:"
    echo "   - Use GitHub CLI: ${BLUE}gh auth login${NC}"
    echo "   - Or use SSH: ${BLUE}git remote set-url origin git@github.com:${github_username}/${repo_name}.git${NC}"
    echo ""
    echo "2. Repository doesn't exist:"
    echo "   - Make sure you created it at: ${BLUE}https://github.com/new${NC}"
    echo ""
    echo "3. Try pushing manually:"
    echo "   ${BLUE}git push -u origin main${NC}"
    exit 1
fi

