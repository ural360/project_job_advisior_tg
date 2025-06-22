import sqlite3
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = 'career_bot.db'):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS professions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                skills TEXT,
                interests TEXT,
                experience TEXT,
                salary_range TEXT,
                demand TEXT,
                category TEXT
            )
        ''')
        self.conn.commit()

    def add_user(self, user_id: int, username: Optional[str], 
                first_name: Optional[str], last_name: Optional[str]):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        self.conn.commit()

    def add_profession(self, name: str, description: str, skills: str, 
                      interests: str, experience: str, salary_range: str, 
                      demand: str, category: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO professions 
            (name, description, skills, interests, experience, salary_range, demand, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, skills, interests, experience, salary_range, demand, category))
        self.conn.commit()

    def search_professions(self, skills: List[str], interests: List[str], 
                         experience: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM professions")
        all_profs = [dict(row) for row in cursor.fetchall()]
        
        results = []
        
        for prof in all_profs:
            # Проверка опыта
            if experience and prof["experience"] not in [experience, "Любой"]:
                continue
                
            # Поиск по навыкам (без учета регистра)
            prof_skills = [s.strip().lower() for s in prof["skills"].split(",")]
            skill_score = sum(
                3 if uskill.lower() in prof_skills 
                else 1 if any(uskill.lower() in skill for skill in prof_skills)
                else 0
                for uskill in map(str.strip, skills)
            )
            
            # Поиск по интересам (без учета регистра)
            prof_interests = [i.strip().lower() for i in prof["interests"].split(",")]
            interest_score = sum(
                2 if uint.lower() in prof_interests 
                else 0.5 if any(uint.lower() in interest for interest in prof_interests)
                else 0
                for uint in map(str.strip, interests)
            )
            
            if (total_score := skill_score + interest_score) > 0:
                prof["match_score"] = total_score
                results.append(prof)
        
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:5]

    def get_all_categories(self) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM professions WHERE category IS NOT NULL')
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        self.conn.close()