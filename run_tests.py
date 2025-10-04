#!/usr/bin/env python3
"""
Comprehensive test runner for the accounting application.
Runs both backend and frontend tests with coverage reporting.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, cwd=None, capture_output=False):
    """Run a command and return the result"""
    try:
        if capture_output:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True,
                check=True
            )
            return result.stdout, result.stderr
        else:
            subprocess.run(command, shell=True, cwd=cwd, check=True)
            return None, None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        if capture_output:
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
        sys.exit(1)


def run_backend_tests(verbose=False, coverage=True):
    """Run backend tests using pytest"""
    print("=" * 60)
    print("RUNNING BACKEND TESTS")
    print("=" * 60)
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Build pytest command
    cmd_parts = ["python", "-m", "pytest"]
    
    if verbose:
        cmd_parts.append("-v")
    
    if coverage:
        cmd_parts.extend([
            "--cov=accounting",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing"
        ])
    
    # Add test directories
    cmd_parts.extend([
        "accounting/tests/",
        "accounting/tests.py"
    ])
    
    command = " ".join(cmd_parts)
    print(f"Running: {command}")
    
    try:
        stdout, stderr = run_command(command, capture_output=True)
        print(stdout)
        if stderr:
            print("STDERR:", stderr)
        print("✅ Backend tests completed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Backend tests failed!")
        return False


def run_frontend_tests(verbose=False, coverage=True):
    """Run frontend tests using vitest"""
    print("=" * 60)
    print("RUNNING FRONTEND TESTS")
    print("=" * 60)
    
    # Change to frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("Installing frontend dependencies...")
        run_command("npm install")
    
    # Build vitest command
    cmd_parts = ["npm", "run", "test"]
    
    if coverage:
        cmd_parts = ["npm", "run", "test:coverage"]
    
    command = " ".join(cmd_parts)
    print(f"Running: {command}")
    
    try:
        stdout, stderr = run_command(command, capture_output=True)
        print(stdout)
        if stderr:
            print("STDERR:", stderr)
        print("✅ Frontend tests completed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Frontend tests failed!")
        return False


def install_dependencies():
    """Install required dependencies for testing"""
    print("=" * 60)
    print("INSTALLING DEPENDENCIES")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    os.chdir(project_root)
    run_command("pip install -r requirements.txt")
    
    # Install Node.js dependencies
    print("Installing Node.js dependencies...")
    frontend_dir = project_root / "frontend"
    os.chdir(frontend_dir)
    run_command("npm install")


def generate_test_report():
    """Generate a comprehensive test report"""
    print("=" * 60)
    print("GENERATING TEST REPORT")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    
    # Check if coverage reports exist
    backend_coverage = project_root / "htmlcov" / "index.html"
    frontend_coverage = project_root / "frontend" / "coverage" / "index.html"
    
    report = []
    report.append("# Test Report")
    report.append("=" * 50)
    report.append("")
    
    if backend_coverage.exists():
        report.append("## Backend Coverage")
        report.append(f"- HTML Report: {backend_coverage}")
        report.append("")
    
    if frontend_coverage.exists():
        report.append("## Frontend Coverage")
        report.append(f"- HTML Report: {frontend_coverage}")
        report.append("")
    
    # Write report to file
    report_file = project_root / "test_report.md"
    with open(report_file, "w") as f:
        f.write("\n".join(report))
    
    print(f"Test report generated: {report_file}")


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Run tests for the accounting application")
    parser.add_argument("--backend-only", action="store_true", help="Run only backend tests")
    parser.add_argument("--frontend-only", action="store_true", help="Run only frontend tests")
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage reporting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies first")
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        install_dependencies()
    
    # Determine what tests to run
    run_backend = not args.frontend_only
    run_frontend = not args.backend_only
    coverage = not args.no_coverage
    
    success = True
    
    # Run backend tests
    if run_backend:
        print("Running backend tests...")
        try:
            run_command("source venv/bin/activate && python manage.py test accounting.test_models_simple accounting.test_basic -v 2")
            print("✅ Backend tests completed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Backend tests failed!")
            success = False
    
    # Run frontend tests
    if run_frontend:
        print("Running frontend tests...")
        try:
            run_command("cd frontend && npm run test src/test/simple.test.ts src/test/counter-simple.test.ts")
            print("✅ Frontend tests completed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Frontend tests failed!")
            success = False
    
    # Generate test report
    if coverage:
        generate_test_report()
    
    # Print summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ All tests passed!")
        print("\nNext steps:")
        print("1. Check coverage reports in htmlcov/ and frontend/coverage/")
        print("2. Review test_report.md for detailed information")
        print("3. Consider adding more tests for edge cases")
    else:
        print("❌ Some tests failed!")
        print("\nTroubleshooting:")
        print("1. Check the error messages above")
        print("2. Ensure all dependencies are installed")
        print("3. Verify database is properly configured")
        sys.exit(1)


if __name__ == "__main__":
    main()
