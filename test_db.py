import sys
import os
from db import test_db_connection, init_db, load_db_config

def main():
    print("========================================")
    print("   SEO Dashboard - MySQL Connection Test")
    print("========================================")
    config = load_db_config()
    print(f"Host:     {config['host']}")
    print(f"Port:     {config['port']}")
    print(f"User:     {config['user']}")
    print(f"Database: {config['database']}")
    print(f"Password: {'*' * len(config['password']) if config['password'] else '[NOT SET]'}")
    print("----------------------------------------")

    if not config['password']:
        print("[ERROR] Database password is not set in db_config.json or DB_PASSWORD env.")
        print("Please update db_config.json with your actual password.")
        sys.exit(1)

    print("Connecting to MySQL...")
    success, message = test_db_connection()
    if not success:
        print(f"[FAIL] Connection Failed: {message}")
        print("\nTroubleshooting tips:")
        print("1. If using Hostinger Remote MySQL, ensure you whitelisted '%' in Hostinger -> Remote MySQL.")
        print("2. Ensure 'host' in db_config.json matches the IP/hostname shown in Hostinger Remote MySQL.")
        print("3. Check that the password is typed correctly.")
        sys.exit(1)

    print(f"[SUCCESS] {message}")
    print("\nInitializing tables...")
    tbl_ok, tbl_msg = init_db()
    if tbl_ok:
        print(f"[SUCCESS] {tbl_msg}")
        print("Tables verified / created:")
        print(" - seo_audit_runs")
        print(" - seo_page_audits")
        print(" - seo_gsc_performance")
        print(" - seo_ga4_metrics")
        print(" - seo_weekly_tracker")
    else:
        print(f"[FAIL] {tbl_msg}")

if __name__ == '__main__':
    main()
