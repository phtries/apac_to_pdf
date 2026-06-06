import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from parser_remessa import ler_remessa, opcoes_cnes, opcoes_procedimentos_principais, formatar_procedimento
from filtros import filtrar_apacs
from gerador_pdf import gerar_pdf_unico
from lookups import buscar_estabelecimento, descricao_procedimento
from paths import OUTPUT_DIR


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de APAC Física por Remessa - v4")
        self.geometry("920x620")
        self.minsize(880, 600)

        self.remessa_path = tk.StringVar()
        self.output_path = tk.StringVar(value=str(OUTPUT_DIR))
        self.cnes_var = tk.StringVar(value="Todos")
        self.status_var = tk.StringVar(value="Selecione uma remessa TXT e clique em 'Ler remessa'.")

        self.apacs = []
        self.header = {}
        self.cnes_map = {"Todos": ""}
        self.proc_map = {}
        self.proc_vars: dict[str, tk.BooleanVar] = {}
        self.proc_frame_interno = None
        self.proc_canvas = None

        self._configurar_tema_escuro()
        self._montar_tela()

    def _configurar_tema_escuro(self):
        self.bg = "#121212"
        self.panel = "#1e1e1e"
        self.panel_2 = "#252525"
        self.fg = "#f2f2f2"
        self.muted = "#b8b8b8"
        self.accent = "#2563eb"
        self.entry_bg = "#2d2d2d"
        self.border = "#3a3a3a"

        self.configure(bg=self.bg)
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=self.bg)
        style.configure("Panel.TFrame", background=self.panel)
        style.configure("TLabel", background=self.bg, foreground=self.fg, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=self.bg, foreground=self.fg, font=("Segoe UI", 17, "bold"))
        style.configure("Status.TLabel", background=self.bg, foreground=self.muted, font=("Consolas", 10))
        style.configure("Hint.TLabel", background=self.bg, foreground=self.muted, font=("Segoe UI", 9))

        style.configure("TLabelframe", background=self.bg, foreground=self.fg, bordercolor=self.border, relief="solid")
        style.configure("TLabelframe.Label", background=self.bg, foreground=self.fg, font=("Segoe UI", 10, "bold"))

        style.configure(
            "TEntry",
            fieldbackground=self.entry_bg,
            foreground=self.fg,
            insertcolor=self.fg,
            bordercolor=self.border,
            lightcolor=self.border,
            darkcolor=self.border,
        )
        style.map("TEntry", fieldbackground=[("readonly", self.entry_bg)])

        style.configure(
            "TCombobox",
            fieldbackground=self.entry_bg,
            background=self.entry_bg,
            foreground=self.fg,
            arrowcolor=self.fg,
            bordercolor=self.border,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.entry_bg)],
            foreground=[("readonly", self.fg)],
            background=[("readonly", self.entry_bg)],
        )

        style.configure("TButton", background=self.panel_2, foreground=self.fg, bordercolor=self.border, padding=(10, 6), font=("Segoe UI", 10))
        style.map("TButton", background=[("active", "#333333"), ("pressed", "#444444")], foreground=[("active", self.fg)])

        style.configure(
            "Primary.TButton",
            background=self.accent,
            foreground="white",
            bordercolor=self.accent,
            padding=(18, 8),
            font=("Segoe UI", 11, "bold"),
        )
        style.map("Primary.TButton", background=[("active", "#1d4ed8"), ("pressed", "#1e40af")], foreground=[("active", "white")])

    def _montar_tela(self):
        pad = {"padx": 16, "pady": 7}

        titulo = ttk.Label(self, text="Gerador de APAC Física por Remessa", style="Title.TLabel")
        titulo.pack(anchor="w", padx=18, pady=(14, 4))

        frame_arquivo = ttk.LabelFrame(self, text="1. Arquivo remessa")
        frame_arquivo.pack(fill="x", **pad)
        frame_arquivo.columnconfigure(0, weight=1)
        ttk.Entry(frame_arquivo, textvariable=self.remessa_path).grid(row=0, column=0, sticky="ew", padx=10, pady=9)
        ttk.Button(frame_arquivo, text="Selecionar TXT", command=self.selecionar_remessa).grid(row=0, column=1, padx=8, pady=9)
        ttk.Button(frame_arquivo, text="Ler remessa", command=self.carregar_remessa).grid(row=0, column=2, padx=(0, 10), pady=9)

        frame_filtros = ttk.LabelFrame(self, text="2. Filtros")
        frame_filtros.pack(fill="both", expand=True, **pad)
        frame_filtros.columnconfigure(1, weight=1)
        frame_filtros.rowconfigure(2, weight=1)

        ttk.Label(frame_filtros, text="CNES executante:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 7))
        self.combo_cnes = ttk.Combobox(frame_filtros, textvariable=self.cnes_var, state="readonly", values=["Todos"])
        self.combo_cnes.grid(row=0, column=1, sticky="ew", padx=10, pady=(10, 7))
        self.combo_cnes.bind("<<ComboboxSelected>>", lambda e: self.atualizar_status())

        header_proc = ttk.Frame(frame_filtros)
        header_proc.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(4, 4))
        ttk.Label(header_proc, text="Procedimentos principais:").pack(side="left")
        ttk.Button(header_proc, text="Marcar todos", command=self.marcar_todos_procedimentos).pack(side="right", padx=(8, 0))
        ttk.Button(header_proc, text="Desmarcar todos", command=self.desmarcar_todos_procedimentos).pack(side="right")

        self.proc_canvas = tk.Canvas(frame_filtros, bg=self.panel, highlightthickness=1, highlightbackground=self.border, height=190)
        scrollbar = ttk.Scrollbar(frame_filtros, orient="vertical", command=self.proc_canvas.yview)
        self.proc_frame_interno = tk.Frame(self.proc_canvas, bg=self.panel)
        self.proc_frame_interno.bind("<Configure>", lambda e: self.proc_canvas.configure(scrollregion=self.proc_canvas.bbox("all")))
        self.proc_canvas.create_window((0, 0), window=self.proc_frame_interno, anchor="nw")
        self.proc_canvas.configure(yscrollcommand=scrollbar.set)
        self.proc_canvas.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=(10, 0), pady=(0, 10))
        scrollbar.grid(row=2, column=2, sticky="ns", padx=(0, 10), pady=(0, 10))
        self._mostrar_placeholder_procedimentos()

        frame_saida = ttk.LabelFrame(self, text="3. Saída")
        frame_saida.pack(fill="x", **pad)
        frame_saida.columnconfigure(0, weight=1)
        ttk.Entry(frame_saida, textvariable=self.output_path).grid(row=0, column=0, sticky="ew", padx=10, pady=9)
        ttk.Button(frame_saida, text="Selecionar pasta", command=self.selecionar_saida).grid(row=0, column=1, padx=10, pady=9)

        frame_acao = ttk.Frame(self)
        frame_acao.pack(fill="x", padx=18, pady=(10, 4))
        ttk.Label(frame_acao, textvariable=self.status_var, style="Status.TLabel").pack(side="left", anchor="w")
        ttk.Button(frame_acao, text="Gerar APACs físicas", style="Primary.TButton", command=self.gerar).pack(side="right")

        rodape = ttk.Label(self, text="O PDF será gerado com todas as APACs que passarem pelos filtros selecionados.", style="Status.TLabel")
        rodape.pack(anchor="w", padx=18, pady=(2, 8))

    def _limpar_procedimentos_ui(self):
        for widget in self.proc_frame_interno.winfo_children():
            widget.destroy()
        self.proc_vars.clear()
        self.proc_map.clear()

    def _mostrar_placeholder_procedimentos(self):
        self._limpar_procedimentos_ui()
        tk.Label(
            self.proc_frame_interno,
            text="Depois de ler a remessa, os procedimentos principais aparecerão aqui.",
            bg=self.panel,
            fg=self.muted,
            font=("Segoe UI", 10),
            anchor="w",
            padx=10,
            pady=10,
        ).pack(fill="x")

    def selecionar_remessa(self):
        path = filedialog.askopenfilename(title="Selecione a remessa APAC", filetypes=[("Arquivos TXT", "*.txt"), ("Todos", "*.*")])
        if path:
            self.remessa_path.set(path)

    def selecionar_saida(self):
        path = filedialog.askdirectory(title="Selecione a pasta de saída")
        if path:
            self.output_path.set(path)

    def carregar_remessa(self):
        if not self.remessa_path.get().strip():
            messagebox.showwarning("Atenção", "Selecione o arquivo TXT da remessa antes de ler.")
            return

        try:
            resultado = ler_remessa(self.remessa_path.get())
            self.apacs = resultado["apacs"]
            self.header = resultado["header"]

            cnes_values = ["Todos"]
            self.cnes_map = {"Todos": ""}
            for cnes in opcoes_cnes(self.apacs):
                desc = buscar_estabelecimento(cnes)
                label = f"{cnes} - {desc}" if desc else cnes
                cnes_values.append(label)
                self.cnes_map[label] = cnes
            self.combo_cnes.configure(values=cnes_values)
            self.cnes_var.set("Todos")

            self._montar_checkboxes_procedimentos()
            self.atualizar_status()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler a remessa:\n{e}")

    def _montar_checkboxes_procedimentos(self):
        self._limpar_procedimentos_ui()
        procedimentos = opcoes_procedimentos_principais(self.apacs)
        if not procedimentos:
            self._mostrar_placeholder_procedimentos()
            return

        for proc in procedimentos:
            desc = descricao_procedimento(proc)
            label = f"{formatar_procedimento(proc)} - {desc}" if desc else formatar_procedimento(proc)
            var = tk.BooleanVar(value=True)
            chk = tk.Checkbutton(
                self.proc_frame_interno,
                text=label,
                variable=var,
                command=self.atualizar_status,
                bg=self.panel,
                fg=self.fg,
                selectcolor=self.entry_bg,
                activebackground=self.panel,
                activeforeground=self.fg,
                anchor="w",
                font=("Segoe UI", 9),
                padx=10,
                pady=4,
            )
            chk.pack(fill="x", anchor="w")
            self.proc_vars[proc] = var
            self.proc_map[proc] = label

    def procedimentos_selecionados(self):
        return [proc for proc, var in self.proc_vars.items() if var.get()]

    def marcar_todos_procedimentos(self):
        for var in self.proc_vars.values():
            var.set(True)
        self.atualizar_status()

    def desmarcar_todos_procedimentos(self):
        for var in self.proc_vars.values():
            var.set(False)
        self.atualizar_status()

    def apacs_filtradas(self):
        cnes = self.cnes_map.get(self.cnes_var.get(), "")
        procs = self.procedimentos_selecionados()
        return filtrar_apacs(self.apacs, cnes_executante=cnes, procedimentos_principais=procs)

    def atualizar_status(self):
        if not self.apacs:
            self.status_var.set("Selecione uma remessa TXT e clique em 'Ler remessa'.")
            return

        filtradas = self.apacs_filtradas()
        competencia = self.header.get("competencia", "")
        marcados = len(self.procedimentos_selecionados())
        total_procs = len(self.proc_vars)
        self.status_var.set(
            f"Competência: {competencia} | APACs: {len(self.apacs)} | Procedimentos marcados: {marcados}/{total_procs} | Após filtros: {len(filtradas)}"
        )

    def gerar(self):
        if not self.apacs:
            messagebox.showwarning("Atenção", "Leia uma remessa antes de gerar os PDFs.")
            return

        if not self.procedimentos_selecionados():
            messagebox.showwarning("Atenção", "Selecione pelo menos um procedimento principal.")
            return

        filtradas = self.apacs_filtradas()
        if not filtradas:
            messagebox.showwarning("Atenção", "Nenhuma APAC encontrada com os filtros escolhidos.")
            return

        pasta_saida = self.output_path.get().strip()
        if not pasta_saida:
            messagebox.showwarning("Atenção", "Selecione uma pasta de saída.")
            return

        try:
            caminho = gerar_pdf_unico(filtradas, pasta_saida)
            messagebox.showinfo("Concluído", f"PDF gerado com sucesso com {len(filtradas)} APACs:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar PDF:\n{e}")
