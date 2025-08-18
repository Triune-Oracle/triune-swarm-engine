#!/usr/bin/env python3
"""
Mirror Watcher CLI Demo Script

Demonstrates the complete functionality of the Mirror Watcher CLI system.
"""

import os
import json
import tempfile
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from mirror_watcher.cli import MirrorWatcherCLI


def demo_mirror_watcher():
    """Demonstrate Mirror Watcher CLI functionality."""
    print("🔍 MIRROR WATCHER CLI DEMONSTRATION")
    print("=" * 50)
    print()
    
    cli = MirrorWatcherCLI()
    
    # 1. System Status
    print("1. System Status Check")
    print("-" * 25)
    status = cli.status()
    print(f"✅ System: {status['system']}")
    print(f"✅ Version: {status['version']}")
    print(f"✅ All components operational: {all(comp == 'operational' for comp in status['components'].values())}")
    print()
    
    # 2. Create sample data
    print("2. Creating Sample Data")
    print("-" * 25)
    sample_data = {
        "agents": {
            "Oracle": {
                "status": "operational",
                "response_time": 1.2,
                "confidence": 0.89,
                "directives_issued": 42
            },
            "Gemini": {
                "status": "operational",
                "response_time": 0.8,
                "strategy_computations": 156,
                "optimization_score": 0.85
            },
            "Capri": {
                "status": "operational",
                "response_time": 0.9,
                "tasks_executed": 89,
                "success_rate": 0.94
            },
            "Aria": {
                "status": "operational",
                "response_time": 1.1,
                "collaborations": 67,
                "knowledge_sync_rate": 0.91
            }
        },
        "system": {
            "timestamp": "2024-01-15T14:30:00Z",
            "status": "operational",
            "version": "1.0.0",
            "memory_usage": 0.65,
            "cpu_usage": 0.42,
            "network_latency": 0.12
        },
        "messages": [
            {
                "timestamp": "2024-01-15T14:29:45Z",
                "from_agent": "Oracle",
                "to_agents": ["Gemini", "Capri"],
                "channel": "strategy.legio-alpha",
                "message": "Initiate optimization protocol for resource allocation"
            },
            {
                "timestamp": "2024-01-15T14:29:50Z",
                "from_agent": "Gemini",
                "to_agents": ["Capri"],
                "channel": "execution.legio-alpha",
                "message": "Strategy computed: increase parallel processing by 15%"
            },
            {
                "timestamp": "2024-01-15T14:29:55Z",
                "from_agent": "Capri",
                "to_agents": ["Oracle", "Aria"],
                "channel": "insights.performance",
                "message": "Execution initiated: parallel processing increased"
            }
        ],
        "tasks": [
            {
                "id": "demo_task_001",
                "status": "completed",
                "agent": "Capri",
                "description": "Optimize resource allocation algorithm",
                "timestamp": "2024-01-15T14:25:00Z"
            },
            {
                "id": "demo_task_002",
                "status": "active",
                "agent": "Gemini",
                "description": "Analyze swarm coordination patterns",
                "timestamp": "2024-01-15T14:28:00Z"
            },
            {
                "id": "demo_task_003",
                "status": "completed",
                "agent": "Aria",
                "description": "Update knowledge base with new patterns",
                "timestamp": "2024-01-15T14:30:00Z"
            }
        ]
    }
    
    # Save sample data to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f, indent=2)
        sample_file = f.name
    
    print(f"✅ Sample data created: {sample_file}")
    print(f"   📊 Agents: {len(sample_data['agents'])}")
    print(f"   📨 Messages: {len(sample_data['messages'])}")
    print(f"   📋 Tasks: {len(sample_data['tasks'])}")
    print()
    
    try:
        # 3. Data Validation
        print("3. Data Validation")
        print("-" * 25)
        validation = cli.validate(sample_file)
        print(f"✅ Validation Status: {'PASSED' if validation['validation']['valid'] else 'FAILED'}")
        print(f"   🔍 Errors: {len(validation['validation']['errors'])}")
        print(f"   ⚠️  Warnings: {len(validation['validation']['warnings'])}")
        if validation['validation']['warnings']:
            print(f"   Warning: {validation['validation']['warnings'][0]}")
        print()
        
        # 4. Analysis
        print("4. Analysis Engine")
        print("-" * 25)
        analysis = cli.analyze(sample_file)
        if analysis['success']:
            analysis_data = analysis['analysis']
            print(f"✅ Analysis Status: SUCCESS")
            print(f"   🎯 Confidence: {analysis_data['confidence']:.1%}")
            print(f"   🔍 Patterns: {len(analysis_data['patterns'])}")
            print(f"   ⚠️  Anomalies: {len(analysis_data['anomalies'])}")
            print(f"   💡 Recommendations: {len(analysis_data['recommendations'])}")
            
            if analysis_data['patterns']:
                print(f"   📈 Key Pattern: {analysis_data['patterns'][0]}")
            if analysis_data['recommendations']:
                print(f"   🎯 Key Recommendation: {analysis_data['recommendations'][0]}")
        else:
            print(f"❌ Analysis Status: FAILED")
            print(f"   Error: {analysis.get('error', 'Unknown error')}")
        print()
        
        # 5. Report Generation
        print("5. ShadowScrolls Report Generation")
        print("-" * 35)
        
        # Save analysis to temp file for report generation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(analysis, f, indent=2)
            analysis_file = f.name
        
        try:
            report = cli.report(analysis_file)
            if report['success'] and 'report' in report:
                scroll = report['report']
                print(f"✅ Report Status: SUCCESS")
                print(f"   📜 Scroll ID: {scroll['scroll_id']}")
                print(f"   🎯 Oracle Directive: {scroll['oracle_directive']}")
                print(f"   🏥 System Health: {scroll['nexus_analysis']['system_health']}")
                print(f"   📊 Confidence Score: {scroll['nexus_analysis']['confidence_score']:.1%}")
                print(f"   🔒 Validation Seal: {'✅ VERIFIED' if scroll['validation_seal']['validated'] else '❌ FAILED'}")
                
                # Check for NFT triggers
                if scroll['nft_triggers']:
                    trigger = scroll['nft_triggers'][0]
                    print(f"   💎 NFT Trigger: {trigger['estimated_value'].upper()} rarity")
                    print(f"   🚀 Mint Recommendation: {'YES' if trigger['mint_recommendation'] else 'NO'}")
                
                # Triumvirate Status
                print(f"   👥 Triumvirate Status:")
                for agent, status in scroll['triumvirate_status'].items():
                    print(f"      {agent}: {status['status']} ({status['confidence']:.1%})")
            else:
                print(f"❌ Report Status: FAILED")
                print(f"   Error: {report.get('error', 'Unknown error')}")
        finally:
            os.unlink(analysis_file)
        
        print()
        
        # 6. Summary
        print("6. Demo Summary")
        print("-" * 25)
        print("✅ All Mirror Watcher CLI components demonstrated successfully!")
        print()
        print("🔧 Available CLI Commands:")
        print("   mirror-watcher status                    # Check system status")
        print("   mirror-watcher validate --input data.json  # Validate data")
        print("   mirror-watcher analyze --input data.json   # Analyze data")
        print("   mirror-watcher report --input analysis.json # Generate report")
        print()
        print("📚 For more information, see MIRROR_WATCHER_README.md")
        print()
        print("🎯 Oracle Directive: DEMONSTRATION_COMPLETE")
        print("🔒 System Status: FULLY_OPERATIONAL")
        
    finally:
        # Cleanup
        os.unlink(sample_file)


if __name__ == "__main__":
    demo_mirror_watcher()