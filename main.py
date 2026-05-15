"""
Ponto de entrada da aplicação Agenda.

Este arquivo é o primeiro que o Python executa quando você roda o programa.
Ele monta as três camadas do padrão MVC (Model-View-Controller):
  - Model (repositório): lê e grava compromissos no calendário do Windows
  - View (interface): janela gráfica com botões e lista de compromissos
  - Controller: liga os cliques da interface às operações no calendário
"""

# Importa a classe que coordena a lógica entre tela e dados
from app.controllers.calendar_controller import CalendarController
# Importa o repositório unificado (tenta Outlook primeiro, depois WinRT)
from app.models.unified_calendar_repository import UnifiedCalendarRepository
# Importa a janela principal da interface gráfica
from app.views.main_view import MainView


def main() -> None:
    """
    Função principal: cria os objetos e inicia o programa.

    Ordem de execução:
      1. Cria o repositório (acesso ao calendário)
      2. Cria a janela (view)
      3. Cria o controlador, que conecta view ↔ repositório
      4. O controlador conecta ao calendário e carrega compromissos
      5. mainloop() mantém a janela aberta até o usuário fechar
    """
    # Objeto responsável por listar, criar, editar e excluir no calendário
    repository = UnifiedCalendarRepository()
    # Janela com lista, botões Novo/Editar/Excluir e filtro de período
    view = MainView()
    # Controlador recebe repositório e view; registra os handlers dos botões
    controller = CalendarController(repository, view)
    # Conecta ao Outlook ou ao app Calendário e carrega a lista inicial
    controller.start()
    # Loop infinito do Tkinter: processa cliques e redesenha a tela
    view.mainloop()


# Só executa main() quando o arquivo é rodado diretamente (python main.py)
# Se outro arquivo importar main.py, este bloco não roda
if __name__ == "__main__":
    main()
