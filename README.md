# python-calendario-windows

Aplicativo desktop em Python para gerenciar compromissos (CRUD) integrado ao **Calendário do Windows** via conta Microsoft / Outlook.

## Funcionalidades

- Listar compromissos por período (7, 30, 90 ou 365 dias)
- Criar, editar e excluir compromissos
- Seletor de data com calendário (formato dd/mm/aaaa)
- Interface moderna com CustomTkinter (tema escuro)
- Arquitetura **MVC** (Model · View · Controller)

## Requisitos

- Windows 10/11
- Python 3.11+
- Microsoft Outlook ou conta Microsoft configurada no Calendário do Windows

## Instalação

```powershell
git clone https://github.com/CarlosBaldoino2005/python-calendario-windows.git
cd python-calendario-windows
pip install -r requirements.txt
```

## Uso

```powershell
python main.py
```

Na primeira execução, o Outlook pode solicitar permissão para acessar o calendário.

## Estrutura do projeto

```
python-calendario-windows/
├── main.py                 # Entrada da aplicação (monta MVC e inicia a janela)
├── agenda.spec             # Configuração PyInstaller para gerar Agenda.exe
├── requirements.txt
└── app/
    ├── models/             # Dados e acesso ao calendário (Outlook COM ou WinRT)
    │   ├── appointment.py
    │   ├── calendar_repository.py
    │   ├── windows_calendar_repository.py
    │   └── unified_calendar_repository.py
    ├── views/              # Interface gráfica (CustomTkinter)
    │   ├── main_view.py
    │   ├── appointment_dialog.py
    │   └── date_picker.py
    └── controllers/        # Liga botões da tela às operações no calendário
        └── calendar_controller.py
```

## Código documentado

Todo o código-fonte principal está comentado em português para facilitar o aprendizado:

- **main.py** — ponto de entrada e fluxo MVC
- **models** — modelo `Appointment` e repositórios (Outlook preferencial, WinRT como fallback)
- **views** — janela principal, formulário de compromisso e seletor de data
- **controllers** — conexão, listagem, criar, editar e excluir
- **agenda.spec** — empacotamento do executável Windows

Fluxo resumido: a `MainView` exibe a lista; o `CalendarController` recebe os cliques; o `UnifiedCalendarRepository` grava no Calendário do Windows.

## Tecnologias

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — interface gráfica
- [pywin32](https://github.com/mhammond/pywin32) — integração Outlook COM
- [tkcalendar](https://github.com/j4321/tkcalendar) — seletor de datas
- [winrt](https://pypi.org/project/winrt/) — API nativa do Calendário Windows (fallback)

## Gerar executável (.exe)

Requisito: `pip install pyinstaller`

```powershell
cd python-calendario-windows
python -m PyInstaller agenda.spec --noconfirm
```

Ou execute `build.bat` (duplo clique).

O arquivo será gerado em: **`dist/Agenda.exe`**

> Requer Windows 10/11 e Outlook ou conta Microsoft configurada no Calendário.

## Licença

MIT
