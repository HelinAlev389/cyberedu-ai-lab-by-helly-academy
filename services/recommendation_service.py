from models.ai_memory import AIMemory
from models.lesson import Lesson


def recommend_lessons_for(user_id, max_results=3):
    # Вземи последните 10 взаимодействия
    memories = AIMemory.query.filter_by(user_id=user_id).order_by(AIMemory.created_at.desc()).limit(10).all()

    # Групирай по тема и провери кои са били проблемни (оценка под 60%)
    topic_issues = {}
    for mem in memories:
        if mem.score is not None and mem.score < 60:
            topic_issues[mem.topic] = topic_issues.get(mem.topic, 0) + 1

    if not topic_issues:
        return []

    # Избери най-проблемната тема
    worst_topic = sorted(topic_issues.items(), key=lambda x: x[1], reverse=True)[0][0]

    # Препоръчай уроци по темата
    return Lesson.query.filter_by(topic=worst_topic).order_by(Lesson.created_at.desc()).limit(max_results).all()
