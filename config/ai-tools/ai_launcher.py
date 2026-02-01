#!/usr/bin/env python3
"""
AI Security Tools Launcher
Central launcher for all AI-powered security tools
"""

import os
import subprocess
import time
import requests
from datetime import datetime

class AISecurityLauncher:
    def __init__(self):
        self.tools = {
            "recon": {
                "name": "ReconAI",
                "description": "AI-powered reconnaissance assistant",
                "container": "recon-ai",
                "port": 8000,
                "script": "/app/recon_ai.py"
            },
            "bugbounty": {
                "name": "BugBountyAI", 
                "description": "AI-assisted bug bounty testing",
                "container": "bugbounty-ai",
                "port": 8001,
                "script": "/app/bugbounty_assistant.py"
            },
            "pentest": {
                "name": "PentestAI",
                "description": "AI-guided penetration testing",
                "container": "pentest-ai", 
                "port": 8002,
                "script": "/app/pentest_assistant.py"
            }
        }
        
        self.results_dir = "/shared/results"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def check_container_status(self, container_name):
        """Check if container is running"""
        try:
            result = subprocess.run(f"docker ps | grep {container_name}", 
                                  shell=True, capture_output=True, text=True)
            return container_name in result.stdout
        except:
            return False
    
    def start_tool(self, tool_key):
        """Start a specific AI tool"""
        if tool_key not in self.tools:
            print(f"❌ Unknown tool: {tool_key}")
            return False
        
        tool = self.tools[tool_key]
        
        if self.check_container_status(tool["container"]):
            print(f"✅ {tool['name']} is already running")
            return True
        
        print(f"🚀 Starting {tool['name']}...")
        
        try:
            # Start the container
            cmd = f"docker start {tool['container']}"
            subprocess.run(cmd, shell=True, check=True)
            
            # Wait a moment for startup
            time.sleep(2)
            
            print(f"✅ {tool['name']} started successfully")
            print(f"📊 Access at: http://172.20.0.{10 + list(self.tools.keys()).index(tool_key)}:{tool['port']}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start {tool['name']}: {e}")
            return False
    
    def stop_tool(self, tool_key):
        """Stop a specific AI tool"""
        if tool_key not in self.tools:
            print(f"❌ Unknown tool: {tool_key}")
            return False
        
        tool = self.tools[tool_key]
        
        print(f"🛑 Stopping {tool['name']}...")
        
        try:
            subprocess.run(f"docker stop {tool['container']}", shell=True, check=True)
            print(f"✅ {tool['name']} stopped")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stop {tool['name']}: {e}")
            return False
    
    def list_tools(self):
        """List all available AI tools"""
        print("\n🤖 Available AI Security Tools:")
        print("=" * 50)
        
        for key, tool in self.tools.items():
            status = "🟢 Running" if self.check_container_status(tool["container"]) else "🔴 Stopped"
            print(f"{key:12} | {tool['name']:15} | {status:10} | {tool['description']}")
    
    def tool_menu(self, tool_key):
        """Interactive menu for a specific tool"""
        if tool_key not in self.tools:
            print(f"❌ Unknown tool: {tool_key}")
            return
        
        tool = self.tools[tool_key]
        
        while True:
            print(f"\n🎯 {tool['name']} Menu:")
            print(f"1. Start {tool['name']}")
            print(f"2. Stop {tool['name']}")
            print(f"3. Access {tool['name']} Interface")
            print(f"4. View {tool['name']} Results")
            print(f"5. Return to Main Menu")
            
            choice = input(f"\nSelect option (1-5): ")
            
            if choice == "1":
                self.start_tool(tool_key)
            elif choice == "2":
                self.stop_tool(tool_key)
            elif choice == "3":
                self.access_tool(tool_key)
            elif choice == "4":
                self.view_results(tool_key)
            elif choice == "5":
                break
            else:
                print("❌ Invalid option")
    
    def access_tool(self, tool_key):
        """Access tool interface"""
        if tool_key not in self.tools:
            print(f"❌ Unknown tool: {tool_key}")
            return
        
        tool = self.tools[tool_key]
        
        if not self.check_container_status(tool["container"]):
            print(f"❌ {tool['name']} is not running. Start it first.")
            return
        
        print(f"🌐 Accessing {tool['name']}...")
        print(f"📊 Interface: http://172.20.0.{10 + list(self.tools.keys()).index(tool_key)}:{tool['port']}")
        print(f"💡 Or connect directly: docker exec -it {tool['container']} python {tool['script']}")
        
        # Try to connect directly
        try:
            cmd = f"docker exec -it {tool['container']} python {tool['script']}"
            print(f"🔗 Running: {cmd}")
            subprocess.run(cmd, shell=True)
        except KeyboardInterrupt:
            print("\n👋 Returning to menu")
    
    def view_results(self, tool_key):
        """View tool results"""
        if tool_key not in self.tools:
            print(f"❌ Unknown tool: {tool_key}")
            return
        
        tool_results_dir = f"{self.results_dir}/{tool_key}"
        
        if not os.path.exists(tool_results_dir):
            print(f"❌ No results found for {tool['name']}")
            return
        
        print(f"\n📁 {tool['name']} Results:")
        
        try:
            result = subprocess.run(f"ls -la {tool_results_dir}", 
                                  shell=True, capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"❌ Error listing results: {e}")
    
    def setup_environment(self):
        """Setup environment variables and dependencies"""
        print("🔧 Setting up AI Security Environment...")
        
        # Check for API keys
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not openai_key:
            print("⚠️  OPENAI_API_KEY not set. Some AI features may be limited.")
        
        if not anthropic_key:
            print("⚠️  ANTHROPIC_API_KEY not set. Some AI features may be limited.")
        
        # Create results directories
        for tool_key in self.tools.keys():
            tool_dir = f"{self.results_dir}/{tool_key}"
            os.makedirs(tool_dir, exist_ok=True)
        
        print("✅ Environment setup complete")
    
    def health_check(self):
        """Perform health check on all tools"""
        print("\n🏥 AI Security Tools Health Check")
        print("=" * 40)
        
        for tool_key, tool in self.tools.items():
            status = "🟢 Healthy" if self.check_container_status(tool["container"]) else "🔴 Stopped"
            print(f"{tool['name']:15} | {status}")
        
        # Check network connectivity
        try:
            result = subprocess.run("docker network ls | grep security_net", 
                                  shell=True, capture_output=True, text=True)
            network_status = "🟢 Available" if "security_net" in result.stdout else "🔴 Missing"
            print(f"{'Security Network':15} | {network_status}")
        except:
            print(f"{'Security Network':15} | 🔴 Error")

