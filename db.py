import os
import json
import logging
from datetime import datetime

try:
    import pymysql
    import pymysql.cursors
except ImportError:
    pymysql = None

logger = logging.getLogger('SEO_Database')

# Default DB Configuration (can be overridden by environment variables or db_config.json)
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db_config.json')

def load_db_config():
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'u565670229_seo_dashboard'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'u565670229_seo_dashboard'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'charset': 'utf8mb4'
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logger.warning(f"Could not read db_config.json: {e}")
            
    return config

def get_connection():
    if not pymysql:
        raise RuntimeError("PyMySQL library is not installed. Run: pip install pymysql")
    
    config = load_db_config()
    if not config.get('password'):
        raise ValueError("Database password is not set in db_config.json or DB_PASSWORD env variable.")
        
    return pymysql.connect(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        port=config['port'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
        autocommit=True
    )

def test_db_connection():
    """Tests connection to MySQL and returns (status_bool, message)"""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 AS test")
            result = cursor.fetchone()
        conn.close()
        if result and result.get('test') == 1:
            return True, "Successfully connected to MySQL Database!"
        return False, "Query executed but returned unexpected result."
    except Exception as e:
        return False, str(e)

def init_db():
    """Initializes the required tables in the MySQL database."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Audit Runs Master Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS seo_audit_runs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                run_id VARCHAR(64) UNIQUE NOT NULL,
                started_at DATETIME NOT NULL,
                completed_at DATETIME,
                target_domain VARCHAR(255) NOT NULL,
                total_pages INT DEFAULT 0,
                avg_health_score FLOAT DEFAULT 0,
                critical_issues_count INT DEFAULT 0,
                warning_issues_count INT DEFAULT 0,
                total_words BIGINT DEFAULT 0,
                status VARCHAR(50) DEFAULT 'COMPLETED',
                summary_json LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # 2. Individual Page Audit Metrics
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS seo_page_audits (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                run_id VARCHAR(64) NOT NULL,
                url VARCHAR(1024) NOT NULL,
                status_code INT DEFAULT 200,
                title TEXT,
                description TEXT,
                h1 TEXT,
                word_count INT DEFAULT 0,
                health_score INT DEFAULT 100,
                cwv_score INT DEFAULT 100,
                lcp VARCHAR(32),
                inp VARCHAR(32),
                cls VARCHAR(32),
                ttfb VARCHAR(32),
                fcp VARCHAR(32),
                tbt VARCHAR(32),
                canonical TEXT,
                robots TEXT,
                issues_json LONGTEXT,
                raw_data_json LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_run_id (run_id),
                INDEX idx_url (url(255))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # 3. GSC Search Performance Data
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS seo_gsc_performance (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                site_url VARCHAR(255) NOT NULL,
                fetch_date DATE NOT NULL,
                total_clicks INT DEFAULT 0,
                total_impressions INT DEFAULT 0,
                avg_ctr FLOAT DEFAULT 0,
                avg_position FLOAT DEFAULT 0,
                top_queries_json LONGTEXT,
                top_pages_json LONGTEXT,
                raw_payload LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_site_date (site_url, fetch_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # 4. GA4 Traffic Metrics
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS seo_ga4_metrics (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                property_id VARCHAR(64) NOT NULL,
                report_date DATE NOT NULL,
                active_users INT DEFAULT 0,
                sessions INT DEFAULT 0,
                engagement_rate FLOAT DEFAULT 0,
                screen_page_views INT DEFAULT 0,
                traffic_sources_json LONGTEXT,
                top_pages_json LONGTEXT,
                raw_payload LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_prop_date (property_id, report_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # 5. Weekly Tracker History
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS seo_weekly_tracker (
                id INT AUTO_INCREMENT PRIMARY KEY,
                week_identifier VARCHAR(32) NOT NULL,
                recorded_at DATETIME NOT NULL,
                health_score INT NOT NULL,
                total_pages INT NOT NULL,
                critical_issues INT NOT NULL,
                gsc_clicks INT DEFAULT 0,
                gsc_impressions INT DEFAULT 0,
                ga4_users INT DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_week (week_identifier)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # 6. 30-Day Action Plan Tasks
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS seo_action_tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id VARCHAR(64) UNIQUE NOT NULL,
                title VARCHAR(255) NOT NULL,
                category VARCHAR(64) DEFAULT 'Technical',
                priority VARCHAR(16) DEFAULT 'P1',
                phase VARCHAR(32) DEFAULT 'Week 1',
                assignee VARCHAR(64) DEFAULT 'Web Developer',
                status VARCHAR(32) DEFAULT 'Pending',
                verified TINYINT DEFAULT 0,
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # 7. Schema Studio Configurations
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS seo_schemas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                page_url VARCHAR(1024) NOT NULL,
                schema_type VARCHAR(64) NOT NULL,
                schema_json LONGTEXT NOT NULL,
                status VARCHAR(32) DEFAULT 'ACTIVE',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_schema_url (page_url(255))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # 8. Off-Page Backlinks & Citations
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS seo_backlinks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                target_url VARCHAR(1024) NOT NULL,
                source_url VARCHAR(1024) NOT NULL,
                anchor_text VARCHAR(255),
                domain_authority INT DEFAULT 0,
                status VARCHAR(32) DEFAULT 'ACTIVE',
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

        conn.commit()
        return True, "Database tables initialized successfully!"
    except Exception as e:
        return False, f"Table creation failed: {e}"
    finally:
        conn.close()

def save_audit_to_db(audit_data):
    """Saves a complete audit payload into MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        logger.error(f"Cannot connect to MySQL to save audit: {e}")
        return False, str(e)
        
    try:
        run_id = audit_data.get('audit_id') or datetime.now().strftime('run_%Y%m%d_%H%M%S')
        started_at = audit_data.get('timestamp') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        target_domain = audit_data.get('domain', 'https://gurupunvaanii.com')
        pages = audit_data.get('pages', [])
        summary = audit_data.get('summary', {})

        total_pages = len(pages)
        avg_health = summary.get('avg_health_score', 0)
        critical_issues = summary.get('critical_issues_count', 0)
        warning_issues = summary.get('warning_issues_count', 0)
        total_words = summary.get('total_words', sum(p.get('word_count', 0) for p in pages))

        with conn.cursor() as cursor:
            # Insert audit run summary
            cursor.execute("""
            INSERT INTO seo_audit_runs 
            (run_id, started_at, completed_at, target_domain, total_pages, avg_health_score, critical_issues_count, warning_issues_count, total_words, status, summary_json)
            VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s, 'COMPLETED', %s)
            ON DUPLICATE KEY UPDATE
            completed_at=NOW(), total_pages=VALUES(total_pages), avg_health_score=VALUES(avg_health_score),
            critical_issues_count=VALUES(critical_issues_count), warning_issues_count=VALUES(warning_issues_count),
            total_words=VALUES(total_words), summary_json=VALUES(summary_json)
            """, (
                run_id, started_at, target_domain, total_pages, avg_health,
                critical_issues, warning_issues, total_words, json.dumps(summary)
            ))

            # Insert pages
            for p in pages:
                cwv = p.get('cwv', {})
                cursor.execute("""
                INSERT INTO seo_page_audits
                (run_id, url, status_code, title, description, h1, word_count, health_score, cwv_score, lcp, inp, cls, ttfb, fcp, tbt, canonical, robots, issues_json, raw_data_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    run_id,
                    p.get('url', ''),
                    p.get('status_code', 200),
                    p.get('title', ''),
                    p.get('meta_description', p.get('description', '')),
                    p.get('h1', ''),
                    p.get('word_count', 0),
                    p.get('health_score', 100),
                    cwv.get('score', 100),
                    cwv.get('lcp', ''),
                    cwv.get('inp', ''),
                    cwv.get('cls', ''),
                    cwv.get('ttfb', ''),
                    cwv.get('fcp', ''),
                    cwv.get('tbt', ''),
                    p.get('canonical', ''),
                    p.get('robots', ''),
                    json.dumps(p.get('issues', [])),
                    json.dumps(p)
                ))

        conn.commit()
        return True, f"Saved audit {run_id} ({total_pages} pages) to MySQL."
    except Exception as e:
        logger.error(f"Error saving audit to DB: {e}")
        return False, str(e)
    finally:
        conn.close()

def get_latest_audit_from_db():
    """Fetches the latest audit run and its pages from MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        return None, str(e)

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM seo_audit_runs ORDER BY id DESC LIMIT 1")
            run = cursor.fetchone()
            if not run:
                return None, "No audit runs found in database."
            
            run_id = run['run_id']
            cursor.execute("SELECT * FROM seo_page_audits WHERE run_id = %s ORDER BY id ASC", (run_id,))
            page_rows = cursor.fetchall()

            pages = []
            for r in page_rows:
                if r.get('raw_data_json'):
                    try:
                        pages.append(json.loads(r['raw_data_json']))
                        continue
                    except Exception:
                        pass
                
                # Fallback to reconstructing page object
                pages.append({
                    'url': r['url'],
                    'status_code': r['status_code'],
                    'title': r['title'],
                    'meta_description': r['description'],
                    'h1': r['h1'],
                    'word_count': r['word_count'],
                    'health_score': r['health_score'],
                    'canonical': r['canonical'],
                    'robots': r['robots'],
                    'cwv': {
                        'score': r['cwv_score'],
                        'lcp': r['lcp'],
                        'inp': r['inp'],
                        'cls': r['cls'],
                        'ttfb': r['ttfb'],
                        'fcp': r['fcp'],
                        'tbt': r['tbt']
                    },
                    'issues': json.loads(r['issues_json']) if r['issues_json'] else []
                })

            summary = json.loads(run['summary_json']) if run.get('summary_json') else {
                'total_pages': run['total_pages'],
                'avg_health_score': run['avg_health_score'],
                'critical_issues_count': run['critical_issues_count'],
                'warning_issues_count': run['warning_issues_count'],
                'total_words': run['total_words']
            }

            audit_result = {
                'audit_id': run['run_id'],
                'timestamp': run['started_at'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(run['started_at'], datetime) else str(run['started_at']),
                'domain': run['target_domain'],
                'summary': summary,
                'pages': pages
            }
            return audit_result, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def save_gsc_to_db(gsc_data):
    """Saves GSC performance data to MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        return False, str(e)
    try:
        site_url = gsc_data.get('site_url', 'sc-domain:gurupunvaanii.com')
        totals = gsc_data.get('totals', {})
        today = datetime.now().strftime('%Y-%m-%d')

        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO seo_gsc_performance 
            (site_url, fetch_date, total_clicks, total_impressions, avg_ctr, avg_position, top_queries_json, top_pages_json, raw_payload)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                site_url,
                today,
                totals.get('clicks', 0),
                totals.get('impressions', 0),
                totals.get('ctr', 0.0),
                totals.get('position', 0.0),
                json.dumps(gsc_data.get('top_queries', [])),
                json.dumps(gsc_data.get('top_pages', [])),
                json.dumps(gsc_data)
            ))
        conn.commit()
        return True, "GSC data saved to MySQL."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def save_ga4_to_db(ga4_data):
    """Saves GA4 metrics to MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        return False, str(e)
    try:
        property_id = ga4_data.get('property_id', '534850003')
        totals = ga4_data.get('totals', {})
        today = datetime.now().strftime('%Y-%m-%d')

        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO seo_ga4_metrics 
            (property_id, report_date, active_users, sessions, engagement_rate, screen_page_views, traffic_sources_json, top_pages_json, raw_payload)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                property_id,
                today,
                totals.get('activeUsers', 0),
                totals.get('sessions', 0),
                totals.get('avgEngagementRate', 0.0),
                totals.get('screenPageViews', 0),
                json.dumps(ga4_data.get('channels', [])),
                json.dumps(ga4_data.get('pages', [])),
                json.dumps(ga4_data)
            ))
        conn.commit()
        return True, "GA4 data saved to MySQL."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def save_weekly_report_to_db(weekly_item):
    """Saves or updates a weekly snapshot in MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        return False, str(e)
    try:
        week = weekly_item.get('week', 'Current Week')
        rec_at = weekly_item.get('recorded_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        score = weekly_item.get('score_numeric', 97)
        pages = weekly_item.get('total_pages', 94)
        crit = weekly_item.get('critical_issues', 0)

        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO seo_weekly_tracker 
            (week_identifier, recorded_at, health_score, total_pages, critical_issues, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                week, rec_at, score, pages, crit, json.dumps(weekly_item)
            ))
        conn.commit()
        return True, "Weekly snapshot saved to MySQL."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# ---------------------------------------------------------
# Action Plan Tasks CRUD
# ---------------------------------------------------------
def save_task_to_db(task):
    """Saves or updates a single action plan task in MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        return False, str(e)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO seo_action_tasks
            (task_id, title, category, priority, phase, assignee, status, verified, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            title=VALUES(title), category=VALUES(category), priority=VALUES(priority),
            phase=VALUES(phase), assignee=VALUES(assignee), status=VALUES(status),
            verified=VALUES(verified), notes=VALUES(notes)
            """, (
                task.get('task_id') or task.get('id'),
                task.get('title', 'Untitled Task'),
                task.get('category', 'Technical'),
                task.get('priority', 'P1'),
                task.get('phase', 'Week 1'),
                task.get('assignee', 'Web Developer'),
                task.get('status', 'Pending'),
                1 if task.get('verified') else 0,
                task.get('notes', '')
            ))
        conn.commit()
        return True, "Task updated in MySQL."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_tasks_from_db():
    """Fetches all action tasks from MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        return None, str(e)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM seo_action_tasks ORDER BY priority ASC, id ASC")
            tasks = cursor.fetchall()
            return tasks, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def update_task_status_in_db(task_id, status, verified=None):
    """Quick update for task completion/verification status."""
    try:
        conn = get_connection()
    except Exception as e:
        return False, str(e)
    try:
        with conn.cursor() as cursor:
            if verified is not None:
                cursor.execute("""
                UPDATE seo_action_tasks 
                SET status = %s, verified = %s 
                WHERE task_id = %s
                """, (status, 1 if verified else 0, task_id))
            else:
                cursor.execute("""
                UPDATE seo_action_tasks 
                SET status = %s 
                WHERE task_id = %s
                """, (status, task_id))
        conn.commit()
        return True, f"Task {task_id} status updated to {status}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# ---------------------------------------------------------
# Schema Studio CRUD
# ---------------------------------------------------------
def save_schema_to_db(page_url, schema_type, schema_json):
    """Saves custom JSON-LD schema to MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        return False, str(e)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO seo_schemas (page_url, schema_type, schema_json)
            VALUES (%s, %s, %s)
            """, (page_url, schema_type, schema_json if isinstance(schema_json, str) else json.dumps(schema_json)))
        conn.commit()
        return True, "Schema saved to MySQL."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_schemas_from_db():
    """Fetches custom schemas from MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        return None, str(e)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM seo_schemas ORDER BY id DESC")
            return cursor.fetchall(), None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

# ---------------------------------------------------------
# Off-Page & Backlinks CRUD
# ---------------------------------------------------------
def save_backlink_to_db(target_url, source_url, anchor_text="", da=0, status="ACTIVE", notes=""):
    """Saves backlink/citation to MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        return False, str(e)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO seo_backlinks (target_url, source_url, anchor_text, domain_authority, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (target_url, source_url, anchor_text, da, status, notes))
        conn.commit()
        return True, "Backlink saved to MySQL."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_backlinks_from_db():
    """Fetches all backlinks and citations from MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        return None, str(e)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM seo_backlinks ORDER BY id DESC")
            return cursor.fetchall(), None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

# ---------------------------------------------------------
# Core Web Vitals Real-Time Sync
# ---------------------------------------------------------
def update_page_cwv_in_db(url, cwv_data):
    """Updates real-time Core Web Vitals metrics for a URL in MySQL."""
    try:
        conn = get_connection()
    except Exception as e:
        return False, str(e)
    try:
        m = cwv_data.get('metrics', {})
        perf_score = cwv_data.get('performance_score', 85)
        lcp = m.get('lcp', {}).get('value', '2.4s') if isinstance(m.get('lcp'), dict) else str(m.get('lcp', '2.4s'))
        inp = m.get('inp', {}).get('value', '140ms') if isinstance(m.get('inp'), dict) else str(m.get('inp', '140ms'))
        cls = m.get('cls', {}).get('value', '0.04') if isinstance(m.get('cls'), dict) else str(m.get('cls', '0.04'))
        ttfb = m.get('ttfb', {}).get('value', '135ms') if isinstance(m.get('ttfb'), dict) else str(m.get('ttfb', '135ms'))
        fcp = m.get('fcp', {}).get('value', '1.2s') if isinstance(m.get('fcp'), dict) else str(m.get('fcp', '1.2s'))
        tbt = m.get('tbt', {}).get('value', '110ms') if isinstance(m.get('tbt'), dict) else str(m.get('tbt', '110ms'))

        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE seo_page_audits 
            SET cwv_score = %s, lcp = %s, inp = %s, cls = %s, ttfb = %s, fcp = %s, tbt = %s
            WHERE url = %s OR url LIKE %s
            """, (
                perf_score, lcp, inp, cls, ttfb, fcp, tbt,
                url, f"%{url.replace('https://gurupunvaanii.com', '')}%"
            ))
            
            # Also log a snapshot to weekly tracker
            today_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
            INSERT INTO seo_weekly_tracker 
            (week_identifier, recorded_at, health_score, total_pages, critical_issues, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                'CWV Live Sync', today_str, perf_score, 94, 0,
                f"Real-time CWV update for {url}: LCP {lcp}, INP {inp}, CLS {cls}, TTFB {ttfb}"
            ))
            
        conn.commit()
        return True, f"CWV metrics updated in MySQL for {url}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()



