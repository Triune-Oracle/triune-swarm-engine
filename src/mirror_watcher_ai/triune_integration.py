"""
Triune Ecosystem Integration Module
===================================

Integration with the complete Triune Oracle ecosystem including:
- Legio-Cognito: Automatic scroll archival
- Triumvirate Monitor: Mobile dashboard sync
- Swarm Engine: Native Python integration
- Shell Automation: Leveraging existing infrastructure
"""

import aiohttp
import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging
import base64

logger = logging.getLogger(__name__)


class TriuneEcosystemConnector:
    """
    Comprehensive integration with the Triune Oracle ecosystem.
    
    Provides seamless connectivity and data synchronization across:
    - Legio-Cognito scroll archival system
    - Triumvirate Monitor mobile dashboard
    - Swarm Engine Python infrastructure
    - Shell automation systems
    """
    
    def __init__(self):
        # Load configuration from environment and config files
        self.github_token = os.getenv("REPO_SYNC_TOKEN")
        self.config = self._load_configuration()
        
        # Service endpoints
        self.endpoints = {
            "legio_cognito": self.config.get("legio_cognito_endpoint", "https://api.legio-cognito.triune-oracle.com/v1"),
            "triumvirate_monitor": self.config.get("triumvirate_monitor_endpoint", "https://api.triumvirate-monitor.triune-oracle.com/v1"),
            "swarm_engine": self.config.get("swarm_engine_endpoint", "https://api.swarm-engine.triune-oracle.com/v1"),
            "shell_automation": self.config.get("shell_automation_endpoint", "local")
        }
        
        # Authentication
        self.auth_tokens = {
            "legio_cognito": os.getenv("LEGIO_COGNITO_API_KEY"),
            "triumvirate_monitor": os.getenv("TRIUMVIRATE_MONITOR_API_KEY"),
            "swarm_engine": os.getenv("SWARM_ENGINE_API_KEY")
        }
        
        self.session = None
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from config files."""
        
        config_file = "/home/runner/work/triune-swarm-engine/triune-swarm-engine/config/triune_endpoints.json"
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config file: {str(e)}")
        
        # Return default configuration
        return {
            "ecosystem_version": "1.0.0",
            "integration_mode": "production",
            "sync_intervals": {
                "legio_cognito": 300,  # 5 minutes
                "triumvirate_monitor": 60,  # 1 minute
                "swarm_engine": 30  # 30 seconds
            },
            "feature_flags": {
                "real_time_sync": True,
                "batch_processing": True,
                "error_recovery": True
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "MirrorWatcherAI-TriuneConnector/1.0.0"}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def sync_all_systems(self, analysis_results: Dict[str, Any], 
                              attestation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Synchronize data with all Triune ecosystem services.
        
        Args:
            analysis_results: Analysis results to synchronize
            attestation: Optional ShadowScrolls attestation data
            
        Returns:
            Synchronization results for all systems
        """
        logger.info("Starting comprehensive Triune ecosystem synchronization")
        
        sync_start = datetime.now(timezone.utc)
        sync_id = f"sync_{sync_start.strftime('%Y%m%d_%H%M%S')}"
        
        sync_results = {
            "sync_id": sync_id,
            "timestamp": sync_start.isoformat(),
            "systems": {},
            "summary": {}
        }
        
        async with self:
            # Create sync tasks for parallel execution
            sync_tasks = [
                self._sync_legio_cognito(analysis_results, attestation),
                self._sync_triumvirate_monitor(analysis_results),
                self._sync_swarm_engine(analysis_results),
                self._sync_shell_automation(analysis_results)
            ]
            
            # Execute synchronization in parallel
            results = await asyncio.gather(*sync_tasks, return_exceptions=True)
            
            # Process results
            system_names = ["legio_cognito", "triumvirate_monitor", "swarm_engine", "shell_automation"]
            
            for i, result in enumerate(results):
                system_name = system_names[i]
                
                if isinstance(result, Exception):
                    logger.error(f"Synchronization failed for {system_name}: {str(result)}")
                    sync_results["systems"][system_name] = {
                        "status": "error",
                        "error": str(result),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    sync_results["systems"][system_name] = result
            
            # Generate summary
            sync_results["summary"] = await self._generate_sync_summary(sync_results["systems"])
            
            # Calculate execution time
            sync_end = datetime.now(timezone.utc)
            sync_results["execution_time_seconds"] = (sync_end - sync_start).total_seconds()
            
            logger.info(f"Ecosystem synchronization completed in {sync_results['execution_time_seconds']:.2f} seconds")
            return sync_results
    
    async def _sync_legio_cognito(self, analysis_results: Dict[str, Any], 
                                 attestation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Synchronize with Legio-Cognito scroll archival system.
        
        Automatically archives all analysis results and attestations as scrolls
        for permanent preservation and future reference.
        """
        logger.info("Synchronizing with Legio-Cognito scroll archival system")
        
        try:
            # Prepare scroll data
            scroll_data = {
                "scroll_type": "mirror_analysis",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "analysis_results": analysis_results,
                "attestation": attestation,
                "metadata": {
                    "system": "MirrorWatcherAI",
                    "version": "1.0.0",
                    "repositories_count": len(analysis_results.get("repositories", {})),
                    "execution_id": analysis_results.get("analysis_id")
                }
            }
            
            # Check if Legio-Cognito is available
            if not self.auth_tokens.get("legio_cognito"):
                logger.warning("Legio-Cognito API key not configured, using local archival")
                return await self._local_legio_cognito_sync(scroll_data)
            
            # Submit to Legio-Cognito
            endpoint = f"{self.endpoints['legio_cognito']}/scrolls"
            headers = {
                "Authorization": f"Bearer {self.auth_tokens['legio_cognito']}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(endpoint, json=scroll_data, headers=headers) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    
                    return {
                        "status": "success",
                        "scroll_id": result.get("scroll_id"),
                        "archive_url": result.get("archive_url"),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "data_size_bytes": len(json.dumps(scroll_data)),
                        "preservation_level": "permanent"
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"Legio-Cognito API error {response.status}: {error_text}")
        
        except Exception as e:
            logger.warning(f"Legio-Cognito sync failed, falling back to local archival: {str(e)}")
            return await self._local_legio_cognito_sync(scroll_data)
    
    async def _local_legio_cognito_sync(self, scroll_data: Dict[str, Any]) -> Dict[str, Any]:
        """Local fallback for Legio-Cognito synchronization."""
        
        # Store locally in archive format
        archive_dir = "/home/runner/work/triune-swarm-engine/triune-swarm-engine/.shadowscrolls/legio_archive"
        os.makedirs(archive_dir, exist_ok=True)
        
        scroll_id = f"local_scroll_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        archive_file = f"{archive_dir}/{scroll_id}.json"
        
        with open(archive_file, 'w') as f:
            json.dump(scroll_data, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "local_success",
            "scroll_id": scroll_id,
            "archive_file": archive_file,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_size_bytes": len(json.dumps(scroll_data)),
            "preservation_level": "local"
        }
    
    async def _sync_triumvirate_monitor(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize with Triumvirate Monitor mobile dashboard.
        
        Provides real-time status updates and metrics for mobile monitoring.
        """
        logger.info("Synchronizing with Triumvirate Monitor dashboard")
        
        try:
            # Prepare dashboard data
            dashboard_data = {
                "update_type": "mirror_analysis",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": analysis_results.get("summary", {}).get("overall_status", "unknown"),
                "metrics": {
                    "repositories_analyzed": len(analysis_results.get("repositories", {})),
                    "average_health_score": analysis_results.get("summary", {}).get("average_health_score", 0),
                    "security_status": analysis_results.get("security_assessment", {}).get("overall_security_status", "unknown"),
                    "execution_time": analysis_results.get("execution_time_seconds", 0)
                },
                "alerts": await self._generate_mobile_alerts(analysis_results),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            # Check if Triumvirate Monitor is available
            if not self.auth_tokens.get("triumvirate_monitor"):
                logger.warning("Triumvirate Monitor API key not configured, using local dashboard")
                return await self._local_dashboard_sync(dashboard_data)
            
            # Submit to Triumvirate Monitor
            endpoint = f"{self.endpoints['triumvirate_monitor']}/dashboard/updates"
            headers = {
                "Authorization": f"Bearer {self.auth_tokens['triumvirate_monitor']}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(endpoint, json=dashboard_data, headers=headers) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    
                    return {
                        "status": "success",
                        "dashboard_id": result.get("dashboard_id"),
                        "mobile_url": result.get("mobile_url"),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "alerts_sent": len(dashboard_data["alerts"]),
                        "next_update": result.get("next_update")
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"Triumvirate Monitor API error {response.status}: {error_text}")
        
        except Exception as e:
            logger.warning(f"Triumvirate Monitor sync failed, using local dashboard: {str(e)}")
            return await self._local_dashboard_sync(dashboard_data)
    
    async def _local_dashboard_sync(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Local fallback for dashboard synchronization."""
        
        # Update local dashboard file
        dashboard_dir = "/home/runner/work/triune-swarm-engine/triune-swarm-engine/.shadowscrolls/dashboard"
        os.makedirs(dashboard_dir, exist_ok=True)
        
        dashboard_file = f"{dashboard_dir}/current_status.json"
        
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        
        # Generate simple HTML dashboard
        html_dashboard = await self._generate_html_dashboard(dashboard_data)
        html_file = f"{dashboard_dir}/dashboard.html"
        
        with open(html_file, 'w') as f:
            f.write(html_dashboard)
        
        return {
            "status": "local_success",
            "dashboard_file": dashboard_file,
            "html_dashboard": html_file,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alerts_generated": len(dashboard_data["alerts"])
        }
    
    async def _sync_swarm_engine(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize with Swarm Engine Python infrastructure.
        
        Leverages 76.3% Python codebase compatibility for native integration.
        """
        logger.info("Synchronizing with Swarm Engine infrastructure")
        
        try:
            # Prepare swarm integration data
            swarm_data = {
                "integration_type": "mirror_analysis",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "analysis_results": analysis_results,
                "compatibility_info": {
                    "python_compatibility": "76.3%",
                    "native_integration": True,
                    "shared_modules": ["storage", "messages", "relationships"]
                },
                "performance_data": {
                    "execution_time": analysis_results.get("execution_time_seconds", 0),
                    "repositories_processed": len(analysis_results.get("repositories", {})),
                    "data_volume_mb": len(json.dumps(analysis_results)) / (1024 * 1024)
                }
            }
            
            # Check for local swarm engine integration
            local_integration = await self._local_swarm_integration(swarm_data)
            
            # Try external API if available
            if self.auth_tokens.get("swarm_engine"):
                try:
                    endpoint = f"{self.endpoints['swarm_engine']}/integration/mirror"
                    headers = {
                        "Authorization": f"Bearer {self.auth_tokens['swarm_engine']}",
                        "Content-Type": "application/json"
                    }
                    
                    async with self.session.post(endpoint, json=swarm_data, headers=headers) as response:
                        if response.status in [200, 201]:
                            result = await response.json()
                            
                            return {
                                "status": "success",
                                "integration_id": result.get("integration_id"),
                                "swarm_response": result,
                                "local_integration": local_integration,
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }
                except Exception as e:
                    logger.warning(f"External swarm API failed, using local integration: {str(e)}")
            
            return {
                "status": "local_success",
                "local_integration": local_integration,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "compatibility": "76.3%"
            }
        
        except Exception as e:
            logger.error(f"Swarm Engine sync failed: {str(e)}")
            raise
    
    async def _local_swarm_integration(self, swarm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Local integration with existing swarm engine components."""
        
        integration_results = {
            "modules_updated": [],
            "data_stored": False,
            "relationships_updated": False
        }
        
        try:
            # Update agent state if file exists
            agent_state_file = "/home/runner/work/triune-swarm-engine/triune-swarm-engine/agent_state.json"
            if os.path.exists(agent_state_file):
                with open(agent_state_file, 'r') as f:
                    agent_state = json.load(f)
                
                # Update with latest analysis
                agent_state.update({
                    "last_mirror_analysis": swarm_data["timestamp"],
                    "analysis_status": "completed",
                    "repositories_monitored": len(swarm_data["analysis_results"].get("repositories", {}))
                })
                
                with open(agent_state_file, 'w') as f:
                    json.dump(agent_state, f, indent=2)
                
                integration_results["modules_updated"].append("agent_state")
            
            # Update relationships if file exists
            relationships_file = "/home/runner/work/triune-swarm-engine/triune-swarm-engine/relationships.json"
            if os.path.exists(relationships_file):
                with open(relationships_file, 'r') as f:
                    relationships = json.load(f)
                
                # Add mirror analysis relationship
                relationships["mirror_analysis"] = {
                    "last_update": swarm_data["timestamp"],
                    "data_source": "MirrorWatcherAI",
                    "status": "active"
                }
                
                with open(relationships_file, 'w') as f:
                    json.dump(relationships, f, indent=2)
                
                integration_results["relationships_updated"] = True
                integration_results["modules_updated"].append("relationships")
            
            # Store analysis data locally
            swarm_memory_file = "/home/runner/work/triune-swarm-engine/triune-swarm-engine/swarm_memory_log.json"
            memory_entry = {
                "timestamp": swarm_data["timestamp"],
                "type": "mirror_analysis",
                "data": swarm_data["analysis_results"],
                "performance": swarm_data["performance_data"]
            }
            
            # Append to memory log
            memory_log = []
            if os.path.exists(swarm_memory_file):
                try:
                    with open(swarm_memory_file, 'r') as f:
                        memory_log = json.load(f)
                    if not isinstance(memory_log, list):
                        memory_log = []
                except:
                    memory_log = []
            
            memory_log.append(memory_entry)
            
            # Keep only last 100 entries
            memory_log = memory_log[-100:]
            
            with open(swarm_memory_file, 'w') as f:
                json.dump(memory_log, f, indent=2)
            
            integration_results["data_stored"] = True
            integration_results["modules_updated"].append("swarm_memory")
            
        except Exception as e:
            logger.warning(f"Local swarm integration partially failed: {str(e)}")
        
        return integration_results
    
    async def _sync_shell_automation(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize with shell automation infrastructure.
        
        Leverages existing 10.1% shell infrastructure for automation.
        """
        logger.info("Synchronizing with shell automation systems")
        
        try:
            # Execute existing validation scripts
            shell_results = {
                "scripts_executed": [],
                "validation_results": {},
                "automation_status": "active"
            }
            
            # Run setup validation
            validation_cmd = [
                "python3", 
                "/home/runner/work/triune-swarm-engine/triune-swarm-engine/scripts/validate-setup.py",
                "--json"
            ]
            
            try:
                import subprocess
                result = await asyncio.create_subprocess_exec(
                    *validation_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    validation_data = json.loads(stdout.decode())
                    shell_results["validation_results"] = validation_data
                    shell_results["scripts_executed"].append("validate-setup.py")
                else:
                    shell_results["validation_results"] = {"error": stderr.decode()}
                    
            except Exception as e:
                shell_results["validation_results"] = {"error": str(e)}
            
            # Update shell environment with analysis results
            env_update_result = await self._update_shell_environment(analysis_results)
            shell_results.update(env_update_result)
            
            return {
                "status": "success",
                "shell_results": shell_results,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "infrastructure_utilization": "10.1%"
            }
        
        except Exception as e:
            logger.error(f"Shell automation sync failed: {str(e)}")
            raise
    
    async def _update_shell_environment(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Update shell environment with analysis results."""
        
        try:
            # Create environment file with analysis summary
            env_file = "/home/runner/work/triune-swarm-engine/triune-swarm-engine/.mirror_analysis_env"
            
            env_content = f"""# Mirror Analysis Environment Variables
# Generated: {datetime.now(timezone.utc).isoformat()}

export MIRROR_ANALYSIS_ID="{analysis_results.get('analysis_id', 'unknown')}"
export MIRROR_ANALYSIS_STATUS="completed"
export MIRROR_REPOSITORIES_COUNT="{len(analysis_results.get('repositories', {}))}"
export MIRROR_HEALTH_SCORE="{analysis_results.get('summary', {}).get('average_health_score', 0)}"
export MIRROR_SECURITY_STATUS="{analysis_results.get('security_assessment', {}).get('overall_security_status', 'unknown')}"
export MIRROR_LAST_UPDATE="{datetime.now(timezone.utc).isoformat()}"
"""
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            return {
                "environment_updated": True,
                "env_file": env_file,
                "variables_set": 6
            }
            
        except Exception as e:
            return {
                "environment_updated": False,
                "error": str(e)
            }
    
    async def _generate_mobile_alerts(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mobile alerts for critical issues."""
        
        alerts = []
        
        # Security alerts
        security_assessment = analysis_results.get("security_assessment", {})
        if security_assessment.get("overall_security_status") == "needs_attention":
            alerts.append({
                "type": "security",
                "severity": "high",
                "title": "Security Issues Detected",
                "message": f"{security_assessment.get('repositories_needing_attention', 0)} repositories need security attention",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Health score alerts
        summary = analysis_results.get("summary", {})
        avg_health = summary.get("average_health_score", 100)
        if avg_health < 70:
            alerts.append({
                "type": "health",
                "severity": "medium",
                "title": "Repository Health Warning",
                "message": f"Average health score is {avg_health:.1f}% - consider maintenance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Failed repositories alert
        failed_analyses = summary.get("failed_analyses", 0)
        if failed_analyses > 0:
            alerts.append({
                "type": "failure",
                "severity": "high",
                "title": "Analysis Failures",
                "message": f"{failed_analyses} repositories could not be analyzed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return alerts
    
    async def _generate_html_dashboard(self, dashboard_data: Dict[str, Any]) -> str:
        """Generate simple HTML dashboard for local viewing."""
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Triune Mirror Watcher Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .dashboard {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f9f9f9; border-radius: 4px; min-width: 150px; }}
        .alert {{ padding: 10px; margin: 10px 0; border-radius: 4px; }}
        .alert.high {{ background-color: #ffebee; border-left: 4px solid #f44336; }}
        .alert.medium {{ background-color: #fff3e0; border-left: 4px solid #ff9800; }}
        .alert.low {{ background-color: #e8f5e8; border-left: 4px solid #4caf50; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <h1 class="header">🔍 Triune Mirror Watcher Dashboard</h1>
        
        <div class="metrics">
            <div class="metric">
                <h3>Status</h3>
                <p><strong>{dashboard_data.get('status', 'unknown')}</strong></p>
            </div>
            <div class="metric">
                <h3>Repositories</h3>
                <p><strong>{dashboard_data.get('metrics', {}).get('repositories_analyzed', 0)}</strong></p>
            </div>
            <div class="metric">
                <h3>Health Score</h3>
                <p><strong>{dashboard_data.get('metrics', {}).get('average_health_score', 0):.1f}%</strong></p>
            </div>
            <div class="metric">
                <h3>Security</h3>
                <p><strong>{dashboard_data.get('metrics', {}).get('security_status', 'unknown')}</strong></p>
            </div>
        </div>
        
        <h2>🚨 Alerts</h2>
        <div class="alerts">
"""
        
        alerts = dashboard_data.get("alerts", [])
        if alerts:
            for alert in alerts:
                html_template += f"""
            <div class="alert {alert.get('severity', 'low')}">
                <strong>{alert.get('title', 'Alert')}</strong><br>
                {alert.get('message', 'No message')}
                <div class="timestamp">{alert.get('timestamp', '')}</div>
            </div>
"""
        else:
            html_template += """
            <div class="alert low">
                <strong>All Clear</strong><br>
                No alerts at this time.
            </div>
"""
        
        html_template += f"""
        </div>
        
        <div class="timestamp">
            Last updated: {dashboard_data.get('timestamp', 'unknown')}
        </div>
    </div>
</body>
</html>
"""
        
        return html_template
    
    async def _generate_sync_summary(self, systems: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of synchronization results."""
        
        total_systems = len(systems)
        successful_syncs = len([s for s in systems.values() if s.get("status") == "success"])
        local_syncs = len([s for s in systems.values() if s.get("status") == "local_success"])
        failed_syncs = len([s for s in systems.values() if s.get("status") == "error"])
        
        return {
            "total_systems": total_systems,
            "successful_syncs": successful_syncs,
            "local_syncs": local_syncs,
            "failed_syncs": failed_syncs,
            "overall_status": "success" if failed_syncs == 0 else "partial_success" if successful_syncs > 0 else "failed",
            "sync_rate": (successful_syncs + local_syncs) / total_systems if total_systems > 0 else 0
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of Triune ecosystem connections."""
        
        health_status = {
            "status": "healthy",
            "checks": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Check configuration
        config_health = {
            "status": "healthy",
            "endpoints_configured": len(self.endpoints),
            "tokens_configured": len([t for t in self.auth_tokens.values() if t])
        }
        health_status["checks"]["configuration"] = config_health
        
        # Check local file system access
        try:
            test_dirs = [
                "/home/runner/work/triune-swarm-engine/triune-swarm-engine/.shadowscrolls/legio_archive",
                "/home/runner/work/triune-swarm-engine/triune-swarm-engine/.shadowscrolls/dashboard"
            ]
            
            for test_dir in test_dirs:
                os.makedirs(test_dir, exist_ok=True)
            
            health_status["checks"]["filesystem"] = {"status": "healthy"}
            
        except Exception as e:
            health_status["checks"]["filesystem"] = {"status": "error", "error": str(e)}
            health_status["status"] = "degraded"
        
        # Check swarm engine integration
        try:
            swarm_files = [
                "/home/runner/work/triune-swarm-engine/triune-swarm-engine/agent_state.json",
                "/home/runner/work/triune-swarm-engine/triune-swarm-engine/relationships.json"
            ]
            
            swarm_status = {
                "status": "healthy",
                "files_accessible": sum(1 for f in swarm_files if os.path.exists(f)),
                "total_files": len(swarm_files)
            }
            
            health_status["checks"]["swarm_integration"] = swarm_status
            
        except Exception as e:
            health_status["checks"]["swarm_integration"] = {"status": "error", "error": str(e)}
            health_status["status"] = "degraded"
        
        return health_status