from openai import AzureOpenAI

class Patcher:
    def __init__(self, api_key, endpoint, deployment_name, api_version):
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        self.deployment_name = deployment_name

    def generate_fix(self, vulnerability, file_content):
        """
        Asks LLM to generate a patch for the given vulnerability.
        Returns the full content of the fixed file.
        """
        print(f"Generating fix for: {vulnerability['type']} in {vulnerability['file']}")
        
        prompt = f"""
        You are a Senior Security Engineer. You have detected a vulnerability in the following code.
        
        ## Vulnerability Details
        - Type: {vulnerability['type']}
        - File: {vulnerability['file']}
        - Line: {vulnerability['line']}
        - Description: {vulnerability['description']}
        - Suggested Fix: {vulnerability['suggested_fix']}

        ## File Content
        ```python
        {file_content}
        ```

        ## Task
        Rewrite the ENTIRE file to fix the vulnerability. 
        - Maintain the original logic and style.
        - Only fix the specified vulnerability.
        - Do not add comments explaining the fix inside the code unless necessary for clarity.
        
        Output ONLY the raw code for the fixed file. Do not include markdown backticks or explanations.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a Senior Security Engineer. Output ONLY the raw code."},
                    {"role": "user", "content": prompt}
                ]
            )
            text = response.choices[0].message.content.strip()
            # Clean up markdown if present
            if text.startswith("```"):
                lines = text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                text = "\n".join(lines)
            return text
        except Exception as e:
            print(f"Error generating fix: {e}")
            return None

    def apply_patch(self, file_path, new_content):
        """
        Applies the fix to the codebase by rewriting the file.
        """
        print(f"Applying patch to {file_path}...")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Patch applied successfully.")
            return True
        except Exception as e:
            print(f"Failed to apply patch: {e}")
            return False

