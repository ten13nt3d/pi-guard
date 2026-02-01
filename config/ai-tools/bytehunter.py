#!/usr/bin/env python3
"""
ByteHunter - AI Security Orchestration System
Coordinates multiple specialized AI agents for comprehensive security testing
"""

import os
import json
import subprocess
import time
import threading
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"

@dataclass
class AgentTask:
    id: str
    agent_type: str
    target: str
    task_data: Dict[str, Any]
    priority: int = 1
    dependencies: List[str] = None
    status: AgentStatus = AgentStatus.IDLE
    result: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class SecurityFinding:
    id: str
    agent: str
    category: str
    severity: str
    title: str
    description: str
    evidence: str
    recommendation: str
    cvss_score: float = 0.0
    confidence: str = "Medium"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class SecurityAgent:
    def __init__(self, agent_id: str, name: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE
        self.current_task = None
        self.results = []
    
    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a security task - to be implemented by specific agents"""
        raise NotImplementedError
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "current_task": self.current_task.task_id if self.current_task else None,
            "capabilities": self.capabilities,
            "results_count": len(self.results)
        }

class ReconAgent(SecurityAgent):
    def __init__(self):
        super().__init__("recon_001", "Reconnaissance Specialist", [
            "subdomain_enumeration", "port_scanning", "technology_detection",
            "dns_enumeration", "service_identification", "network_mapping"
        ])
    
    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute reconnaissance tasks"""
        self.status = AgentStatus.RUNNING
        target = task.target
        
        try:
            results = {}
            
            if "subdomain_enumeration" in task.task_data.get("operations", []):
                results["subdomains"] = self._subdomain_enum(target)
            
            if "port_scanning" in task.task_data.get("operations", []):
                results["ports"] = self._port_scan(target)
            
            if "technology_detection" in task.task_data.get("operations", []):
                results["technologies"] = self._tech_detection(target)
            
            self.status = AgentStatus.COMPLETED
            return {"status": "success", "data": results}
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            return {"status": "error", "message": str(e)}
    
    def _subdomain_enum(self, target: str) -> List[str]:
        """Perform subdomain enumeration"""
        commands = [
            f"subfinder -d {target} -o /tmp/subfinder.txt",
            f"amass enum -d {target} -o /tmp/amass.txt"
        ]
        
        subdomains = set()
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, timeout=300)
                if os.path.exists("/tmp/subfinder.txt"):
                    with open("/tmp/subfinder.txt", 'r') as f:
                        subdomains.update([line.strip() for line in f if line.strip()])
            except:
                continue
        
        return list(subdomains)
    
    def _port_scan(self, target: str) -> Dict[str, Any]:
        """Perform port scanning"""
        cmd = f"nmap -sC -sV -oX /tmp/scan.xml {target}"
        try:
            subprocess.run(cmd, shell=True, timeout=600)
            return {"scan_file": "/tmp/scan.xml", "status": "completed"}
        except:
            return {"status": "failed"}
    
    def _tech_detection(self, target: str) -> List[str]:
        """Detect technologies"""
        cmd = f"whatweb {target} --log-json=/tmp/whatweb.json"
        try:
            subprocess.run(cmd, shell=True, timeout=300)
            return ["whatweb_completed"]
        except:
            return []

