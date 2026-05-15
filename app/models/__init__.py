"""
Camada de dados: compromissos e repositórios de calendário.

Repositórios
------------
UnifiedCalendarRepository
    Fachada usada pela aplicação; tenta Outlook e, em falha, WinRT.
CalendarRepository
    Backend Outlook COM (pywin32).
WindowsCalendarRepository
    Backend app Calendário do Windows (WinRT).
"""

from app.models.appointment import Appointment
from app.models.calendar_repository import CalendarConnectionError, CalendarRepository
from app.models.unified_calendar_repository import UnifiedCalendarRepository
from app.models.windows_calendar_repository import WindowsCalendarRepository

__all__ = [
    "Appointment",
    "CalendarConnectionError",
    "CalendarRepository",
    "UnifiedCalendarRepository",
    "WindowsCalendarRepository",
]
