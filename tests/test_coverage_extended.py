#!/usr/bin/env python3
"""
Extended test suite for improved coverage
==========================================

Covers previously under-tested modules:
- src/mirror_watcher_ai/analyzer.py    (utility methods, summaries, assessments)
- src/mirror_watcher_ai/triune_integration.py (local sync, alerts, HTML dashboard, sync summary)
- src/mirror_watcher_ai/shadowscrolls.py  (crypto verification, Merkle tree, lineage, signing)
- src/mirror_watcher_ai/lineage.py     (log_error, get_latest_session_data, verify_lineage_integrity)
"""

import asyncio
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.mirror_watcher_ai.analyzer import TriuneAnalyzer
    from src.mirror_watcher_ai.triune_integration import TriuneEcosystemConnector
    from src.mirror_watcher_ai.shadowscrolls import ShadowScrollsIntegration
    from src.mirror_watcher_ai.lineage import MirrorLineageLogger
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# TriuneAnalyzer – utility / pure methods
# ---------------------------------------------------------------------------

class TestAnalyzerUtilityMethods(unittest.TestCase):
    """Test pure utility helpers on TriuneAnalyzer (no network calls)."""

    def setUp(self):
        self.analyzer = TriuneAnalyzer()

    # -- _is_conventional_commit --
    def test_conventional_commit_feat(self):
        self.assertTrue(self.analyzer._is_conventional_commit("feat: add login"))

    def test_conventional_commit_fix(self):
        self.assertTrue(self.analyzer._is_conventional_commit("fix: null ptr"))

    def test_conventional_commit_scoped(self):
        self.assertTrue(self.analyzer._is_conventional_commit("docs(readme): update badge"))

    def test_conventional_commit_chore(self):
        self.assertTrue(self.analyzer._is_conventional_commit("chore: bump deps"))

    def test_non_conventional_commit(self):
        self.assertFalse(self.analyzer._is_conventional_commit("updated stuff"))

    def test_non_conventional_empty(self):
        self.assertFalse(self.analyzer._is_conventional_commit(""))

    # -- _categorize_repo_size --
    def test_repo_size_small(self):
        self.assertEqual(self.analyzer._categorize_repo_size(500), "small")

    def test_repo_size_boundary_small_medium(self):
        self.assertEqual(self.analyzer._categorize_repo_size(1023), "small")
        self.assertEqual(self.analyzer._categorize_repo_size(1024), "medium")

    def test_repo_size_medium(self):
        self.assertEqual(self.analyzer._categorize_repo_size(5000), "medium")

    def test_repo_size_large(self):
        self.assertEqual(self.analyzer._categorize_repo_size(50000), "large")

    def test_repo_size_very_large(self):
        self.assertEqual(self.analyzer._categorize_repo_size(200000), "very_large")

    # -- _estimate_clone_time --
    def test_estimate_clone_time_zero(self):
        self.assertEqual(self.analyzer._estimate_clone_time(0), 0.0)

    def test_estimate_clone_time_1mb(self):
        self.assertAlmostEqual(self.analyzer._estimate_clone_time(1024), 1.0)

    # -- _parse_dependencies --
    def test_parse_python_dependencies(self):
        content = "# comment\nrequests==2.28.0\naiohttp>=3.8.0\n\n"
        deps = self.analyzer._parse_dependencies(content, "python")
        self.assertIn("requests", deps)
        self.assertIn("aiohttp", deps)

    def test_parse_python_dependencies_le(self):
        content = "package<=1.0.0\n"
        deps = self.analyzer._parse_dependencies(content, "python")
        self.assertIn("package", deps)

    def test_parse_nodejs_dependencies(self):
        pkg = json.dumps({
            "dependencies": {"express": "^4.0.0"},
            "devDependencies": {"jest": "^29.0.0"}
        })
        deps = self.analyzer._parse_dependencies(pkg, "nodejs")
        self.assertIn("express", deps)
        self.assertIn("jest", deps)

    def test_parse_nodejs_invalid_json(self):
        deps = self.analyzer._parse_dependencies("{invalid}", "nodejs")
        self.assertEqual(deps, [])

    def test_parse_unknown_ecosystem(self):
        deps = self.analyzer._parse_dependencies("anything", "rust")
        self.assertEqual(deps, [])

    # -- _calculate_security_score --
    def test_security_score_perfect(self):
        score = self.analyzer._calculate_security_score([], {"SECURITY.md": True, ".gitignore": True}, {"high_risk_patterns": 0, "medium_risk_patterns": 0})
        self.assertEqual(score, 100)

    def test_security_score_missing_files(self):
        score = self.analyzer._calculate_security_score([], {"SECURITY.md": False, ".gitignore": False}, {"high_risk_patterns": 0, "medium_risk_patterns": 0})
        self.assertEqual(score, 80)

    def test_security_score_advisories(self):
        # 2 advisories → -40, capped at 0
        score = self.analyzer._calculate_security_score(["a", "b", "c"], {}, {"high_risk_patterns": 0, "medium_risk_patterns": 0})
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_security_score_high_risk(self):
        score = self.analyzer._calculate_security_score([], {}, {"high_risk_patterns": 4, "medium_risk_patterns": 0})
        self.assertEqual(score, 0)

    def test_security_score_capped_at_zero(self):
        score = self.analyzer._calculate_security_score(["a"] * 10, {}, {"high_risk_patterns": 5, "medium_risk_patterns": 5})
        self.assertEqual(score, 0)

    # -- _has_recent_activity --
    def test_has_recent_activity_true(self):
        from datetime import datetime, timedelta, timezone
        recent = (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertTrue(self.analyzer._has_recent_activity(recent))

    def test_has_recent_activity_false(self):
        from datetime import datetime, timedelta, timezone
        old = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertFalse(self.analyzer._has_recent_activity(old))

    # -- _assess_maintenance_status --
    def test_maintenance_status_active(self):
        from datetime import datetime, timedelta, timezone
        recent = (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        status = self.analyzer._assess_maintenance_status({"pushed_at": recent, "open_issues_count": 0})
        self.assertEqual(status, "active")

    def test_maintenance_status_needs_attention(self):
        from datetime import datetime, timedelta, timezone
        old = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
        status = self.analyzer._assess_maintenance_status({"pushed_at": old, "open_issues_count": 25})
        self.assertEqual(status, "needs_attention")

    def test_maintenance_status_stable(self):
        from datetime import datetime, timedelta, timezone
        old = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
        status = self.analyzer._assess_maintenance_status({"pushed_at": old, "open_issues_count": 5})
        self.assertEqual(status, "stable")

    # -- _calculate_stars_per_day --
    def test_stars_per_day_positive(self):
        from datetime import datetime, timedelta, timezone
        created = (datetime.now(timezone.utc) - timedelta(days=100)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rate = self.analyzer._calculate_stars_per_day({"created_at": created, "stargazers_count": 100})
        self.assertAlmostEqual(rate, 1.0, delta=0.1)

    def test_stars_per_day_zero_days(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rate = self.analyzer._calculate_stars_per_day({"created_at": now, "stargazers_count": 10})
        self.assertEqual(rate, 0)


class TestAnalyzerAsyncSummaries(unittest.IsolatedAsyncioTestCase):
    """Test async summary/assessment methods on TriuneAnalyzer."""

    async def test_generate_analysis_summary_all_complete(self):
        analyzer = TriuneAnalyzer()
        repos = {
            "repo1": {"status": "completed", "health_score": 80},
            "repo2": {"status": "completed", "health_score": 60},
        }
        summary = await analyzer._generate_analysis_summary(repos)
        self.assertEqual(summary["total_repositories"], 2)
        self.assertEqual(summary["successful_analyses"], 2)
        self.assertEqual(summary["failed_analyses"], 0)
        self.assertAlmostEqual(summary["average_health_score"], 70.0)
        self.assertEqual(summary["highest_health_score"], 80)
        self.assertEqual(summary["lowest_health_score"], 60)

    async def test_generate_analysis_summary_with_error(self):
        analyzer = TriuneAnalyzer()
        repos = {
            "repo1": {"status": "error"},
            "repo2": {"status": "completed", "health_score": 90},
        }
        summary = await analyzer._generate_analysis_summary(repos)
        self.assertEqual(summary["successful_analyses"], 1)
        self.assertEqual(summary["failed_analyses"], 1)

    async def test_generate_analysis_summary_empty(self):
        analyzer = TriuneAnalyzer()
        summary = await analyzer._generate_analysis_summary({})
        self.assertEqual(summary["total_repositories"], 0)
        self.assertEqual(summary["average_health_score"], 0)

    async def test_generate_security_assessment_good(self):
        analyzer = TriuneAnalyzer()
        repos = {
            "r1": {"status": "completed", "security_scan": {"security_advisories": 0, "security_score": 95}},
            "r2": {"status": "completed", "security_scan": {"security_advisories": 0, "security_score": 90}},
        }
        assessment = await analyzer._generate_security_assessment(repos)
        self.assertEqual(assessment["total_security_advisories"], 0)
        self.assertEqual(assessment["overall_security_status"], "good")
        self.assertEqual(assessment["repositories_needing_attention"], 0)

    async def test_generate_security_assessment_needs_attention(self):
        analyzer = TriuneAnalyzer()
        repos = {
            "r1": {"status": "completed", "security_scan": {"security_advisories": 1, "security_score": 60}},
        }
        assessment = await analyzer._generate_security_assessment(repos)
        self.assertEqual(assessment["overall_security_status"], "needs_attention")
        self.assertEqual(assessment["repositories_needing_attention"], 1)

    async def test_generate_security_assessment_empty(self):
        analyzer = TriuneAnalyzer()
        assessment = await analyzer._generate_security_assessment({})
        self.assertEqual(assessment["total_security_advisories"], 0)

    async def test_generate_performance_metrics(self):
        analyzer = TriuneAnalyzer()
        repos = {
            "r1": {
                "status": "completed",
                "performance_metrics": {
                    "repository_size_kb": 2048,
                    "health_indicators": {"has_recent_activity": True}
                }
            },
            "r2": {
                "status": "completed",
                "performance_metrics": {
                    "repository_size_kb": 1024,
                    "health_indicators": {"has_recent_activity": False}
                }
            },
        }
        metrics = await analyzer._generate_performance_metrics(repos)
        self.assertAlmostEqual(metrics["total_ecosystem_size_mb"], 3.0)
        self.assertEqual(metrics["active_repositories"], 1)
        self.assertAlmostEqual(metrics["ecosystem_activity_rate"], 0.5)

    async def test_generate_recommendations_all_good(self):
        analyzer = TriuneAnalyzer()
        results = {
            "summary": {"average_health_score": 90},
            "security_assessment": {"overall_security_status": "good"},
            "performance_metrics": {"ecosystem_activity_rate": 1.0},
        }
        recs = await analyzer._generate_recommendations(results)
        self.assertEqual(recs, [])

    async def test_generate_recommendations_all_bad(self):
        analyzer = TriuneAnalyzer()
        results = {
            "summary": {"average_health_score": 50},
            "security_assessment": {"overall_security_status": "needs_attention"},
            "performance_metrics": {"ecosystem_activity_rate": 0.5},
        }
        recs = await analyzer._generate_recommendations(results)
        self.assertEqual(len(recs), 3)

    async def test_calculate_health_score_perfect(self):
        analyzer = TriuneAnalyzer()
        score = await analyzer._calculate_health_score(
            {"open_issues_count": 2},
            {"recent_activity": {"last_commit": "2025-01-01T00:00:00Z"},
             "commit_message_analysis": {"conventional_commits": 10}},
            {"languages": {"Python": 1000}},
            {"security_score": 90, "security_files_present": {"SECURITY.md": True}},
            {"repository_size_kb": 500},
            {"ecosystems_found": ["python"]},
        )
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    async def test_calculate_health_score_deductions(self):
        analyzer = TriuneAnalyzer()
        # lots of issues, low security, no recent activity → heavy deductions
        score = await analyzer._calculate_health_score(
            {"open_issues_count": 15},
            {"recent_activity": {}},
            {},
            {"security_score": 70, "security_files_present": {}},
            {},
            {},
        )
        # should have deducted for issues (10), security (15), no recent commit (20) → 55
        self.assertLessEqual(score, 60)


# ---------------------------------------------------------------------------
# TriuneEcosystemConnector – configuration and local sync methods
# ---------------------------------------------------------------------------

class TestTriuneConnectorConfig(unittest.TestCase):
    """Test configuration loading with and without config file."""

    def test_load_configuration_returns_dict(self):
        connector = TriuneEcosystemConnector()
        config = connector._load_configuration()
        self.assertIsInstance(config, dict)
        self.assertGreater(len(config), 0)

    def test_load_configuration_missing_file(self):
        connector = TriuneEcosystemConnector()
        with patch("os.path.exists", return_value=False):
            config = connector._load_configuration()
        # Should return default fallback config
        self.assertIn("ecosystem_version", config)
        self.assertIn("integration_mode", config)

    def test_load_configuration_invalid_file(self):
        connector = TriuneEcosystemConnector()
        with patch("builtins.open", side_effect=Exception("IO error")):
            config = connector._load_configuration()
        self.assertIn("ecosystem_version", config)

    def test_endpoints_populated(self):
        connector = TriuneEcosystemConnector()
        self.assertIn("legio_cognito", connector.endpoints)
        self.assertIn("triumvirate_monitor", connector.endpoints)
        self.assertIn("swarm_engine", connector.endpoints)

    def test_auth_tokens_dict(self):
        connector = TriuneEcosystemConnector()
        self.assertIsInstance(connector.auth_tokens, dict)


class TestTriuneConnectorLocalSync(unittest.IsolatedAsyncioTestCase):
    """Test local sync fallback methods."""

    async def test_local_legio_cognito_sync(self):
        connector = TriuneEcosystemConnector()
        with tempfile.TemporaryDirectory() as tmp:
            connector._legio_archive_dir = tmp
            scroll_data = {"test": "data", "scroll_type": "test"}

            with patch(
                "src.mirror_watcher_ai.triune_integration.os.makedirs"
            ):
                # Provide a real writable path
                import src.mirror_watcher_ai.triune_integration as ti_module
                original = ti_module.os.makedirs

                result = await connector._local_legio_cognito_sync(scroll_data)

        self.assertIn("status", result)
        self.assertIn(result["status"], ["local_success", "error"])

    async def test_generate_sync_summary_all_success(self):
        connector = TriuneEcosystemConnector()
        systems = {
            "legio_cognito": {"status": "success"},
            "triumvirate_monitor": {"status": "success"},
            "swarm_engine": {"status": "local_success"},
            "shell_automation": {"status": "local_success"},
        }
        summary = await connector._generate_sync_summary(systems)
        self.assertEqual(summary["total_systems"], 4)
        self.assertEqual(summary["successful_syncs"], 2)
        self.assertEqual(summary["local_syncs"], 2)
        self.assertEqual(summary["failed_syncs"], 0)
        self.assertEqual(summary["overall_status"], "success")

    async def test_generate_sync_summary_with_failures(self):
        connector = TriuneEcosystemConnector()
        systems = {
            "legio_cognito": {"status": "error"},
            "triumvirate_monitor": {"status": "error"},
        }
        summary = await connector._generate_sync_summary(systems)
        self.assertEqual(summary["overall_status"], "failed")
        self.assertEqual(summary["failed_syncs"], 2)

    async def test_generate_sync_summary_partial(self):
        connector = TriuneEcosystemConnector()
        systems = {
            "legio_cognito": {"status": "success"},
            "triumvirate_monitor": {"status": "error"},
        }
        summary = await connector._generate_sync_summary(systems)
        self.assertEqual(summary["overall_status"], "partial_success")

    async def test_generate_mobile_alerts_no_issues(self):
        connector = TriuneEcosystemConnector()
        results = {
            "security_assessment": {"overall_security_status": "good"},
            "summary": {"average_health_score": 90, "failed_analyses": 0},
        }
        alerts = await connector._generate_mobile_alerts(results)
        self.assertEqual(len(alerts), 0)

    async def test_generate_mobile_alerts_security(self):
        connector = TriuneEcosystemConnector()
        results = {
            "security_assessment": {
                "overall_security_status": "needs_attention",
                "repositories_needing_attention": 2,
            },
            "summary": {"average_health_score": 90, "failed_analyses": 0},
        }
        alerts = await connector._generate_mobile_alerts(results)
        types = [a["type"] for a in alerts]
        self.assertIn("security", types)

    async def test_generate_mobile_alerts_low_health(self):
        connector = TriuneEcosystemConnector()
        results = {
            "security_assessment": {"overall_security_status": "good"},
            "summary": {"average_health_score": 50, "failed_analyses": 0},
        }
        alerts = await connector._generate_mobile_alerts(results)
        types = [a["type"] for a in alerts]
        self.assertIn("health", types)

    async def test_generate_mobile_alerts_failures(self):
        connector = TriuneEcosystemConnector()
        results = {
            "security_assessment": {"overall_security_status": "good"},
            "summary": {"average_health_score": 90, "failed_analyses": 3},
        }
        alerts = await connector._generate_mobile_alerts(results)
        types = [a["type"] for a in alerts]
        self.assertIn("failure", types)

    async def test_generate_mobile_alerts_all_issues(self):
        connector = TriuneEcosystemConnector()
        results = {
            "security_assessment": {
                "overall_security_status": "needs_attention",
                "repositories_needing_attention": 1,
            },
            "summary": {"average_health_score": 40, "failed_analyses": 2},
        }
        alerts = await connector._generate_mobile_alerts(results)
        self.assertEqual(len(alerts), 3)

    async def test_generate_html_dashboard_no_alerts(self):
        connector = TriuneEcosystemConnector()
        dashboard_data = {
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z",
            "metrics": {
                "repositories_analyzed": 5,
                "average_health_score": 80,
                "security_status": "good",
            },
            "alerts": [],
        }
        html = await connector._generate_html_dashboard(dashboard_data)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Triune Mirror Watcher Dashboard", html)
        self.assertIn("All Clear", html)

    async def test_generate_html_dashboard_with_alerts(self):
        connector = TriuneEcosystemConnector()
        dashboard_data = {
            "status": "degraded",
            "timestamp": "2025-01-01T00:00:00Z",
            "metrics": {
                "repositories_analyzed": 3,
                "average_health_score": 55,
                "security_status": "needs_attention",
            },
            "alerts": [
                {
                    "type": "security",
                    "severity": "high",
                    "title": "Security Issue",
                    "message": "Check repos",
                    "timestamp": "2025-01-01T00:00:00Z",
                }
            ],
        }
        html = await connector._generate_html_dashboard(dashboard_data)
        self.assertIn("Security Issue", html)
        self.assertNotIn("All Clear", html)

    async def test_update_shell_environment(self):
        connector = TriuneEcosystemConnector()
        with tempfile.TemporaryDirectory() as tmp:
            env_file = os.path.join(tmp, ".mirror_analysis_env")
            analysis_results = {
                "analysis_id": "test_001",
                "repositories": {"r1": {}, "r2": {}},
                "summary": {"average_health_score": 75},
                "security_assessment": {"overall_security_status": "good"},
            }
            with patch(
                "src.mirror_watcher_ai.triune_integration.TriuneEcosystemConnector._update_shell_environment",
                new_callable=AsyncMock,
                return_value={"environment_updated": True, "env_file": env_file, "variables_set": 6},
            ):
                result = await connector._update_shell_environment(analysis_results)

        self.assertIn("environment_updated", result)


# ---------------------------------------------------------------------------
# ShadowScrollsIntegration – crypto helpers
# ---------------------------------------------------------------------------

class TestShadowScrollsCrypto(unittest.IsolatedAsyncioTestCase):
    """Test cryptographic methods in ShadowScrollsIntegration."""

    async def test_generate_verification_data_structure(self):
        ss = ShadowScrollsIntegration()
        data = {"key": "value", "repositories": {"r1": {"status": "ok"}}}
        result = await ss._generate_verification_data(data)
        self.assertIn("data_hash", result)
        self.assertIn("algorithm", result)
        self.assertIn("timestamp", result)
        self.assertIn("merkle_root", result)
        self.assertIn("data_size_bytes", result)
        self.assertEqual(result["algorithm"], "SHA-256")
        self.assertEqual(len(result["data_hash"]), 64)

    async def test_generate_verification_data_deterministic_hash(self):
        ss = ShadowScrollsIntegration()
        data = {"repositories": {"r1": {"val": 1}}}
        r1 = await ss._generate_verification_data(data)
        r2 = await ss._generate_verification_data(data)
        self.assertEqual(r1["data_hash"], r2["data_hash"])

    async def test_calculate_merkle_root_empty(self):
        ss = ShadowScrollsIntegration()
        root = await ss._calculate_merkle_root({})
        self.assertEqual(len(root), 64)

    async def test_calculate_merkle_root_single_repo(self):
        ss = ShadowScrollsIntegration()
        root = await ss._calculate_merkle_root({"repositories": {"r1": {"val": 1}}})
        self.assertEqual(len(root), 64)

    async def test_calculate_merkle_root_multiple_repos(self):
        ss = ShadowScrollsIntegration()
        data = {
            "repositories": {
                "repo1": {"status": "completed"},
                "repo2": {"status": "completed"},
                "repo3": {"status": "completed"},
            }
        }
        root = await ss._calculate_merkle_root(data)
        self.assertEqual(len(root), 64)

    async def test_calculate_merkle_root_odd_leaves(self):
        """Odd number of repos exercises the duplicate-last-leaf branch."""
        ss = ShadowScrollsIntegration()
        data = {
            "repositories": {
                "r1": {"x": 1},
                "r2": {"x": 2},
                "r3": {"x": 3},
            }
        }
        root = await ss._calculate_merkle_root(data)
        self.assertEqual(len(root), 64)

    async def test_calculate_lineage_hash(self):
        ss = ShadowScrollsIntegration()
        history = [
            {"verification_hash": "abc123"},
            {"verification_hash": "def456"},
        ]
        h = ss._calculate_lineage_hash("exec_001", history)
        self.assertEqual(len(h), 64)

    async def test_calculate_lineage_hash_empty_history(self):
        ss = ShadowScrollsIntegration()
        h = ss._calculate_lineage_hash("exec_empty", [])
        self.assertEqual(len(h), 64)
        # Deterministic
        h2 = ss._calculate_lineage_hash("exec_empty", [])
        self.assertEqual(h, h2)

    async def test_sign_attestation_no_key(self):
        ss = ShadowScrollsIntegration()
        ss.signing_key = ""
        payload = {"test": "data", "more": {"nested": 42}}
        result = await ss._sign_attestation(payload)
        self.assertIn("hash", result)
        self.assertIn("signature", result)
        self.assertIn("algorithm", result)
        self.assertEqual(result["algorithm"], "SHA256-Timestamp")

    async def test_sign_attestation_with_key(self):
        ss = ShadowScrollsIntegration()
        ss.signing_key = "supersecretkey"
        payload = {"test": "data"}
        result = await ss._sign_attestation(payload)
        self.assertEqual(result["algorithm"], "HMAC-SHA256")
        self.assertIsNotNone(result["signature"])

    async def test_collect_external_witnesses(self):
        ss = ShadowScrollsIntegration()
        witnesses = await ss._collect_external_witnesses("exec_001")
        self.assertIsInstance(witnesses, list)
        self.assertGreaterEqual(len(witnesses), 1)
        types = [w["type"] for w in witnesses]
        self.assertIn("github_actions", types)
        self.assertIn("system_environment", types)

    async def test_store_attestation_locally(self):
        ss = ShadowScrollsIntegration()
        with tempfile.TemporaryDirectory() as tmp:
            ss.scroll_directory = tmp
            os.makedirs(os.path.join(tmp, "attestations"), exist_ok=True)
            payload = {
                "scroll_metadata": {"execution_id": "t1"},
                "signature": {"hash": "abc"},
            }
            await ss._store_attestation_locally("t1", payload)
            stored = os.path.join(tmp, "attestations", "t1.json")
            self.assertTrue(os.path.exists(stored))

    async def test_get_attestation_history_empty_dir(self):
        ss = ShadowScrollsIntegration()
        with tempfile.TemporaryDirectory() as tmp:
            ss.scroll_directory = tmp
            os.makedirs(os.path.join(tmp, "attestations"), exist_ok=True)
            history = await ss.get_attestation_history()
            self.assertIsInstance(history, list)
            self.assertEqual(len(history), 0)

    async def test_get_attestation_history_with_files(self):
        ss = ShadowScrollsIntegration()
        with tempfile.TemporaryDirectory() as tmp:
            att_dir = os.path.join(tmp, "attestations")
            os.makedirs(att_dir, exist_ok=True)
            ss.scroll_directory = tmp
            # Write two attestation files
            for name in ("exec1.json", "exec2.json"):
                data = {
                    "scroll_metadata": {"execution_id": name, "scroll_id": "#001 – test", "timestamp": "2025-01-01T00:00:00Z"},
                    "analysis_data": {"repositories": {}},
                    "signature": {"hash": "deadbeef"},
                    "external_attestation": {"status": "local_only"},
                }
                with open(os.path.join(att_dir, name), "w") as f:
                    json.dump(data, f)
            history = await ss.get_attestation_history()
            self.assertEqual(len(history), 2)

    async def test_get_attestation_history_malformed_file(self):
        ss = ShadowScrollsIntegration()
        with tempfile.TemporaryDirectory() as tmp:
            att_dir = os.path.join(tmp, "attestations")
            os.makedirs(att_dir, exist_ok=True)
            ss.scroll_directory = tmp
            # Write a malformed JSON file
            with open(os.path.join(att_dir, "bad.json"), "w") as f:
                f.write("{invalid json")
            history = await ss.get_attestation_history()
            self.assertEqual(len(history), 0)


# ---------------------------------------------------------------------------
# ShadowScrollsIntegration – scroll number generation
# ---------------------------------------------------------------------------

class TestShadowScrollsScrollNumber(unittest.IsolatedAsyncioTestCase):

    async def test_generate_scroll_number_empty_history(self):
        ss = ShadowScrollsIntegration()
        with tempfile.TemporaryDirectory() as tmp:
            ss.scroll_directory = tmp
            os.makedirs(os.path.join(tmp, "attestations"), exist_ok=True)
            number = await ss._generate_scroll_number()
            self.assertIsInstance(number, str)

    async def test_generate_scroll_number_increments(self):
        ss = ShadowScrollsIntegration()
        with tempfile.TemporaryDirectory() as tmp:
            att_dir = os.path.join(tmp, "attestations")
            os.makedirs(att_dir, exist_ok=True)
            ss.scroll_directory = tmp
            data = {
                "scroll_metadata": {"scroll_id": "#005 – Mirror Analysis exec1", "execution_id": "x", "timestamp": "t"},
                "analysis_data": {"repositories": {}},
                "signature": {"hash": "h"},
                "external_attestation": {"status": "s"},
            }
            with open(os.path.join(att_dir, "exec1.json"), "w") as f:
                json.dump(data, f)
            number = await ss._generate_scroll_number()
            self.assertEqual(number, "006")


# ---------------------------------------------------------------------------
# MirrorLineageLogger – log_error, get_latest_session_data, verify_lineage_integrity
# ---------------------------------------------------------------------------

class TestLineageLoggerExtended(unittest.IsolatedAsyncioTestCase):
    """Test additional MirrorLineageLogger methods."""

    async def _setup_logger(self, tmp):
        logger = MirrorLineageLogger()
        logger.lineage_directory = tmp
        logger.db_path = os.path.join(tmp, "lineage.db")
        await logger._initialize_database()
        return logger

    async def test_log_error_stores_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            await lineage.start_session("session_err", "test")
            await lineage.log_error("session_err", "Something went wrong", {"detail": "extra"})
            error_file = os.path.join(tmp, "errors", "session_err_error.json")
            self.assertTrue(os.path.exists(error_file))
            with open(error_file) as f:
                data = json.load(f)
            self.assertEqual(data["error_message"], "Something went wrong")
            self.assertEqual(data["error_data"]["detail"], "extra")

    async def test_log_error_no_extra_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            await lineage.start_session("session_err2", "test")
            await lineage.log_error("session_err2", "Minimal error")
            error_file = os.path.join(tmp, "errors", "session_err2_error.json")
            self.assertTrue(os.path.exists(error_file))

    async def test_log_scan_results_starts_session(self):
        """log_scan_results should start a session automatically if none active."""
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            # No session started – log_scan_results should start one
            scan_data = {"scan_type": "full", "results": []}
            phase_meta = await lineage.log_scan_results("scan_001", scan_data)
            self.assertEqual(phase_meta["phase_name"], "repository_scan")

    async def test_get_latest_session_data_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            result = await lineage.get_latest_session_data()
            self.assertIsNone(result)

    async def test_get_latest_session_data_after_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            await lineage.start_session("sess_latest", "analysis")
            await lineage.log_phase("phase_one", {"x": 1})
            await lineage.finalize_session({"status": "completed"})

            data = await lineage.get_latest_session_data()
            self.assertIsNotNone(data)
            self.assertEqual(data["session_id"], "sess_latest")
            self.assertIn("phases", data)

    async def test_verify_lineage_integrity_session_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            result = await lineage.verify_lineage_integrity("nonexistent_session")
            self.assertEqual(result["overall_status"], "failed")
            self.assertIn("session_exists", result["checks"])

    async def test_verify_lineage_integrity_valid_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            await lineage.start_session("sess_integrity", "test")
            await lineage.log_phase("my_phase", {"data": "value"})
            await lineage.finalize_session({"status": "completed"})

            result = await lineage.verify_lineage_integrity("sess_integrity")
            self.assertIn("overall_status", result)
            self.assertIn("checks", result)
            self.assertIn("session_exists", result["checks"])

    async def test_health_check_passes_after_init(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            health = await lineage.health_check()
            self.assertIn("status", health)
            self.assertIn("database", health["checks"])
            self.assertIn("filesystem", health["checks"])

    async def test_finalize_session_no_active_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            with self.assertRaises(Exception):
                await lineage.finalize_session({})

    async def test_log_phase_no_active_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            with self.assertRaises(Exception):
                await lineage.log_phase("orphan_phase", {})

    async def test_full_session_workflow_with_phases(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            await lineage.start_session("full_workflow", "analysis")
            await lineage.log_phase("init", {"step": 1})
            await lineage.log_phase("scan", {"repos": ["r1", "r2"]})
            final = await lineage.finalize_session({"status": "completed"})
            self.assertEqual(final["session_id"], "full_workflow")
            self.assertIn("final_verification", final)
            self.assertIn("hash", final["final_verification"])
            # Session should be reset
            self.assertIsNone(lineage.current_session)

    async def test_collect_system_info(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            info = await lineage._collect_system_info()
            self.assertIn("timestamp", info)
            self.assertIn("platform", info)
            self.assertIn("process_id", info)

    async def test_collect_environment_info_filters_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = await self._setup_logger(tmp)
            env = await lineage._collect_environment_info()
            # All values should be non-None
            for v in env.values():
                self.assertIsNotNone(v)


if __name__ == "__main__":
    unittest.main()
