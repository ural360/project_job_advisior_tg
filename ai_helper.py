import aiohttp
import logging
from typing import List, Dict, Optional, Tuple
from openai import OpenAI

class AIHelper:
    def __init__(self):
        self.session = None
        self.services = {
            'huggingface': {
                'url': 'https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1',
                'headers': {'Authorization': 'Bearer your_hugging_face_api'},  
                'free': True
            }
        }

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    async def get_ai_response(self, prompt: str) -> Tuple[str, str]:
        """Универсальный метод для запросов к ИИ"""
        for name, config in self.services.items():
            if not config['free']:
                continue
                
            try:
                payload = {
                    "inputs": prompt if name == 'huggingface' else "",
                    "messages": [{"role": "user", "content": prompt}] if name != 'huggingface' else None
                }

                async with self.session.post(
                    config['url'],
                    json=payload if name == 'huggingface' else {"messages": [{"role": "user", "content": prompt}]},
                    headers=config.get('headers', {}),
                    timeout=30
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._parse_response(name, data), name
                    else:
                        error = await resp.text()
                        logging.error(f"Ошибка {name} API: {resp.status} - {error}")
            except Exception as e:
                logging.warning(f"Ошибка подключения к {name}: {str(e)}")
        
        return self._local_fallback(prompt), "local"

    async def get_career_recommendations(self, skills: List[str], interests: List[str], experience: str) -> Tuple[str, str]:
        """Генерация рекомендаций по карьере"""
        prompt = f"""
        Ты карьерный консультант. Сгенерируй 3-5 профессий для человека с:
        - Навыки: {', '.join(skills)}
        - Интересы: {', '.join(interests)}
        - Опыт: {experience}

        Формат для каждой профессии:
        • [Название]: [Краткое описание]
        • Соответствие: [почему подходит]
        • Перспективы: [возможности роста]

        Вывод на русском языке.
        """
        return await self.get_ai_response(prompt)

    async def evaluate_profession_fit(self, profession: str, skills: List[str], interests: List[str]) -> Tuple[str, str]:
        """Оценка соответствия профессии"""
        prompt = f"""
        Оцени от 1 до 10 насколько профессия {profession} подходит человеку с:
        - Навыки: {', '.join(skills)}
        - Интересы: {', '.join(interests)}

        Формат ответа:
        Оценка: X/10
        Обоснование: [анализ соответствия]
        Рекомендации: [что изучить]
        """
        return await self.get_ai_response(prompt)

    def _parse_response(self, service: str, data: dict) -> str:
        try:
            if service == 'deepseek':
                return data['choices'][0]['message']['content']
            elif service == 'huggingface':
                return data[0]['generated_text']
        except (KeyError, IndexError) as e:
            logging.error(f"Ошибка парсинга ответа {service}: {str(e)}")
        return "Не удалось обработать ответ API"

    def _local_fallback(self, prompt: str) -> str:
        professions = ["Разработчик ПО", "Аналитик данных", "Дизайнер UX/UI"]
        return "Локальные рекомендации:\n" + "\n".join(f"- {p}" for p in professions)

    async def close(self):
        if self.session:
            await self.session.close()