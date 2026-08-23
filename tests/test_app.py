import os
import sqlite3
import tempfile
import unittest

import database as dbmod
from app import app


class AngieAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db = dbmod.DATABASE_PATH
        dbmod.DATABASE_PATH = os.path.join(self.temp_dir.name, 'angie.db')
        dbmod.initialize_database()
        self.client = app.test_client()

    def tearDown(self):
        dbmod.DATABASE_PATH = self.original_db
        self.temp_dir.cleanup()

    def test_signup_login_and_preferences(self):
        signup = self.client.post('/api/signup', json={
            'username': 'tester',
            'email': 'tester@example.com',
            'password': 'secret123',
            'full_name': 'Tester',
        })
        self.assertEqual(signup.status_code, 200)
        self.assertTrue(signup.get_json()['ok'])

        login = self.client.post('/api/login', json={
            'email': 'tester@example.com',
            'password': 'secret123',
        })
        self.assertEqual(login.status_code, 200)
        self.assertTrue(login.get_json()['ok'])

        settings = self.client.post('/api/settings', json={
            'language': 'English',
            'voice': 'female',
            'theme': 'dark',
            'wallpaper': 'sunset',
            'voice_reply': True,
            'daily_quotes': False,
            'scripture': True,
            'notifications': False,
        })
        self.assertEqual(settings.status_code, 200)
        self.assertTrue(settings.get_json()['ok'])

    def test_stale_session_redirects_to_auth(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 999999

        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/auth')

    def test_legacy_database_schema_is_migrated(self):
        conn = sqlite3.connect(dbmod.DATABASE_PATH)
        conn.execute("DROP TABLE users")
        conn.execute("""
            CREATE TABLE users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        user_id = conn.execute(
            "INSERT INTO users(username, email, password_hash) VALUES(?, ?, ?)",
            ("legacy", "legacy@example.com", "hash"),
        ).lastrowid
        conn.commit()
        conn.close()

        dbmod.initialize_database()

        with self.client.session_transaction() as sess:
            sess['user_id'] = user_id

        response = self.client.post('/api/settings', json={
            'language': 'English',
            'voice': 'female',
            'theme': 'dark',
            'wallpaper': 'sunset',
            'voice_reply': True,
            'daily_quotes': False,
            'scripture': True,
            'notifications': False,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['ok'])


if __name__ == '__main__':
    unittest.main()
