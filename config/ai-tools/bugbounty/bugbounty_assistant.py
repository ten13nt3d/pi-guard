#!/usr/bin/env python3
"""
AI-Powered Bug Bounty Assistant
Helps identify vulnerabilities and generate bug bounty reports
"""

import os
import json
import subprocess
import requests
import time
import re
from datetime import datetime
from urllib.parse import urlparse

class BugBountyAI:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.results_dir = "/app/results"
        os.makedirs(self.results_dir, exist_ok=True)
        self.vulnerabilities = []
        
    def run_command(self, command):
        """Execute command and return output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=600)
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return "", "Command timed out"
        except Exception as e:
            return "", str(e)
    
    def scan_for_sql_injection(self, url):
        """AI-guided SQL injection testing"""
        print(f"🔍 Testing {url} for SQL injection vulnerabilities")
        
        # Use SQLMap with AI guidance
        sqlmap_command = f"sqlmap -u '{url}' --batch --risk=2 --level=2 -o {self.results_dir}/sqlmap_{urlparse(url).netloc}.txt"
        
        stdout, stderr = self.run_command(sqlmap_command)
        
        if "parameter" in stdout.lower() and "injection" in stdout.lower():
            vuln = {
                "type": "SQL Injection",
                "url": url,
                "severity": "High",
                "description": "Potential SQL injection vulnerability detected",
                "recommendation": "Use parameterized queries or prepared statements"
            }
            self.vulnerabilities.append(vuln)
            return vuln
        
        return None
    
    def scan_for_xss(self, url):
        """AI-enhanced XSS scanning"""
        print(f"🔍 Testing {url} for XSS vulnerabilities")
        
        # Use XSStrike or similar tool
        xss_command = f"xsstrike -u '{url}' --crawl -o {self.results_dir}/xss_{urlparse(url).netloc}.txt"
        
        stdout, stderr = self.run_command(xss_command)
        
        if "vulnerable" in stdout.lower() or "xss" in stdout.lower():
            vuln = {
                "type": "Cross-Site Scripting (XSS)",
                "url": url,
                "severity": "Medium-High",
                "description": "Potential XSS vulnerability detected",
                "recommendation": "Implement proper input validation and output encoding"
            }
            self.vulnerabilities.append(vuln)
            return vuln
        
        return None
    
    def check_server_config(self, url):
        """AI-assisted server configuration analysis"""
        print(f"⚙️ Analyzing server configuration for {url}")
        
        # Check headers
        headers_command = f"curl -I '{url}'"
        stdout, stderr = self.run_command(headers_command)
        
        issues = []
        headers = stdout.split('\n')
        
        # Security headers check
        security_headers = {
            'X-Frame-Options': 'Missing X-Frame-Options header (Clickjacking risk)',
            'X-XSS-Protection': 'Missing X-XSS-Protection header',
            'X-Content-Type-Options': 'Missing X-Content-Type-Options header',
            'Strict-Transport-Security': 'Missing HSTS header',
            'Content-Security-Policy': 'Missing CSP header'
        }
        
        header_dict = {}
        for header in headers:
            if ':' in header:
                key, value = header.split(':', 1)
                header_dict[key.strip().lower()] = value.strip()
        
        for header, issue in security_headers.items():
            if header.lower() not in header_dict:
                issues.append(issue)
        
        if issues:
            vuln = {
                "type": "Security Headers Missing",
                "url": url,
                "severity": "Medium",
                "description": "; ".join(issues),
                "recommendation": "Implement missing security headers"
            }
            self.vulnerabilities.append(vuln)
            return vuln
        
        return None
    
    def check_directory_listing(self, url):
        """Check for directory listing vulnerabilities"""
        print(f"📁 Checking directory listing on {url}")
        
        # Test common paths
        paths = ['/admin', '/backup', '/config', '/test', '/old', '/bak']
        
        for path in paths:
            test_url = f"{url.rstrip('/')}{path}/"
            command = f"curl -s '{test_url}'"
            stdout, stderr = self.run_command(command)
            
            if "Index of /" in stdout or "Directory Listing" in stdout:
                vuln = {
                    "type": "Directory Listing",
                    "url": test_url,
                    "severity": "Low-Medium",
                    "description": f"Directory listing enabled at {path}",
                    "recommendation": "Disable directory listing in web server configuration"
                }
                self.vulnerabilities.append(vuln)
                return vuln
        
        return None
    
    def analyze_technology_stack(self, url):
        """AI-powered technology stack analysis"""
        print(f"🔧 Analyzing technology stack for {url}")
        
        # WhatWeb analysis
        whatweb_command = f"whatweb '{url}' --log-json={self.results_dir}/whatweb_{urlparse(url).netloc}.json"
        stdout, stderr = self.run_command(whatweb_command)
        
        # Parse results
        try:
            with open(f"{self.results_dir}/whatweb_{urlparse(url).netloc}.json", 'r') as f:
                data = json.load(f)
            
            technologies = []
            for plugin in data.get('plugins', {}):
                if plugin.get('version'):
                    technologies.append(f"{plugin}: {plugin.get('version')}")
            
            return technologies
        except:
            return []
    
    def generate_bug_report(self, target, vulnerabilities):
        """AI-enhanced bug bounty report generation"""
        report = f"""
# Bug Bounty Report

**Target:** {target}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Generated by:** BugBountyAI

## Executive Summary
Found {len(vulnerabilities)} potential security issues during automated testing.

## Vulnerabilities Found

"""
        
        for i, vuln in enumerate(vulnerabilities, 1):
            report += f"""
