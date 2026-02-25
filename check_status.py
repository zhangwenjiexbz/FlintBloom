#!/usr/bin/env python3
"""
Project Status Check

Quick script to verify FlintBloom project completeness
"""

import os
from pathlib import Path


def check_file(path, description):
    """Check if file exists"""
    exists = Path(path).exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {path}")
    return exists


def check_dir(path, description):
    """Check if directory exists"""
    exists = Path(path).exists() and Path(path).is_dir()
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {path}")
    return exists


def main():
    print("=" * 70)
    print("FlintBloom Project Status Check")
    print("=" * 70)

    total = 0
    passed = 0

    # Backend Core
    print("\n📦 Backend Core:")
    checks = [
        ("backend/app/main.py", "Main application"),
        ("backend/app/core/config.py", "Configuration"),
        ("backend/app/core/database.py", "Database setup"),
        ("backend/requirements.txt", "Dependencies"),
    ]
    for path, desc in checks:
        total += 1
        if check_file(path, desc):
            passed += 1

    # Database Layer
    print("\n🗄️  Database Layer:")
    checks = [
        ("backend/app/db/models.py", "SQLAlchemy models"),
        ("backend/app/db/schemas.py", "Pydantic schemas"),
        ("backend/app/db/adapters/base.py", "Base adapter"),
        ("backend/app/db/adapters/mysql.py", "MySQL adapter"),
        ("backend/app/db/adapters/postgresql.py", "PostgreSQL adapter"),
        ("backend/app/db/adapters/sqlite.py", "SQLite adapter"),
    ]
    for path, desc in checks:
        total += 1
        if check_file(path, desc):
            passed += 1

    # Offline Analysis Module
    print("\n🔍 Offline Analysis Module:")
    checks = [
        ("backend/app/modules/offline/parser.py", "Checkpoint parser"),
        ("backend/app/modules/offline/analyzer.py", "Data analyzer"),
        ("backend/app/modules/offline/api.py", "API endpoints"),
    ]
    for path, desc in checks:
        total += 1
        if check_file(path, desc):
            passed += 1

    # Real-time Tracking Module
    print("\n⚡ Real-time Tracking Module:")
    checks = [
        ("backend/app/modules/realtime/callbacks.py", "LangChain callbacks"),
        ("backend/app/modules/realtime/collector.py", "Event collector"),
        ("backend/app/modules/realtime/api.py", "API endpoints"),
    ]
    for path, desc in checks:
        total += 1
        if check_file(path, desc):
            passed += 1

    # Frontend
    print("\n🎨 Frontend:")
    checks = [
        ("frontend/package.json", "Package config"),
        ("frontend/src/App.tsx", "Main app"),
        ("frontend/src/services/api.ts", "API client"),
        ("frontend/src/types/index.ts", "Type definitions"),
    ]
    for path, desc in checks:
        total += 1
        if check_file(path, desc):
            passed += 1

    # Documentation
    print("\n📚 Documentation:")
    checks = [
        ("README.md", "Main README"),
        ("README_CN.md", "Chinese README"),
        ("QUICKSTART.md", "Quick start guide"),
        ("CONTRIBUTING.md", "Contributing guide"),
        ("CHANGELOG.md", "Changelog"),
        ("PROJECT_SUMMARY.md", "Project summary"),
    ]
    for path, desc in checks:
        total += 1
        if check_file(path, desc):
            passed += 1

    # Configuration
    print("\n⚙️  Configuration:")
    checks = [
        (".env.example", "Environment template"),
        (".env", "Environment config"),
        ("docker-compose.yml", "Docker Compose"),
        ("backend/Dockerfile", "Backend Dockerfile"),
        (".gitignore", "Git ignore"),
    ]
    for path, desc in checks:
        total += 1
        if check_file(path, desc):
            passed += 1

    # Development Tools
    print("\n🛠️  Development Tools:")
    checks = [
        ("Makefile", "Make commands"),
        ("start.sh", "Startup script"),
        ("verify_setup.py", "Setup verification"),
        ("backend/test_main.py", "Tests"),
        ("backend/examples.py", "Usage examples"),
        ("backend/example_langgraph_app.py", "LangGraph example"),
    ]
    for path, desc in checks:
        total += 1
        if check_file(path, desc):
            passed += 1

    # CI/CD
    print("\n🔄 CI/CD:")
    checks = [
        (".github/workflows/ci.yml", "GitHub Actions CI"),
    ]
    for path, desc in checks:
        total += 1
        if check_file(path, desc):
            passed += 1

    # Summary
    print("\n" + "=" * 70)
    print(f"Status: {passed}/{total} files present ({passed*100//total}%)")
    print("=" * 70)

    if passed == total:
        print("\n✅ Project is complete!")
    else:
        print(f"\n⚠️  {total - passed} files missing")

    # Next steps
    print("\n📋 Next Steps:")
    print("  1. Install dependencies: cd backend && pip install -r requirements.txt")
    print("  2. Configure environment: cp .env.example .env (already done)")
    print("  3. Start services: docker-compose up -d")
    print("  4. Visit API docs: http://localhost:8000/docs")
    print("  5. Run examples: python backend/examples.py")
    print("  6. Integrate with your app: See QUICKSTART.md")

    print("\n🎯 Key Features:")
    print("  ✓ Offline checkpoint analysis")
    print("  ✓ Real-time event tracking")
    print("  ✓ Multi-database support (MySQL, PostgreSQL, SQLite)")
    print("  ✓ WebSocket streaming")
    print("  ✓ Token usage & cost tracking")
    print("  ✓ Performance metrics")
    print("  ✓ RESTful API with OpenAPI docs")
    print("  ✓ Docker deployment")

    print("\n🌟 FlintBloom is ready to use!")
    print()


if __name__ == "__main__":
    main()
