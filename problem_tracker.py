from datetime import datetime

class Problem:
    def __init__(self, title, category, difficulty, status, link, notes=None):
        self.title = title
        self.category = category
        self.difficulty = difficulty
        self.status = status
        self.link = link
        self.notes = notes or []

    def to_dict(self):
        return {
            "title": self.title,
            "category": self.category,
            "difficulty": self.difficulty,
            "status": self.status,
            "link": self.link,
            "notes": self.notes
        }

    def get_time_stats(self):
        from utils.time_parse import parse_time
        times = []
        for note in self.notes:
            t = parse_time(note.get("time_spent", ""))
            if t is not None:
                times.append(t)
        if not times:
            return {"average": None, "shortest": None, "longest": None}
        avg = sum(times) / len(times)
        return {
            "average": round(avg, 2),
            "shortest": min(times),
            "longest": max(times)
        }
