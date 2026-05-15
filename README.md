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
git clone https://github.com/SEU_USUARIO/python-calendario-windows.git
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
├── main.py                 # Entrada da aplicação
├── requirements.txt
└── app/
    ├── models/             # Appointment, repositórios de calendário
    ├── views/              # Interface (CustomTkinter)
    └── controllers/        # Lógica de negócio
```

## Tecnologias

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — interface gráfica
- [pywin32](https://github.com/mhammond/pywin32) — integração Outlook COM
- [tkcalendar](https://github.com/j4321/tkcalendar) — seletor de datas
- [winrt](https://pypi.org/project/winrt/) — API nativa do Calendário Windows (fallback)

## Licença

MIT
