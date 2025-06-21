import aiohttp
import logging
from typing import List, Tuple
from config import HF_TOKEN

class AIHelper:
    def __init__(self):
        self.session = None
        self.hf_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    async def ensure_session(self):
        
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            logging.info("Сессия aiohttp создана")

    async def get_hf_response(self, prompt: str) -> str:
        
        await self.ensure_session()
        
        try:
            async with self.session.post(
                self.hf_url,
                json={"inputs": prompt},
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                
                if resp.status == 200:
                    data = await resp.json()
                    return data[0]['generated_text']
                
                error = await resp.text()
                logging.error(f"HF API error: {resp.status} - {error}")
                return f"Ошибка API: {error}"
                
        except Exception as e:
            logging.error(f"Connection error: {str(e)}", exc_info=True)
            return "Ошибка подключения к сервису"

    async def get_career_recommendations(self, skills: List[str], interests: List[str], experience: str) -> str:
        """Генерация рекомендаций по карьере"""
        prompt = f"""
        [INST]Ты карьерный консультант. Сгенерируй 3-5 профессий для человека с:
        - Навыки: {', '.join(skills)}
        - Интересы: {', '.join(interests)}
        - Опыт: {experience}

        Формат для каждой профессии:
        • Название: Краткое описание
        • Соответствие: почему подходит
        • Перспективы: возможности роста
        • Что изучить: ключевые навыки

        Вывод на русском языке.[/INST]
        """
        return await self.get_hf_response(prompt)

    async def evaluate_profession_fit(self, profession: str, skills: List[str], interests: List[str]) -> str:
        
        prompt = f"""
        [INST]Оцени от 1 до 10 насколько профессия {profession} подходит человеку с:
        - Навыки: {', '.join(skills)}
        - Интересы: {', '.join(interests)}

        Формат ответа:
        Оценка: X/10
        Обоснование: анализ соответствия
        Рекомендации: что изучить
        Перспективы: возможности роста[/INST]
        """
        return await self.get_hf_response(prompt)

    async def close(self):
        
        if self.session and not self.session.closed:
            await self.session.close()
            logging.info("Сессия aiohttp закрыта")