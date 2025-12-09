import subprocess
import json
from openai import AzureOpenAI

class Scanner:
    def __init__(self, api_key, endpoint, deployment_name, api_version):
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        self.deployment_name = deployment_name

    def scan(self, diff, files):
        """
        Orchestrates the scanning process:
        1. Run SAST (Semgrep)
        2. Analyze with LLM
        """
        print("Running hybrid scan...")
        sast_results = self._run_sast()
        llm_results = self._analyze_with_llm(diff, files, sast_results)
        return llm_results

    def _run_sast(self):
        """
        Runs Semgrep on the current directory and returns JSON results.
        """
        print("Running Semgrep...")
        try:
            # Run semgrep with json output
            result = subprocess.run(
                ['semgrep', 'scan', '--config=auto', '--json', '.'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0 and result.stderr:
                print(f"Semgrep warning/error: {result.stderr}")
            
            output = json.loads(result.stdout)
            return output.get('results', [])
        except FileNotFoundError:
            print("Semgrep not found. Skipping SAST scan.")
            return []
        except json.JSONDecodeError:
            print("Failed to parse Semgrep output.")
            return []

    def _analyze_with_llm(self, diff, files, sast_results):
        """
        Prompts LLM to analyze the diff and SAST results.
        """
        print("Analyzing with LLM...")
        
        prompt = f"""
        You are a Senior Security Engineer. Your task is to review a Pull Request for security vulnerabilities.
        
        ## Context
        I will provide you with:
        1. The PR Diff (changes made).
        2. SAST Scan Results (from Semgrep).
        3. Full content of relevant files (if needed, currently using diff context).

        ## Input Data
        
        ### 1. PR Diff
        ```diff
        {diff}
        ```

        ### 2. SAST Results
        ```json
        {json.dumps(sast_results, indent=2)}
        ```

        ## Instructions
        1. Analyze the Diff for new vulnerabilities (e.g., Injection, XSS, Broken Auth).
        2. Review the SAST results. Confirm if they are true positives relevant to the changes or existing code.
        3. Ignore low-severity style issues. Focus on HIGH and MEDIUM severity security risks.
        4. Provide a JSON output with the following structure:
        
        ```json
        {
            "summary": "A short, high-level code review summary of the changes (2-3 sentences). Focus on security code quality.",
            "vulnerabilities": [
                {
                    "file": "path/to/file",
                    "line": <line_number>,
                    "severity": "HIGH" | "MEDIUM",
                    "type": "Vulnerability Type",
                    "description": "Detailed description of the issue.",
                    "suggested_fix": "Description of how to fix it."
                }
            ]
        }
        ```
        
        If no vulnerabilities are found, return `{"summary": "...", "vulnerabilities": []}`.
        Output ONLY valid JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a Senior Security Engineer. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            text = response.choices[0].message.content.strip()
            
            return json.loads(text)
        except Exception as e:
            print(f"Error calling Azure OpenAI: {e}")
            return {"summary": "Error analyzing changes.", "vulnerabilities": []}
