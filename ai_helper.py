from database import Database
from typing import List
import sqlite3 
class AIHelper:
    def __init__(self):
        self.db = Database()

    async def get_recommendations(self, skills: List[str], interests: List[str], 
                                experience: str) -> str:
        try:
            professions = self.db.search_professions(
                skills=[s.strip() for s in skills if s.strip()],
                interests=[i.strip() for i in interests if i.strip()],
                experience=experience
            )

            if not professions:
                return self._get_fallback_recommendations()
            
            response = "🏆 Топ рекомендованных профессий:\n\n"
            for prof in professions:
                response += (
                    f"• <b>{prof['name']}</b> ({prof.get('category', 'Разное')})\n"
                    f"   {prof['description']}\n"
                    f"   💰 Зарплата: {prof['salary_range']}\n"
                    f"   🔥 Востребованность: {prof['demand']}\n"
                    f"   🛠 Навыки: {prof['skills']}\n"
                    f"   ⭐ Совпадение: {prof['match_score']:.1f}/10.0\n\n"
                )
            return response
            
        except Exception as e:
            print(f"Ошибка: {e}")
            return self._get_fallback_recommendations()

    def _get_fallback_recommendations(self) -> str:
        cursor = self.db.conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute('SELECT * FROM professions ORDER BY RANDOM() LIMIT 3')
        profs = [dict(row) for row in cursor.fetchall()]
        
        response = "🔍 Попробуйте эти профессии:\n\n"
        for prof in profs:
            response += (
                f"• <b>{prof['name']}</b> ({prof.get('category', 'Разное')})\n"
                f"   {prof['description']}\n"
                f"   💰 Зарплата: {prof['salary_range']}\n\n"
            )
        return response

    async def get_categories(self) -> List[str]:
        return self.db.get_all_categories()

    async def close(self):
        self.db.close()