"""
Triune Analyzer - Core analysis functionality for mirrored repositories
Provides comprehensive code analysis and pattern detection
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import mimetypes
import hashlib
from datetime import datetime, timezone


class TriuneAnalyzer:
    """Core analyzer for repository structure, code patterns, and metrics"""
    
    # Language extensions mapping
    LANGUAGE_EXTENSIONS = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.sh': 'Shell',
        '.sql': 'SQL',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.sass': 'SASS',
        '.less': 'LESS',
        '.vue': 'Vue',
        '.jsx': 'JSX',
        '.tsx': 'TSX',
        '.md': 'Markdown',
        '.yml': 'YAML',
        '.yaml': 'YAML',
        '.json': 'JSON',
        '.xml': 'XML',
        '.toml': 'TOML',
        '.ini': 'INI',
        '.cfg': 'Config',
        '.conf': 'Config',
        '.dockerfile': 'Dockerfile',
        '.r': 'R',
        '.m': 'MATLAB',
        '.pl': 'Perl',
        '.lua': 'Lua',
        '.dart': 'Dart',
        '.sol': 'Solidity',
        '.vyper': 'Vyper'
    }
    
    # File patterns to ignore
    IGNORE_PATTERNS = {
        '.git', '.svn', '.hg', '.bzr',  # VCS
        'node_modules', '__pycache__', '.pytest_cache',  # Dependencies/Cache
        '.venv', 'venv', 'env', '.env',  # Virtual environments
        'dist', 'build', 'target', 'out',  # Build outputs
        '.idea', '.vscode', '.vs',  # IDEs
        'vendor', 'third_party',  # Dependencies
        'logs', 'log', 'tmp', 'temp',  # Temporary files
        '.DS_Store', 'Thumbs.db'  # OS files
    }
    
    # Binary file extensions
    BINARY_EXTENSIONS = {
        '.exe', '.dll', '.so', '.dylib', '.a', '.lib', '.o', '.obj',  # Executables/Libraries
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',  # Images
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',  # Videos
        '.mp3', '.wav', '.flac', '.aac', '.ogg',  # Audio
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  # Documents
        '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2',  # Archives
        '.ttf', '.otf', '.woff', '.woff2', '.eot'  # Fonts
    }
    
    def __init__(self):
        self.analysis_timestamp = datetime.now(timezone.utc).isoformat()
    
    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a repository
        
        Args:
            repo_path: Path to the repository root
            
        Returns:
            Dictionary containing analysis results
        """
        repo_path = Path(repo_path)
        
        if not repo_path.exists():
            return {"error": f"Repository path does not exist: {repo_path}"}
        
        analysis = {
            "timestamp": self.analysis_timestamp,
            "repository_path": str(repo_path),
            "repository_name": repo_path.resolve().name,
            "summary": {},
            "file_analysis": {},
            "language_analysis": {},
            "structure_analysis": {},
            "pattern_analysis": {},
            "security_analysis": {},
            "dependencies": {},
            "quality_metrics": {}
        }
        
        try:
            # Analyze repository structure and files
            file_data = self._analyze_files(repo_path)
            analysis["file_analysis"] = file_data
            
            # Language distribution analysis
            language_data = self._analyze_languages(file_data)
            analysis["language_analysis"] = language_data
            
            # Repository structure analysis
            structure_data = self._analyze_structure(repo_path)
            analysis["structure_analysis"] = structure_data
            
            # Code pattern analysis
            pattern_data = self._analyze_patterns(repo_path, file_data)
            analysis["pattern_analysis"] = pattern_data
            
            # Security analysis
            security_data = self._analyze_security(repo_path, file_data)
            analysis["security_analysis"] = security_data
            
            # Dependency analysis
            dependency_data = self._analyze_dependencies(repo_path)
            analysis["dependencies"] = dependency_data
            
            # Quality metrics
            quality_data = self._calculate_quality_metrics(file_data, language_data, structure_data)
            analysis["quality_metrics"] = quality_data
            
            # Generate summary
            analysis["summary"] = self._generate_summary(analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}", "partial_data": analysis}
    
    def _analyze_files(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze all files in the repository"""
        file_data = {
            "total_files": 0,
            "total_lines": 0,
            "total_size": 0,
            "file_types": Counter(),
            "language_files": defaultdict(list),
            "large_files": [],
            "empty_files": [],
            "binary_files": [],
            "text_files": []
        }
        
        for file_path in self._walk_repository(repo_path):
            try:
                file_info = self._analyze_single_file(file_path)
                file_data["total_files"] += 1
                file_data["total_size"] += file_info["size"]
                file_data["file_types"][file_info["extension"]] += 1
                
                if file_info["is_binary"]:
                    file_data["binary_files"].append(file_info)
                else:
                    file_data["text_files"].append(file_info)
                    file_data["total_lines"] += file_info["line_count"]
                    
                    if file_info["line_count"] == 0:
                        file_data["empty_files"].append(file_info)
                    
                    if file_info["size"] > 100000:  # Files larger than 100KB
                        file_data["large_files"].append(file_info)
                    
                    if file_info["language"]:
                        file_data["language_files"][file_info["language"]].append(file_info)
                        
            except Exception as e:
                # Skip files that can't be analyzed
                continue
        
        return file_data
    
    def _analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file"""
        stat = file_path.stat()
        extension = file_path.suffix.lower()
        
        file_info = {
            "path": str(file_path),
            "name": file_path.name,
            "extension": extension,
            "size": stat.st_size,
            "language": self.LANGUAGE_EXTENSIONS.get(extension),
            "is_binary": extension in self.BINARY_EXTENSIONS,
            "line_count": 0,
            "hash": self._calculate_file_hash(file_path)
        }
        
        # Analyze text files
        if not file_info["is_binary"] and stat.st_size < 1000000:  # Skip very large files
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    file_info["line_count"] = len(lines)
            except Exception:
                file_info["is_binary"] = True
        
        return file_info
    
    def _analyze_languages(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze language distribution"""
        language_stats = defaultdict(lambda: {
            "file_count": 0,
            "total_lines": 0,
            "total_size": 0,
            "files": []
        })
        
        for file_info in file_data["text_files"]:
            if file_info["language"]:
                lang = file_info["language"]
                language_stats[lang]["file_count"] += 1
                language_stats[lang]["total_lines"] += file_info["line_count"]
                language_stats[lang]["total_size"] += file_info["size"]
                language_stats[lang]["files"].append(file_info["path"])
        
        # Calculate percentages
        total_lines = file_data["total_lines"]
        total_files = len(file_data["text_files"])
        
        for lang_data in language_stats.values():
            lang_data["line_percentage"] = (lang_data["total_lines"] / total_lines * 100) if total_lines > 0 else 0
            lang_data["file_percentage"] = (lang_data["file_count"] / total_files * 100) if total_files > 0 else 0
        
        return {
            "languages": dict(language_stats),
            "primary_language": max(language_stats.keys(), key=lambda k: language_stats[k]["total_lines"]) if language_stats else None,
            "language_count": len(language_stats)
        }
    
    def _analyze_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze repository structure"""
        structure = {
            "directories": [],
            "depth": 0,
            "has_readme": False,
            "has_license": False,
            "has_gitignore": False,
            "has_ci": False,
            "config_files": [],
            "documentation_files": [],
            "test_directories": []
        }
        
        # Check for common files
        for file_name in os.listdir(repo_path):
            file_path = repo_path / file_name
            lower_name = file_name.lower()
            
            if "readme" in lower_name:
                structure["has_readme"] = True
            elif "license" in lower_name or "licence" in lower_name:
                structure["has_license"] = True
            elif file_name == ".gitignore":
                structure["has_gitignore"] = True
            elif file_name in [".github", ".gitlab-ci.yml", ".travis.yml", "Jenkinsfile"]:
                structure["has_ci"] = True
            elif file_name.endswith(('.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf')):
                structure["config_files"].append(file_name)
            elif file_name.endswith('.md') or "doc" in lower_name:
                structure["documentation_files"].append(file_name)
            elif file_path.is_dir() and ("test" in lower_name or "spec" in lower_name):
                structure["test_directories"].append(file_name)
        
        # Calculate directory depth
        max_depth = 0
        for path in self._walk_repository(repo_path):
            relative_path = path.relative_to(repo_path)
            depth = len(relative_path.parts) - 1  # Exclude the file itself
            max_depth = max(max_depth, depth)
        
        structure["depth"] = max_depth
        
        return structure
    
    def _analyze_patterns(self, repo_path: Path, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code patterns and architecture"""
        patterns = {
            "framework_indicators": [],
            "architecture_patterns": [],
            "testing_frameworks": [],
            "build_tools": [],
            "package_managers": []
        }
        
        # Check for framework indicators
        framework_files = {
            "package.json": "Node.js/NPM",
            "requirements.txt": "Python/pip",
            "Pipfile": "Python/Pipenv",
            "setup.py": "Python Package",
            "pom.xml": "Java/Maven",
            "build.gradle": "Java/Gradle",
            "Cargo.toml": "Rust/Cargo",
            "go.mod": "Go Modules",
            "composer.json": "PHP/Composer",
            "Gemfile": "Ruby/Bundler",
            "mix.exs": "Elixir/Mix",
            "pubspec.yaml": "Dart/Flutter"
        }
        
        for file_name, framework in framework_files.items():
            if (repo_path / file_name).exists():
                patterns["framework_indicators"].append(framework)
        
        # Check for testing frameworks
        test_indicators = {
            "pytest", "unittest", "nose", "jest", "mocha", "jasmine", 
            "junit", "testng", "rspec", "minitest", "go test"
        }
        
        for file_info in file_data["text_files"]:
            file_content_lower = Path(file_info["path"]).name.lower()
            for indicator in test_indicators:
                if indicator in file_content_lower:
                    patterns["testing_frameworks"].append(indicator)
                    break
        
        return patterns
    
    def _analyze_security(self, repo_path: Path, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security aspects"""
        security = {
            "potential_secrets": [],
            "security_files": [],
            "vulnerable_patterns": [],
            "security_score": 100
        }
        
        # Check for potential security files
        security_files = [".env", ".env.local", "secrets.yml", "private.key", "id_rsa"]
        for file_name in security_files:
            if (repo_path / file_name).exists():
                security["security_files"].append(file_name)
                security["security_score"] -= 20
        
        # Look for potential secrets in file names
        secret_patterns = ["password", "secret", "key", "token", "api_key", "private"]
        for file_info in file_data["text_files"]:
            file_name_lower = file_info["name"].lower()
            for pattern in secret_patterns:
                if pattern in file_name_lower:
                    security["potential_secrets"].append(file_info["path"])
                    security["security_score"] -= 5
                    break
        
        security["security_score"] = max(0, security["security_score"])
        return security
    
    def _analyze_dependencies(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze project dependencies"""
        dependencies = {
            "package_files": [],
            "dependency_counts": {},
            "package_managers": []
        }
        
        # Package file analysis
        package_files = {
            "package.json": self._analyze_npm_dependencies,
            "requirements.txt": self._analyze_pip_dependencies,
            "Pipfile": self._analyze_pipenv_dependencies,
            "Cargo.toml": self._analyze_cargo_dependencies,
            "go.mod": self._analyze_go_dependencies
        }
        
        for file_name, analyzer in package_files.items():
            file_path = repo_path / file_name
            if file_path.exists():
                dependencies["package_files"].append(file_name)
                try:
                    deps = analyzer(file_path)
                    dependencies["dependency_counts"][file_name] = len(deps)
                    dependencies[f"{file_name}_dependencies"] = deps
                except Exception:
                    dependencies["dependency_counts"][file_name] = 0
        
        return dependencies
    
    def _analyze_npm_dependencies(self, package_json_path: Path) -> List[str]:
        """Analyze NPM dependencies"""
        try:
            with open(package_json_path) as f:
                data = json.load(f)
            
            deps = []
            for dep_type in ["dependencies", "devDependencies", "peerDependencies"]:
                if dep_type in data:
                    deps.extend(data[dep_type].keys())
            
            return deps
        except Exception:
            return []
    
    def _analyze_pip_dependencies(self, requirements_path: Path) -> List[str]:
        """Analyze pip dependencies"""
        try:
            with open(requirements_path) as f:
                lines = f.readlines()
            
            deps = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before version specifiers)
                    package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('~=')[0]
                    deps.append(package_name.strip())
            
            return deps
        except Exception:
            return []
    
    def _analyze_pipenv_dependencies(self, pipfile_path: Path) -> List[str]:
        """Analyze Pipenv dependencies"""
        # This would require toml parsing, simplified for now
        return []
    
    def _analyze_cargo_dependencies(self, cargo_path: Path) -> List[str]:
        """Analyze Cargo dependencies"""
        # This would require toml parsing, simplified for now
        return []
    
    def _analyze_go_dependencies(self, go_mod_path: Path) -> List[str]:
        """Analyze Go module dependencies"""
        try:
            with open(go_mod_path) as f:
                lines = f.readlines()
            
            deps = []
            in_require = False
            for line in lines:
                line = line.strip()
                if line.startswith('require'):
                    in_require = True
                    continue
                elif in_require and line == ')':
                    in_require = False
                elif in_require and line:
                    # Extract module name
                    parts = line.split()
                    if parts:
                        deps.append(parts[0])
            
            return deps
        except Exception:
            return []
    
    def _calculate_quality_metrics(self, file_data: Dict[str, Any], language_data: Dict[str, Any], 
                                 structure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate code quality metrics"""
        metrics = {
            "maintainability_score": 50,
            "complexity_indicators": {},
            "documentation_ratio": 0,
            "test_coverage_indicators": {},
            "code_organization": {}
        }
        
        # Calculate documentation ratio
        total_files = file_data["total_files"]
        doc_files = len(structure_data["documentation_files"])
        metrics["documentation_ratio"] = (doc_files / total_files * 100) if total_files > 0 else 0
        
        # Maintainability factors
        if structure_data["has_readme"]:
            metrics["maintainability_score"] += 10
        if structure_data["has_license"]:
            metrics["maintainability_score"] += 5
        if structure_data["has_gitignore"]:
            metrics["maintainability_score"] += 5
        if structure_data["has_ci"]:
            metrics["maintainability_score"] += 15
        if structure_data["test_directories"]:
            metrics["maintainability_score"] += 15
        
        # Complexity indicators
        metrics["complexity_indicators"] = {
            "directory_depth": structure_data["depth"],
            "average_file_size": file_data["total_size"] / max(1, file_data["total_files"]),
            "large_file_count": len(file_data["large_files"]),
            "language_diversity": language_data["language_count"]
        }
        
        return metrics
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis summary"""
        return {
            "repository_name": analysis["repository_name"],
            "total_files": analysis["file_analysis"]["total_files"],
            "total_lines": analysis["file_analysis"]["total_lines"],
            "total_size_bytes": analysis["file_analysis"]["total_size"],
            "primary_language": analysis["language_analysis"]["primary_language"],
            "language_count": analysis["language_analysis"]["language_count"],
            "has_documentation": analysis["structure_analysis"]["has_readme"],
            "has_tests": bool(analysis["structure_analysis"]["test_directories"]),
            "maintainability_score": analysis["quality_metrics"]["maintainability_score"],
            "security_score": analysis["security_analysis"]["security_score"],
            "analysis_timestamp": analysis["timestamp"]
        }
    
    def _walk_repository(self, repo_path: Path):
        """Walk repository files, excluding ignored patterns"""
        for root, dirs, files in os.walk(repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in self.IGNORE_PATTERNS]
            
            for file_name in files:
                if file_name not in self.IGNORE_PATTERNS:
                    yield Path(root) / file_name
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return "error"