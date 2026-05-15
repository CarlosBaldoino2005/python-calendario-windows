"""
Componente de seleção de data com calendário popup.

Encapsula o DateEntry do tkcalendar com cores alinhadas ao tema da aplicação.
"""

from __future__ import annotations

import customtkinter as ctk
from datetime import date, datetime
from tkcalendar import DateEntry  # Widget de calendário para Tkinter

from app.views.main_view import COLORS  # Paleta de cores compartilhada


class DatePicker(ctk.CTkFrame):
    """
    Campo de data com calendário popup no formato dd/mm/aaaa.

    Herda CTkFrame para encaixar no layout CustomTkinter do formulário.
    """

    def __init__(
        self,
        master,
        default: date | None = None,
        width: int = 14,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        # Opções visuais do calendário (cores do tema escuro)
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
            # Tenta português do Brasil para nomes de meses/dias
            self._picker = DateEntry(self, locale="pt_BR", **picker_kwargs)
        except Exception:
            self._picker = DateEntry(self, **picker_kwargs)

        self._picker.pack(fill="x", ipady=4)

        self.set_date(default or date.today())

    def get_date(self) -> date:
        """Retorna a data selecionada como objeto date (sem hora)."""
        value = self._picker.get_date()
        if isinstance(value, datetime):
            return value.date()
        return value

    def get(self) -> str:
        """Retorna a data como texto dd/mm/aaaa."""
        return self.get_date().strftime("%d/%m/%Y")

    def set_date(self, value: date) -> None:
        """Define a data exibida no campo."""
        self._picker.set_date(value)
