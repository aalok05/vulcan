import datetime
import html
import json

class HTMLReporter:
    def __init__(self):
        self.css = """
            :root {
                --bg-primary: #0f172a;
                --bg-secondary: #1e293b;
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
                --accent: #38bdf8;
                --danger: #ef4444;
                --warning: #f59e0b;
                --success: #22c55e;
                --border: #334155;
            }
            body {
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                background-color: var(--bg-primary);
                color: var(--text-primary);
                line-height: 1.6;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                padding: 2rem;
            }
            header {
                border-bottom: 1px solid var(--border);
                padding-bottom: 2rem;
                margin-bottom: 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            h1 { font-size: 2rem; font-weight: 700; margin: 0; color: var(--accent); }
            h2 { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; }
            .meta { color: var(--text-secondary); font-size: 0.9rem; }
            
            .card {
                background-color: var(--bg-secondary);
                border: 1px solid var(--border);
                border-radius: 0.75rem;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .stat-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }
            .stat-card h3 { margin: 0; font-size: 0.9rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
            .stat-card p { margin: 0.5rem 0 0; font-size: 2rem; font-weight: 700; }
            
            .vuln-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 1rem;
            }
            .vuln-title { font-weight: 600; font-size: 1.1rem; }
            .badge {
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            .badge-HIGH { background-color: rgba(239, 68, 68, 0.2); color: var(--danger); }
            .badge-MEDIUM { background-color: rgba(245, 158, 11, 0.2); color: var(--warning); }
            .badge-FIXED { background-color: rgba(34, 197, 94, 0.2); color: var(--success); }
            .badge-OPEN { background-color: rgba(148, 163, 184, 0.2); color: var(--text-secondary); }
            
            code {
                background-color: rgba(0,0,0,0.3);
                padding: 0.2rem 0.4rem;
                border-radius: 0.25rem;
                font-family: monospace;
                font-size: 0.9em;
            }
            .summary-text { font-size: 1.1rem; color: var(--text-secondary); }
            
            .empty-state { text-align: center; padding: 3rem; color: var(--text-secondary); }
        """

    def generate_report(self, scan_results, fixed_files):
        vulnerabilities = scan_results.get("vulnerabilities", [])
        summary = scan_results.get("summary", "No summary provided.")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Stats
        total_vulns = len(vulnerabilities)
        high_sev = sum(1 for v in vulnerabilities if v.get('severity') == 'HIGH')
        med_sev = sum(1 for v in vulnerabilities if v.get('severity') == 'MEDIUM')
        fixed_count = len(fixed_files)

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vulcan Security Report</title>
    <style>{self.css}</style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🛡️ Vulcan Report</h1>
                <div class="meta">Agentic Security Scan Results</div>
            </div>
            <div class="meta">
                Generated: {timestamp}
            </div>
        </header>

        <section class="stat-grid">
            <div class="card stat-card">
                <h3>Total Issues</h3>
                <p style="color: var(--text-primary)">{total_vulns}</p>
            </div>
            <div class="card stat-card">
                <h3>High Severity</h3>
                <p style="color: var(--danger)">{high_sev}</p>
            </div>
            <div class="card stat-card">
                <h3>Fixed</h3>
                <p style="color: var(--success)">{fixed_count}</p>
            </div>
        </section>

        <section class="card">
            <h2>🔎 Executive Summary</h2>
            <p class="summary-text">{html.escape(summary)}</p>
        </section>

        <section>
            <h2>🚩 Vulnerabilities</h2>
        """

        if not vulnerabilities:
            html_content += """
            <div class="card empty-state">
                <h3>✅ No Vulnerabilities Found</h3>
                <p>The code appears clean based on current analysis.</p>
            </div>
            """
        else:
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'UNKNOWN').upper()
                file_path = vuln.get('file', 'unknown')
                is_fixed = file_path in fixed_files
                status_badge = '<span class="badge badge-FIXED">FIXED</span>' if is_fixed else '<span class="badge badge-OPEN">OPEN</span>'
                
                html_content += f"""
            <div class="card">
                <div class="vuln-header">
                    <span class="vuln-title">{html.escape(vuln.get('type', 'Unknown Issue'))}</span>
                    <div>
                        <span class="badge badge-{severity}">{severity}</span>
                        {status_badge}
                    </div>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <strong>File:</strong> <code>{html.escape(file_path)}:{vuln.get('line', '?')}</code>
                </div>
                <p>{html.escape(vuln.get('description', ''))}</p>
                <div style="margin-top: 1rem; border-top: 1px solid var(--border); padding-top: 1rem;">
                    <strong>Suggested Fix:</strong>
                    <p style="color: var(--text-secondary);">{html.escape(vuln.get('suggested_fix', ''))}</p>
                </div>
            </div>
                """

        html_content += """
        </section>
    </div>
</body>
</html>
        """
        return html_content