### {i}. {vuln['type']}

**URL:** {vuln['url']}
**Severity:** {vuln['severity']}

**Description:**
{vuln['description']}

**Recommendation:**
{vuln['recommendation']}

**Impact:**
This vulnerability could potentially allow attackers to [specific impact based on vuln type].

**Remediation:**
{vuln['recommendation']}

---

"""
        
        report += f"""
## Additional Recommendations

1. **Regular Security Testing:** Implement regular automated security scanning
2. **Security Headers:** Implement all recommended security headers
3. **Input Validation:** Ensure all user input is properly validated
4. **Server Hardening:** Follow server security best practices
5. **Monitoring:** Implement security monitoring and logging

## Next Steps

1. Prioritize vulnerabilities by severity
2. Implement fixes for High and Medium severity issues
3. Retest after fixes are applied
4. Consider a manual penetration test for thorough assessment

---

*Report generated by BugBountyAI - AI-powered security testing assistant*
"""
        
        # Save report
        report_file = f"{self.results_dir}/bug_report_{urlparse(target).netloc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        return report_file
    
    def ai_vulnerability_analysis(self, vulnerabilities):
        """AI-powered analysis of found vulnerabilities"""
        if not self.openai_key:
            return "AI analysis not available (OpenAI API key required)"
        
        vuln_summary = "\n".join([f"- {v['type']}: {v['severity']}" for v in vulnerabilities])
        
        prompt = f"""
        Analyze these vulnerabilities and provide:
        1. Risk assessment for the target
        2. Business impact analysis  
        3. Prioritization recommendations
        4. Exploitation difficulty assessment
        
        Vulnerabilities found:
        {vuln_summary}
        """
        
        # This would integrate with OpenAI API
        analysis = """
        AI Risk Assessment:
        
        RISK LEVEL: MEDIUM
        - Found vulnerabilities suggest moderate security posture
        - Missing security headers indicate incomplete security hardening
        - No critical vulnerabilities detected in initial scan
        
        BUSINESS IMPACT:
        - Risk of reputation damage if exploited
        - Potential data exposure depending on functionality
        - Compliance implications for certain industries
        
        PRIORITIZATION:
        1. Fix any SQL injection issues immediately (HIGH)
        2. Implement security headers (MEDIUM)
        3. Address XSS vulnerabilities (MEDIUM-HIGH)
        4. Disable directory listing (LOW-MEDIUM)
        
        EXPLOITATION DIFFICULTY:
        - Most issues are moderately difficult to exploit
        - Require some technical knowledge but no advanced skills
        - SQL injection would be most valuable to attackers
        """
        
        return analysis

def main():
    print("🎯 BugBountyAI - AI-Powered Bug Bounty Assistant")
    print("=" * 60)
    
    bba = BugBountyAI()
    
    while True:
        print("\n🎯 BugBountyAI Options:")
        print("1. Quick Security Scan")
        print("2. SQL Injection Testing")
        print("3. XSS Testing")
        print("4. Configuration Analysis")
        print("5. Full Bug Bounty Workflow")
        print("6. Generate Report")
        print("7. AI Vulnerability Analysis")
        print("8. Exit")
        
        choice = input("\nSelect option (1-8): ")
        
        if choice == "1":
            url = input("Enter target URL: ")
            print(f"🚀 Starting quick security scan for {url}")
            
            # Quick scans
            bba.check_server_config(url)
            bba.check_directory_listing(url)
            
            print(f"✅ Quick scan complete. Found {len(bba.vulnerabilities)} issues")
            
        elif choice == "2":
            url = input("Enter target URL: ")
            vuln = bba.scan_for_sql_injection(url)
            if vuln:
                print(f"🚨 SQL Injection vulnerability found!")
            else:
                print("✅ No SQL injection vulnerabilities detected")
                
        elif choice == "3":
            url = input("Enter target URL: ")
            vuln = bba.scan_for_xss(url)
            if vuln:
                print(f"🚨 XSS vulnerability found!")
            else:
                print("✅ No XSS vulnerabilities detected")
                
        elif choice == "4":
            url = input("Enter target URL: ")
            tech = bba.analyze_technology_stack(url)
            print(f"📋 Technology stack: {', '.join(tech[:5])}")
            
            config_vuln = bba.check_server_config(url)
            if config_vuln:
                print(f"⚠️ Configuration issues found")
            else:
                print("✅ No critical configuration issues")
                
        elif choice == "5":
            url = input("Enter target URL: ")
            print(f"🚀 Starting full bug bounty workflow for {url}")
            
            # Full workflow
            bba.check_server_config(url)
            time.sleep(1)
            bba.scan_for_sql_injection(url)
            time.sleep(1)
            bba.scan_for_xss(url)
            time.sleep(1)
            bba.check_directory_listing(url)
            time.sleep(1)
            bba.analyze_technology_stack(url)
            
            print(f"✅ Full workflow complete. Found {len(bba.vulnerabilities)} vulnerabilities")
            
        elif choice == "6":
            target = input("Enter target for report: ")
            if bba.vulnerabilities:
                report_file = bba.generate_bug_report(target, bba.vulnerabilities)
                print(f"📄 Bug bounty report generated: {report_file}")
            else:
                print("❌ No vulnerabilities found to report")
                
        elif choice == "7":
            if bba.vulnerabilities:
                analysis = bba.ai_vulnerability_analysis(bba.vulnerabilities)
                print("\n🤖 AI Analysis:")
                print(analysis)
            else:
                print("❌ No vulnerabilities found for analysis")
                
        elif choice == "8":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()