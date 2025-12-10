import os
import sys
import requests
from dotenv import load_dotenv
from github import Github, InputGitAuthor
from scanner import Scanner
from patcher import Patcher

def main():
    print("Starting Agentic Security Scanner...")
    load_dotenv()
    
    # 1. Setup
    github_token = os.getenv("GITHUB_TOKEN")
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    if not github_token or not azure_key or not azure_endpoint or not azure_deployment:
        print("Error: Missing environment variables (GITHUB_TOKEN, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, or AZURE_OPENAI_DEPLOYMENT_NAME).")
        sys.exit(1)

    # Initialize GitHub client
    g = Github(github_token)
    repo_name = os.getenv("GITHUB_REPOSITORY")
    
    # Handle PR number from GITHUB_REF or input
    ref = os.getenv("GITHUB_REF")
    if ref and "pull" in ref:
        pr_number = int(ref.split('/')[-2])
    else:
        print("Not a PR workflow. Exiting.")
        sys.exit(0)

    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    print(f"Scanning PR #{pr_number} in {repo_name}")

    # 2. Fetch Data
    print("Fetching PR diff and files...")
    headers = {"Authorization": f"token {github_token}"}
    diff_content = requests.get(pr.diff_url, headers=headers).text
    
    # Get content of changed files
    files_content = {}
    for file in pr.get_files():
        if file.status in ['removed', 'renamed']:
            continue
        try:
            content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode('utf-8')
            files_content[file.filename] = content
        except Exception as e:
            print(f"Could not read {file.filename}: {e}")

    # 3. Scan
    scanner = Scanner(azure_key, azure_endpoint, azure_deployment, azure_api_version)
    scan_results = scanner.scan(diff_content, files_content)
    
    vulnerabilities = scan_results.get("vulnerabilities", [])
    summary = scan_results.get("summary", "No summary provided.")
    
    print(f"Scan complete. Found {len(vulnerabilities)} vulnerabilities.")
    print(f"Summary: {summary}")

    # 4. Patch & Report
    patcher = Patcher(azure_key, azure_endpoint, azure_deployment, azure_api_version)
    fixed_files = []
    comments = []

    for vuln in vulnerabilities:
        file_path = vuln['file']
        if file_path not in files_content:
            print(f"Skipping {file_path} (not found in PR files)")
            continue
            
        print(f"Fixing {vuln['type']} in {file_path}...")
        
        # Generate Fix
        new_content = patcher.generate_fix(vuln, files_content[file_path])
        
        if new_content:
            # Apply Fix (Commit directly to PR branch)
            try:
                # Get current file sha for update
                contents = repo.get_contents(file_path, ref=pr.head.ref)
                
                # Define Bot Identity
                bot_author = InputGitAuthor(name="Vulcan Security Bot", email="bot@vulcan.security")
                
                repo.update_file(
                    path=file_path,
                    message=f"Security Fix: {vuln['type']}",
                    content=new_content,
                    sha=contents.sha,
                    branch=pr.head.ref,
                    author=bot_author,
                    committer=bot_author
                )
                fixed_files.append(file_path)
                comments.append(f"- **Fixed** {vuln['type']} in `{file_path}`: {vuln['description']}")
            except Exception as e:
                print(f"Failed to push fix for {file_path}: {e}")
                comments.append(f"- **Failed to Fix** {vuln['type']} in `{file_path}`: {e}")

    # 5. Comment on PR
    body = "## 🛡️ Security Agent Report\n\n"
    body += f"### Code Review Summary\n{summary}\n\n"
    
    if vulnerabilities:
        body += "### Vulnerabilities & Fixes\n"
        body += "I found and attempted to fix the following vulnerabilities:\n\n"
        if comments:
            body += "\n".join(comments)
        else:
            # If vulns were found but no fixes attempted/succeeded (or only manual fixable)
            # For now we only add to comments if we try to fix. 
            # If we want to list vulns even if no fix, we'd need to change loop logic.
            # But adhering to existing pattern + summary:
            pass 
    else:
        body += "✅ No high-severity vulnerabilities found."

    # Always post comment if there's a summary or vulnerabilities
    pr.create_issue_comment(body)
    print("Posted summary comment to PR.")

    print("Scan complete.")

if __name__ == "__main__":
    main()

