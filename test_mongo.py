import sys
from mongo_db import test_mongo_connection, init_mongo_indexes, sync_all_local_files_to_mongo, load_mongo_config

def main():
    print("=" * 60)
    print("  GURU PUNVAANII SEO ENGINE - MONGODB ATLAS CONNECTION TEST")
    print("=" * 60)
    
    cfg = load_mongo_config()
    uri = cfg.get('uri', '')
    masked_uri = uri
    if '@' in uri:
        prefix, rest = uri.split('@', 1)
        masked_uri = prefix.split('://')[0] + "://***:***@" + rest
        
    print(f"\n[1] Configuration:")
    print(f"    URI Target: {masked_uri or 'NOT SET'}")
    print(f"    Database  : {cfg.get('database')}")
    
    print("\n[2] Testing MongoDB Atlas Connection...")
    success, msg = test_mongo_connection()
    
    if success:
        print(f"    [+] STATUS: SUCCESSFUL!")
        print(f"    Details  : {msg}")
        
        print("\n[3] Initializing Collections & Indexes...")
        init_mongo_indexes()
        
        print("\n[4] Syncing Local SEO Audit Data to MongoDB Collections...")
        sync_ok, sync_res = sync_all_local_files_to_mongo()
        if sync_ok:
            print(f"    [+] SYNC COMPLETE: {sync_res}")
        else:
            print(f"    [-] Sync error: {sync_res}")
            
        print("\n" + "=" * 60)
        print("MongoDB is fully configured, connected and synced!")
        print("=" * 60)
    else:
        print(f"    [-] STATUS: FAILED TO CONNECT")
        print(f"    Reason   : {msg}")
        print("\n" + "=" * 60)
        print("TO FIX THIS:")
        print("1. Open 'mongo_config.json' and paste your valid connection string in 'uri':")
        print('   "uri": "mongodb+srv://<username>:<password>@cluster0.your-subdomain.mongodb.net/?retryWrites=true&w=majority"')
        print("2. In MongoDB Atlas, make sure your IP is whitelisted (Network Access -> Add IP Address: 0.0.0.0/0).")
        print("3. Run: python test_mongo.py")
        print("=" * 60)

if __name__ == '__main__':
    main()
