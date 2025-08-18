"""
Mirror Watcher Analyzer - Core Analysis Engine
Provides comprehensive repository analysis and mirroring capabilities
"""

import os
import git
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import tempfile
import shutil


class TriuneAnalyzer:
    """Core analyzer for repository mirroring and analysis"""
    
    def __init__(self, source_url: str, target_dir: Optional[str] = None):
        self.source_url = source_url
        self.target_dir = target_dir or self._generate_target_dir()
        self.start_time = time.time()
        
    def _generate_target_dir(self) -> str:
        """Generate target directory name from source URL"""
        repo_name = self.source_url.split('/')[-1].replace('.git', '')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"/tmp/mirror_{repo_name}_{timestamp}"
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive repository analysis
        
        Returns:
            Dict containing analysis results, statistics, and metadata
        """
        try:
            # Clone or update repository
            repo_path = self._ensure_repository()
            
            # Analyze repository structure
            analysis_result = {
                'metadata': {
                    'source_url': self.source_url,
                    'target_dir': self.target_dir,
                    'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                    'analyzer_version': '0.1.0'
                },
                'repository': self._analyze_repository(repo_path),
                'files': self._analyze_files(repo_path),
                'stats': self._calculate_statistics(repo_path),
                'git_info': self._extract_git_info(repo_path)
            }
            
            # Add execution time
            execution_time = time.time() - self.start_time
            analysis_result['metadata']['execution_time'] = f"{execution_time:.2f}s"
            
            return analysis_result
            
        except Exception as e:
            return {
                'error': str(e),
                'metadata': {
                    'source_url': self.source_url,
                    'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                    'execution_time': f"{time.time() - self.start_time:.2f}s"
                }
            }
    
    def _ensure_repository(self) -> str:
        """Clone repository if it doesn't exist, otherwise update it"""
        if os.path.exists(self.target_dir):
            # Repository exists, try to update it
            try:
                repo = git.Repo(self.target_dir)
                repo.remotes.origin.pull()
                return self.target_dir
            except Exception:
                # If update fails, remove and re-clone
                shutil.rmtree(self.target_dir)
        
        # Clone repository
        os.makedirs(os.path.dirname(self.target_dir), exist_ok=True)
        
        # Try HTTPS first, fallback to SSH if available
        try:
            git.Repo.clone_from(self.source_url, self.target_dir)
        except git.exc.GitCommandError as e:
            if 'https' in self.source_url:
                # Try converting to SSH format
                ssh_url = self.source_url.replace('https://github.com/', 'git@github.com:')
                if not ssh_url.endswith('.git'):
                    ssh_url += '.git'
                try:
                    git.Repo.clone_from(ssh_url, self.target_dir)
                except git.exc.GitCommandError:
                    raise Exception(f"Failed to clone repository: {e}")
            else:
                raise Exception(f"Failed to clone repository: {e}")
        
        return self.target_dir
    
    def _analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository structure and properties"""
        repo = git.Repo(repo_path)
        
        return {
            'name': os.path.basename(repo_path),
            'remote_url': self.source_url,
            'local_path': repo_path,
            'is_bare': repo.bare,
            'active_branch': repo.active_branch.name if not repo.bare else None,
            'branches': [ref.name for ref in repo.refs if 'origin/' in ref.name],
            'tags': [tag.name for tag in repo.tags],
            'is_dirty': repo.is_dirty(),
            'head_commit': str(repo.head.commit) if repo.head.is_valid() else None
        }
    
    def _analyze_files(self, repo_path: str) -> List[Dict[str, Any]]:
        """Analyze files in the repository"""
        files = []
        
        for root, dirs, filenames in os.walk(repo_path):
            # Skip .git directory
            if '.git' in root:
                continue
                
            for filename in filenames:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, repo_path)
                
                try:
                    stat_info = os.stat(file_path)
                    file_info = {
                        'path': relative_path,
                        'size': stat_info.st_size,
                        'size_human': self._format_size(stat_info.st_size),
                        'modified': datetime.fromtimestamp(stat_info.st_mtime, timezone.utc).isoformat(),
                        'type': self._detect_file_type(filename),
                        'extension': os.path.splitext(filename)[1].lower()
                    }
                    
                    # Add content hash for small files
                    if stat_info.st_size < 1024 * 1024:  # 1MB limit
                        try:
                            with open(file_path, 'rb') as f:
                                content_hash = hashlib.sha256(f.read()).hexdigest()
                                file_info['content_hash'] = content_hash[:16]  # Shortened hash
                        except Exception:
                            pass
                    
                    files.append(file_info)
                    
                except (OSError, IOError):
                    continue
        
        return sorted(files, key=lambda x: x['size'], reverse=True)
    
    def _calculate_statistics(self, repo_path: str) -> Dict[str, Any]:
        """Calculate repository statistics"""
        total_files = 0
        total_size = 0
        file_types = {}
        languages = {}
        
        for root, dirs, filenames in os.walk(repo_path):
            if '.git' in root:
                continue
                
            for filename in filenames:
                file_path = os.path.join(root, filename)
                
                try:
                    size = os.path.getsize(file_path)
                    total_files += 1
                    total_size += size
                    
                    # Count file types
                    ext = os.path.splitext(filename)[1].lower()
                    if ext:
                        file_types[ext] = file_types.get(ext, 0) + 1
                        
                        # Language detection based on extension
                        lang = self._extension_to_language(ext)
                        if lang:
                            languages[lang] = languages.get(lang, 0) + 1
                    
                except (OSError, IOError):
                    continue
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_human': self._format_size(total_size),
            'file_types': dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]),
            'languages': dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def _extract_git_info(self, repo_path: str) -> Dict[str, Any]:
        """Extract Git repository information"""
        try:
            repo = git.Repo(repo_path)
            
            # Get recent commits
            commits = []
            for commit in repo.iter_commits(max_count=5):
                commits.append({
                    'hash': str(commit),
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'date': commit.committed_datetime.isoformat()
                })
            
            return {
                'total_commits': len(list(repo.iter_commits())),
                'recent_commits': commits,
                'contributors': len(set(commit.author.email for commit in repo.iter_commits())),
                'last_commit_date': commits[0]['date'] if commits else None
            }
            
        except Exception as e:
            return {'error': f"Failed to extract Git info: {e}"}
    
    def generate_witness_proof(self, analysis_result: Dict[str, Any]) -> str:
        """Generate cryptographic proof for external witnessing"""
        # Create deterministic hash of analysis result
        content = json.dumps(analysis_result, sort_keys=True, separators=(',', ':'))
        witness_data = {
            'analysis_hash': hashlib.sha256(content.encode()).hexdigest(),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_url': self.source_url,
            'analyzer_version': '0.1.0'
        }
        
        witness_content = json.dumps(witness_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(witness_content.encode()).hexdigest()
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def _detect_file_type(filename: str) -> str:
        """Detect file type based on extension"""
        ext = os.path.splitext(filename)[1].lower()
        
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift'}
        config_extensions = {'.json', '.yml', '.yaml', '.toml', '.ini', '.conf', '.cfg'}
        doc_extensions = {'.md', '.txt', '.rst', '.pdf', '.doc', '.docx'}
        web_extensions = {'.html', '.htm', '.css', '.scss', '.less', '.jsx', '.tsx', '.vue'}
        
        if ext in code_extensions:
            return 'code'
        elif ext in config_extensions:
            return 'config'
        elif ext in doc_extensions:
            return 'documentation'
        elif ext in web_extensions:
            return 'web'
        elif ext in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico'}:
            return 'image'
        else:
            return 'other'
    
    @staticmethod
    def _extension_to_language(ext: str) -> Optional[str]:
        """Map file extension to programming language"""
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.sh': 'Shell',
            '.sql': 'SQL',
            '.r': 'R',
            '.matlab': 'MATLAB'
        }
        return lang_map.get(ext)


# Import json at the top level if not already imported
import json