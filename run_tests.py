#!/usr/bin/env python3
"""
Actions Vocabulary Test Runner

A pytest-based test runner for SHACL validation of the Actions Vocabulary.
Uses pyshacl library for validation instead of CLI.
"""

import sys
import argparse
from pathlib import Path
import subprocess
from typing import List, Optional


def run_pytest(
    verbose: bool = False,
    quick: bool = False,
    verbose_validation: bool = False,
    extra_args: Optional[List[str]] = None
) -> int:
    """
    Run pytest with appropriate arguments.
    
    Args:
        verbose: Show verbose pytest output
        quick: Run only basic tests (skip slow tests)
        verbose_validation: Show detailed SHACL validation output
        extra_args: Additional arguments to pass to pytest
        
    Returns:
        Exit code from pytest
    """
    cmd = ["uv", "run", "pytest", "tests/"]
    
    # Add pytest verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.extend(["-q", "--tb=short"])
    
    # Add custom options
    if verbose_validation:
        cmd.append("--verbose-validation")
    
    if quick:
        cmd.extend(["--quick", "-m", "not slow"])
    
    # Add extra arguments
    if extra_args:
        cmd.extend(extra_args)
    
    # Add default good options
    cmd.extend([
        "--strict-markers",
        "--strict-config",
        "-ra",  # Show all test results summary
    ])
    
    print("=" * 60)
    print("SHACL Validation Test Suite (pytest + pyshacl)")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return 130
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Actions Vocabulary SHACL Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --verbose          # Verbose output
  python run_tests.py --quick            # Skip slow tests
  python run_tests.py --verbose-validation  # Show SHACL details
  python run_tests.py --help             # This help
  
Test organization:
  tests/data/valid/     - Test data that should pass validation
  tests/data/invalid/   - Test data that should fail validation
  tests/results/        - Validation reports saved here
        """
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose pytest output"
    )
    
    parser.add_argument(
        "-q", "--quick", 
        action="store_true",
        help="Run only basic tests (skip complex/slow cases)"
    )
    
    parser.add_argument(
        "--verbose-validation",
        action="store_true", 
        help="Show detailed SHACL validation output"
    )
    
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install dependencies and exit"
    )
    
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Additional arguments to pass to pytest"
    )
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing dependencies with uv...")
        result = subprocess.run(["uv", "sync"], cwd=Path(__file__).parent)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
        else:
            print("❌ Failed to install dependencies")
        return result.returncode
    
    # Check if uv is available
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv is not installed or not in PATH")
        print("Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return 1
    
    # Run the tests
    exit_code = run_pytest(
        verbose=args.verbose,
        quick=args.quick,
        verbose_validation=args.verbose_validation,
        extra_args=args.pytest_args
    )
    
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Valid data conforms to SHACL shapes")
        print("✅ Invalid data properly rejected")
        print("✅ Ontology consistency validated")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check test output above for details")
        print("Validation reports saved in: tests/results/")
    print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())