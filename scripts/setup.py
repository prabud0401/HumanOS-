#!/usr/bin/env python
"""
HumanOS Setup Script — First-time project bootstrap.

Usage:
    python scripts/setup.py

What it does:
    1. Creates a virtual environment (if not already active)
    2. Copies DNA template files if they don't exist
    3. Installs Python dependencies
    4. Runs Django migrations
    5. Creates a superuser (optional)
    6. Prints next steps
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DNA_DIR = ROOT / "dna"


def run(cmd, **kwargs):
    print(f"  → {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=str(ROOT), **kwargs)
    if result.returncode != 0:
        print(f"  ✗ Command failed (exit {result.returncode})")
    return result.returncode


def main():
    print("=" * 60)
    print("  HumanOS — First-Time Setup")
    print("=" * 60)

    # Step 1: Check virtual environment
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        venv_path = ROOT / ".venv"
        if not venv_path.exists():
            print("\n[1/5] Creating virtual environment...")
            run(f"{sys.executable} -m venv .venv")
            if os.name == "nt":
                pip = str(venv_path / "Scripts" / "pip")
                python = str(venv_path / "Scripts" / "python")
            else:
                pip = str(venv_path / "bin" / "pip")
                python = str(venv_path / "bin" / "python")
            print(f"\n⚠  Virtual environment created at .venv")
            print(f"   Activate it first, then re-run this script:")
            if os.name == "nt":
                print(f"     .venv\\Scripts\\activate")
            else:
                print(f"     source .venv/bin/activate")
            print(f"     python scripts/setup.py")
            return
        else:
            print("\n⚠  Virtual environment exists but is not activated.")
            print("   Activate it first:")
            if os.name == "nt":
                print("     .venv\\Scripts\\activate")
            else:
                print("     source .venv/bin/activate")
            return
    else:
        print("\n[1/5] Virtual environment: active ✓")

    # Step 2: Copy DNA templates
    print("\n[2/5] Setting up DNA configuration...")
    identity_yaml = DNA_DIR / "identity.yaml"
    env_file = DNA_DIR / ".env"

    if not identity_yaml.exists():
        template = DNA_DIR / "identity.example.yaml"
        if template.exists():
            shutil.copy2(template, identity_yaml)
            print(f"  → Copied identity.example.yaml → identity.yaml")
            print(f"  ⚠  Edit dna/identity.yaml with YOUR data")
        else:
            print(f"  ✗ Template not found: {template}")
    else:
        print(f"  → identity.yaml already exists ✓")

    if not env_file.exists():
        template = DNA_DIR / ".env.example"
        if template.exists():
            shutil.copy2(template, env_file)
            print(f"  → Copied .env.example → .env")
            print(f"  ⚠  Edit dna/.env with your API keys and secrets")
        else:
            print(f"  ✗ Template not found: {template}")
    else:
        print(f"  → .env already exists ✓")

    # Step 3: Install dependencies
    print("\n[3/5] Installing Python dependencies...")
    run(f"{sys.executable} -m pip install --upgrade pip")
    run(f"{sys.executable} -m pip install -r requirements.txt")

    # Step 4: Run migrations
    print("\n[4/5] Running database migrations...")
    run(f"{sys.executable} manage.py migrate")

    # Step 5: Create superuser prompt
    print("\n[5/5] Setup complete!")
    print()
    print("=" * 60)
    print("  Next steps:")
    print("=" * 60)
    print()
    print("  1. Start infrastructure:")
    print("       docker-compose up -d")
    print()
    print("  2. Edit your DNA:")
    print("       dna/identity.yaml   — Your identity config")
    print("       dna/.env            — API keys & secrets")
    print()
    print("  3. Create admin user (optional):")
    print("       python manage.py createsuperuser")
    print()
    print("  4. Start HumanOS:")
    print("       python manage.py runserver")
    print()
    print("  5. Open in browser:")
    print("       http://localhost:8000          — Root")
    print("       http://localhost:8000/api/docs — API Documentation")
    print("       http://localhost:8000/admin/   — Django Admin")
    print("       http://localhost:8000/health/  — System Health")
    print()
    print("  6. (Optional) Start async workers:")
    print("       celery -A config worker -l info")
    print("       celery -A config beat -l info")
    print()


if __name__ == "__main__":
    main()