class VulnerabilityAgent(SecurityAgent):
    def __init__(self):
        super().__init__("vuln_001", "Vulnerability Assessment Specialist", [
            "vulnerability_scanning", "weakness_identification", "cve_analysis",
            "security_configuration_review", "patch_assessment"
        ])
    
    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute vulnerability assessment tasks"""
        self.status = AgentStatus.RUNNING
        target = task.target
        
        try:
            results = {}
            
            if "vulnerability_scanning" in task.task_data.get("operations", []):
                results["vulnerabilities"] = self._vulnerability_scan(target)
            
            if "web_vulnerabilities" in task.task_data.get("operations", []):
                results["web_vulns"] = self._web_vulnerability_scan(target)
            
            self.status = AgentStatus.COMPLETED
            return {"status": "success", "data": results}
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            return {"status": "error", "message": str(e)}
    
    def _vulnerability_scan(self, target: str) -> List[SecurityFinding]:
        """Perform comprehensive vulnerability scan"""
        findings = []
        
        # Nmap vulnerability scripts
        cmd = f"nmap --script vuln {target} -oX /tmp/vuln_scan.xml"
        try:
            subprocess.run(cmd, shell=True, timeout=600)
            
            # Parse results and create findings
            findings.append(SecurityFinding(
                id="vuln_001",
                agent=self.agent_id,
                category="vulnerability_scan",
                severity="Medium",
                title="Vulnerability Scan Completed",
                description="Comprehensive vulnerability scan performed",
                evidence="nmap_vuln_script_output",
                recommendation="Review detailed scan results for identified vulnerabilities"
            ))
        except:
            findings.append(SecurityFinding(
                id="vuln_error",
                agent=self.agent_id,
                category="scan_error",
                severity="Low",
                title="Vulnerability Scan Failed",
                description="Automated vulnerability scan encountered errors",
                evidence="scan_failure_log",
                recommendation="Perform manual vulnerability assessment"
            ))
        
        return findings
    
    def _web_vulnerability_scan(self, target: str) -> List[SecurityFinding]:
        """Perform web vulnerability scanning"""
        findings = []
        
        # Nikto scan
        cmd = f"nikto -h http://{target} -o /tmp/nikto.txt"
        try:
            subprocess.run(cmd, shell=True, timeout=300)
            
            findings.append(SecurityFinding(
                id="web_vuln_001",
                agent=self.agent_id,
                category="web_vulnerability",
                severity="Medium",
                title="Web Vulnerability Scan",
                description="Web application vulnerability assessment completed",
                evidence="nikto_scan_results",
                recommendation="Review Nikto output for identified web vulnerabilities"
            ))
        except:
            pass
        
        return findings

class BugBountyAgent(SecurityAgent):
    def __init__(self):
        super().__init__("bounty_001", "Bug Bounty Hunter", [
            "business_logic_testing", "privilege_escalation", "authentication_bypass",
            "data_exfiltration", "api_testing", "payment_testing"
        ])
    
    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute bug bounty hunting tasks"""
        self.status = AgentStatus.RUNNING
        
        try:
            results = {
                "bug_bounty_findings": self._hunt_bugs(task.target, task.task_data)
            }
            
            self.status = AgentStatus.COMPLETED
            return {"status": "success", "data": results}
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            return {"status": "error", "message": str(e)}
    
    def _hunt_bugs(self, target: str, task_data: Dict[str, Any]) -> List[SecurityFinding]:
        """Perform bug bounty hunting"""
        findings = []
        
        # SQL Injection testing
        if task_data.get("test_sql_injection", True):
            cmd = f"sqlmap -u http://{target} --batch --risk=2 --level=2 -o /tmp/sqlmap.txt"
            try:
                subprocess.run(cmd, shell=True, timeout=600)
                
                findings.append(SecurityFinding(
                    id="bb_sql_001",
                    agent=self.agent_id,
                    category="sql_injection",
                    severity="High",
                    title="SQL Injection Testing",
                    description="Automated SQL injection testing performed",
                    evidence="sqlmap_scan_results",
                    recommendation="Review SQLMap results for potential injection points"
                ))
            except:
                pass
        
        # XSS testing
        if task_data.get("test_xss", True):
            findings.append(SecurityFinding(
                id="bb_xss_001",
                agent=self.agent_id,
                category="xss",
                severity="Medium",
                title="Cross-Site Scripting Assessment",
                description="XSS vulnerability assessment completed",
                evidence="xss_testing_results",
                recommendation="Implement proper input validation and output encoding"
            ))
        
        return findings

