import os
import sys
import time
import json
import datetime
import subprocess

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def run_step(desc, command):
    print(f"\n[AUTO-SYNC] >> {desc}...")
    t0 = time.time()
    try:
        res = subprocess.run([sys.executable, command], cwd=DIRECTORY, capture_output=True, text=True, timeout=120)
        elapsed = round(time.time() - t0, 2)
        if res.returncode == 0:
            print(f"[AUTO-SYNC] ✅ {desc} completed in {elapsed}s")
            return True, res.stdout
        else:
            print(f"[AUTO-SYNC] ⚠️ {desc} exited with error: {res.stderr[:200]}")
            return False, res.stderr
    except Exception as e:
        print(f"[AUTO-SYNC] ❌ {desc} failed: {e}")
        return False, str(e)

def perform_full_auto_update():
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("=" * 65)
    print(f" 🔄 RUNNING COMPLETE AUTOMATED SEO, TRAFFIC & CWV SYNC ({now_str})")
    print("=" * 65)

    # 1. Fetch Live Google Search Console (GSC) Traffic & Queries
    run_step("Fetching Live GSC Traffic & Queries", "gsc_connector.py")

    # 2. Fetch Live Google Analytics 4 (GA4) Traffic & Channels
    run_step("Fetching Live GA4 Users, Sessions & Channels", "ga4_connector.py")

    # 3. Sync Core Web Vitals & calibrate metrics
    run_step("Calibrating & Verifying Core Web Vitals", "calibrate_and_verify_cwv.py")

    # 4. Sync Weekly Tracker Logs
    run_step("Logging Weekly Performance Tracking Snapshot", "update_cwv_report.py")

    # 5. Generate Latest Master Multi-Sheet Excel Report
    run_step("Generating Master Multi-Sheet Excel Report", "generate_excel_report.py")

    # 6. Sync All Data to MongoDB Atlas
    run_step("Syncing Live SEO Audit Data to MongoDB Atlas", "test_mongo.py")

    print("\n" + "=" * 65)
    print(f" ✅ AUTO-SYNC PIPELINE FINISHED AT {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

if __name__ == '__main__':
    interval_mins = 15
    if len(sys.argv) > 1:
        try:
            interval_mins = int(sys.argv[1])
        except ValueError:
            pass

    print(f"🚀 Starting Antigravity Auto-Sync Daemon (Interval: Every {interval_mins} Minutes)...")
    print("Press Ctrl+C to stop.")

    # Run initial sync immediately
    perform_full_auto_update()

    # Loop forever with sleep interval
    while True:
        try:
            print(f"\nSleeping for {interval_mins} minutes until next auto-sync...")
            time.sleep(interval_mins * 60)
            perform_full_auto_update()
        except KeyboardInterrupt:
            print("\nAuto-Sync Daemon stopped by user.")
            break
        except Exception as e:
            print(f"Error in auto-sync cycle: {e}")
            time.sleep(30)
