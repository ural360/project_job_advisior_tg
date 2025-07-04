import sqlite3
from typing import List, Dict
from ai_helper import AIHelper 

class CareerAdvisor:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ai_helper = AIHelper()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS professions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    required_skills TEXT,
                    related_interests TEXT,
                    experience_level TEXT
                )
            ''')
            
            cursor.execute('SELECT COUNT(*) FROM professions')
            if cursor.fetchone()[0] == 0:
                self._add_sample_data(cursor)
            
            conn.commit()

    def _add_sample_data(self, cursor):
        sample_professions = [
            {
                'name': 'Веб-разработчик',
                'description': 'Создание веб-сайтов и приложений',
                'required_skills': 'программирование,html,css,javascript',
                'related_interests': 'технологии,веб-дизайн,it',
                'experience_level': '1-3 года'
            },
            {
                'name': 'Графический дизайнер',
                'description': 'Создание визуального контента',
                'required_skills': 'дизайн,креативность,photoshop',
                'related_interests': 'искусство,графика,творчество',
                'experience_level': 'Менее 1 года'
            },
            {
                'name': 'Аналитик данных',
                'description': 'Анализ и интерпретация данных',
                'required_skills': 'аналитика,математика,excel,sql',
                'related_interests': 'данные,статистика,исследования',
                'experience_level': '1-3 года'
            },
            {
                'name': 'Маркетолог',
                'description': 'Продвижение продуктов и услуг',
                'required_skills': 'коммуникация,аналитика,креативность',
                'related_interests': 'реклама,бизнес,психология',
                'experience_level': 'Более 3 лет'
            },
            {
                'name': 'Младший разработчик Python',
                'description': 'Разработка на Python под руководством',
                'required_skills': 'python,программирование,алгоритмы',
                'related_interests': 'технологии,it,автоматизация',
                'experience_level': 'Нет опыта'
            }
        ]
        
        for prof in sample_professions:
            cursor.execute('''
                INSERT INTO professions (name, description, required_skills, related_interests, experience_level)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                prof['name'],
                prof['description'],
                prof['required_skills'],
                prof['related_interests'],
                prof['experience_level']
            ))

    def get_recommendations(self, skills: List[str], interests: List[str], experience: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM professions 
                WHERE experience_level = ? OR experience_level = 'Любой'
            ''', (experience,))
            
            professions = cursor.fetchall()
            
            professions = [dict(prof) for prof in professions]
            for prof in professions:
                prof['score'] = self._calculate_match_score(prof, skills, interests)
            
            professions.sort(key=lambda x: x['score'], reverse=True)
            
            return professions

    def _calculate_match_score(self, profession: Dict, skills: List[str], interests: List[str]) -> int:
        score = 0
        
        prof_skills = [s.strip().lower() for s in profession['required_skills'].split(',')]
        prof_interests = [i.strip().lower() for i in profession['related_interests'].split(',')]
        user_skills = [s.strip().lower() for s in skills]
        user_interests = [i.strip().lower() for i in interests]
        
        for skill in user_skills:
            if skill in prof_skills:
                score += 2
        
        for interest in user_interests:
            if interest in prof_interests:
                score += 1
        
        return score

    def get_all_professions(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT name, description FROM professions')
            return [dict(prof) for prof in cursor.fetchall()]

    async def get_ai_recommendations(self, skills: List[str], interests: List[str], experience: str) -> str:
        return await self.ai_helper.get_career_recommendations(skills, interests, experience)

    async def evaluate_profession(self, profession: str, skills: List[str], interests: List[str]) -> str:

        return await self.ai_helper.evaluate_profession_fit(profession, skills, interests)

    async def close(self):
        await self.ai_helper.close()