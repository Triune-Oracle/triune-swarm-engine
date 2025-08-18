#!/usr/bin/env python3
"""
Mirror Watcher CLI - Main Command Line Interface
Provides analyze command with ShadowScrolls integration for immutable logging
"""

import click
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .analyzer import TriuneAnalyzer
from .shadowscrolls import ShadowScrolls

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Mirror Watcher - CLI Mirroring & Analysis for Triune Projects"""
    pass


@cli.command()
@click.option('--source', '-s', required=True, help='Source repository URL')
@click.option('--target', '-t', help='Target directory for mirroring')
@click.option('--format', '-f', default='json', type=click.Choice(['json', 'table']), 
              help='Output format')
@click.option('--witness', '-w', is_flag=True, help='Enable external witnessing')
@click.option('--shadowscrolls', is_flag=True, default=True, 
              help='Enable ShadowScrolls immutable logging')
@click.option('--lineage-id', help='MirrorLineage-Δ identifier for traceability')
def analyze(source, target, format, witness, shadowscrolls, lineage_id):
    """
    Analyze repository mirrors with ShadowScrolls attestation
    
    This command performs comprehensive analysis of mirrored repositories,
    generating structured output with immutable logging capabilities.
    """
    try:
        if format != 'json':
            console.print(Panel(
                f"[bold blue]Mirror Watcher Analysis[/bold blue]\n"
                f"Source: {source}\n"
                f"Target: {target or 'auto-detected'}\n"
                f"Format: {format}\n"
                f"ShadowScrolls: {'✅ Enabled' if shadowscrolls else '❌ Disabled'}\n"
                f"External Witnessing: {'✅ Enabled' if witness else '❌ Disabled'}",
                title="🔍 Analysis Configuration"
            ))
        
        # Initialize analyzer
        analyzer = TriuneAnalyzer(source_url=source, target_dir=target)
        
        # Perform analysis
        if format != 'json':
            console.print("🔄 [yellow]Performing repository analysis...[/yellow]")
        analysis_result = analyzer.analyze()
        
        # Initialize ShadowScrolls if enabled
        if shadowscrolls:
            scrolls = ShadowScrolls()
            effective_lineage_id = lineage_id or scrolls.generate_lineage_id()
            
            # Create attestation
            attestation = scrolls.create_attestation(
                analysis_result=analysis_result,
                lineage_id=effective_lineage_id,
                witness_enabled=witness
            )
            
            # Add attestation to result
            analysis_result['shadowscrolls_attestation'] = attestation
            
            if format != 'json':
                console.print(f"✅ [green]ShadowScrolls attestation created[/green] (ID: {effective_lineage_id})")
        
        # External witnessing
        if witness:
            witness_hash = analyzer.generate_witness_proof(analysis_result)
            analysis_result['external_witness'] = {
                'hash': witness_hash,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'blockchain_ready': True
            }
            if format != 'json':
                console.print(f"🔐 [green]External witness proof generated[/green] (Hash: {witness_hash[:16]}...)")
        
        # Output results
        if format == 'json':
            # For JSON output, suppress rich console output during analysis
            print(json.dumps(analysis_result, indent=2))
        else:
            display_table_results(analysis_result)
            
            # Success summary (only for table format)
            console.print(Panel(
                f"[bold green]✅ Analysis Complete[/bold green]\n"
                f"Files analyzed: {analysis_result.get('stats', {}).get('total_files', 0)}\n"
                f"Repository size: {analysis_result.get('stats', {}).get('total_size_human', 'Unknown')}\n"
                f"Execution time: {analysis_result.get('metadata', {}).get('execution_time', 'Unknown')}",
                title="📊 Results Summary"
            ))
        
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}", file=sys.stderr)
        sys.exit(1)


def display_table_results(result):
    """Display analysis results in table format"""
    
    # Main stats table
    stats_table = Table(title="📊 Repository Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")
    
    stats = result.get('stats', {})
    for key, value in stats.items():
        stats_table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(stats_table)
    
    # Files table
    if 'files' in result:
        files_table = Table(title="📁 File Analysis")
        files_table.add_column("Path", style="blue")
        files_table.add_column("Type", style="yellow")
        files_table.add_column("Size", style="green")
        
        for file_info in result['files'][:10]:  # Show first 10 files
            files_table.add_row(
                file_info.get('path', ''),
                file_info.get('type', ''),
                str(file_info.get('size_human', file_info.get('size', '')))
            )
        
        console.print(files_table)
    
    # Attestation info
    if 'shadowscrolls_attestation' in result:
        attestation = result['shadowscrolls_attestation']
        console.print(Panel(
            f"Hash: {attestation.get('hash', '')}\n"
            f"Timestamp: {attestation.get('timestamp', '')}\n"
            f"Lineage: {attestation.get('lineage_id', '')}",
            title="🔏 ShadowScrolls Attestation"
        ))


def main():
    """Main entry point for CLI"""
    cli()


if __name__ == '__main__':
    main()