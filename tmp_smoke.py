import os
import database as dbmod
from app import app

os.environ['SECRET_KEY'] = 'test-secret'
# point at a temporary database
new_db = dbmod.DATA_DIR / 'tmp_test.db'
if new_db.exists():
    new_db.unlink()
dbmod.DATABASE_PATH = new_db
dbmod.initialize_database()

client = app.test_client()
for name, path, payload in [
    ('root', '/', None),
    ('auth', '/auth', None),
    ('signup', '/api/signup', {'username':'tester','email':'tester@example.com','password':'secret123','full_name':'Tester'}),
    ('login', '/api/login', {'email':'tester@example.com','password':'secret123'}),
    ('journal', '/api/journal', {'entry':'hello world'}),
    ('mood', '/api/mood', {'mood':'happy'}),
    ('settings', '/api/settings', {'language':'English','voice':'female','theme':'dark','wallpaper':'sunset','voice_reply':True,'daily_quotes':False,'scripture':True,'notifications':False}),
]:
    if payload is None:
        resp = client.get(path)
    else:
        resp = client.post(path, json=payload)
    print(name, resp.status_code, resp.get_json())