def main():
    print("🤖 AI Security Tools Launcher")
    print("Enhanced Pi-Guard with AI-Powered Security Testing")
    print("=" * 60)
    
    launcher = AISecurityLauncher()
    launcher.setup_environment()
    
    while True:
        print("\n🎯 Main Menu:")
        print("1. List All AI Tools")
        print("2. Start All Tools")
        print("3. Stop All Tools")
        print("4. Access Specific Tool")
        print("5. Health Check")
        print("6. View Documentation")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ")
        
        if choice == "1":
            launcher.list_tools()
            
        elif choice == "2":
            print("🚀 Starting all AI tools...")
            for tool_key in launcher.tools.keys():
                launcher.start_tool(tool_key)
            
        elif choice == "3":
            print("🛑 Stopping all AI tools...")
            for tool_key in launcher.tools.keys():
                launcher.stop_tool(tool_key)
                
        elif choice == "4":
            launcher.list_tools()
            tool_choice = input(f"\nEnter tool key ({', '.join(launcher.tools.keys())}): ")
            launcher.tool_menu(tool_choice)
            
        elif choice == "5":
            launcher.health_check()
            
        elif choice == "6":
            print("\n📚 AI Security Tools Documentation:")
            print("""
            ReconAI: Automated reconnaissance with AI analysis
            BugBountyAI: Vulnerability scanning and bug bounty reporting
            PentestAI: Full penetration testing workflow with guidance
            
            Environment Variables Required:
            - OPENAI_API_KEY: For advanced AI analysis
            - ANTHROPIC_API_KEY: For Claude-powered insights
            
            Access Methods:
            1. Direct container access: docker exec -it <container> python <script>
            2. Web interface (if configured): http://172.20.0.X:PORT
            3. Through this launcher for guided interaction
            
            Results Location: /shared/results/
            """)
            
        elif choice == "7":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()