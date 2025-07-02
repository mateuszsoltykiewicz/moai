#!/usr/bin/env python3
"""
Helm Chart Processor: Automates Helm dependency updates and template validation.

Features:
- Discovers Helm charts in directory structure
- Parallel processing of charts using multiprocessing
- Dependency updates with 'helm dependency update'
- Template validation with 'helm template'
- Detailed reporting with success/failure status

Usage:
./helm_processor.py [--skip-template]
"""

import os
import subprocess
import logging
import argparse
from multiprocessing import Pool
from typing import List, Tuple, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Suggested improvements (could be implemented as future enhancements):
# 1. Add configuration file support for custom paths/patterns
# 2. Implement chart version validation
# 3. Add Kubernetes manifest validation with kubeval
# 4. Add support for custom values files
# 5. Implement timeout handling for long-running operations

def find_helm_charts(base_dir: str) -> List[str]:
    """Discover Helm charts in subdirectories containing Chart.yaml
    
    Args:
        base_dir: Root directory to search for Helm charts
        
    Returns:
        List of paths to directories containing Helm charts
    """
    charts = []
    for entry in os.listdir(base_dir):
        chart_dir = os.path.join(base_dir, entry)
        chart_file = os.path.join(chart_dir, 'Chart.yaml')
        if os.path.isdir(chart_dir) and os.path.isfile(chart_file):
            charts.append(chart_dir)
    return charts

def helm_dependency_update(chart_dir: str) -> Tuple[str, bool, str]:
    """Run helm dependency update for a single chart
    
    Args:
        chart_dir: Path to Helm chart directory
        
    Returns:
        Tuple containing (chart_path, success, message)
    """
    try:
        logger.info(f"Updating dependencies in {chart_dir}")
        result = subprocess.run(
            ['helm', 'dependency', 'update', chart_dir],
            capture_output=True,
            text=True,
            check=True
        )
        return (chart_dir, True, result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Dependency update failed for {chart_dir}: {e.stderr}")
        return (chart_dir, False, e.stderr)
    except Exception as e:
        logger.error(f"Unexpected error in {chart_dir}: {str(e)}")
        return (chart_dir, False, str(e))

def helm_template(chart_dir: str) -> Tuple[str, bool, str]:
    """Run helm template validation for a single chart
    
    Args:
        chart_dir: Path to Helm chart directory
        
    Returns:
        Tuple containing (chart_path, success, message)
    """
    try:
        logger.info(f"Templating {chart_dir}")
        result = subprocess.run(
            ['helm', 'template', chart_dir],
            capture_output=True,
            text=True,
            check=True
        )
        return (chart_dir, True, result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Templating failed for {chart_dir}: {e.stderr}")
        return (chart_dir, False, e.stderr)
    except Exception as e:
        logger.error(f"Unexpected error in {chart_dir}: {str(e)}")
        return (chart_dir, False, str(e))

def process_charts(charts: List[str], skip_template: bool) -> Dict[str, list]:
    """Orchestrate chart processing with multiprocessing
    
    Args:
        charts: List of chart directories to process
        skip_template: Whether to skip template validation
        
    Returns:
        Dictionary containing processing results
    """
    results = {'dependency_update': [], 'template': []}
    
    # Using half of available CPUs for resource efficiency
    with Pool(os.cpu_count() // 2 or 1) as pool:
        results['dependency_update'] = pool.map(helm_dependency_update, charts)
    
    if not skip_template:
        with Pool(os.cpu_count() // 2 or 1) as pool:
            results['template'] = pool.map(helm_template, charts)
    
    return results

def generate_report(results: Dict[str, list]) -> int:
    """Generate consolidated processing report
    
    Args:
        results: Processing results dictionary
        
    Returns:
        Exit code (0 for success, 1 for any failures)
    """
    exit_code = 0
    print("\n=== Processing Report ===")
    
    # Dependency update results
    print("\n[ Dependency Updates ]")
    for chart_dir, success, message in results['dependency_update']:
        status = "SUCCESS" if success else "FAILED"
        print(f"  {chart_dir}: {status}")
        if not success:
            exit_code = 1
            print(f"    Error: {message.strip()}")
    
    # Template results
    if results['template']:
        print("\n[ Template Validation ]")
        for chart_dir, success, message in results['template']:
            status = "SUCCESS" if success else "FAILED"
            print(f"  {chart_dir}: {status}")
            if not success:
                exit_code = 1
                print(f"    Error: {message.strip()}")
    
    return exit_code

def main() -> int:
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description='Helm Charts Processing Automation',
        epilog='Example: ./helm_processor.py --skip-template'
    )
    parser.add_argument(
        '--skip-template', 
        action='store_true',
        help='Skip Helm template validation step'
    )
    args = parser.parse_args()
    
    # Chart discovery
    charts = find_helm_charts('.')
    if not charts:
        logger.error("No Helm charts found in current directory")
        return 1
    
    logger.info(f"Discovered {len(charts)} Helm charts")
    
    # Parallel processing
    results = process_charts(charts, args.skip_template)
    
    # Report generation
    return generate_report(results)

if __name__ == '__main__':
    try:
        exit_code = main()
    except KeyboardInterrupt:
        logger.error("Processing interrupted by user")
        exit_code = 1
    except Exception as e:
        logger.exception("Fatal error occurred:")
        exit_code = 1
    finally:
        print(f"\nExit code: {exit_code}")
        exit(exit_code)
