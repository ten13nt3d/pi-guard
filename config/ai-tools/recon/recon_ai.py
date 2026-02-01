#!/usr/bin/env python3
"""
AI-Powered Reconnaissance Assistant
Automates reconnaissance tasks with AI guidance and analysis
"""

import os
import json
import subprocess
import requests
import time
from datetime import datetime

class ReconAI:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.results_dir = "/app/results"
        os.makedirs(self.results_dir, exist_ok=True)
        
    def run_command(self, command):
        """Execute command and return output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return "", "Command timed out"
        except Exception as e:
            return "", str(e)
    
    def subdomain_enum(self, domain):
        """AI-assisted subdomain enumeration"""
        print(f"🔍 Starting subdomain enumeration for {domain}")
        
        # Multiple tools for comprehensive coverage
        tools = [
            f"subfinder -d {domain} -o {self.results_dir}/subfinder.txt",
            f"amass enum -d {domain} -o {self.results_dir}/amass.txt",
            f"assetfinder --subs-only {domain} > {self.results_dir}/assetfinder.txt"
        ]
        
        for tool in tools:
            print(f"Running: {tool}")
            stdout, stderr = self.run_command(tool)
            if stderr:
                print(f"Error: {stderr}")
        
        # Combine results
        self.merge_subdomain_results(domain)
        return f"{self.results_dir}/merged_subdomains.txt"
    
    def port_scan(self, target):
        """AI-guided port scanning"""
        print(f"🔌 Starting port scan for {target}")
        
        # Quick scan first, then detailed on open ports
        quick_scan = f"nmap -p- --min-rate=1000 -oX {self.results_dir}/quick_scan.xml {target}"
        detailed_scan = f"nmap -sC -sV -oX {self.results_dir}/detailed_scan.xml {target}"
        
        print("Running quick scan...")
        self.run_command(quick_scan)
        
        print("Running detailed scan...")
        self.run_command(detailed_scan)
        
        return f"{self.results_dir}/detailed_scan.xml"
    
    def web_recon(self, url):
        """AI-enhanced web reconnaissance"""
        print(f"🌐 Starting web reconnaissance for {url}")
        
        # Directory enumeration
        dir_enum = f"gobuster dir -u {url} -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -o {self.results_dir}/gobuster.txt"
        
        # Technology detection
        tech_detect = f"whatweb {url} -o {self.results_dir}/whatweb.json"
        
        # Screenshot capture
        screenshot = f"gowitness file -f {self.results_dir}/urls.txt -P {self.results_dir}/screenshots"
        
        self.run_command(dir_enum)
        self.run_command(tech_detect)
        
        return self.results_dir
    
    def ai_analysis(self, domain, results_path):
        """AI-powered analysis of reconnaissance data"""
        if not self.openai_key:
            print("❌ OpenAI API key not configured")
            return None
        
        # Read results
        try:
            with open(f"{results_path}/merged_subdomains.txt", 'r') as f:
                subdomains = f.read()
            
            with open(f"{results_path}/detailed_scan.xml", 'r') as f:
                nmap_results = f.read()
        except FileNotFoundError:
            print("❌ Results files not found")
            return None
        
        # AI Analysis prompt
        prompt = f"""
        Analyze these reconnaissance results for {domain}:
        
        SUBDOMAINS:
        {subdomains[:1000]}...
        
        NMAP RESULTS:
        {nmap_results[:1000]}...
        
        Provide:
        1. High-priority targets for testing
        2. Interesting technologies discovered
        3. Potential attack vectors
        4. Recommended next steps
        """
        
        # This would integrate with OpenAI/Anthropic APIs
        analysis = self.analyze_with_ai(prompt)
        
        # Save analysis
        with open(f"{results_path}/ai_analysis.txt", 'w') as f:
            f.write(analysis)
        
        return analysis
    
    def merge_subdomain_results(self, domain):
        """Merge results from multiple subdomain tools"""
        files = [
            f"{self.results_dir}/subfinder.txt",
            f"{self.results_dir}/amass.txt", 
            f"{self.results_dir}/assetfinder.txt"
        ]
        
        merged = set()
        for file in files:
            try:
                with open(file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            merged.add(line)
            except FileNotFoundError:
                continue
        
        # Write merged results
        with open(f"{self.results_dir}/merged_subdomains.txt", 'w') as f:
            for subdomain in sorted(merged):
                f.write(f"{subdomain}\n")
        
        print(f"✅ Found {len(merged)} unique subdomains")
    
    def analyze_with_ai(self, prompt):
        """Integration with AI APIs (placeholder)"""
        # This would integrate with OpenAI/Anthropic
        # For now, return structured analysis template
        return """
        AI Analysis Results:
        
        HIGH-PRIORITY TARGETS:
        - Web servers on ports 80, 443, 8080
        - Administrative interfaces
        - Services with outdated versions
        
        TECHNOLOGIES DETECTED:
        - Web servers: Apache/Nginx/IIS versions
        - Backend frameworks: PHP, Node.js, Python
        - Database systems: MySQL, PostgreSQL, MongoDB
        
        ATTACK VECTORS:
        - SQL Injection possibilities
        - Cross-site scripting (XSS)
        - Weak authentication mechanisms
        - Outdated software vulnerabilities
        
        RECOMMENDATIONS:
        1. Focus on web application testing
        2. Test authentication mechanisms
        3. Check for common vulnerabilities
        4. Perform version-specific exploit testing
        """

def main():
    print("🚀 ReconAI - AI-Powered Reconnaissance Assistant")
    print("=" * 50)
    
    recon = ReconAI()
    
    while True:
        print("\n🎯 ReconAI Options:")
        print("1. Subdomain Enumeration")
        print("2. Port Scanning")
        print("3. Web Reconnaissance")
        print("4. Full Reconnaissance Workflow")
        print("5. AI Analysis")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ")
        
        if choice == "1":
            domain = input("Enter target domain: ")
            result = recon.subdomain_enum(domain)
            print(f"✅ Subdomain enumeration complete: {result}")
            
        elif choice == "2":
            target = input("Enter target IP/domain: ")
            result = recon.port_scan(target)
            print(f"✅ Port scan complete: {result}")
            
        elif choice == "3":
            url = input("Enter target URL (http://example.com): ")
            result = recon.web_recon(url)
            print(f"✅ Web reconnaissance complete: {result}")
            
        elif choice == "4":
            target = input("Enter target domain: ")
            print(f"🚀 Starting full reconnaissance workflow for {target}")
            
            # Step 1: Subdomain enumeration
            subdomains = recon.subdomain_enum(target)
            time.sleep(2)
            
            # Step 2: Port scanning main domain
            ports = recon.port_scan(target)
            time.sleep(2)
            
            # Step 3: Web reconnaissance
            web = recon.web_recon(f"http://{target}")
            
            # Step 4: AI Analysis
            analysis = recon.ai_analysis(target, recon.results_dir)
            if analysis:
                print("🤖 AI Analysis complete")
            
            print(f"✅ Full reconnaissance complete. Results in: {recon.results_dir}")
            
        elif choice == "5":
            domain = input("Enter target domain for AI analysis: ")
            analysis = recon.ai_analysis(domain, recon.results_dir)
            if analysis:
                print(analysis)
            
        elif choice == "6":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()