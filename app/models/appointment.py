from dataclasses import dataclass
from datetime import datetime


@dataclass
class Appointment:
    entry_id: str
    subject: str
    start: datetime
    end: datetime
    location: str = ""
    body: str = ""
    all_day: bool = False

    @property
    def duration_minutes(self) -> int:
        delta = self.end - self.start
        return max(int(delta.total_seconds() // 60), 0)

    @property
    def display_date(self) -> str:
        return self.start.strftime("%d/%m/%Y")

    @property
    def display_time_range(self) -> str:
        if self.all_day:
            return "Dia inteiro"
        return f"{self.start.strftime('%H:%M')} – {self.end.strftime('%H:%M')}"