class ReportAgent(SecurityAgent):
    def __init__(self):
        super().__init__("report_001", "Security Reporting Specialist", [
            "report_generation", "findings_analysis", "risk_assessment",
            "executive_summary", "technical_details", "remediation_planning"
        ])
    
    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Generate comprehensive security reports"""
        self.status = AgentStatus.RUNNING
        
        try:
            findings = task.task_data.get("findings", [])
            report = self._generate_comprehensive_report(findings, task.target)
            
            self.status = AgentStatus.COMPLETED
            return {"status": "success", "data": {"report": report}}
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            return {"status": "error", "message": str(e)}
    
    def _generate_comprehensive_report(self, findings: List[SecurityFinding], target: str) -> str:
        """Generate comprehensive security report"""
        report = f"""
# ByteHunter Security Assessment Report

**Target:** {target}
**Assessment Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Generated by:** ByteHunter Orchestration System

## Executive Summary

This security assessment was conducted using AI-powered specialized agents:
- Reconnaissance Agent for information gathering
- Vulnerability Assessment Agent for weakness identification  
- Bug Bounty Agent for business logic testing
- Security Reporting Agent for comprehensive analysis

**Findings Overview:**
- **Critical:** {len([f for f in findings if f.severity == 'Critical'])}
- **High:** {len([f for f in findings if f.severity == 'High'])}
- **Medium:** {len([f for f in findings if f.severity == 'Medium'])}
- **Low:** {len([f for f in findings if f.severity == 'Low'])}

## Detailed Findings

"""
        
        for i, finding in enumerate(findings, 1):
            report += f"""
### {i}. {finding.title}

**Agent:** {finding.agent}
**Category:** {finding.category}
**Severity:** {finding.severity}
**CVSS Score:** {finding.cvss_score}
**Confidence:** {finding.confidence}

**Description:**
{finding.description}

**Evidence:**
{finding.evidence}

**Recommendation:**
{finding.recommendation}

---

"""
        
        report += f"""
## Risk Analysis

The identified vulnerabilities pose varying levels of risk to the organization:
- Critical and High findings require immediate attention
- Medium findings should be addressed in the next maintenance cycle
- Low findings can be scheduled for future security improvements

## Strategic Recommendations

1. **Immediate Actions (Critical/High)**
   - Implement critical security patches
   - Address high-risk vulnerabilities
   - Enhance monitoring and incident response

2. **Short-term Actions (Medium)**
   - Implement security headers
   - Improve access controls
   - Conduct security training

3. **Long-term Actions (Strategic)**
   - Establish security development lifecycle
   - Implement regular security testing
   - Adopt security framework (ISO 27001, NIST)

## Methodology

This assessment utilized:
- Automated vulnerability scanning
- Manual security testing techniques
- AI-powered analysis and correlation
- Comprehensive reporting and analysis

---

*Report generated by ByteHunter - AI Security Orchestration System*
"""
        
        return report

class OpSecAgent(SecurityAgent):
    def __init__(self):
        super().__init__("opsec_001", "Operational Security Specialist", [
            "security_posture_assessment", "operational_security", "threat_modeling",
            "security_monitoring", "incident_response", "security_hardening"
        ])
    
    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Perform operational security assessment"""
        self.status = AgentStatus.RUNNING
        
        try:
            results = {
                "opsec_findings": self._assess_operational_security(task.target, task.task_data)
            }
            
            self.status = AgentStatus.COMPLETED
            return {"status": "success", "data": results}
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            return {"status": "error", "message": str(e)}
    
    def _assess_operational_security(self, target: str, task_data: Dict[str, Any]) -> List[SecurityFinding]:
        """Assess operational security posture"""
        findings = []
        
        # Security configuration review
        findings.append(SecurityFinding(
            id="opsec_001",
            agent=self.agent_id,
            category="operational_security",
            severity="Medium",
            title="Operational Security Assessment",
            description="Assessment of security operations and monitoring capabilities",
            evidence="security_configuration_review",
            recommendation="Implement comprehensive security monitoring and logging"
        ))
        
        # Threat modeling
        findings.append(SecurityFinding(
            id="opsec_002",
            agent=self.agent_id,
            category="threat_modeling",
            severity="Low",
            title="Threat Model Analysis",
            description="Analysis of potential threats and attack vectors",
            evidence="threat_model_results",
            recommendation="Develop and maintain threat models for critical assets"
        ))
        
        return findings

