#!/usr/bin/env python3
"""
FlintBloom Setup Verification Script

This script checks if FlintBloom is properly installed and configured.
"""

import sys
import subprocess
import os
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_header(text):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} (requires 3.11+)")
        return False


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description} not found: {filepath}")
        return False


def check_directory_structure():
    """Check if all required directories exist"""
    print("\nChecking directory structure...")

    required_dirs = [
        ("backend/app/core", "Core module"),
        ("backend/app/db", "Database module"),
        ("backend/app/db/adapters", "Database adapters"),
        ("backend/app/modules/offline", "Offline analysis module"),
        ("backend/app/modules/realtime", "Real-time tracking module"),
        ("frontend/src", "Frontend source"),
    ]

    all_exist = True
    for dir_path, description in required_dirs:
        if Path(dir_path).exists():
            print_success(f"{description}: {dir_path}")
        else:
            print_error(f"{description} not found: {dir_path}")
            all_exist = False

    return all_exist


def check_required_files():
    """Check if all required files exist"""
    print("\nChecking required files...")

    required_files = [
        ("backend/requirements.txt", "Backend requirements"),
        ("backend/app/main.py", "Main application"),
        ("backend/app/core/config.py", "Configuration"),
        ("backend/app/core/database.py", "Database setup"),
        ("backend/app/db/models.py", "Database models"),
        ("backend/app/db/schemas.py", "Pydantic schemas"),
        (".env.example", "Environment template"),
        ("docker-compose.yml", "Docker Compose config"),
        ("README.md", "Documentation"),
    ]

    all_exist = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_exist = False

    return all_exist


def check_dependencies():
    """Check if required Python packages are installed"""
    print("\nChecking Python dependencies...")

    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "langchain",
        "langgraph",
    ]

    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not installed")
            all_installed = False

    return all_installed


def check_docker():
    """Check if Docker is available"""
    print("\nChecking Docker...")

    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success(f"Docker: {result.stdout.strip()}")
            return True
        else:
            print_warning("Docker not available")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_warning("Docker not available")
        return False


def check_docker_compose():
    """Check if Docker Compose is available"""
    print("\nChecking Docker Compose...")

    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success(f"Docker Compose: {result.stdout.strip()}")
            return True
        else:
            print_warning("Docker Compose not available")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_warning("Docker Compose not available")
        return False


def check_env_file():
    """Check if .env file exists"""
    print("\nChecking environment configuration...")

    if Path(".env").exists():
        print_success(".env file exists")
        return True
    else:
        print_warning(".env file not found (will use .env.example)")
        if Path(".env.example").exists():
            print_warning("Run: cp .env.example .env")
        return False


def main():
    """Run all checks"""
    print_header("FlintBloom Setup Verification")

    checks = [
        ("Python Version", check_python_version),
        ("Directory Structure", check_directory_structure),
        ("Required Files", check_required_files),
        ("Python Dependencies", check_dependencies),
        ("Docker", check_docker),
        ("Docker Compose", check_docker_compose),
        ("Environment Config", check_env_file),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Error checking {name}: {e}")
            results[name] = False

    # Summary
    print_header("Verification Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} - {name}")

    print(f"\n{Colors.BLUE}Results: {passed}/{total} checks passed{Colors.END}")

    if passed == total:
        print_success("\n🎉 All checks passed! FlintBloom is ready to use.")
        print("\nNext steps:")
        print("  1. Configure .env file if needed")
        print("  2. Start services: docker-compose up -d")
        print("  3. Visit: http://localhost:8000/docs")
        return 0
    else:
        print_error("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("  - Install dependencies: pip install -r backend/requirements.txt")
        print("  - Create .env file: cp .env.example .env")
        print("  - Install Docker: https://docs.docker.com/get-docker/")
        return 1


if __name__ == "__main__":
    sys.exit(main())
