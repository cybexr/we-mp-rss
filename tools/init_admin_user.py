#!/usr/bin/env python3
"""
Admin User Role Initialization Utility

This script ensures the admin user in the database has the correct 'admin' role.
It was created to fix issues introduced by commit 416bb6f (sec-003) which added
RBAC checks without migrating existing admin users' role values.

Usage:
    # Check current admin user role status
    python tools/init_admin_user.py --check

    # Fix admin user role (set to 'admin' if not already)
    python tools/init_admin_user.py --fix

    # Show help
    python tools/init_admin_user.py --help

Background:
    Commit 416bb6f (2026-01-04) added role-based access control to the QR code
    endpoint but did not include a database migration to update existing admin users.
    This caused admin users with role=NULL or empty string to be locked out.

    This utility fixes that by checking and updating the admin user's role.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.models import User
from core.db import Db
from core.print import print_info, print_success, print_warning, print_error


def check_admin_role():
    """Check the current role value for the admin user."""
    db = Db(tag="Admin Role Check")
    session = db.get_session()

    try:
        admin_user = session.query(User).filter(User.username == 'admin').first()

        if not admin_user:
            print_warning("No user with username 'admin' found in database")
            print_info("You may need to create an admin user first")
            return None

        current_role = admin_user.role if admin_user.role else "(NULL)"
        print_info(f"Admin user found:")
        print(f"  Username: {admin_user.username}")
        print(f"  Role: {current_role}")

        if current_role == 'admin':
            print_success("✓ Admin user has correct role='admin'")
            return True
        else:
            print_warning("✗ Admin user role is not set to 'admin'")
            print_info("This may cause permission errors on RBAC-protected endpoints")
            return False

    except Exception as e:
        print_error(f"Error checking admin user: {str(e)}")
        return None
    finally:
        session.close()


def fix_admin_role():
    """Update the admin user's role to 'admin' if needed."""
    db = Db(tag="Admin Role Fix")
    session = db.get_session()

    try:
        admin_user = session.query(User).filter(User.username == 'admin').first()

        if not admin_user:
            print_error("No user with username 'admin' found in database")
            print_info("Cannot fix: admin user does not exist")
            return False

        current_role = admin_user.role if admin_user.role else "(NULL)"

        if admin_user.role == 'admin':
            print_success("✓ Admin user already has role='admin' (no fix needed)")
            return True

        # Update role to 'admin'
        print_info(f"Updating admin user role from '{current_role}' to 'admin'...")
        admin_user.role = 'admin'
        session.commit()

        print_success("✓ Admin user role updated successfully")
        print_info(f"  Username: {admin_user.username}")
        print_info(f"  New role: {admin_user.role}")

        # Clear user cache to ensure changes take effect immediately
        from core.auth import clear_user_cache
        clear_user_cache('admin')
        print_info("✓ Cleared user cache for 'admin'")

        return True

    except Exception as e:
        session.rollback()
        print_error(f"Error updating admin user role: {str(e)}")
        return False
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Admin user role initialization utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Check current admin user role status (no changes made)'
    )

    parser.add_argument(
        '--fix',
        action='store_true',
        help='Update admin user role to "admin" if needed'
    )

    args = parser.parse_args()

    if not any([args.check, args.fix]):
        parser.print_help()
        print_info("\nNo action specified. Use --check or --fix")
        return 1

    if args.check:
        print_info("Checking admin user role...\n")
        result = check_admin_role()
        if result is True:
            return 0
        elif result is False:
            return 1
        else:
            return 2

    if args.fix:
        print_info("Fixing admin user role...\n")
        if fix_admin_role():
            print_success("\n✓ Fix completed successfully")
            return 0
        else:
            print_error("\n✗ Fix failed")
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
