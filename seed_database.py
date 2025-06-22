from database import Database

def seed_professions():
    db = Database()
    
    professions = [
        {
            "name": "Python-разработчик",
            "description": "Разработка приложений на Python",
            "skills": "Python, Django, Flask, SQL, Алгоритмы",
            "interests": "Программирование, IT, Веб-разработка",
            "experience": "1-3 года",
            "salary_range": "120000-250000 руб.",
            "demand": "Высокая",
            "category": "IT"
        },
        {
            "name": "Веб-дизайнер",
            "description": "Создание дизайна сайтов и интерфейсов",
            "skills": "Photoshop, Figma, UI/UX, HTML/CSS",
            "interests": "Дизайн, Креатив, Визуальное искусство",
            "experience": "Нет опыта",
            "salary_range": "60000-150000 руб.",
            "demand": "Средняя",
            "category": "Дизайн"
        },
        {
            "name": "Маркетолог",
            "description": "Продвижение продуктов и услуг",
            "skills": "SMM, Копирайтинг, Аналитика",
            "interests": "Маркетинг, Психология, Бизнес",
            "experience": "1-3 года",
            "salary_range": "80000-180000 руб.",
            "demand": "Высокая",
            "category": "Маркетинг"
        }
    ]

    
    
    for p in professions:
        db.add_profession(
            name=p['name'],
            description=p['description'],
            skills=p['skills'],
            interests=p['interests'],
            experience=p['experience'],
            salary_range=p['salary_range'],
            demand=p['demand'],
            category=p['category']
        )
    
    db.close()
    print(f"Добавлено {len(professions)} профессий")

if __name__ == "__main__":
    seed_professions()