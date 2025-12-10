import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scanner import Scanner
from src.patcher import Patcher

# Load environment variables
load_dotenv()

def test_agent():
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    if not azure_key or not azure_endpoint or not azure_deployment:
        print("Skipping test: Azure environment variables not set.")
        return

    # 1. Read vulnerable code
    file_path = os.path.join(os.path.dirname(__file__), 'vulnerable_code.py')
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {file_path}")
        return

    # 2. Scan
    print("\n--- Scanning ---")
    scanner = Scanner(azure_key, azure_endpoint, azure_deployment, azure_api_version)
    # Simulate a diff (entire file is new)
    diff = f"+ {content}" 
    files = {'tests/vulnerable_code.py': content}
    
    scan_results = scanner.scan(diff, files)
    vulnerabilities = scan_results.get("vulnerabilities", [])
    print(f"Found {len(vulnerabilities)} vulnerabilities.")

    # 3. Patch
    fixed_files = [] # For report
    if vulnerabilities:
        print("\n--- Patching ---")
        patcher = Patcher(azure_key, azure_endpoint, azure_deployment, azure_api_version)
        for vuln in vulnerabilities:
            print(f"Fixing {vuln['type']}...")
            new_content = patcher.generate_fix(vuln, content)
            print("Generated Fix:")
            print(new_content)
            fixed_files.append("tests/vulnerable_code.py")
            
    # 4. Report
    from src.reporter import HTMLReporter
    reporter = HTMLReporter()
    report_html = reporter.generate_report(scan_results, fixed_files)
    
    os.makedirs("public", exist_ok=True)
    with open("public/test_report.html", "w", encoding='utf-8') as f:
        f.write(report_html)
    print("\nGenerated public/test_report.html")

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    test_agent()
