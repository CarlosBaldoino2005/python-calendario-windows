"""Ponto de entrada — Agenda Windows (MVC)."""

from app.controllers.calendar_controller import CalendarController
from app.models.unified_calendar_repository import UnifiedCalendarRepository
from app.views.main_view import MainView


def main() -> None:
  repository = UnifiedCalendarRepository()
  view = MainView()
  controller = CalendarController(repository, view)
  controller.start()
  view.mainloop()


if __name__ == "__main__":
  main()
