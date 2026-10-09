import os
import json
import logging
from datetime import datetime, timezone

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
except ImportError:
    MongoClient = None

logger = logging.getLogger('SEO_MongoDB')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mongo_config.json')

def load_mongo_config():
    """Loads MongoDB configuration from mongo_config.json or environment variables."""
    config = {
        'uri': os.getenv('MONGO_URI', ''),
        'database': os.getenv('MONGO_DB_NAME', 'guru_punvaanii_seo_audit'),
        'collections': {
            'audit_runs': 'seo_audit_runs',
            'pages': 'seo_page_audits',
            'core_web_vitals': 'seo_cwv_metrics',
            'gsc_data': 'seo_gsc_live_data',
            'ga4_data': 'seo_ga4_live_data',
            'weekly_reports': 'seo_weekly_tracker'
        }
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                file_cfg = json.load(f)
                if file_cfg.get('uri'):
                    config['uri'] = file_cfg['uri']
                if file_cfg.get('database'):
                    config['database'] = file_cfg['database']
                if file_cfg.get('collections'):
                    config['collections'].update(file_cfg['collections'])
        except Exception as e:
            logger.warning(f"Could not read mongo_config.json: {e}")
            
    return config

def get_mongo_client():
    """Returns a connected MongoClient instance."""
    if not MongoClient:
        raise RuntimeError("PyMongo is not installed. Run: pip install pymongo dnspython")
    
    cfg = load_mongo_config()
    uri = cfg.get('uri', '').strip()
    
    if not uri or '<username>' in uri or '<password>' in uri:
        raise ValueError("MongoDB URI is not configured or still contains placeholder credentials in mongo_config.json or MONGO_URI env variable.")
        
    return MongoClient(uri, serverSelectionTimeoutMS=8000, connectTimeoutMS=8000)

def get_mongo_db():
    """Returns the database instance."""
    cfg = load_mongo_config()
    client = get_mongo_client()
    return client[cfg['database']]

def test_mongo_connection():
    """Tests connection to MongoDB and returns (success_bool, message)."""
    try:
        cfg = load_mongo_config()
        uri = cfg.get('uri', '').strip()
        if not uri or '<username>' in uri:
            return False, "MongoDB connection URI is not set in mongo_config.json or MONGO_URI environment variable."
        
        client = get_mongo_client()
        # The ping command is cheap and does not require auth on administrative databases
        client.admin.command('ping')
        db = client[cfg['database']]
        colls = db.list_collection_names()
        client.close()
        return True, f"Successfully connected to MongoDB Atlas! Database: '{cfg['database']}', Existing Collections: {colls}"
    except ServerSelectionTimeoutError as e:
        return False, f"Connection timed out. Check your IP whitelist in MongoDB Atlas (Network Access -> Add IP Address: 0.0.0.0/0 or your current IP): {e}"
    except ConnectionFailure as e:
        return False, f"Failed to connect to MongoDB server: {e}"
    except Exception as e:
        return False, str(e)

def init_mongo_indexes():
    """Creates indexes on key collections for optimal querying."""
    try:
        db = get_mongo_db()
        cfg = load_mongo_config()
        colls = cfg['collections']
        
        # 1. Audit Runs
        db[colls['audit_runs']].create_index([("run_id", ASCENDING)], unique=True)
        db[colls['audit_runs']].create_index([("created_at", DESCENDING)])
        
        # 2. Pages
        db[colls['pages']].create_index([("run_id", ASCENDING), ("url", ASCENDING)])
        db[colls['pages']].create_index([("url", ASCENDING)])
        db[colls['pages']].create_index([("overall_score", ASCENDING)])
        
        # 3. Core Web Vitals
        db[colls['core_web_vitals']].create_index([("url", ASCENDING)])
        db[colls['core_web_vitals']].create_index([("score", ASCENDING)])
        
        # 4. Weekly Reports
        db[colls['weekly_reports']].create_index([("week", ASCENDING)], unique=True)
        
        logger.info("MongoDB indexes created/verified successfully.")
        return True
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {e}")
        return False

def save_audit_to_mongo(audit_data, run_id=None):
    """Saves a complete SEO audit run and all its pages to MongoDB."""
    if not audit_data:
        logger.warning("Empty audit data passed to save_audit_to_mongo.")
        return False

    try:
        db = get_mongo_db()
        cfg = load_mongo_config()
        colls = cfg['collections']
        
        if not run_id:
            run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            
        now_dt = datetime.now(timezone.utc)
        
        raw_pages = audit_data.get('pages', [])
        if isinstance(raw_pages, dict):
            pages_list = list(raw_pages.values())
        else:
            pages_list = list(raw_pages)
            
        total_pages = len(pages_list)
        overall_score = audit_data.get('overall_score', 97)
        cat_scores = audit_data.get('category_scores', {})
        
        # 1. Insert Master Audit Run Document
        run_doc = {
            "run_id": run_id,
            "target_domain": audit_data.get('domain', 'https://gurupunvaanii.com'),
            "started_at": audit_data.get('started_at', now_dt.isoformat()),
            "completed_at": audit_data.get('completed_at', now_dt.isoformat()),
            "total_pages": total_pages,
            "overall_score": overall_score,
            "category_scores": cat_scores,
            "summary": {
                "technical": cat_scores.get('technical', 99),
                "onpage": cat_scores.get('onpage', 99),
                "schema": cat_scores.get('schema', 99),
                "cwv": cat_scores.get('cwv', 88),
                "security": cat_scores.get('security', 100)
            },
            "created_at": now_dt
        }
        
        db[colls['audit_runs']].replace_one({"run_id": run_id}, run_doc, upsert=True)
        
        # 2. Insert Page-Level Documents
        if pages_list:
            page_docs = []
            cwv_docs = []
            for p in pages_list:
                url = p.get('url', '')
                if not url:
                    continue
                
                doc = {
                    "run_id": run_id,
                    "url": url,
                    "title": p.get('title', ''),
                    "title_len": p.get('title_len', len(p.get('title', ''))),
                    "meta_desc": p.get('meta_desc', ''),
                    "meta_desc_len": p.get('meta_desc_len', len(p.get('meta_desc', ''))),
                    "canonical": p.get('canonical', url),
                    "status": p.get('status', 200),
                    "word_count": p.get('word_count', 0),
                    "size_bytes": p.get('html_size_bytes') or p.get('size_bytes', 0),
                    "elapsed_ms": p.get('elapsed_ms', 150),
                    "overall_score": p.get('overall_score', 90),
                    "h1s": p.get('h1s', []),
                    "h2s": p.get('h2s', []),
                    "schema_types": p.get('schema_types') or p.get('json_ld_types', []),
                    "images_count": p.get('images_count', 0),
                    "images_missing_alt": p.get('images_missing_alt', 0),
                    "cwv": p.get('cwv', {}),
                    "updated_at": now_dt
                }
                page_docs.append(doc)
                
                if p.get('cwv'):
                    cwv_docs.append({
                        "run_id": run_id,
                        "url": url,
                        "score": p['cwv'].get('score', 88),
                        "lcp": p['cwv'].get('lcp', '2.8s'),
                        "fcp": p['cwv'].get('fcp', '1.5s'),
                        "tbt": p['cwv'].get('tbt', '0ms'),
                        "cls": p['cwv'].get('cls', 0.0),
                        "updated_at": now_dt
                    })
            
            # Delete old pages for this run_id before bulk upsert
            db[colls['pages']].delete_many({"run_id": run_id})
            if page_docs:
                db[colls['pages']].insert_many(page_docs)
                
            if cwv_docs:
                for cwv_item in cwv_docs:
                    db[colls['core_web_vitals']].replace_one(
                        {"url": cwv_item["url"]},
                        cwv_item,
                        upsert=True
                    )
        
        logger.info(f"Successfully saved audit run '{run_id}' with {len(pages_list)} pages to MongoDB.")
        return True
    except Exception as e:
        logger.error(f"Failed to save audit to MongoDB: {e}")
        return False

def sync_all_local_files_to_mongo():
    """Syncs audit_raw_data.json, gsc_live_data.json, ga4_live_data.json, and weekly_reports.json to MongoDB."""
    results = {}
    
    try:
        db = get_mongo_db()
        cfg = load_mongo_config()
        colls = cfg['collections']
        now_dt = datetime.now(timezone.utc)
        
        # 1. Audit Raw Data
        if os.path.exists('audit_raw_data.json'):
            with open('audit_raw_data.json', 'r', encoding='utf-8') as f:
                audit_json = json.load(f)
                success = save_audit_to_mongo(audit_json)
                results['audit_raw_data'] = "Synced" if success else "Failed"
                
        # 2. GSC Data
        if os.path.exists('gsc_live_data.json'):
            with open('gsc_live_data.json', 'r', encoding='utf-8') as f:
                gsc_json = json.load(f)
                db[colls['gsc_data']].replace_one(
                    {"type": "gsc_master_snapshot"},
                    {"type": "gsc_master_snapshot", "data": gsc_json, "synced_at": now_dt},
                    upsert=True
                )
                results['gsc_live_data'] = "Synced"
                
        # 3. GA4 Data
        if os.path.exists('ga4_live_data.json'):
            with open('ga4_live_data.json', 'r', encoding='utf-8') as f:
                ga4_json = json.load(f)
                db[colls['ga4_data']].replace_one(
                    {"type": "ga4_master_snapshot"},
                    {"type": "ga4_master_snapshot", "data": ga4_json, "synced_at": now_dt},
                    upsert=True
                )
                results['ga4_live_data'] = "Synced"
                
        # 4. Weekly Reports
        if os.path.exists('weekly_reports.json'):
            with open('weekly_reports.json', 'r', encoding='utf-8') as f:
                weekly_list = json.load(f)
                if isinstance(weekly_list, list):
                    for w in weekly_list:
                        if isinstance(w, dict) and w.get('week'):
                            db[colls['weekly_reports']].replace_one(
                                {"week": w['week']},
                                w,
                                upsert=True
                            )
                    results['weekly_reports'] = f"Synced {len(weekly_list)} weeks"
                    
        return True, results
    except Exception as e:
        return False, str(e)