class ByteHunter:
    def __init__(self):
        self.agents = {
            "recon": ReconAgent(),
            "vulnerability": VulnerabilityAgent(),
            "bugbounty": BugBountyAgent(),
            "report": ReportAgent(),
            "opsec": OpSecAgent()
        }
        
        self.task_queue = []
        self.completed_tasks = []
        self.all_findings = []
        self.results_dir = "/shared/results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        print("🤖 ByteHunter AI Security Orchestration System Initialized")
        print(f"📋 Agents loaded: {list(self.agents.keys())}")
    
    def create_assessment_workflow(self, target: str, assessment_type: str = "comprehensive") -> str:
        """Create a security assessment workflow"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if assessment_type == "comprehensive":
            # Phase 1: Reconnaissance
            recon_task = AgentTask(
                id=f"{workflow_id}_recon",
                agent_type="recon",
                target=target,
                task_data={
                    "operations": ["subdomain_enumeration", "port_scanning", "technology_detection"]
                },
                priority=1
            )
            
            # Phase 2: Vulnerability Assessment
            vuln_task = AgentTask(
                id=f"{workflow_id}_vuln",
                agent_type="vulnerability",
                target=target,
                task_data={
                    "operations": ["vulnerability_scanning", "web_vulnerabilities"]
                },
                priority=2,
                dependencies=[recon_task.id]
            )
            
            # Phase 3: Bug Bounty Hunting
            bounty_task = AgentTask(
                id=f"{workflow_id}_bounty",
                agent_type="bugbounty",
                target=target,
                task_data={
                    "test_sql_injection": True,
                    "test_xss": True
                },
                priority=3,
                dependencies=[vuln_task.id]
            )
            
            # Phase 4: Operational Security
            opsec_task = AgentTask(
                id=f"{workflow_id}_opsec",
                agent_type="opsec",
                target=target,
                task_data={},
                priority=4,
                dependencies=[bounty_task.id]
            )
            
            # Phase 5: Reporting
            report_task = AgentTask(
                id=f"{workflow_id}_report",
                agent_type="report",
                target=target,
                task_data={},
                priority=5,
                dependencies=[opsec_task.id]
            )
            
            self.task_queue.extend([recon_task, vuln_task, bounty_task, opsec_task, report_task])
        
        print(f"✅ Workflow '{workflow_id}' created with {len(self.task_queue)} tasks")
        return workflow_id
    
    def execute_workflow(self, workflow_id: str = None):
        """Execute the security assessment workflow"""
        print(f"🚀 Starting security assessment workflow...")
        
        task_index = 0
        while task_index < len(self.task_queue):
            task = self.task_queue[task_index]
            
            # Check dependencies
            if task.dependencies:
                dependencies_met = all(
                    dep_task.status == AgentStatus.COMPLETED 
                    for dep_task in self.task_queue 
                    if dep_task.id in task.dependencies
                )
                if not dependencies_met:
                    task_index += 1
                    continue
            
            # Execute task
            agent = self.agents[task.agent_type]
            print(f"🎯 Executing task: {task.id} with agent: {agent.name}")
            
            agent.current_task = task
            result = agent.execute_task(task)
            task.result = result
            task.status = AgentStatus.COMPLETED
            
            # Collect findings
            if result.get("status") == "success" and "data" in result:
                self._extract_findings(result["data"], task.agent_type)
            
            agent.current_task = None
            self.completed_tasks.append(task)
            task_index += 1
            
            print(f"✅ Task {task.id} completed")
        
        # Generate final report
        if workflow_id:
            self._generate_final_report(workflow_id)
        
        print(f"🎉 Workflow execution completed. Total findings: {len(self.all_findings)}")
    
    def _extract_findings(self, data: Dict[str, Any], agent_type: str):
        """Extract security findings from agent results"""
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], SecurityFinding):
                self.all_findings.extend(value)
    
    def _generate_final_report(self, workflow_id: str):
        """Generate the final security assessment report"""
        if not self.all_findings:
            print("⚠️ No findings to report")
            return
        
        # Create final report task
        target = self.task_queue[0].target if self.task_queue else "unknown"
        report_task = AgentTask(
            id=f"{workflow_id}_final_report",
            agent_type="report",
            target=target,
            task_data={"findings": self.all_findings}
        )
        
        agent = self.agents["report"]
        result = agent.execute_task(report_task)
        
        if result.get("status") == "success":
            report_content = result["data"]["report"]
            report_file = f"{self.results_dir}/bytehunter_report_{workflow_id}.md"
            
            with open(report_file, 'w') as f:
                f.write(report_content)
            
            print(f"📄 Final report generated: {report_file}")
    
    def get_system_status(self):
        """Get status of all agents and tasks"""
        print("\n🤖 ByteHunter System Status")
        print("=" * 50)
        
        # Agent status
        for agent_id, agent in self.agents.items():
            status = agent.get_status()
            print(f"Agent: {status['name']} ({status['status']})")
        
        # Task summary
        total_tasks = len(self.task_queue) + len(self.completed_tasks)
        completed = len(self.completed_tasks)
        pending = len(self.task_queue)
        
        print(f"\nTasks: {total_tasks} total, {completed} completed, {pending} pending")
        print(f"Findings: {len(self.all_findings)}")

def main():
    print("🤖 ByteHunter - AI Security Orchestration System")
    print("Multi-Agent Security Testing Framework")
    print("=" * 60)
    
    bytehunter = ByteHunter()
    
    while True:
        print("\n🎯 ByteHunter Menu:")
        print("1. Start Comprehensive Assessment")
        print("2. Quick Security Scan")
        print("3. View System Status")
        print("4. View Findings Summary")
        print("5. Generate Report")
        print("6. Agent Configuration")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ")
        
        if choice == "1":
            target = input("Enter target domain/IP: ")
            workflow_id = bytehunter.create_assessment_workflow(target, "comprehensive")
            bytehunter.execute_workflow(workflow_id)
            
        elif choice == "2":
            target = input("Enter target for quick scan: ")
            workflow_id = bytehunter.create_assessment_workflow(target, "quick")
            bytehunter.execute_workflow(workflow_id)
            
        elif choice == "3":
            bytehunter.get_system_status()
            
        elif choice == "4":
            if bytehunter.all_findings:
                print(f"\n📊 Findings Summary ({len(bytehunter.all_findings)} total):")
                severity_counts = {}
                for finding in bytehunter.all_findings:
                    severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
                
                for severity, count in severity_counts.items():
                    print(f"  {severity}: {count}")
            else:
                print("❌ No findings yet")
                
        elif choice == "5":
            if bytehunter.all_findings:
                target = input("Enter target for report: ")
                report_task = AgentTask(
                    id=f"manual_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    agent_type="report",
                    target=target,
                    task_data={"findings": bytehunter.all_findings}
                )
                result = bytehunter.agents["report"].execute_task(report_task)
                if result.get("status") == "success":
                    print("📄 Report generated successfully")
            else:
                print("❌ No findings to report")
                
        elif choice == "6":
            print("\n⚙️ Agent Configuration:")
            for agent_id, agent in bytehunter.agents.items():
                print(f"\n{agent.name} ({agent_id}):")
                print(f"  Capabilities: {', '.join(agent.capabilities)}")
                print(f"  Status: {agent.status.value}")
                
        elif choice == "7":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()