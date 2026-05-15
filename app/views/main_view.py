from __future__ import annotations

import customtkinter as ctk
from datetime import date, timedelta
from typing import Callable

from app.models.appointment import Appointment

COLORS = {
    "bg": "#0f1419",
    "surface": "#1a2332",
    "surface_hover": "#243044",
    "accent": "#3b82f6",
    "accent_hover": "#2563eb",
    "danger": "#ef4444",
    "danger_hover": "#dc2626",
    "text": "#f1f5f9",
    "text_muted": "#94a3b8",
    "border": "#334155",
    "card_selected": "#1e3a5f",
}


class MainView(ctk.CTk):
  def __init__(self) -> None:
    super().__init__()
    self.title("Agenda — Calendário Windows")
    self.geometry("960x640")
    self.minsize(800, 520)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    self.configure(fg_color=COLORS["bg"])

    self._selected_entry_id: str | None = None
    self._appointment_cards: dict[str, ctk.CTkFrame] = {}

    self._on_refresh: Callable[[date, date], None] | None = None
    self._on_create: Callable[[], None] | None = None
    self._on_edit: Callable[[str], None] | None = None
    self._on_delete: Callable[[str], None] | None = None

    self._build_layout()

  def bind_handlers(
    self,
    on_refresh: Callable[[date, date], None],
    on_create: Callable[[], None],
    on_edit: Callable[[str], None],
    on_delete: Callable[[str], None],
  ) -> None:
    self._on_refresh = on_refresh
    self._on_create = on_create
    self._on_edit = on_edit
    self._on_delete = on_delete

  def get_date_range(self) -> tuple[date, date]:
    days = int(self._range_var.get())
    start = date.today()
    return start, start + timedelta(days=days)

  def show_appointments(self, appointments: list[Appointment]) -> None:
    for widget in self._list_frame.winfo_children():
      widget.destroy()
    self._appointment_cards.clear()
    self._selected_entry_id = None
    self._update_action_buttons()

    if not appointments:
      empty = ctk.CTkLabel(
        self._list_frame,
        text="Nenhum compromisso neste período.\nClique em + Novo para criar.",
        font=ctk.CTkFont(size=14),
        text_color=COLORS["text_muted"],
      )
      empty.pack(pady=48)
      self._status_label.configure(text="0 compromissos")
      return

    for appt in appointments:
      self._add_appointment_card(appt)

    self._status_label.configure(
      text=f"{len(appointments)} compromisso(s)"
    )

  def show_error(self, message: str) -> None:
    self._status_label.configure(text=f"Erro: {message}", text_color=COLORS["danger"])

  def show_info(self, message: str) -> None:
    self._status_label.configure(text=message, text_color=COLORS["text_muted"])

  def get_selected_entry_id(self) -> str | None:
    return self._selected_entry_id

  def select_appointment(self, entry_id: str) -> None:
    if entry_id in self._appointment_cards:
      self._select_card(entry_id)

  def _build_layout(self) -> None:
    header = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0, height=64)
    header.pack(fill="x")
    header.pack_propagate(False)

    title = ctk.CTkLabel(
      header,
      text="Agenda",
      font=ctk.CTkFont(size=22, weight="bold"),
      text_color=COLORS["text"],
    )
    title.pack(side="left", padx=24, pady=16)

    subtitle = ctk.CTkLabel(
      header,
      text="Calendário do Windows",
      font=ctk.CTkFont(size=13),
      text_color=COLORS["text_muted"],
    )
    subtitle.pack(side="left", pady=16)

    actions = ctk.CTkFrame(header, fg_color="transparent")
    actions.pack(side="right", padx=16)

    self._btn_new = ctk.CTkButton(
      actions, text="+ Novo", width=100, height=36,
      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
      command=self._handle_create,
    )
    self._btn_new.pack(side="left", padx=4)

    self._btn_edit = ctk.CTkButton(
      actions, text="Editar", width=90, height=36,
      fg_color=COLORS["surface_hover"], hover_color=COLORS["border"],
      command=self._handle_edit, state="disabled",
    )
    self._btn_edit.pack(side="left", padx=4)

    self._btn_delete = ctk.CTkButton(
      actions, text="Excluir", width=90, height=36,
      fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
      command=self._handle_delete, state="disabled",
    )
    self._btn_delete.pack(side="left", padx=4)

    body = ctk.CTkFrame(self, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=20, pady=16)

    sidebar = ctk.CTkFrame(body, fg_color=COLORS["surface"], width=200, corner_radius=12)
    sidebar.pack(side="left", fill="y", padx=(0, 12))
    sidebar.pack_propagate(False)

    ctk.CTkLabel(
      sidebar, text="Período",
      font=ctk.CTkFont(size=13, weight="bold"),
      text_color=COLORS["text"],
    ).pack(anchor="w", padx=16, pady=(16, 8))

    self._range_var = ctk.StringVar(value="30")
    for label, value in [("7 dias", "7"), ("30 dias", "30"), ("90 dias", "90"), ("365 dias", "365")]:
      ctk.CTkRadioButton(
        sidebar, text=label, variable=self._range_var, value=value,
        font=ctk.CTkFont(size=13),
        command=self._handle_refresh,
      ).pack(anchor="w", padx=20, pady=4)

    ctk.CTkButton(
      sidebar, text="Atualizar", height=36,
      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
      command=self._handle_refresh,
    ).pack(fill="x", padx=16, pady=(24, 16))

    list_container = ctk.CTkFrame(body, fg_color=COLORS["surface"], corner_radius=12)
    list_container.pack(side="left", fill="both", expand=True)

    self._list_frame = ctk.CTkScrollableFrame(
      list_container, fg_color="transparent",
      scrollbar_button_color=COLORS["border"],
    )
    self._list_frame.pack(fill="both", expand=True, padx=8, pady=8)

    footer = ctk.CTkFrame(self, fg_color=COLORS["surface"], height=32, corner_radius=0)
    footer.pack(fill="x", side="bottom")
    footer.pack_propagate(False)

    self._status_label = ctk.CTkLabel(
      footer, text="Conectando...",
      font=ctk.CTkFont(size=12),
      text_color=COLORS["text_muted"],
    )
    self._status_label.pack(side="left", padx=16, pady=6)

  def _add_appointment_card(self, appt: Appointment) -> None:
    card = ctk.CTkFrame(
      self._list_frame, fg_color=COLORS["bg"],
      corner_radius=10, border_width=1, border_color=COLORS["border"],
    )
    card.pack(fill="x", pady=6, padx=4)
    self._appointment_cards[appt.entry_id] = card

    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="x", padx=16, pady=12)

    date_badge = ctk.CTkLabel(
      inner,
      text=appt.start.strftime("%d\n%b").upper(),
      font=ctk.CTkFont(size=11, weight="bold"),
      width=44, height=44,
      fg_color=COLORS["accent"],
      corner_radius=8,
    )
    date_badge.pack(side="left")

    info = ctk.CTkFrame(inner, fg_color="transparent")
    info.pack(side="left", fill="x", expand=True, padx=12)

    subject = appt.subject or "(Sem título)"
    title_label = ctk.CTkLabel(
      info, text=subject,
      font=ctk.CTkFont(size=15, weight="bold"),
      text_color=COLORS["text"], anchor="w",
    )
    title_label.pack(fill="x")

    time_text = appt.display_time_range
    if appt.location:
      time_text += f"  ·  {appt.location}"

    detail_label = ctk.CTkLabel(
      info, text=time_text,
      font=ctk.CTkFont(size=12),
      text_color=COLORS["text_muted"], anchor="w",
    )
    detail_label.pack(fill="x")

    self._bind_card_selection(card, appt.entry_id)

  def _bind_card_selection(self, widget: ctk.CTkBaseClass, entry_id: str) -> None:
    """Vincula clique em todo o card (labels não propagam evento ao pai)."""
    def on_select(_event=None) -> None:
      self._select_card(entry_id)

    def on_double_click(_event=None) -> None:
      self._select_card(entry_id)
      self._handle_edit()

    widget.bind("<Button-1>", on_select)
    widget.bind("<Double-Button-1>", on_double_click)
    try:
      widget.configure(cursor="hand2")
    except Exception:
      pass

    for child in widget.winfo_children():
      self._bind_card_selection(child, entry_id)

  def _select_card(self, entry_id: str) -> None:
    self._selected_entry_id = entry_id
    for eid, card in self._appointment_cards.items():
      if eid == entry_id:
        card.configure(fg_color=COLORS["card_selected"], border_color=COLORS["accent"])
      else:
        card.configure(fg_color=COLORS["bg"], border_color=COLORS["border"])
    self._update_action_buttons()

  def _update_action_buttons(self) -> None:
    enabled = self._selected_entry_id is not None
    edit_state = "normal" if enabled else "disabled"
    delete_state = "normal" if enabled else "disabled"
    self._btn_edit.configure(state=edit_state)
    self._btn_delete.configure(state=delete_state)
    if enabled:
      self._status_label.configure(
        text="Compromisso selecionado — Editar ou Excluir",
        text_color=COLORS["text_muted"],
      )

  def _handle_refresh(self) -> None:
    if self._on_refresh:
      start, end = self.get_date_range()
      self._on_refresh(start, end)

  def _handle_create(self) -> None:
    if self._on_create:
      self._on_create()

  def _handle_edit(self) -> None:
    if self._on_edit and self._selected_entry_id:
      self._on_edit(self._selected_entry_id)

  def _handle_delete(self) -> None:
    if self._on_delete and self._selected_entry_id:
      self._on_delete(self._selected_entry_id)
