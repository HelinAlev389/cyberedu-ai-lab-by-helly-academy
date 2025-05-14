def get_ctf_feedback(username, mission_id, tier, questions, answers, log_data=None):
    feedback = []

    for i, (q, a) in enumerate(zip(questions, answers)):
        fb = f"{i + 1}. Въпрос: {q}\nОтговор: {a}\nАнализ: TODO - AI ще анализира това."
        feedback.append(fb)

    if log_data:
        feedback.append("\n🔍 Допълнителен анализ на лог файл:\n")
        feedback.append(str(log_data))  # в реално приложение - формат и анализ

    return "\n\n".join(feedback)
