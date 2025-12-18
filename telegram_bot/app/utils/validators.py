def validate_rating(rating: str) -> bool:
    """Валидация оценки"""
    try:
        rating_num = float(rating)
        return 1 <= rating_num <= 10
    except ValueError:
        return False

def validate_title(title: str) -> bool:
    """Валидация названия"""
    return len(title.strip()) >= 2

def validate_notes(notes: str) -> bool:
    """Валидация заметок"""
    return len(notes.strip()) <= 500