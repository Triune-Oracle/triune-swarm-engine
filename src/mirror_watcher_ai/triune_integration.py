"""
Triune Ecosystem Integration Module

Provides seamless integration with all Triune Oracle ecosystem components:
- Legio-Cognito: Automatic scroll archival
- Triumvirate Monitor: Mobile dashboard sync  
- Swarm Engine: Native Python integration
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import aiohttp
import subprocess

logger = logging.getLogger(__name__)

class LegioCognitoArchival:
    """Integration with Legio-Cognito for automatic scroll archival"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.auto_archival = self.config.get('auto_archival', True)
        self.scroll_format = self.config.get('scroll_format', 'json')
        self.archive_directory = Path(self.config.get('archive_directory', '.shadowscrolls/legio-cognito'))
        self.api_endpoint = self.config.get('api_endpoint', os.getenv('LEGIO_COGNITO_ENDPOINT'))
        self.api_key = self.config.get('api_key', os.getenv('LEGIO_COGNITO_API_KEY'))
        
        # Ensure archive directory exists
        self.archive_directory.mkdir(parents=True, exist_ok=True)
    
    async def archive_analysis(self, repository: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Archive analysis results to Legio-Cognito scrolls"""
        try:
            if not self.auto_archival:
                logger.debug("Auto-archival disabled, skipping Legio-Cognito archive")
                return {"status": "disabled", "message": "Auto-archival disabled"}
            
            logger.info(f"Archiving analysis results for {repository} to Legio-Cognito")
            
            # Create scroll metadata
            scroll_metadata = {
                "scroll_type": "mirror_watcher_analysis",
                "repository": repository,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "format": self.scroll_format,
                "version": "1.0.0",
                "source": "triune-swarm-engine/mirror-watcher-ai"
            }
            
            # Prepare scroll content
            scroll_content = {
                "metadata": scroll_metadata,
                "analysis_result": analysis_result,
                "archive_info": {
                    "archived_at": datetime.now(timezone.utc).isoformat(),
                    "archival_method": "automatic",
                    "preservation_guarantee": "immutable"
                }
            }
            
            # Generate scroll ID
            scroll_id = self._generate_scroll_id(repository, analysis_result.get("timestamp"))
            
            # Save locally first
            local_archive_result = await self._save_local_archive(scroll_id, scroll_content)
            
            # Upload to Legio-Cognito if API is available
            remote_archive_result = None
            if self.api_endpoint and self.api_key:
                remote_archive_result = await self._upload_to_legio_cognito(scroll_id, scroll_content)
            
            logger.info(f"Analysis archived for {repository}: {scroll_id}")
            
            return {
                "status": "archived",
                "scroll_id": scroll_id,
                "repository": repository,
                "local_archive": local_archive_result,
                "remote_archive": remote_archive_result,
                "archived_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to archive analysis for {repository}: {e}")
            return {
                "status": "error",
                "repository": repository,
                "error": str(e)
            }
    
    def _generate_scroll_id(self, repository: str, timestamp: Optional[str] = None) -> str:
        """Generate unique scroll ID for archival"""
        if not timestamp:
            timestamp = datetime.now(timezone.utc).isoformat()
        
        # Extract repository name from path/URL
        repo_name = repository.split('/')[-1] if '/' in repository else repository
        
        # Create timestamp suffix
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        timestamp_suffix = dt.strftime("%Y%m%d_%H%M%S")
        
        scroll_id = f"MW_{repo_name}_{timestamp_suffix}"
        return scroll_id
    
    async def _save_local_archive(self, scroll_id: str, scroll_content: Dict[str, Any]) -> Dict[str, Any]:
        """Save scroll to local archive directory"""
        try:
            # Create filename
            filename = f"{scroll_id}.{self.scroll_format}"
            file_path = self.archive_directory / filename
            
            # Save content based on format
            if self.scroll_format == 'json':
                with open(file_path, 'w') as f:
                    json.dump(scroll_content, f, indent=2, default=str)
            else:
                # Default to JSON for now
                with open(file_path, 'w') as f:
                    json.dump(scroll_content, f, indent=2, default=str)
            
            return {
                "status": "saved",
                "file_path": str(file_path),
                "size_bytes": file_path.stat().st_size
            }
            
        except Exception as e:
            logger.error(f"Failed to save local archive {scroll_id}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _upload_to_legio_cognito(self, scroll_id: str, scroll_content: Dict[str, Any]) -> Dict[str, Any]:
        """Upload scroll to Legio-Cognito API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "MirrorWatcherAI/1.0.0 TriuneSwarmEngine"
            }
            
            payload = {
                "scroll_id": scroll_id,
                "content": scroll_content,
                "metadata": {
                    "source": "mirror_watcher_ai",
                    "auto_generated": True,
                    "preservation_level": "immutable"
                }
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                url = f"{self.api_endpoint.rstrip('/')}/scrolls"
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        return {
                            "status": "uploaded",
                            "legio_cognito_id": result.get("id"),
                            "preservation_url": result.get("url"),
                            "immutable_hash": result.get("hash")
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "upload_failed",
                            "error": f"API returned {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"Failed to upload to Legio-Cognito: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def retrieve_scroll(self, scroll_id: str) -> Dict[str, Any]:
        """Retrieve a scroll from local or remote archive"""
        try:
            # Try local first
            local_file = self.archive_directory / f"{scroll_id}.{self.scroll_format}"
            if local_file.exists():
                with open(local_file, 'r') as f:
                    content = json.load(f)
                
                return {
                    "status": "found",
                    "source": "local",
                    "scroll_id": scroll_id,
                    "content": content
                }
            
            # Try remote if API available
            if self.api_endpoint and self.api_key:
                return await self._retrieve_from_legio_cognito(scroll_id)
            
            return {
                "status": "not_found",
                "scroll_id": scroll_id
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve scroll {scroll_id}: {e}")
            return {
                "status": "error",
                "scroll_id": scroll_id,
                "error": str(e)
            }
    
    async def _retrieve_from_legio_cognito(self, scroll_id: str) -> Dict[str, Any]:
        """Retrieve scroll from Legio-Cognito API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "MirrorWatcherAI/1.0.0 TriuneSwarmEngine"
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                url = f"{self.api_endpoint.rstrip('/')}/scrolls/{scroll_id}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "found",
                            "source": "remote",
                            "scroll_id": scroll_id,
                            "content": result.get("content"),
                            "metadata": result.get("metadata")
                        }
                    else:
                        return {
                            "status": "not_found",
                            "scroll_id": scroll_id
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "scroll_id": scroll_id,
                "error": str(e)
            }

class TriumvirateMonitorSync:
    """Integration with Triumvirate Monitor for real-time status updates"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.real_time_sync = self.config.get('real_time_sync', True)
        self.mobile_dashboard = self.config.get('mobile_dashboard', True)
        self.api_endpoint = self.config.get('api_endpoint', os.getenv('TRIUMVIRATE_MONITOR_ENDPOINT'))
        self.api_key = self.config.get('api_key', os.getenv('TRIUMVIRATE_MONITOR_API_KEY'))
        self.sync_interval = self.config.get('sync_interval', 30)  # seconds
    
    async def update_status(self, repository: str, status: str, details: Optional[str] = None) -> Dict[str, Any]:
        """Update repository analysis status in real-time"""
        try:
            if not self.real_time_sync:
                logger.debug("Real-time sync disabled, skipping status update")
                return {"status": "disabled", "message": "Real-time sync disabled"}
            
            logger.debug(f"Updating status for {repository}: {status}")
            
            status_update = {
                "repository": repository,
                "status": status,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "mirror_watcher_ai",
                "update_type": "repository_status"
            }
            
            # Send to API if available
            if self.api_endpoint and self.api_key:
                api_result = await self._send_status_update(status_update)
            else:
                api_result = {"status": "no_api", "message": "API not configured"}
            
            # Update local dashboard data if enabled
            local_result = None
            if self.mobile_dashboard:
                local_result = await self._update_local_dashboard(status_update)
            
            return {
                "status": "updated",
                "repository": repository,
                "api_result": api_result,
                "local_result": local_result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update status for {repository}: {e}")
            return {
                "status": "error",
                "repository": repository,
                "error": str(e)
            }
    
    async def update_dashboard(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update main dashboard with comprehensive data"""
        try:
            if not self.real_time_sync:
                return {"status": "disabled", "message": "Real-time sync disabled"}
            
            logger.info("Updating Triumvirate Monitor dashboard")
            
            dashboard_update = {
                "update_type": "dashboard_sync",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "mirror_watcher_ai",
                "data": dashboard_data,
                "metadata": {
                    "version": "1.0.0",
                    "update_method": "automatic"
                }
            }
            
            # Send to API
            api_result = None
            if self.api_endpoint and self.api_key:
                api_result = await self._send_dashboard_update(dashboard_update)
            
            # Update local dashboard
            local_result = None
            if self.mobile_dashboard:
                local_result = await self._update_local_dashboard(dashboard_update)
            
            return {
                "status": "updated",
                "api_result": api_result,
                "local_result": local_result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _send_status_update(self, status_update: Dict[str, Any]) -> Dict[str, Any]:
        """Send status update to Triumvirate Monitor API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "MirrorWatcherAI/1.0.0 TriuneSwarmEngine"
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                url = f"{self.api_endpoint.rstrip('/')}/status"
                
                async with session.post(url, json=status_update, headers=headers) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        return {
                            "status": "sent",
                            "monitor_id": result.get("id")
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "send_failed",
                            "error": f"API returned {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _send_dashboard_update(self, dashboard_update: Dict[str, Any]) -> Dict[str, Any]:
        """Send dashboard update to Triumvirate Monitor API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "MirrorWatcherAI/1.0.0 TriuneSwarmEngine"
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                url = f"{self.api_endpoint.rstrip('/')}/dashboard"
                
                async with session.put(url, json=dashboard_update, headers=headers) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        return {
                            "status": "sent",
                            "dashboard_id": result.get("id"),
                            "mobile_url": result.get("mobile_url")
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "send_failed",
                            "error": f"API returned {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _update_local_dashboard(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update local dashboard data for mobile sync"""
        try:
            dashboard_dir = Path(".triumvirate-monitor")
            dashboard_dir.mkdir(exist_ok=True)
            
            # Update status file
            status_file = dashboard_dir / "current_status.json"
            current_status = {}
            
            if status_file.exists():
                with open(status_file, 'r') as f:
                    current_status = json.load(f)
            
            # Update with new data
            current_status.update({
                "last_update": datetime.now(timezone.utc).isoformat(),
                "update_data": update_data
            })
            
            # Save updated status
            with open(status_file, 'w') as f:
                json.dump(current_status, f, indent=2, default=str)
            
            return {
                "status": "saved",
                "file_path": str(status_file)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

class SwarmEngineIntegration:
    """Native integration with Triune Swarm Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.native_integration = self.config.get('native_integration', True)
        self.compatibility_mode = self.config.get('compatibility_mode', "76.3%")
        self.swarm_config_path = Path(self.config.get('swarm_config_path', 'triune_config.json'))
        
    async def get_target_repositories(self) -> List[str]:
        """Get list of target repositories from Swarm Engine configuration"""
        try:
            if not self.native_integration:
                logger.warning("Native integration disabled, using default repositories")
                return self._get_default_repositories()
            
            logger.info("Retrieving target repositories from Swarm Engine")
            
            # Try to load from swarm configuration
            repositories = []
            
            if self.swarm_config_path.exists():
                repositories = await self._load_from_swarm_config()
            else:
                # Try to discover from current environment
                repositories = await self._discover_repositories()
            
            if not repositories:
                logger.warning("No repositories found, using defaults")
                repositories = self._get_default_repositories()
            
            logger.info(f"Found {len(repositories)} target repositories")
            return repositories
            
        except Exception as e:
            logger.error(f"Failed to get target repositories: {e}")
            return self._get_default_repositories()
    
    async def _load_from_swarm_config(self) -> List[str]:
        """Load repository list from Swarm Engine configuration"""
        try:
            with open(self.swarm_config_path, 'r') as f:
                swarm_config = json.load(f)
            
            repositories = swarm_config.get('mirror_watcher', {}).get('target_repositories', [])
            
            # Also check for general repository configuration
            if not repositories:
                repositories = swarm_config.get('repositories', [])
            
            return repositories
            
        except Exception as e:
            logger.error(f"Failed to load swarm config: {e}")
            return []
    
    async def _discover_repositories(self) -> List[str]:
        """Discover repositories from current environment"""
        try:
            repositories = []
            
            # Check if we're in a git repository
            if Path('.git').exists():
                try:
                    # Get current repository remote URL
                    result = subprocess.run(
                        ['git', 'remote', 'get-url', 'origin'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        current_repo = result.stdout.strip()
                        repositories.append(current_repo)
                        
                        # Try to find related repositories
                        if 'triune' in current_repo.lower():
                            related_repos = await self._discover_triune_repositories(current_repo)
                            repositories.extend(related_repos)
                            
                except subprocess.TimeoutExpired:
                    logger.warning("Git command timed out during repository discovery")
                except Exception as e:
                    logger.debug(f"Git discovery failed: {e}")
            
            return repositories
            
        except Exception as e:
            logger.error(f"Repository discovery failed: {e}")
            return []
    
    async def _discover_triune_repositories(self, base_repo: str) -> List[str]:
        """Discover related Triune repositories"""
        try:
            # Extract organization/user from repository URL
            if 'github.com' in base_repo:
                parts = base_repo.split('/')
                if len(parts) >= 2:
                    org_user = parts[-2]
                    
                    # Common Triune repository patterns
                    triune_repos = [
                        f"https://github.com/{org_user}/triune-memory-core",
                        f"https://github.com/{org_user}/legio-cognito",
                        f"https://github.com/{org_user}/triumvirate-monitor",
                        f"https://github.com/{org_user}/shadowscrolls-core"
                    ]
                    
                    # Filter out the current repository
                    return [repo for repo in triune_repos if repo != base_repo]
            
            return []
            
        except Exception as e:
            logger.debug(f"Failed to discover Triune repositories: {e}")
            return []
    
    def _get_default_repositories(self) -> List[str]:
        """Get default repository list when discovery fails"""
        return [
            "https://github.com/Triune-Oracle/triune-swarm-engine",
            "https://github.com/Triune-Oracle/triune-memory-core"
        ]
    
    async def register_analysis_session(self, session_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Register analysis session with Swarm Engine"""
        try:
            if not self.native_integration:
                return {"status": "disabled", "message": "Native integration disabled"}
            
            logger.info(f"Registering analysis session with Swarm Engine: {session_id}")
            
            session_data = {
                "session_id": session_id,
                "type": "mirror_watcher_analysis",
                "start_time": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata,
                "compatibility_mode": self.compatibility_mode,
                "integration_version": "1.0.0"
            }
            
            # Save session data locally for Swarm Engine access
            swarm_sessions_dir = Path(".swarm-engine/sessions")
            swarm_sessions_dir.mkdir(parents=True, exist_ok=True)
            
            session_file = swarm_sessions_dir / f"{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            return {
                "status": "registered",
                "session_id": session_id,
                "session_file": str(session_file),
                "compatibility_mode": self.compatibility_mode
            }
            
        except Exception as e:
            logger.error(f"Failed to register session with Swarm Engine: {e}")
            return {
                "status": "error",
                "session_id": session_id,
                "error": str(e)
            }
    
    async def get_swarm_engine_status(self) -> Dict[str, Any]:
        """Get current Swarm Engine status and configuration"""
        try:
            status = {
                "native_integration": self.native_integration,
                "compatibility_mode": self.compatibility_mode,
                "swarm_config_available": self.swarm_config_path.exists(),
                "integration_health": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Check for swarm engine processes or indicators
            swarm_indicators = [
                Path("loop_engine.js").exists(),
                Path("memory_engine.js").exists(),
                Path("server.js").exists(),
                Path("swarm_memory_log.json").exists()
            ]
            
            status["swarm_indicators"] = {
                "loop_engine": swarm_indicators[0],
                "memory_engine": swarm_indicators[1], 
                "server": swarm_indicators[2],
                "memory_log": swarm_indicators[3]
            }
            
            status["swarm_components_detected"] = sum(swarm_indicators)
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get Swarm Engine status: {e}")
            return {
                "native_integration": False,
                "integration_health": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }