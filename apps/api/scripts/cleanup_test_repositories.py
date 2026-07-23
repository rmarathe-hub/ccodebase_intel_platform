#!/usr/bin/env python3
"""Delete ephemeral local test/fixture repositories.

Usage (from repo root or apps/api):

  PYTHONPATH=apps/api apps/api/.venv/bin/python apps/api/scripts/cleanup_test_repositories.py
  PYTHONPATH=apps/api apps/api/.venv/bin/python apps/api/scripts/cleanup_test_repositories.py --dry-run
"""

from __future__ import annotations

import argparse
import sys

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.entities import Repository
from app.services.import_repository import delete_test_repositories, is_test_repository


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List matching repositories without deleting",
    )
    args = parser.parse_args()

    session = SessionLocal()
    try:
        if args.dry_run:
            repos = list(
                session.scalars(select(Repository).order_by(Repository.created_at.desc())).all()
            )
            matches = [r for r in repos if is_test_repository(r)]
            print(f"Would delete {len(matches)} repositor(ies):")
            for r in matches:
                print(f"  {r.id}  {r.owner_name}/{r.name}")
            return 0
        deleted = delete_test_repositories(session)
        print(f"Deleted {len(deleted)} repositor(ies):")
        for r in deleted:
            print(f"  {r['id']}  {r['owner_name']}/{r['name']}")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
