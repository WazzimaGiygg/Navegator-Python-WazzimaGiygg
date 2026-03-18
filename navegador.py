import sys
import os
import tempfile
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import *
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from PyQt5.QtNetwork import QNetworkProxy, QNetworkProxyFactory

class NetworkProxyFactory(QNetworkProxyFactory):
    """Factory para configurar proxies de rede"""
    def __init__(self):
        super().__init__()
    
    def queryProxy(self, query):
        return [QNetworkProxy(QNetworkProxy.DefaultProxy)]

class AuthDialog(QDialog):
    """Diálogo personalizado para autenticação"""
    def __init__(self, url, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Autenticação Necessária")
        self.setModal(True)
        self.setGeometry(300, 300, 400, 200)
        
        layout = QVBoxLayout()
        
        info_label = QLabel(f"O site <b>{url.host()}</b> requer autenticação:")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Digite seu usuário")
        form_layout.addRow("Usuário:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Digite sua senha")
        form_layout.addRow("Senha:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        layout.addSpacing(20)
        
        botoes_layout = QHBoxLayout()
        
        btn_login = QPushButton("Login")
        btn_login.clicked.connect(self.accept)
        btn_login.setDefault(True)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        botoes_layout.addWidget(btn_login)
        botoes_layout.addWidget(btn_cancelar)
        
        layout.addLayout(botoes_layout)
        
        self.setLayout(layout)
    
    def get_credentials(self):
        return self.username_edit.text(), self.password_edit.text()

class CustomWebEnginePage(QWebEnginePage):
    """Página web personalizada com suporte a autenticação e diagnóstico"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.createWindow = self.handle_create_window
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """Capturar mensagens do console JavaScript"""
        if "ChunkLoadError" in message or "SyntaxError" in message:
            erro_msg = f"JS Error: {message} (linha {lineNumber})"
            print(f"🔴 {erro_msg}")
            
            # Mostrar no console se disponível
            if self.parent_window and hasattr(self.parent_window, 'log_diagnostico'):
                self.parent_window.log_diagnostico(erro_msg, "ERRO")
    
    def authenticationRequired(self, request_url, auth_challenge):
        """Handler para requisições de autenticação"""
        dialog = AuthDialog(request_url, self.parent_window)
        
        if dialog.exec_() == QDialog.Accepted:
            username, password = dialog.get_credentials()
            auth_challenge.setUser(username)
            auth_challenge.setPassword(password)
            return True
        return False
    
    def certificateError(self, error):
        """Lidar com erros de certificado SSL"""
        print(f"⚠️ Erro de certificado: {error.description()}")
        return True
    
    def handle_create_window(self, window_type):
        """Handle para criação de novas janelas"""
        if self.parent_window and hasattr(self.parent_window, 'adicionar_nova_aba'):
            nova_pagina = CustomWebEnginePage(self.parent_window)
            nova_pagina.parent_window = self.parent_window
            self.parent_window.adicionar_nova_aba(QUrl(), nova_pagina)
            return nova_pagina
        return None

class NavegadorAbas(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuração da janela principal
        self.setWindowTitle("Navegador WazzimaGiygg - Modo Diagnóstico")
        self.setGeometry(100, 100, 1200, 800)
        
        # URLs
        self.url_home = "https://wazzimagiygg.wikidot.com"
        self.github_url = "https://github.com/WazzimaGiygg/Navegator-Python-WazzimaGiygg"
        
        # Lista de favoritos
        self.favoritos = [self.url_home]
        
        # Configurar proxy
        QNetworkProxyFactory.setApplicationProxyFactory(NetworkProxyFactory())
        
        # CRIAR CONSOLE PRIMEIRO (antes da barra de ferramentas)
        self.criar_console_diagnostico()
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        
        # Barra de ferramentas (agora o console_dock já existe)
        self.criar_barra_ferramentas()
        
        # Barra de abas
        self.aba_widget = QTabWidget()
        self.aba_widget.setTabsClosable(True)
        self.aba_widget.tabCloseRequested.connect(self.fechar_aba)
        self.aba_widget.currentChanged.connect(self.aba_mudou)
        layout_principal.addWidget(self.aba_widget)
        
        # Barra de status
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Pronto - Modo Diagnóstico Ativo")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(100)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Atalhos de teclado
        self.criar_atalhos()
        
        # Menu
        self.criar_menu()
        
        # Configurar perfil
        self.setup_profile()
        
        # Adicionar primeira aba
        self.adicionar_nova_aba(QUrl(self.url_home))
    
    def criar_console_diagnostico(self):
        """Criar um dock widget para mostrar mensagens de diagnóstico"""
        self.console_dock = QDockWidget("Console de Diagnóstico", self)
        self.console_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setMaximumHeight(150)
        self.console_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        
        self.console_dock.setWidget(self.console_text)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)
        
        # Inicialmente escondido
        self.console_dock.hide()
    
    def log_diagnostico(self, mensagem, tipo="INFO"):
        """Adicionar mensagem ao console de diagnóstico"""
        cores = {
            "INFO": "#00ff00",
            "ERRO": "#ff5555",
            "AVISO": "#ffff55",
            "SUCESSO": "#55ff55"
        }
        cor = cores.get(tipo, "#ffffff")
        timestamp = time.strftime("%H:%M:%S")
        
        html = f'<span style="color: #888888;">[{timestamp}]</span> <span style="color: {cor};">{tipo}:</span> {mensagem}<br>'
        self.console_text.insertHtml(html)
        
        # Rolar para o final
        scrollbar = self.console_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def criar_barra_ferramentas(self):
        """Criar barra de ferramentas com opções de diagnóstico"""
        barra = self.addToolBar("Ferramentas")
        barra.setMovable(False)
        barra.setIconSize(QSize(20, 20))
        
        # Botões de navegação
        btn_voltar = QAction("←", self)
        btn_voltar.setToolTip("Voltar")
        btn_voltar.triggered.connect(self.voltar_aba_atual)
        barra.addAction(btn_voltar)
        
        btn_avancar = QAction("→", self)
        btn_avancar.setToolTip("Avançar")
        btn_avancar.triggered.connect(self.avancar_aba_atual)
        barra.addAction(btn_avancar)
        
        btn_recarregar = QAction("↻", self)
        btn_recarregar.setToolTip("Recarregar (F5)")
        btn_recarregar.triggered.connect(self.recarregar_aba_atual)
        barra.addAction(btn_recarregar)
        
        btn_home = QAction("🏠", self)
        btn_home.setToolTip("Página Inicial")
        btn_home.triggered.connect(self.ir_para_home_aba_atual)
        barra.addAction(btn_home)
        
        # Barra de endereço
        self.barra_endereco = QLineEdit()
        self.barra_endereco.setPlaceholderText("Digite uma URL...")
        self.barra_endereco.returnPressed.connect(self.navegar_para_url_aba_atual)
        barra.addWidget(self.barra_endereco)
        
        # Botões de ação
        btn_nova_aba = QAction("+", self)
        btn_nova_aba.setToolTip("Nova Aba (Ctrl+T)")
        btn_nova_aba.triggered.connect(self.adicionar_nova_aba)
        barra.addAction(btn_nova_aba)
        
        btn_favorito = QAction("★", self)
        btn_favorito.setToolTip("Adicionar favorito (Ctrl+D)")
        btn_favorito.triggered.connect(self.adicionar_favorito_aba_atual)
        barra.addAction(btn_favorito)
        
        btn_github = QAction("🐙 GitHub", self)
        btn_github.setToolTip("Abrir GitHub (Ctrl+G)")
        btn_github.triggered.connect(self.abrir_github)
        barra.addAction(btn_github)
        
        # Botão para mostrar/esconder console
        btn_console = QAction("📟 Console", self)
        btn_console.setToolTip("Mostrar/Esconder console (Ctrl+`)")
        btn_console.setCheckable(True)
        btn_console.triggered.connect(self.console_dock.setVisible)
        barra.addAction(btn_console)
    
    def abrir_github(self):
        """Abrir GitHub com tratamento especial"""
        self.log_diagnostico(f"Abrindo GitHub: {self.github_url}", "INFO")
        
        # Tentar com User-Agent específico para o GitHub
        user_agent_github = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.profile.setHttpUserAgent(user_agent_github)
        
        self.adicionar_nova_aba(QUrl(self.github_url))
        self.status_bar.showMessage(f"Abrindo GitHub: {self.github_url}", 3000)
    
    def setup_profile(self):
        """Configurar perfil com melhorias para compatibilidade"""
        self.profile = QWebEngineProfile.defaultProfile()
        
        # Cache em disco
        cache_path = os.path.join(tempfile.gettempdir(), "wazzima_navegador_cache")
        os.makedirs(cache_path, exist_ok=True)
        self.profile.setCachePath(cache_path)
        self.profile.setPersistentStoragePath(cache_path)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        
        self.log_diagnostico(f"Cache configurado: {cache_path}", "INFO")
        
        # Configurações avançadas
        settings = self.profile.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
        
        # User-Agent padrão
        self.profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        self.log_diagnostico("Perfil configurado com sucesso", "SUCESSO")
    
    def criar_atalhos(self):
        """Criar atalhos de teclado"""
        atalho_nova_aba = QShortcut(QKeySequence("Ctrl+T"), self)
        atalho_nova_aba.activated.connect(self.adicionar_nova_aba)
        
        atalho_fechar_aba = QShortcut(QKeySequence("Ctrl+W"), self)
        atalho_fechar_aba.activated.connect(self.fechar_aba_atual)
        
        atalho_recarregar_forcado = QShortcut(QKeySequence("Ctrl+Shift+R"), self)
        atalho_recarregar_forcado.activated.connect(self.recarregar_forcado_aba_atual)
        
        atalho_github = QShortcut(QKeySequence("Ctrl+G"), self)
        atalho_github.activated.connect(self.abrir_github)
        
        atalho_console = QShortcut(QKeySequence("Ctrl+`"), self)
        atalho_console.activated.connect(lambda: self.console_dock.setVisible(not self.console_dock.isVisible()))
    
    def recarregar_forcado_aba_atual(self):
        """Recarregar ignorando cache"""
        navegador = self.obter_aba_atual()
        if navegador:
            self.log_diagnostico("Recarregando página sem cache", "AVISO")
            navegador.page().profile().clearHttpCache()
            navegador.reload()
            self.status_bar.showMessage("Recarregado (sem cache)", 2000)
    
    def criar_menu(self):
        """Criar menu da aplicação"""
        menubar = self.menuBar()
        
        # Menu Arquivo
        menu_arquivo = menubar.addMenu("Arquivo")
        
        nova_aba = QAction("Nova Aba", self)
        nova_aba.setShortcut("Ctrl+T")
        nova_aba.triggered.connect(self.adicionar_nova_aba)
        menu_arquivo.addAction(nova_aba)
        
        fechar_aba = QAction("Fechar Aba", self)
        fechar_aba.setShortcut("Ctrl+W")
        fechar_aba.triggered.connect(self.fechar_aba_atual)
        menu_arquivo.addAction(fechar_aba)
        
        menu_arquivo.addSeparator()
        
        sair = QAction("Sair", self)
        sair.triggered.connect(self.close)
        menu_arquivo.addAction(sair)
        
        # Menu Diagnóstico
        menu_diagnostico = menubar.addMenu("Diagnóstico")
        
        ver_console = QAction("Mostrar Console", self)
        ver_console.setShortcut("Ctrl+`")
        ver_console.triggered.connect(lambda: self.console_dock.setVisible(True))
        menu_diagnostico.addAction(ver_console)
        
        limpar_console = QAction("Limpar Console", self)
        limpar_console.triggered.connect(self.console_text.clear)
        menu_diagnostico.addAction(limpar_console)
        
        menu_diagnostico.addSeparator()
        
        limpar_cache = QAction("Limpar Cache e Cookies", self)
        limpar_cache.triggered.connect(self.limpar_dados)
        menu_diagnostico.addAction(limpar_cache)
        
        # Menu Ajuda
        menu_ajuda = menubar.addMenu("Ajuda")
        
        sobre = QAction("Sobre", self)
        sobre.triggered.connect(self.mostrar_sobre)
        menu_ajuda.addAction(sobre)
    
    def obter_aba_atual(self):
        """Retorna o navegador da aba atual"""
        if self.aba_widget.count() > 0:
            return self.aba_widget.currentWidget()
        return None
    
    def adicionar_nova_aba(self, url=None):
        """Adicionar nova aba"""
        nova_pagina = CustomWebEnginePage(self)
        nova_pagina.parent_window = self
        
        novo_navegador = QWebEngineView()
        novo_navegador.setPage(nova_pagina)
        
        if url and not url.isEmpty():
            novo_navegador.setUrl(url)
        else:
            novo_navegador.setUrl(QUrl(self.url_home))
        
        # Conectar sinais
        novo_navegador.urlChanged.connect(self.atualizar_url_aba_atual)
        novo_navegador.loadStarted.connect(self.on_load_started)
        novo_navegador.loadProgress.connect(self.on_load_progress)
        novo_navegador.loadFinished.connect(self.on_load_finished)
        novo_navegador.titleChanged.connect(self.atualizar_titulo_aba)
        novo_navegador.iconChanged.connect(self.atualizar_icone_aba)
        
        index = self.aba_widget.addTab(novo_navegador, "Nova Aba")
        self.aba_widget.setCurrentIndex(index)
        
        return novo_navegador
    
    def on_load_started(self):
        """Quando o carregamento começa"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Carregando...")
        self.log_diagnostico("Iniciando carregamento da página", "INFO")
    
    def on_load_progress(self, progress):
        """Atualizar progresso"""
        self.progress_bar.setValue(progress)
    
    def on_load_finished(self, ok):
        """Quando o carregamento termina"""
        self.progress_bar.setVisible(False)
        if ok:
            self.status_bar.showMessage("Página carregada", 2000)
            self.log_diagnostico("Página carregada com sucesso", "SUCESSO")
        else:
            self.status_bar.showMessage("Erro ao carregar página", 2000)
            self.log_diagnostico("Falha no carregamento da página", "ERRO")
    
    def fechar_aba(self, index):
        """Fechar aba"""
        if self.aba_widget.count() > 1:
            self.aba_widget.removeTab(index)
        else:
            navegador = self.obter_aba_atual()
            if navegador:
                navegador.setUrl(QUrl(self.url_home))
    
    def fechar_aba_atual(self):
        """Fechar aba atual"""
        if self.aba_widget.count() > 0:
            self.fechar_aba(self.aba_widget.currentIndex())
    
    def voltar_aba_atual(self):
        """Voltar"""
        navegador = self.obter_aba_atual()
        if navegador:
            navegador.back()
    
    def avancar_aba_atual(self):
        """Avançar"""
        navegador = self.obter_aba_atual()
        if navegador:
            navegador.forward()
    
    def recarregar_aba_atual(self):
        """Recarregar"""
        navegador = self.obter_aba_atual()
        if navegador:
            navegador.reload()
            self.log_diagnostico("Recarregando página", "INFO")
    
    def ir_para_home_aba_atual(self):
        """Ir para home"""
        navegador = self.obter_aba_atual()
        if navegador:
            navegador.setUrl(QUrl(self.url_home))
    
    def navegar_para_url_aba_atual(self):
        """Navegar para URL"""
        url = self.barra_endereco.text()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        navegador = self.obter_aba_atual()
        if navegador:
            self.log_diagnostico(f"Navegando para: {url}", "INFO")
            navegador.setUrl(QUrl(url))
    
    def atualizar_url_aba_atual(self, url):
        """Atualizar barra de endereço"""
        if self.sender() == self.obter_aba_atual():
            self.barra_endereco.setText(url.toString())
    
    def aba_mudou(self, index):
        """Quando a aba muda"""
        navegador = self.aba_widget.widget(index)
        if navegador:
            url = navegador.url().toString()
            self.barra_endereco.setText(url)
    
    def atualizar_titulo_aba(self, titulo):
        """Atualizar título da aba"""
        navegador = self.sender()
        index = self.aba_widget.indexOf(navegador)
        if index >= 0 and titulo:
            titulo_curto = titulo[:30] + "..." if len(titulo) > 30 else titulo
            self.aba_widget.setTabText(index, titulo_curto)
            self.aba_widget.setTabToolTip(index, titulo)
    
    def atualizar_icone_aba(self, icone):
        """Atualizar ícone da aba"""
        navegador = self.sender()
        index = self.aba_widget.indexOf(navegador)
        if index >= 0 and not icone.isNull():
            self.aba_widget.setTabIcon(index, icone)
    
    def adicionar_favorito_aba_atual(self):
        """Adicionar favorito"""
        navegador = self.obter_aba_atual()
        if navegador:
            url_atual = navegador.url().toString()
            titulo = navegador.page().title()
            
            if url_atual not in self.favoritos:
                self.favoritos.append(url_atual)
                self.log_diagnostico(f"Favorito adicionado: {titulo}", "SUCESSO")
                QMessageBox.information(self, "Favorito", "Página adicionada aos favoritos!")
            else:
                QMessageBox.information(self, "Aviso", "Esta página já está nos favoritos!")
    
    def limpar_dados(self):
        """Limpar cache e cookies"""
        reply = QMessageBox.question(self, "Limpar Dados", 
                                    "Deseja limpar todo o cache e cookies?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.profile.cookieStore().deleteAllCookies()
            self.profile.clearHttpCache()
            self.log_diagnostico("Cache e cookies limpos", "SUCESSO")
            QMessageBox.information(self, "Dados Limpos", "Cache e cookies foram limpos!")
    
    def mostrar_sobre(self):
        """Sobre"""
        QMessageBox.about(self, "Sobre o Navegador",
                         "Navegador Python com PyQt5\n"
                         "Versão 2.5 - Modo Diagnóstico\n\n"
                         "Funcionalidades:\n"
                         "• Console JS integrado\n"
                         "• Recarregamento forçado\n"
                         "• Log de erros detalhado\n"
                         f"• GitHub: {self.github_url}")

# Executar o aplicativo
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Navegador Diagnóstico")
    app.setApplicationVersion("2.5")
    
    print("=" * 70)
    print("🚀 NAVEGADOR COM DIAGNÓSTICO ATIVADO")
    print("=" * 70)
    print("📝 Para usar:")
    print("   • Clique em 'Console' para ver erros em tempo real")
    print("   • Use Ctrl+Shift+R para recarregar sem cache")
    print("   • Ctrl+` para abrir/fechar console")
    print("=" * 70)
    
    navegador = NavegadorAbas()
    navegador.show()
    
    sys.exit(app.exec_())
