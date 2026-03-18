import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import *
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
import webbrowser

class AuthDialog(QDialog):
    """Diálogo personalizado para autenticação"""
    def __init__(self, url, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Autenticação Necessária")
        self.setModal(True)
        self.setGeometry(300, 300, 400, 200)
        
        layout = QVBoxLayout()
        
        # Informações do site
        info_label = QLabel(f"O site <b>{url.host()}</b> requer autenticação:")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Campos de usuário e senha
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
        
        # Botões
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

class MenuContextualWebEnginePage(QWebEnginePage):
    """Página web personalizada com menu de contexto e suporte a autenticação"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Conectar sinal de criação de nova janela
        self.createWindow = self.handle_create_window
    
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
        print(f"Erro de certificado: {error.description()}")
        return True
    
    def handle_create_window(self, window_type):
        """Handle para criação de novas janelas (popups, links com target=_blank)"""
        if self.parent_window and hasattr(self.parent_window, 'parent'):
            main_window = self.parent_window.parent
            if main_window and hasattr(main_window, 'adicionar_nova_aba'):
                # Criar nova página
                nova_pagina = MenuContextualWebEnginePage(main_window)
                nova_pagina.parent_window = main_window
                # Adicionar aba
                main_window.adicionar_nova_aba(QUrl(), nova_pagina)
                return nova_pagina
        return None
    
    def createStandardContextMenu(self):
        """Criar menu de contexto personalizado"""
        menu = super().createStandardContextMenu()
        
        # Adicionar separador
        menu.addSeparator()
        
        # Ação para ver código fonte
        ver_codigo_action = QAction("Exibir Código Fonte", menu)
        ver_codigo_action.triggered.connect(self.exibir_codigo_fonte)
        menu.addAction(ver_codigo_action)
        
        return menu
    
    def exibir_codigo_fonte(self):
        """Exibir código fonte da página em uma nova aba"""
        # Callback para receber o HTML
        def callback_html(html):
            if html and self.parent_window and hasattr(self.parent_window, 'parent'):
                main_window = self.parent_window.parent
                if main_window:
                    # Escapar o HTML para evitar problemas com caracteres especiais
                    html_escapado = html.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
                    
                    # Criar HTML formatado para exibição do código fonte
                    html_formatado = f'''<!DOCTYPE html>
<html>
<head>
    <title>Código Fonte: {self.url().toString()}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #1e1e1e;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
        }}
        #toolbar {{
            background: #2d2d2d;
            padding: 10px 20px;
            position: sticky;
            top: 0;
            border-bottom: 1px solid #444;
            margin-bottom: 20px;
            color: #fff;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 5px;
        }}
        #url-info {{
            color: #0099ff;
            font-size: 12px;
        }}
        #source-code {{
            background: #2d2d2d;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #d4d4d4;
            border: 1px solid #444;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .tag {{
            color: #569cd6;
        }}
        .attr {{
            color: #9cdcfe;
        }}
        .value {{
            color: #ce9178;
        }}
        .comment {{
            color: #6a9955;
        }}
        .line-number {{
            display: inline-block;
            width: 40px;
            color: #858585;
            text-align: right;
            padding-right: 15px;
            user-select: none;
            border-right: 1px solid #404040;
            margin-right: 15px;
        }}
        .line {{
            display: flex;
        }}
        .line-content {{
            flex: 1;
        }}
        .line:hover {{
            background: #3a3a3a;
        }}
        .stats {{
            color: #888;
            font-size: 12px;
        }}
        .btn {{
            background: #0e639c;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }}
        .btn:hover {{
            background: #1177bb;
        }}
        .btn-copy {{
            background: #2d2d2d;
            border: 1px solid #555;
        }}
        .btn-copy:hover {{
            background: #3d3d3d;
        }}
    </style>
    <script>
        function copyToClipboard() {{
            const code = document.getElementById('source-code').innerText;
            navigator.clipboard.writeText(code).then(function() {{
                const btn = document.getElementById('copyBtn');
                btn.textContent = 'Copiado!';
                setTimeout(() => btn.textContent = 'Copiar', 2000);
            }});
        }}
        
        function wordWrap() {{
            document.getElementById('source-code').style.whiteSpace = 
                document.getElementById('source-code').style.whiteSpace === 'pre-wrap' ? 'pre' : 'pre-wrap';
        }}
        
        function toggleLineNumbers() {{
            const lines = document.querySelectorAll('.line');
            lines.forEach(line => {{
                const lineNum = line.querySelector('.line-number');
                if (lineNum) {{
                    lineNum.style.display = lineNum.style.display === 'none' ? 'inline-block' : 'none';
                }}
            }});
        }}
    </script>
</head>
<body>
    <div id="toolbar">
        <div>
            <strong>📄 CÓDIGO FONTE</strong>
            <span id="url-info"> | {self.url().toString()}</span>
        </div>
        <div>
            <span class="stats" id="stats"></span>
            <button class="btn" onclick="wordWrap()">Quebra de Linha</button>
            <button class="btn" onclick="toggleLineNumbers()">Linhas</button>
            <button class="btn btn-copy" id="copyBtn" onclick="copyToClipboard()">Copiar</button>
        </div>
    </div>
    <div id="source-code"></div>
    <script>
        // Função para escapar HTML
        function escapeHtml(unsafe) {{
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }}
        
        // Função para syntax highlight simples
        function highlightHtml(code) {{
            // Escapar primeiro
            let escaped = escapeHtml(code);
            
            // Highlight tags
            escaped = escaped.replace(/&lt;(\\/?)(\\w+)(.*?)&gt;/g, function(match, slash, tag, attrs) {{
                let result = '&lt;<span class="tag">' + slash + tag + '</span>';
                if (attrs) {{
                    // Highlight attributes
                    result += attrs.replace(/(\\w+)(=)(&quot;.*?&quot;)/g, 
                        '<span class="attr">$1</span>$2<span class="value">$3</span>');
                }}
                result += '&gt;';
                return result;
            }});
            
            // Highlight comments
            escaped = escaped.replace(/&lt;!--(.*?)--&gt;/g, 
                '&lt;!--<span class="comment">$1</span>--&gt;');
            
            return escaped;
        }}
        
        // Processar o código
        const rawCode = `{html_escapado}`;
        const lines = rawCode.split('\\n');
        let html = '';
        
        lines.forEach((line, index) => {{
            const lineNumber = index + 1;
            const highlightedLine = highlightHtml(line);
            html += '<div class="line">' +
                    '<span class="line-number">' + lineNumber + '</span>' +
                    '<span class="line-content">' + (highlightedLine || '&nbsp;') + '</span>' +
                    '</div>';
        }});
        
        document.getElementById('source-code').innerHTML = html;
        document.getElementById('stats').textContent = 'Linhas: ' + lines.length + ' | Tamanho: ' + rawCode.length + ' chars';
    </script>
</body>
</html>'''
                    
                    # Abrir em nova aba
                    main_window.adicionar_nova_aba_com_html(html_formatado, f"Código Fonte: {self.url().host()}")
        
        # Obter HTML da página
        self.toHtml(callback_html)

class NavegadorAbas(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuração da janela principal
        self.setWindowTitle("Navegador WazzimaGiygg")
        self.setGeometry(100, 100, 1200, 800)
        
        # URL da página inicial
        self.url_home = "https://wazzimagiygg.wikidot.com"
        
        # URL do GitHub
        self.github_url = "https://github.com/WazzimaGiygg/Navegator-Python-WazzimaGiygg"
        
        # Lista de favoritos (compartilhada entre todas as abas)
        self.favoritos = [self.url_home]
        
        # Widget central e layout principal
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        
        # === BARRA DE FERRAMENTAS SUPERIOR ===
        barra_ferramentas = QToolBar()
        barra_ferramentas.setMovable(False)
        barra_ferramentas.setIconSize(QSize(20, 20))
        self.addToolBar(barra_ferramentas)
        
        # Botões de navegação
        btn_voltar = QPushButton("←")
        btn_voltar.setToolTip("Voltar (Alt+←)")
        btn_voltar.clicked.connect(self.voltar_aba_atual)
        barra_ferramentas.addWidget(btn_voltar)
        
        btn_avancar = QPushButton("→")
        btn_avancar.setToolTip("Avançar (Alt+→)")
        btn_avancar.clicked.connect(self.avancar_aba_atual)
        barra_ferramentas.addWidget(btn_avancar)
        
        btn_recarregar = QPushButton("↻")
        btn_recarregar.setToolTip("Recarregar (F5)")
        btn_recarregar.clicked.connect(self.recarregar_aba_atual)
        barra_ferramentas.addWidget(btn_recarregar)
        
        btn_home = QPushButton("🏠")
        btn_home.setToolTip("Página Inicial (Alt+Home)")
        btn_home.clicked.connect(self.ir_para_home_aba_atual)
        barra_ferramentas.addWidget(btn_home)
        
        # Barra de endereço
        self.barra_endereco = QLineEdit()
        self.barra_endereco.setPlaceholderText("Digite uma URL ou pesquisa...")
        self.barra_endereco.returnPressed.connect(self.navegar_para_url_aba_atual)
        barra_ferramentas.addWidget(self.barra_endereco)
        
        # Botões de ação
        btn_nova_aba = QPushButton("+")
        btn_nova_aba.setToolTip("Nova Aba (Ctrl+T)")
        btn_nova_aba.clicked.connect(self.adicionar_nova_aba)
        barra_ferramentas.addWidget(btn_nova_aba)
        
        btn_favorito = QPushButton("★")
        btn_favorito.setToolTip("Adicionar aos favoritos (Ctrl+D)")
        btn_favorito.clicked.connect(self.adicionar_favorito_aba_atual)
        barra_ferramentas.addWidget(btn_favorito)
        
        # Botão para abrir arquivo HTML local
        btn_abrir_arquivo = QPushButton("📁 HTML")
        btn_abrir_arquivo.setToolTip("Abrir arquivo HTML local")
        btn_abrir_arquivo.clicked.connect(self.abrir_arquivo_html)
        barra_ferramentas.addWidget(btn_abrir_arquivo)
        
        # Botão do GitHub
        btn_github = QPushButton("🐙 GitHub")
        btn_github.setToolTip("Abrir projeto no GitHub")
        btn_github.clicked.connect(self.abrir_github)
        barra_ferramentas.addWidget(btn_github)
        
        # === BARRA DE ABAS ===
        self.aba_widget = QTabWidget()
        self.aba_widget.setTabsClosable(True)
        self.aba_widget.tabCloseRequested.connect(self.fechar_aba)
        self.aba_widget.currentChanged.connect(self.aba_mudou)
        layout_principal.addWidget(self.aba_widget)
        
        # === BARRA DE STATUS ===
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Pronto")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(100)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Atalhos de teclado
        self.criar_atalhos()
        
        # Criar menu
        self.criar_menu()
        
        # Configurar perfil
        self.setup_profile()
        
        # Adicionar primeira aba
        self.adicionar_nova_aba(QUrl(self.url_home))
    
    def abrir_github(self):
        """Abrir o projeto GitHub em uma nova aba"""
        self.adicionar_nova_aba(QUrl(self.github_url))
        self.status_bar.showMessage(f"Abrindo GitHub: {self.github_url}", 3000)
    
    def setup_profile(self):
        """Configurar perfil do navegador"""
        self.profile = QWebEngineProfile.defaultProfile()
        
        # Configurar user-agent moderno
        self.profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Configurações
        settings = self.profile.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
    
    def criar_atalhos(self):
        """Criar atalhos de teclado"""
        # Ctrl+T - Nova aba
        atalho_nova_aba = QShortcut(QKeySequence("Ctrl+T"), self)
        atalho_nova_aba.activated.connect(self.adicionar_nova_aba)
        
        # Ctrl+W - Fechar aba
        atalho_fechar_aba = QShortcut(QKeySequence("Ctrl+W"), self)
        atalho_fechar_aba.activated.connect(self.fechar_aba_atual)
        
        # Ctrl+Tab - Próxima aba
        atalho_proxima_aba = QShortcut(QKeySequence("Ctrl+Tab"), self)
        atalho_proxima_aba.activated.connect(self.proxima_aba)
        
        # Ctrl+Shift+Tab - Aba anterior
        atalho_aba_anterior = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        atalho_aba_anterior.activated.connect(self.aba_anterior)
        
        # F5 - Recarregar
        atalho_recarregar = QShortcut(QKeySequence("F5"), self)
        atalho_recarregar.activated.connect(self.recarregar_aba_atual)
        
        # Ctrl+D - Adicionar favorito
        atalho_favorito = QShortcut(QKeySequence("Ctrl+D"), self)
        atalho_favorito.activated.connect(self.adicionar_favorito_aba_atual)
        
        # Alt+Home - Página inicial
        atalho_home = QShortcut(QKeySequence("Alt+Home"), self)
        atalho_home.activated.connect(self.ir_para_home_aba_atual)
        
        # Ctrl+L - Focar barra de endereço
        atalho_focar_url = QShortcut(QKeySequence("Ctrl+L"), self)
        atalho_focar_url.activated.connect(self.focar_barra_endereco)
        
        # Ctrl+U - Ver código fonte
        atalho_codigo_fonte = QShortcut(QKeySequence("Ctrl+U"), self)
        atalho_codigo_fonte.activated.connect(self.exibir_codigo_fonte_aba_atual)
        
        # Ctrl+G - Abrir GitHub
        atalho_github = QShortcut(QKeySequence("Ctrl+G"), self)
        atalho_github.activated.connect(self.abrir_github)
    
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
        
        abrir_arquivo = QAction("Abrir Arquivo HTML", self)
        abrir_arquivo.triggered.connect(self.abrir_arquivo_html)
        menu_arquivo.addAction(abrir_arquivo)
        
        menu_arquivo.addSeparator()
        
        sair = QAction("Sair", self)
        sair.triggered.connect(self.close)
        menu_arquivo.addAction(sair)
        
        # Menu Abas
        menu_abas = menubar.addMenu("Abas")
        
        prox_aba = QAction("Próxima Aba", self)
        prox_aba.setShortcut("Ctrl+Tab")
        prox_aba.triggered.connect(self.proxima_aba)
        menu_abas.addAction(prox_aba)
        
        aba_ant = QAction("Aba Anterior", self)
        aba_ant.setShortcut("Ctrl+Shift+Tab")
        aba_ant.triggered.connect(self.aba_anterior)
        menu_abas.addAction(aba_ant)
        
        # Menu Exibir
        menu_exibir = menubar.addMenu("Exibir")
        
        codigo_fonte = QAction("Código Fonte", self)
        codigo_fonte.setShortcut("Ctrl+U")
        codigo_fonte.triggered.connect(self.exibir_codigo_fonte_aba_atual)
        menu_exibir.addAction(codigo_fonte)
        
        # Menu Projeto
        menu_projeto = menubar.addMenu("Projeto")
        
        github_action = QAction("GitHub Project", self)
        github_action.setShortcut("Ctrl+G")
        github_action.triggered.connect(self.abrir_github)
        menu_projeto.addAction(github_action)
        
        # Menu Favoritos
        menu_favoritos = menubar.addMenu("Favoritos")
        
        ver_favoritos = QAction("Gerenciar Favoritos", self)
        ver_favoritos.triggered.connect(self.mostrar_favoritos)
        menu_favoritos.addAction(ver_favoritos)
        
        # Menu Ferramentas
        menu_ferramentas = menubar.addMenu("Ferramentas")
        
        limpar_dados = QAction("Limpar Cookies e Cache", self)
        limpar_dados.triggered.connect(self.limpar_dados)
        menu_ferramentas.addAction(limpar_dados)
        
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
    
    def adicionar_nova_aba(self, url=None, pagina_personalizada=None):
        """Adicionar nova aba ao navegador"""
        # Criar nova página web
        if pagina_personalizada:
            nova_pagina = pagina_personalizada
        else:
            nova_pagina = MenuContextualWebEnginePage(self)
            nova_pagina.parent_window = self
        
        # Criar novo widget de navegação
        novo_navegador = QWebEngineView()
        novo_navegador.setPage(nova_pagina)
        
        # Configurar URL
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
        
        # Adicionar ao tab widget
        index = self.aba_widget.addTab(novo_navegador, "Nova Aba")
        self.aba_widget.setCurrentIndex(index)
        
        return novo_navegador
    
    def adicionar_nova_aba_com_html(self, conteudo_html, titulo="Código Fonte"):
        """Adicionar nova aba com conteúdo HTML personalizado"""
        # Criar página temporária
        pagina_temp = QWebEnginePage(self)
        
        # Criar navegador
        novo_navegador = QWebEngineView()
        novo_navegador.setPage(pagina_temp)
        
        # Carregar HTML
        novo_navegador.setHtml(conteudo_html)
        
        # Conectar sinais básicos
        novo_navegador.titleChanged.connect(self.atualizar_titulo_aba)
        
        # Adicionar ao tab widget
        index = self.aba_widget.addTab(novo_navegador, titulo)
        self.aba_widget.setCurrentIndex(index)
        
        return novo_navegador
    
    def fechar_aba(self, index):
        """Fechar aba pelo índice"""
        if self.aba_widget.count() > 1:
            self.aba_widget.removeTab(index)
        else:
            # Se for a última aba, apenas recarrega a página inicial
            navegador = self.obter_aba_atual()
            if navegador:
                navegador.setUrl(QUrl(self.url_home))
    
    def fechar_aba_atual(self):
        """Fechar a aba atual"""
        if self.aba_widget.count() > 0:
            self.fechar_aba(self.aba_widget.currentIndex())
    
    def proxima_aba(self):
        """Ir para próxima aba"""
        atual = self.aba_widget.currentIndex()
        proxima = (atual + 1) % self.aba_widget.count()
        self.aba_widget.setCurrentIndex(proxima)
    
    def aba_anterior(self):
        """Ir para aba anterior"""
        atual = self.aba_widget.currentIndex()
        anterior = (atual - 1) if atual > 0 else self.aba_widget.count() - 1
        self.aba_widget.setCurrentIndex(anterior)
    
    def focar_barra_endereco(self):
        """Focar na barra de endereço"""
        self.barra_endereco.setFocus()
        self.barra_endereco.selectAll()
    
    def exibir_codigo_fonte_aba_atual(self):
        """Exibir código fonte da aba atual"""
        navegador = self.obter_aba_atual()
        if navegador and navegador.page():
            # Acessar o método da página
            if hasattr(navegador.page(), 'exibir_codigo_fonte'):
                navegador.page().exibir_codigo_fonte()
    
    def atualizar_titulo_aba(self, titulo):
        """Atualizar título da aba quando a página carregar"""
        navegador = self.sender()
        index = self.aba_widget.indexOf(navegador)
        if index >= 0:
            if titulo:
                # Limitar tamanho do título
                titulo_curto = titulo[:30] + "..." if len(titulo) > 30 else titulo
                self.aba_widget.setTabText(index, titulo_curto)
                self.aba_widget.setTabToolTip(index, titulo)
            else:
                self.aba_widget.setTabText(index, "Sem título")
    
    def atualizar_icone_aba(self, icone):
        """Atualizar ícone da aba (favicon)"""
        navegador = self.sender()
        index = self.aba_widget.indexOf(navegador)
        if index >= 0 and not icone.isNull():
            self.aba_widget.setTabIcon(index, icone)
    
    def voltar_aba_atual(self):
        """Voltar na aba atual"""
        navegador = self.obter_aba_atual()
        if navegador:
            navegador.back()
    
    def avancar_aba_atual(self):
        """Avançar na aba atual"""
        navegador = self.obter_aba_atual()
        if navegador:
            navegador.forward()
    
    def recarregar_aba_atual(self):
        """Recarregar aba atual"""
        navegador = self.obter_aba_atual()
        if navegador:
            navegador.reload()
    
    def ir_para_home_aba_atual(self):
        """Ir para página inicial na aba atual"""
        navegador = self.obter_aba_atual()
        if navegador:
            navegador.setUrl(QUrl(self.url_home))
    
    def navegar_para_url_aba_atual(self):
        """Navegar para URL digitada na aba atual"""
        url = self.barra_endereco.text()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        navegador = self.obter_aba_atual()
        if navegador:
            navegador.setUrl(QUrl(url))
    
    def atualizar_url_aba_atual(self, url):
        """Atualizar barra de endereço quando a URL mudar"""
        if self.sender() == self.obter_aba_atual():
            self.barra_endereco.setText(url.toString())
    
    def aba_mudou(self, index):
        """Quando a aba atual muda, atualizar a barra de endereço"""
        navegador = self.aba_widget.widget(index)
        if navegador:
            url = navegador.url().toString()
            self.barra_endereco.setText(url)
    
    def adicionar_favorito_aba_atual(self):
        """Adicionar página atual aos favoritos"""
        navegador = self.obter_aba_atual()
        if navegador:
            url_atual = navegador.url().toString()
            titulo = navegador.page().title()
            
            if url_atual not in self.favoritos:
                self.favoritos.append(url_atual)
                QMessageBox.information(self, "Favorito adicionado", 
                                      f"'{titulo}' foi adicionado aos favoritos!")
            else:
                QMessageBox.information(self, "Aviso", 
                                      "Esta página já está nos favoritos!")
    
    def on_load_started(self):
        """Quando o carregamento da página começa"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Carregando...")
    
    def on_load_progress(self, progress):
        """Atualizar barra de progresso"""
        self.progress_bar.setValue(progress)
    
    def on_load_finished(self, ok):
        """Quando o carregamento da página termina"""
        self.progress_bar.setVisible(False)
        if ok:
            self.status_bar.showMessage("Página carregada", 2000)
        else:
            self.status_bar.showMessage("Erro ao carregar página", 2000)
    
    def abrir_arquivo_html(self):
        """Abrir arquivo HTML local"""
        arquivo, _ = QFileDialog.getOpenFileName(
            self, 
            "Selecionar arquivo HTML", 
            "", 
            "Arquivos HTML (*.html *.htm);;Todos os arquivos (*.*)"
        )
        
        if arquivo:
            navegador = self.obter_aba_atual()
            if navegador:
                navegador.setUrl(QUrl.fromLocalFile(arquivo))
    
    def mostrar_favoritos(self):
        """Mostrar diálogo de favoritos"""
        if not self.favoritos:
            QMessageBox.information(self, "Favoritos", 
                                  "Nenhum favorito adicionado ainda.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Meus Favoritos")
        dialog.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout()
        
        lista_favoritos = QListWidget()
        for favorito in self.favoritos:
            lista_favoritos.addItem(favorito)
        
        # Botões
        botoes_layout = QHBoxLayout()
        
        btn_ir = QPushButton("Ir para página")
        btn_ir.clicked.connect(lambda: self.ir_para_favorito(lista_favoritos, dialog))
        
        btn_remover = QPushButton("Remover favorito")
        btn_remover.clicked.connect(lambda: self.remover_favorito(lista_favoritos))
        
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(dialog.close)
        
        botoes_layout.addWidget(btn_ir)
        botoes_layout.addWidget(btn_remover)
        botoes_layout.addWidget(btn_fechar)
        
        layout.addWidget(QLabel("Clique duas vezes para abrir em nova aba:"))
        layout.addWidget(lista_favoritos)
        layout.addLayout(botoes_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def ir_para_favorito(self, lista_favoritos, dialog):
        """Ir para favorito selecionado"""
        item = lista_favoritos.currentItem()
        if item:
            url = item.text()
            # Abrir em nova aba
            self.adicionar_nova_aba(QUrl(url))
            dialog.close()
    
    def remover_favorito(self, lista_favoritos):
        """Remover favorito da lista"""
        item = lista_favoritos.currentItem()
        if item:
            url = item.text()
            self.favoritos.remove(url)
            lista_favoritos.takeItem(lista_favoritos.row(item))
    
    def limpar_dados(self):
        """Limpar cookies e cache do navegador"""
        reply = QMessageBox.question(self, "Limpar Dados", 
                                    "Deseja limpar todos os cookies e cache?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            profile = QWebEngineProfile.defaultProfile()
            profile.cookieStore().deleteAllCookies()
            profile.clearHttpCache()
            QMessageBox.information(self, "Dados Limpos", 
                                  "Cookies e cache foram limpos com sucesso!")
    
    def mostrar_sobre(self):
        """Mostrar diálogo sobre"""
        QMessageBox.about(self, "Sobre o Navegador",
                         "Navegador Python com PyQt5\n"
                         "Versão 2.1 - Multi-abas + Código Fonte\n\n"
                         "Funcionalidades:\n"
                         "• Navegação por abas (Ctrl+T nova aba)\n"
                         "• Visualizar código fonte (Ctrl+U ou botão direito)\n"
                         "• Código fonte com syntax highlighting\n"
                         "• Copiar código fonte\n"
                         "• Suporte a autenticação (auth-popup)\n"
                         f"• Página inicial: {self.url_home}\n"
                         f"• GitHub: {self.github_url}\n\n"
                         "Desenvolvido com PyQt5 e QtWebEngine")

# Criar um arquivo HTML de exemplo
def criar_arquivo_exemplo():
    html_exemplo = """<!DOCTYPE html>
<html>
<head>
    <title>Navegador Multi-abas com Código Fonte</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        h1 {
            color: #fff;
            text-align: center;
            margin-bottom: 30px;
        }
        .feature-box {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .feature {
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .feature h3 {
            margin-top: 0;
            color: #FFD700;
        }
        .shortcut {
            background: rgba(0,0,0,0.3);
            padding: 5px 10px;
            border-radius: 5px;
            font-family: monospace;
        }
        .btn {
            background: #FF9100;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin: 5px;
            border: none;
            cursor: pointer;
        }
        .btn:hover {
            background: #FF6D00;
        }
        .code-demo {
            background: #1e1e1e;
            padding: 15px;
            border-radius: 8px;
            text-align: left;
            font-family: monospace;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Navegador com Visualização de Código Fonte</h1>
        
        <div class="feature-box">
            <div class="feature">
                <h3>📑 Múltiplas Abas</h3>
                <p>Navegue com várias abas</p>
                <p><span class="shortcut">Ctrl+T</span> Nova aba</p>
            </div>
            <div class="feature">
                <h3>🔍 Código Fonte</h3>
                <p>Veja o código HTML de qualquer página</p>
                <p><span class="shortcut">Ctrl+U</span> ou botão direito</p>
            </div>
            <div class="feature">
                <h3>📋 Copiar Código</h3>
                <p>Copie o código fonte com formatação</p>
                <p>Botão "Copiar" na visualização</p>
            </div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <p><strong>Teste agora:</strong> Clique com botão direito nesta página e selecione "Exibir Código Fonte"</p>
            <button class="btn" onclick="alert('O código fonte será aberto em nova aba!')">Testar Código Fonte</button>
        </div>
        
        <div class="code-demo">
            <p style="color: #569cd6;">&lt;!-- Exemplo de código formatado --&gt;</p>
            <p style="color: #d4d4d4;"><span style="color: #569cd6;">&lt;div</span> <span style="color: #9cdcfe;">class=</span><span style="color: #ce9178;">"container"</span><span style="color: #569cd6;">&gt;</span></p>
            <p style="color: #d4d4d4; margin-left: 20px;"><span style="color: #569cd6;">&lt;h1&gt;</span>Olá Mundo!<span style="color: #569cd6;">&lt;/h1&gt;</span></p>
            <p style="color: #569cd6;">&lt;/div&gt;</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <p><strong>Links de teste:</strong></p>
            <a href="https://wazzimagiygg.wikidot.com" class="btn">🏠 Página Inicial</a>
            <a href="https://github.com/WazzimaGiygg/Navegator-Python-WazzimaGiygg" class="btn">🐙 GitHub Project</a>
            <a href="https://www.google.com" class="btn">Google</a>
            <a href="https://httpbin.org/basic-auth/user/passwd" class="btn">Testar Auth (user/passwd)</a>
        </div>
    </div>
</body>
</html>"""
    
    with open("exemplo_multiplas_abas.html", "w", encoding="utf-8") as f:
        f.write(html_exemplo)
    
    return "exemplo_multiplas_abas.html"

# Executar o aplicativo
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Criar arquivo HTML de exemplo
    arquivo_exemplo = criar_arquivo_exemplo()
    
    print("=" * 70)
    print("✅ NAVEGADOR MULTI-ABAS COM CÓDIGO FONTE!")
    print("=" * 70)
    print(f"📄 Página exemplo: {arquivo_exemplo}")
    print(f"🏠 Página inicial: https://wazzimagiygg.wikidot.com")
    print(f"🐙 GitHub: https://github.com/WazzimaGiygg/Navegator-Python-WazzimaGiygg")
    print("🔐 Suporte a autenticação: ATIVADO")
    print("🔍 Visualização de código fonte: ATIVADO")
    print("\n📝 ATALHOS:")
    print("   Ctrl+T    - Nova aba")
    print("   Ctrl+W    - Fechar aba")
    print("   Ctrl+U    - Ver código fonte")
    print("   Ctrl+G    - Abrir GitHub Project")
    print("   Ctrl+L    - Focar URL")
    print("   F5        - Recarregar")
    print("   Ctrl+D    - Adicionar favorito")
    print("\n🖱️  BOTÃO DIREITO:")
    print("   'Exibir Código Fonte' no menu de contexto")
    print("=" * 70)
    
    # Criar e mostrar o navegador
    navegador = NavegadorAbas()
    navegador.show()
    
    sys.exit(app.exec_())
