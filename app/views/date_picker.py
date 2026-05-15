from __future__ import annotations

import customtkinter as ctk
from datetime import date, datetime
from tkcalendar import DateEntry

from app.views.main_view import COLORS


class DatePicker(ctk.CTkFrame):
  """Campo de data com calendário popup no formato dd/mm/aaaa."""

  def __init__(
    self,
    master,
    default: date | None = None,
    width: int = 14,
    **kwargs,
  ) -> None:
    super().__init__(master, fg_color="transparent", **kwargs)

    picker_kwargs = dict(
      width=width,
      date_pattern="dd/mm/yyyy",
      background=COLORS["bg"],
      foreground=COLORS["text"],
      borderwidth=1,
      headersbackground=COLORS["accent"],
      headersforeground=COLORS["text"],
      selectbackground=COLORS["accent"],
      selectforeground=COLORS["text"],
      normalbackground=COLORS["bg"],
      normalforeground=COLORS["text"],
      weekendbackground=COLORS["surface_hover"],
      weekendforeground=COLORS["text_muted"],
      othermonthforeground=COLORS["text_muted"],
      othermonthbackground=COLORS["surface"],
      othermonthweforeground=COLORS["text_muted"],
      othermonthwebackground=COLORS["surface"],
      disabledforeground=COLORS["text_muted"],
    )

    try:
      self._picker = DateEntry(self, locale="pt_BR", **picker_kwargs)
    except Exception:
      self._picker = DateEntry(self, **picker_kwargs)

    self._picker.pack(fill="x", ipady=4)

    self.set_date(default or date.today())

  def get_date(self) -> date:
    value = self._picker.get_date()
    if isinstance(value, datetime):
      return value.date()
    return value

  def get(self) -> str:
    return self.get_date().strftime("%d/%m/%Y")

  def set_date(self, value: date) -> None:
    self._picker.set_date(value)
