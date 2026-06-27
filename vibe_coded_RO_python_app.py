"""
Operational Research Desktop Application
Mohammadia School of Engineers (EMI)
Dr. EL MKHALET MOUNA

Algorithms:
  Graph: Welsh-Powell, Kruskal, Dijkstra, Bellman-Ford, Ford-Fulkerson, Potentiel Metra
  Transport: North-West Corner, Least Cost
  LP: Simplex
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import math, random, copy
from collections import defaultdict

# ──────────────────────────────────────────────────────────────────────────────
# COLOUR PALETTE
# ──────────────────────────────────────────────────────────────────────────────
BG_DARK   = "#0d1117"
BG_CARD   = "#161b22"
BG_INPUT  = "#1c2128"
BG_TABLE  = "#1c2128"
ACCENT    = "#2ea043"          # green
ACCENT2   = "#1f6feb"          # blue
ACCENT3   = "#d29922"          # amber
TEXT_PRI  = "#e6edf3"
TEXT_SEC  = "#8b949e"
BORDER    = "#30363d"
BTN_HOV   = "#238636"
RED_ACC   = "#da3633"
PURPLE    = "#8b5cf6"

BTN_ALGOS = [
    ("Welsh-Powell",   "welsh_powell",  ACCENT2),
    ("Kruskal",        "kruskal",       ACCENT),
    ("Dijkstra",       "dijkstra",      ACCENT3),
    ("Bellman-Ford",   "bellman_ford",  RED_ACC),
    ("Ford-Fulkerson", "ford_fulkerson",PURPLE),
    ("Potentiel Metra","potentiel",     "#06b6d4"),
    ("North-West",     "northwest",     "#f97316"),
    ("Least Cost",     "leastcost",     "#ec4899"),
    ("Simplex",        "simplex",       "#a78bfa"),
]

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS – styled widgets
# ──────────────────────────────────────────────────────────────────────────────
def styled_btn(parent, text, command, color=ACCENT, width=18, **kw):
    b = tk.Button(parent, text=text, command=command,
                  bg=color, fg=TEXT_PRI, relief="flat",
                  font=("Segoe UI", 10, "bold"),
                  activebackground=color, activeforeground="white",
                  cursor="hand2", width=width, pady=6, **kw)
    return b

def card_frame(parent, **kw):
    return tk.Frame(parent, bg=BG_CARD, relief="flat",
                    highlightbackground=BORDER,
                    highlightthickness=1, **kw)

def lbl(parent, text, size=10, bold=False, color=TEXT_PRI, **kw):
    w = tk.Label(parent, text=text, bg=parent["bg"], fg=color,
                 font=("Segoe UI", size, "bold" if bold else "normal"), **kw)
    return w

# ──────────────────────────────────────────────────────────────────────────────
# MATRIX INPUT WIDGET
# ──────────────────────────────────────────────────────────────────────────────
class MatrixInput(tk.Frame):
    """
    Editable grid for adjacency / cost matrices.
    n×n  or  r×c  depending on mode.
    """
    def __init__(self, parent, rows=4, cols=4, labels=None,
                 col_labels=None, title="", **kw):
        super().__init__(parent, bg=BG_INPUT, **kw)
        self.rows = rows
        self.cols = cols
        self.cells = []
        if title:
            lbl(self, title, 9, color=TEXT_SEC).grid(
                row=0, column=0, columnspan=cols+1, pady=(4,2))
        top = 1 if title else 0
        # col headers
        for j in range(cols):
            hdr = col_labels[j] if col_labels else str(j)
            lbl(self, hdr, 8, color=ACCENT2).grid(row=top, column=j+1, padx=2)
        for i in range(rows):
            row_cells = []
            hdr = labels[i] if labels else str(i)
            lbl(self, hdr, 8, color=ACCENT2).grid(row=top+i+1, column=0, padx=4)
            for j in range(cols):
                var = tk.StringVar(value="0")
                e = tk.Entry(self, textvariable=var, width=5,
                             bg=BG_DARK, fg=TEXT_PRI,
                             insertbackground=TEXT_PRI,
                             relief="flat",
                             font=("Consolas", 9),
                             justify="center",
                             highlightbackground=BORDER,
                             highlightthickness=1)
                e.grid(row=top+i+1, column=j+1, padx=2, pady=2)
                row_cells.append(var)
            self.cells.append(row_cells)

    def get_matrix(self):
        mat = []
        for row in self.cells:
            mat.append([v.get().strip() for v in row])
        return mat

    def get_float_matrix(self, inf_val=None):
        """Returns float matrix; '0','inf','' handled."""
        mat = []
        INF = float('inf')
        for row in self.cells:
            r = []
            for v in row:
                s = v.get().strip().lower()
                if s in ("", "inf", "∞"):
                    r.append(INF if inf_val is None else inf_val)
                else:
                    try:
                        r.append(float(s))
                    except ValueError:
                        r.append(0.0)
            mat.append(r)
        return mat

    def set_matrix(self, mat):
        for i, row in enumerate(mat):
            for j, val in enumerate(row):
                if i < self.rows and j < self.cols:
                    self.cells[i][j].set(str(val))

# ──────────────────────────────────────────────────────────────────────────────
# REPORT WINDOW
# ──────────────────────────────────────────────────────────────────────────────
class ReportWindow(tk.Toplevel):
    def __init__(self, parent, title, content):
        super().__init__(parent)
        self.title(f"Report – {title}")
        self.configure(bg=BG_DARK)
        self.geometry("700x520")
        self.resizable(True, True)

        hdr = tk.Frame(self, bg=ACCENT2, pady=8)
        hdr.pack(fill="x")
        lbl(hdr, f"📋  {title}  —  Algorithm Report",
            12, bold=True, color="white").pack()

        fr = tk.Frame(self, bg=BG_CARD, padx=12, pady=12)
        fr.pack(fill="both", expand=True, padx=10, pady=10)

        sb_y = tk.Scrollbar(fr, orient="vertical")
        sb_x = tk.Scrollbar(fr, orient="horizontal")
        self.txt = tk.Text(fr, bg=BG_DARK, fg=TEXT_PRI,
                           font=("Consolas", 10),
                           relief="flat", wrap="none",
                           yscrollcommand=sb_y.set,
                           xscrollcommand=sb_x.set,
                           padx=10, pady=10)
        sb_y.config(command=self.txt.yview)
        sb_x.config(command=self.txt.xview)
        sb_y.pack(side="right", fill="y")
        sb_x.pack(side="bottom", fill="x")
        self.txt.pack(fill="both", expand=True)

        # tags for colouring
        self.txt.tag_config("head",  foreground=ACCENT2, font=("Consolas",11,"bold"))
        self.txt.tag_config("ok",    foreground=ACCENT)
        self.txt.tag_config("warn",  foreground=ACCENT3)
        self.txt.tag_config("err",   foreground=RED_ACC)
        self.txt.tag_config("data",  foreground=TEXT_SEC)
        self.txt.tag_config("value", foreground="#79c0ff")

        self._write(content)
        self.txt.config(state="disabled")

        btn_row = tk.Frame(self, bg=BG_DARK)
        btn_row.pack(pady=6)
        styled_btn(btn_row, "Close", self.destroy, RED_ACC, 10).pack()

    def _write(self, content):
        """content = list of (text, tag) tuples or plain string."""
        if isinstance(content, str):
            self.txt.insert("end", content)
        else:
            for item in content:
                if isinstance(item, tuple):
                    self.txt.insert("end", item[0], item[1])
                else:
                    self.txt.insert("end", item)

# ──────────────────────────────────────────────────────────────────────────────
# ALGORITHM SCREENS (base)
# ──────────────────────────────────────────────────────────────────────────────
class AlgoScreen(tk.Frame):
    def __init__(self, parent, app, title, color):
        super().__init__(parent, bg=BG_DARK)
        self.app   = app
        self.title = title
        self.color = color
        self._build_header()
        self.body = tk.Frame(self, bg=BG_DARK)
        self.body.pack(fill="both", expand=True, padx=14, pady=6)
        self._build_body()

    def _build_header(self):
        hdr = tk.Frame(self, bg=self.color, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=self.title, bg=self.color, fg="white",
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=16)
        tk.Button(hdr, text="← Back", command=self.app.show_home,
                  bg=BG_DARK, fg=TEXT_PRI, relief="flat",
                  font=("Segoe UI", 9), cursor="hand2",
                  activebackground=BORDER, padx=8).pack(side="right", padx=10)

    def _build_body(self):
        pass   # override

    def show_report(self, content):
        ReportWindow(self.app.root, self.title, content)

    # ── label helpers for body ──
    def section(self, parent, text):
        f = tk.Frame(parent, bg=BG_DARK)
        f.pack(fill="x", pady=(10,2))
        lbl(f, text, 10, bold=True, color=self.color).pack(side="left")
        tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x",
                                              expand=True, padx=8)
        return f

# ──────────────────────────────────────────────────────────────────────────────
# GRAPH HELPERS shared across graph algorithms
# ──────────────────────────────────────────────────────────────────────────────
class GraphInputPanel(tk.Frame):
    """
    Reusable panel: spinbox to choose N, button to resize matrix, matrix widget.
    mode: 'undirected_weight' | 'directed_weight' | 'undirected_binary'
    """
    def __init__(self, parent, mode="undirected_weight",
                 default_n=5, max_n=12, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self.mode = mode
        self.max_n = max_n
        self.n_var = tk.IntVar(value=default_n)
        self.matrix_widget = None

        ctrl = tk.Frame(self, bg=BG_DARK)
        ctrl.pack(fill="x")
        lbl(ctrl, "Number of nodes:", color=TEXT_SEC).pack(side="left")
        sb = tk.Spinbox(ctrl, from_=2, to=max_n, textvariable=self.n_var,
                        width=4, bg=BG_INPUT, fg=TEXT_PRI,
                        buttonbackground=BG_INPUT,
                        relief="flat", font=("Segoe UI",10))
        sb.pack(side="left", padx=6)
        styled_btn(ctrl, "Resize Matrix", self._resize, ACCENT2, 14).pack(
            side="left", padx=6)
        styled_btn(ctrl, "Random Fill", self._random_fill, ACCENT3, 12).pack(
            side="left", padx=4)
        styled_btn(ctrl, "Clear", self._clear, TEXT_SEC, 8).pack(
            side="left", padx=2)

        note = ""
        if mode == "undirected_weight":
            note = "Enter edge weights (0 = no edge). Matrix is symmetric."
        elif mode == "directed_weight":
            note = "Directed: enter weight from row-node to col-node (0 = no edge, use 'inf' for blocked)."
        elif mode == "undirected_binary":
            note = "Enter 1 if edge exists, 0 otherwise."
        lbl(self, note, 8, color=TEXT_SEC).pack(anchor="w", pady=(2,4))

        self.mat_frame = tk.Frame(self, bg=BG_DARK)
        self.mat_frame.pack(fill="both", expand=True)
        self._resize()

    def _node_labels(self):
        n = self.n_var.get()
        return [f"N{i}" for i in range(1, n+1)]

    def _resize(self):
        for w in self.mat_frame.winfo_children():
            w.destroy()
        n = self.n_var.get()
        lbls = self._node_labels()
        self.matrix_widget = MatrixInput(
            self.mat_frame, rows=n, cols=n,
            labels=lbls, col_labels=lbls)
        self.matrix_widget.pack()

    def _random_fill(self):
        if not self.matrix_widget:
            return
        n = self.n_var.get()
        mat = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(i+1, n):
                if random.random() < 0.55:
                    w = random.randint(1, 20)
                    mat[i][j] = w
                    if self.mode in ("undirected_weight", "undirected_binary"):
                        mat[j][i] = w
                    else:
                        mat[j][i] = random.randint(1,20) if random.random()<0.4 else 0
        self.matrix_widget.set_matrix(mat)

    def _clear(self):
        if self.matrix_widget:
            n = self.n_var.get()
            self.matrix_widget.set_matrix([[0]*n for _ in range(n)])

    def get_adj(self):
        """Returns (n, adj_matrix_float, node_labels)"""
        n = self.n_var.get()
        mat = self.matrix_widget.get_float_matrix()
        lbls = self._node_labels()
        return n, mat, lbls

# ──────────────────────────────────────────────────────────────────────────────
# 1. WELSH-POWELL
# ──────────────────────────────────────────────────────────────────────────────
class WelshPowellScreen(AlgoScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Welsh-Powell — Graph Coloring", ACCENT2)

    def _build_body(self):
        self.section(self.body, "Graph Input (Adjacency Matrix — undirected, 1=edge)")
        self.gip = GraphInputPanel(self.body, mode="undirected_binary", default_n=6)
        self.gip.pack(fill="x")
        self.section(self.body, "Run")
        styled_btn(self.body, "▶  Run Welsh-Powell", self._run, ACCENT2, 22).pack(pady=8)

    def _run(self):
        n, mat, lbls = self.gip.get_adj()
        # build adjacency list
        adj = defaultdict(set)
        for i in range(n):
            for j in range(n):
                if mat[i][j] > 0 and i != j:
                    adj[i].add(j)
                    adj[j].add(i)

        # Welsh-Powell
        degrees = sorted(range(n), key=lambda v: -len(adj[v]))
        color_map = {}
        c = 0
        while len(color_map) < n:
            c += 1
            available = [v for v in degrees if v not in color_map]
            colored = []
            for v in available:
                if not any(color_map.get(u) == c for u in adj[v]):
                    color_map[v] = c
                    colored.append(v)
        num_colors = max(color_map.values())

        # report
        rep = []
        rep.append(("═"*60 + "\n", "data"))
        rep.append(("  WELSH-POWELL — GRAPH COLORING REPORT\n", "head"))
        rep.append(("═"*60 + "\n", "data"))
        rep.append((f"\n  Nodes  : {n}\n", "data"))
        rep.append((f"  Edges  : {sum(len(s) for s in adj.values())//2}\n", "data"))
        rep.append((f"  Chromatic Number χ(G) = {num_colors}\n\n", "value"))
        rep.append(("  Node Coloring:\n", "head"))
        for color in range(1, num_colors+1):
            nodes = [lbls[v] for v in range(n) if color_map[v] == color]
            rep.append((f"    Color {color:>2}:  {', '.join(nodes)}\n", "ok"))
        rep.append(("\n  Degree Order (desc):\n", "head"))
        for v in sorted(range(n), key=lambda x: -len(adj[x])):
            rep.append((f"    {lbls[v]:>4}  deg={len(adj[v])}  color={color_map[v]}\n","data"))
        rep.append(("\n" + "═"*60 + "\n", "data"))
        self.show_report(rep)

# ──────────────────────────────────────────────────────────────────────────────
# 2. KRUSKAL
# ──────────────────────────────────────────────────────────────────────────────
class KruskalScreen(AlgoScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Kruskal — Minimum Spanning Tree", ACCENT)

    def _build_body(self):
        self.section(self.body, "Graph Input (Weighted Undirected — 0 = no edge)")
        self.gip = GraphInputPanel(self.body, mode="undirected_weight", default_n=6)
        self.gip.pack(fill="x")
        self.section(self.body, "Run")
        styled_btn(self.body, "▶  Run Kruskal", self._run, ACCENT, 22).pack(pady=8)

    def _run(self):
        n, mat, lbls = self.gip.get_adj()
        edges = []
        for i in range(n):
            for j in range(i+1, n):
                w = mat[i][j]
                if w > 0 and w != float('inf'):
                    edges.append((w, i, j))
        edges.sort()

        parent = list(range(n))
        rank   = [0]*n

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra == rb: return False
            if rank[ra] < rank[rb]: ra, rb = rb, ra
            parent[rb] = ra
            if rank[ra] == rank[rb]: rank[ra] += 1
            return True

        mst_edges = []
        total_cost = 0
        steps = []
        for w, u, v in edges:
            accepted = union(u, v)
            steps.append((w, u, v, accepted))
            if accepted:
                mst_edges.append((w, u, v))
                total_cost += w

        rep = []
        rep.append(("═"*60 + "\n", "data"))
        rep.append(("  KRUSKAL — MINIMUM SPANNING TREE REPORT\n", "head"))
        rep.append(("═"*60 + "\n\n", "data"))
        rep.append((f"  Nodes : {n}   Edges considered : {len(edges)}\n\n","data"))
        rep.append(("  Step-by-step edge processing:\n", "head"))
        rep.append(("  " + "-"*50 + "\n", "data"))
        rep.append((f"  {'Edge':<14} {'Weight':>8}   {'Decision'}\n", "warn"))
        rep.append(("  " + "-"*50 + "\n", "data"))
        for w, u, v, acc in steps:
            decision = "✔ ADDED" if acc else "✘ Skipped (cycle)"
            tag = "ok" if acc else "err"
            rep.append((f"  {lbls[u]} — {lbls[v]:<10} {w:>8.2f}   ", "data"))
            rep.append((f"{decision}\n", tag))
        rep.append(("  " + "-"*50 + "\n\n", "data"))
        rep.append(("  MST Edges:\n", "head"))
        for w, u, v in mst_edges:
            rep.append((f"    {lbls[u]} ——— {lbls[v]}  (weight {w:.2f})\n", "ok"))
        rep.append(("\n", ""))
        rep.append((f"  ► Total MST Cost = {total_cost:.4f}\n", "value"))
        if len(mst_edges) < n-1:
            rep.append(("  ⚠  Graph is not connected — MST incomplete.\n","err"))
        rep.append(("\n" + "═"*60 + "\n", "data"))
        self.show_report(rep)

# ──────────────────────────────────────────────────────────────────────────────
# 3. DIJKSTRA
# ──────────────────────────────────────────────────────────────────────────────
class DijkstraScreen(AlgoScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Dijkstra — Shortest Paths", ACCENT3)

    def _build_body(self):
        self.section(self.body, "Graph Input (Weighted Directed — 0 = no edge)")
        self.gip = GraphInputPanel(self.body, mode="directed_weight", default_n=5)
        self.gip.pack(fill="x")

        self.section(self.body, "Source Node")
        row = tk.Frame(self.body, bg=BG_DARK)
        row.pack(fill="x", pady=4)
        lbl(row, "Source index (0-based):", color=TEXT_SEC).pack(side="left")
        self.src_var = tk.IntVar(value=0)
        tk.Spinbox(row, from_=0, to=99, textvariable=self.src_var, width=4,
                   bg=BG_INPUT, fg=TEXT_PRI, relief="flat").pack(side="left",padx=6)
        self.section(self.body, "Run")
        styled_btn(self.body, "▶  Run Dijkstra", self._run, ACCENT3, 22).pack(pady=8)

    def _run(self):
        n, mat, lbls = self.gip.get_adj()
        src = self.src_var.get()
        if src >= n:
            messagebox.showerror("Error", f"Source index must be < {n}")
            return
        INF = float('inf')
        dist = [INF]*n
        dist[src] = 0
        prev = [-1]*n
        visited = [False]*n

        for _ in range(n):
            u = min((d, i) for i, d in enumerate(dist) if not visited[i])[1]
            if dist[u] == INF:
                break
            visited[u] = True
            for v in range(n):
                w = mat[u][v]
                if w > 0 and w != INF and not visited[v]:
                    if dist[u] + w < dist[v]:
                        dist[v] = dist[u] + w
                        prev[v] = u

        def reconstruct(t):
            path = []
            while t != -1:
                path.append(lbls[t])
                t = prev[t]
            return " → ".join(reversed(path))

        rep = []
        rep.append(("═"*60 + "\n", "data"))
        rep.append(("  DIJKSTRA — SHORTEST PATHS REPORT\n", "head"))
        rep.append(("═"*60 + "\n\n", "data"))
        rep.append((f"  Source  : {lbls[src]}\n  Nodes   : {n}\n\n", "data"))
        rep.append(("  Results:\n", "head"))
        rep.append(("  " + "-"*54 + "\n", "data"))
        rep.append((f"  {'Destination':<10} {'Distance':>12}   {'Path'}\n","warn"))
        rep.append(("  " + "-"*54 + "\n", "data"))
        for v in range(n):
            d = dist[v]
            ds = f"{d:.4f}" if d != INF else "∞ (unreachable)"
            path = reconstruct(v) if d != INF else "—"
            tag = "ok" if d != INF else "err"
            rep.append((f"  {lbls[v]:<10} {ds:>12}   {path}\n", tag))
        rep.append(("  " + "-"*54 + "\n\n", "data"))
        reachable = [d for d in dist if d != INF]
        rep.append((f"  ► Reachable nodes  : {len(reachable)}/{n}\n", "value"))
        if len(reachable) > 1:
            rep.append((f"  ► Max distance     : {max(reachable):.4f}\n","value"))
        rep.append(("\n" + "═"*60 + "\n", "data"))
        self.show_report(rep)

# ──────────────────────────────────────────────────────────────────────────────
# 4. BELLMAN-FORD
# ──────────────────────────────────────────────────────────────────────────────
class BellmanFordScreen(AlgoScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Bellman-Ford — Shortest Paths (Negative Weights)", RED_ACC)

    def _build_body(self):
        self.section(self.body, "Graph Input (Directed — negative weights allowed, 0=no edge)")
        lbl(self.body, "Tip: use negative numbers freely. Leave 0 for no edge.",
            8, color=TEXT_SEC).pack(anchor="w")
        self.gip = GraphInputPanel(self.body, mode="directed_weight", default_n=5)
        self.gip.pack(fill="x")

        self.section(self.body, "Source Node")
        row = tk.Frame(self.body, bg=BG_DARK)
        row.pack(fill="x", pady=4)
        lbl(row, "Source index (0-based):", color=TEXT_SEC).pack(side="left")
        self.src_var = tk.IntVar(value=0)
        tk.Spinbox(row, from_=0, to=99, textvariable=self.src_var, width=4,
                   bg=BG_INPUT, fg=TEXT_PRI, relief="flat").pack(side="left",padx=6)
        self.section(self.body, "Run")
        styled_btn(self.body, "▶  Run Bellman-Ford", self._run, RED_ACC, 22).pack(pady=8)

    def _run(self):
        n, mat, lbls = self.gip.get_adj()
        src = self.src_var.get()
        if src >= n:
            messagebox.showerror("Error", f"Source must be < {n}")
            return
        INF = float('inf')

        # Build edge list (include negative, skip 0 and inf)
        edges = []
        for i in range(n):
            for j in range(n):
                w = mat[i][j]
                if w != 0 and w != INF and i != j:
                    edges.append((i, j, w))

        dist = [INF]*n
        dist[src] = 0
        prev = [-1]*n
        iteration_log = []

        for iteration in range(n-1):
            updated = []
            for u, v, w in edges:
                if dist[u] != INF and dist[u]+w < dist[v]:
                    dist[v] = dist[u]+w
                    prev[v] = u
                    updated.append((lbls[u], lbls[v], w, dist[v]))
            iteration_log.append((iteration+1, updated))

        # Check negative cycle
        neg_cycle = False
        neg_cycle_edges = []
        for u, v, w in edges:
            if dist[u] != INF and dist[u]+w < dist[v]:
                neg_cycle = True
                neg_cycle_edges.append((lbls[u], lbls[v], w))

        def reconstruct(t):
            path, visited = [], set()
            while t != -1 and t not in visited:
                path.append(lbls[t])
                visited.add(t)
                t = prev[t]
            return " → ".join(reversed(path))

        rep = []
        rep.append(("═"*62 + "\n", "data"))
        rep.append(("  BELLMAN-FORD — SHORTEST PATHS REPORT\n", "head"))
        rep.append(("═"*62 + "\n\n", "data"))
        rep.append((f"  Source: {lbls[src]}    Nodes: {n}    Edges: {len(edges)}\n\n","data"))
        if neg_cycle:
            rep.append(("  ⚠  NEGATIVE CYCLE DETECTED!\n", "err"))
            for u,v,w in neg_cycle_edges:
                rep.append((f"     Edge {u}→{v} weight {w}\n","err"))
            rep.append(("\n",""))
        rep.append(("  Final Distances:\n", "head"))
        rep.append(("  " + "-"*54 + "\n", "data"))
        rep.append((f"  {'Destination':<10} {'Distance':>12}   {'Path'}\n","warn"))
        rep.append(("  " + "-"*54 + "\n", "data"))
        for v in range(n):
            d = dist[v]
            ds = f"{d:.4f}" if d != INF else "∞"
            path = reconstruct(v) if d != INF else "—"
            tag = "ok" if d != INF else "err"
            rep.append((f"  {lbls[v]:<10} {ds:>12}   {path}\n", tag))
        rep.append(("  " + "-"*54 + "\n\n", "data"))
        rep.append(("  Iteration Log (updates only):\n", "head"))
        for it, updates in iteration_log:
            if updates:
                rep.append((f"\n  Iteration {it}:\n", "warn"))
                for u,v,w,nw in updates:
                    rep.append((f"    Relax {u}→{v}  (w={w:.2f})  dist[{v}] = {nw:.4f}\n","data"))
        rep.append(("\n" + "═"*62 + "\n", "data"))
        self.show_report(rep)

# ──────────────────────────────────────────────────────────────────────────────
# 5. FORD-FULKERSON (BFS / Edmonds-Karp)
# ──────────────────────────────────────────────────────────────────────────────
class FordFulkersonScreen(AlgoScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Ford-Fulkerson — Maximum Flow", PURPLE)

    def _build_body(self):
        self.section(self.body, "Capacity Matrix (Directed — 0 = no arc)")
        self.gip = GraphInputPanel(self.body, mode="directed_weight", default_n=6)
        self.gip.pack(fill="x")

        self.section(self.body, "Source & Sink")
        row = tk.Frame(self.body, bg=BG_DARK)
        row.pack(fill="x", pady=4)
        lbl(row, "Source index:", color=TEXT_SEC).pack(side="left")
        self.src_var = tk.IntVar(value=0)
        tk.Spinbox(row, from_=0, to=99, textvariable=self.src_var, width=4,
                   bg=BG_INPUT, fg=TEXT_PRI, relief="flat").pack(side="left",padx=4)
        lbl(row, "  Sink index:", color=TEXT_SEC).pack(side="left")
        self.snk_var = tk.IntVar(value=5)
        tk.Spinbox(row, from_=0, to=99, textvariable=self.snk_var, width=4,
                   bg=BG_INPUT, fg=TEXT_PRI, relief="flat").pack(side="left",padx=4)

        self.section(self.body, "Run")
        styled_btn(self.body, "▶  Run Ford-Fulkerson", self._run, PURPLE, 24).pack(pady=8)

    def _bfs(self, cap, src, snk, parent):
        n = len(cap)
        visited = [False]*n
        visited[src] = True
        queue = [src]
        while queue:
            u = queue.pop(0)
            for v in range(n):
                if not visited[v] and cap[u][v] > 0:
                    visited[v] = True
                    parent[v] = u
                    if v == snk:
                        return True
                    queue.append(v)
        return False

    def _run(self):
        n, mat, lbls = self.gip.get_adj()
        src = self.src_var.get()
        snk = self.snk_var.get()
        if src >= n or snk >= n or src == snk:
            messagebox.showerror("Error", "Invalid source/sink indices.")
            return
        cap = [[int(mat[i][j]) for j in range(n)] for i in range(n)]
        orig_cap = copy.deepcopy(cap)
        parent = [-1]*n
        max_flow = 0
        augmentations = []

        while self._bfs(cap, src, snk, parent):
            path_flow = float('inf')
            v = snk
            path = []
            while v != src:
                u = parent[v]
                path.append((u, v))
                path_flow = min(path_flow, cap[u][v])
                v = u
            path.reverse()
            for u, v in path:
                cap[u][v] -= path_flow
                cap[v][u] += path_flow
            max_flow += path_flow
            augmentations.append((path, path_flow))
            parent = [-1]*n

        rep = []
        rep.append(("═"*60 + "\n", "data"))
        rep.append(("  FORD-FULKERSON — MAXIMUM FLOW REPORT\n", "head"))
        rep.append(("═"*60 + "\n\n", "data"))
        rep.append((f"  Source : {lbls[src]}    Sink : {lbls[snk]}    Nodes : {n}\n\n","data"))
        rep.append(("  Augmenting Paths:\n", "head"))
        rep.append(("  " + "-"*54 + "\n", "data"))
        for i, (path, flow) in enumerate(augmentations, 1):
            p_str = " → ".join([lbls[u] for u, v in path] + [lbls[path[-1][1]]])
            rep.append((f"  [{i}] {p_str}\n", "data"))
            rep.append((f"      Bottleneck flow = {flow}\n", "ok"))
        rep.append(("  " + "-"*54 + "\n\n", "data"))
        rep.append((f"  ► Maximum Flow = {max_flow}\n\n", "value"))
        # flow on each arc
        rep.append(("  Final Arc Flows  (flow / capacity):\n", "head"))
        for i in range(n):
            for j in range(n):
                oc = orig_cap[i][j]
                if oc > 0:
                    flow_ij = oc - cap[i][j]
                    rep.append((f"    {lbls[i]} → {lbls[j]}:  {flow_ij} / {oc}\n","data"))
        rep.append(("\n" + "═"*60 + "\n", "data"))
        self.show_report(rep)

# ──────────────────────────────────────────────────────────────────────────────
# 6. POTENTIEL METRA (CPM / Critical Path)
# ──────────────────────────────────────────────────────────────────────────────
class PotentielScreen(AlgoScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Potentiel Métra — Critical Path Method (CPM)", "#06b6d4")

    def _build_body(self):
        self.section(self.body, "Tasks (rows = tasks, cols = duration / predecessors)")
        note = ("Enter task names in the first column, durations in the second.\n"
                "For predecessors, list task names separated by commas in col 3.")
        lbl(self.body, note, 8, color=TEXT_SEC).pack(anchor="w", pady=2)

        # Dynamic task table
        self.section(self.body, "Number of Tasks")
        ctrl = tk.Frame(self.body, bg=BG_DARK)
        ctrl.pack(fill="x")
        lbl(ctrl, "Tasks:", color=TEXT_SEC).pack(side="left")
        self.ntask_var = tk.IntVar(value=6)
        tk.Spinbox(ctrl, from_=2, to=20, textvariable=self.ntask_var, width=4,
                   bg=BG_INPUT, fg=TEXT_PRI, relief="flat").pack(side="left",padx=4)
        styled_btn(ctrl, "Resize", self._resize_table, "#06b6d4", 10).pack(side="left",padx=4)
        styled_btn(ctrl, "Example", self._example, ACCENT3, 10).pack(side="left",padx=4)

        self.table_frame = tk.Frame(self.body, bg=BG_DARK)
        self.table_frame.pack(fill="x", pady=6)
        self._build_table()
        self.section(self.body, "Run")
        styled_btn(self.body, "▶  Run Potentiel Métra", self._run, "#06b6d4", 24).pack(pady=8)

    def _build_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()
        n = self.ntask_var.get()
        self.task_entries = []
        hdrs = ["Task Name", "Duration", "Predecessors (comma-sep)"]
        for c, h in enumerate(hdrs):
            lbl(self.table_frame, h, 9, bold=True, color=ACCENT2).grid(
                row=0, column=c, padx=6, pady=2)
        for i in range(n):
            row_vars = []
            defaults = [f"T{i+1}", "1", ""]
            widths = [8, 6, 20]
            for c in range(3):
                var = tk.StringVar(value=defaults[c])
                e = tk.Entry(self.table_frame, textvariable=var,
                             width=widths[c], bg=BG_DARK, fg=TEXT_PRI,
                             insertbackground=TEXT_PRI, relief="flat",
                             font=("Consolas", 9),
                             highlightbackground=BORDER, highlightthickness=1)
                e.grid(row=i+1, column=c, padx=4, pady=2)
                row_vars.append(var)
            self.task_entries.append(row_vars)

    def _resize_table(self):
        self._build_table()

    def _example(self):
        # classic CPM example
        example = [
            ("A","3",""),("B","4",""),("C","2","A"),
            ("D","5","A"),("E","3","B,C"),("F","4","D,E"),
        ]
        self.ntask_var.set(len(example))
        self._build_table()
        for i, (name,dur,pred) in enumerate(example):
            if i < len(self.task_entries):
                self.task_entries[i][0].set(name)
                self.task_entries[i][1].set(dur)
                self.task_entries[i][2].set(pred)

    def _run(self):
        tasks = {}
        for row in self.task_entries:
            name = row[0].get().strip()
            try:
                dur  = float(row[1].get().strip())
            except ValueError:
                messagebox.showerror("Error", f"Invalid duration for task '{name}'")
                return
            preds_raw = row[2].get().strip()
            preds = [p.strip() for p in preds_raw.split(",") if p.strip()]
            tasks[name] = {"dur": dur, "preds": preds}

        task_names = list(tasks.keys())
        # topological sort
        in_deg = {t: 0 for t in task_names}
        for t, data in tasks.items():
            for p in data["preds"]:
                if p not in tasks:
                    messagebox.showerror("Error",f"Unknown predecessor '{p}'")
                    return
        # Kahn's
        in_deg = {t: len(tasks[t]["preds"]) for t in task_names}
        queue = [t for t in task_names if in_deg[t]==0]
        topo = []
        while queue:
            u = queue.pop(0)
            topo.append(u)
            for t in task_names:
                if u in tasks[t]["preds"]:
                    in_deg[t] -= 1
                    if in_deg[t] == 0:
                        queue.append(t)
        if len(topo) != len(task_names):
            messagebox.showerror("Error","Cycle detected in task dependencies!")
            return

        # earliest start / finish
        ES = {t: 0.0 for t in task_names}
        EF = {}
        for t in topo:
            if tasks[t]["preds"]:
                ES[t] = max(EF[p] for p in tasks[t]["preds"])
            EF[t] = ES[t] + tasks[t]["dur"]

        project_dur = max(EF.values())

        # latest start / finish
        LF = {t: project_dur for t in task_names}
        LS = {}
        for t in reversed(topo):
            successors = [s for s in task_names if t in tasks[s]["preds"]]
            if successors:
                LF[t] = min(LS[s] for s in successors)
            LS[t] = LF[t] - tasks[t]["dur"]

        float_slack = {t: LS[t]-ES[t] for t in task_names}
        critical = [t for t in task_names if abs(float_slack[t]) < 1e-9]

        rep = []
        rep.append(("═"*70 + "\n", "data"))
        rep.append(("  POTENTIEL MÉTRA — CRITICAL PATH METHOD REPORT\n", "head"))
        rep.append(("═"*70 + "\n\n", "data"))
        rep.append((f"  Tasks : {len(task_names)}    Project Duration : {project_dur:.2f} units\n\n","value"))
        rep.append(("  Full Schedule Table:\n","head"))
        rep.append(("  "+"-"*66+"\n","data"))
        rep.append((f"  {'Task':<8}{'Dur':>6}{'ES':>7}{'EF':>7}{'LS':>7}{'LF':>7}{'Slack':>8}  {'Critical?'}\n","warn"))
        rep.append(("  "+"-"*66+"\n","data"))
        for t in topo:
            is_crit = t in critical
            tag = "err" if is_crit else "data"
            crit_str = "★ YES" if is_crit else "no"
            rep.append((f"  {t:<8}{tasks[t]['dur']:>6.1f}{ES[t]:>7.1f}{EF[t]:>7.1f}"
                        f"{LS[t]:>7.1f}{LF[t]:>7.1f}{float_slack[t]:>8.1f}  {crit_str}\n", tag))
        rep.append(("  "+"-"*66+"\n\n","data"))
        rep.append(("  Critical Path:\n","head"))
        rep.append(("  " + " → ".join(critical) + "\n\n","err"))
        rep.append((f"  ► Minimum Project Duration = {project_dur:.2f} units\n","value"))
        rep.append(("\n" + "═"*70 + "\n","data"))
        self.show_report(rep)

# ──────────────────────────────────────────────────────────────────────────────
# TRANSPORT PROBLEM base
# ──────────────────────────────────────────────────────────────────────────────
class TransportInputPanel(tk.Frame):
    """Reusable panel for m suppliers × n customers transport problems."""
    def __init__(self, parent, default_m=3, default_n=4, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        self.m_var = tk.IntVar(value=default_m)
        self.n_var = tk.IntVar(value=default_n)

        ctrl = tk.Frame(self, bg=BG_DARK)
        ctrl.pack(fill="x")
        lbl(ctrl, "Suppliers (m):", color=TEXT_SEC).pack(side="left")
        tk.Spinbox(ctrl, from_=2, to=10, textvariable=self.m_var, width=4,
                   bg=BG_INPUT, fg=TEXT_PRI, relief="flat").pack(side="left",padx=4)
        lbl(ctrl, "  Customers (n):", color=TEXT_SEC).pack(side="left")
        tk.Spinbox(ctrl, from_=2, to=10, textvariable=self.n_var, width=4,
                   bg=BG_INPUT, fg=TEXT_PRI, relief="flat").pack(side="left",padx=4)
        styled_btn(ctrl, "Resize", self._resize, ACCENT2, 10).pack(side="left",padx=4)
        styled_btn(ctrl, "Random", self._random, ACCENT3, 10).pack(side="left",padx=4)

        self.body = tk.Frame(self, bg=BG_DARK)
        self.body.pack(fill="both", expand=True, pady=6)
        self._resize()

    def _resize(self):
        for w in self.body.winfo_children():
            w.destroy()
        m = self.m_var.get()
        n = self.n_var.get()
        sup_lbls = [f"S{i+1}" for i in range(m)]
        cus_lbls = [f"C{j+1}" for j in range(n)]

        lbl(self.body, "Cost Matrix (suppliers × customers):", 9,
            bold=True, color=ACCENT2).pack(anchor="w")
        self.cost_mat = MatrixInput(self.body, m, n,
                                    labels=sup_lbls, col_labels=cus_lbls)
        self.cost_mat.pack(anchor="w", pady=4)

        row = tk.Frame(self.body, bg=BG_DARK)
        row.pack(fill="x", pady=2)

        col1 = tk.Frame(row, bg=BG_DARK)
        col1.pack(side="left", padx=8)
        lbl(col1, "Supply (one per row):", 9, bold=True, color=ACCENT2).pack(anchor="w")
        self.supply_vars = []
        for i in range(m):
            v = tk.StringVar(value="10")
            f = tk.Frame(col1, bg=BG_DARK)
            f.pack(fill="x")
            lbl(f, f"{sup_lbls[i]}:", 9, color=TEXT_SEC).pack(side="left")
            tk.Entry(f, textvariable=v, width=6, bg=BG_DARK, fg=TEXT_PRI,
                     relief="flat", font=("Consolas",9),
                     highlightbackground=BORDER, highlightthickness=1,
                     insertbackground=TEXT_PRI).pack(side="left", padx=2)
            self.supply_vars.append(v)

        col2 = tk.Frame(row, bg=BG_DARK)
        col2.pack(side="left", padx=8)
        lbl(col2, "Demand (one per col):", 9, bold=True, color=ACCENT2).pack(anchor="w")
        self.demand_vars = []
        for j in range(n):
            v = tk.StringVar(value="8")
            f = tk.Frame(col2, bg=BG_DARK)
            f.pack(fill="x")
            lbl(f, f"{cus_lbls[j]}:", 9, color=TEXT_SEC).pack(side="left")
            tk.Entry(f, textvariable=v, width=6, bg=BG_DARK, fg=TEXT_PRI,
                     relief="flat", font=("Consolas",9),
                     highlightbackground=BORDER, highlightthickness=1,
                     insertbackground=TEXT_PRI).pack(side="left", padx=2)
            self.demand_vars.append(v)

    def _random(self):
        m = self.m_var.get()
        n = self.n_var.get()
        costs = [[random.randint(1,20) for _ in range(n)] for _ in range(m)]
        self.cost_mat.set_matrix(costs)
        total = (m + n) * 8
        sup_raw = [random.randint(8,20) for _ in range(m-1)]
        sup_raw.append(total - sum(sup_raw))
        dem_raw = [random.randint(8,20) for _ in range(n-1)]
        dem_raw.append(sum(sup_raw) - sum(dem_raw))
        for i, v in enumerate(self.supply_vars):
            v.set(str(max(1, sup_raw[i])))
        for j, v in enumerate(self.demand_vars):
            v.set(str(max(1, dem_raw[j])))

    def get_data(self):
        m = self.m_var.get()
        n = self.n_var.get()
        costs = self.cost_mat.get_float_matrix()
        supply = []
        for v in self.supply_vars:
            try: supply.append(float(v.get()))
            except ValueError: supply.append(0.0)
        demand = []
        for v in self.demand_vars:
            try: demand.append(float(v.get()))
            except ValueError: demand.append(0.0)
        return m, n, costs, supply, demand

    def balance(self):
        m, n, costs, supply, demand = self.get_data()
        S, D = sum(supply), sum(demand)
        if abs(S-D) > 1e-6:
            # add dummy
            if S > D:
                demand.append(S-D)
                for row in costs:
                    row.append(0)
                n += 1
            else:
                supply.append(D-S)
                costs.append([0]*n)
                m += 1
        return m, n, costs, supply, demand, (S, D)

# ──────────────────────────────────────────────────────────────────────────────
# 7. NORTH-WEST CORNER
# ──────────────────────────────────────────────────────────────────────────────
class NorthWestScreen(AlgoScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app, "North-West Corner — Transportation", "#f97316")

    def _build_body(self):
        self.section(self.body, "Transportation Problem Input")
        self.tip = TransportInputPanel(self.body)
        self.tip.pack(fill="x")
        self.section(self.body, "Run")
        styled_btn(self.body, "▶  Run North-West Corner", self._run, "#f97316", 26).pack(pady=8)

    def _run(self):
        m, n, costs, supply, demand, (S, D) = self.tip.balance()
        s = supply[:]
        d = demand[:]
        alloc = [[0.0]*n for _ in range(m)]
        i = j = 0
        while i < m and j < n:
            amt = min(s[i], d[j])
            alloc[i][j] = amt
            s[i] -= amt
            d[j] -= amt
            if s[i] == 0 and d[j] == 0:
                i += 1; j += 1
            elif s[i] == 0:
                i += 1
            else:
                j += 1

        total = sum(alloc[i][j]*costs[i][j] for i in range(m) for j in range(n))
        self._report(m, n, alloc, costs, total, S, D)

    def _report(self, m, n, alloc, costs, total, S, D):
        rep = []
        rep.append(("═"*64 + "\n","data"))
        rep.append(("  NORTH-WEST CORNER — TRANSPORT REPORT\n","head"))
        rep.append(("═"*64 + "\n\n","data"))
        rep.append((f"  Total Supply={S:.1f}   Total Demand={D:.1f}\n\n","data"))
        if abs(S-D) > 1e-6:
            rep.append(("  (Dummy row/col added to balance problem)\n\n","warn"))
        rep.append(("  Allocation Table  (allocation × unit cost):\n","head"))
        rep.append(("  "+"-"*58+"\n","data"))
        header = "  " + " "*8 + "".join(f"   C{j+1:>2}  " for j in range(n)) + "\n"
        rep.append((header,"warn"))
        rep.append(("  "+"-"*58+"\n","data"))
        for i in range(m):
            line = f"  S{i+1:>2}   "
            for j in range(n):
                a = alloc[i][j]
                c = costs[i][j]
                cell = f" {a:>3.0f}×{c:<3.0f}" if a > 0 else "   —    "
                line += cell
            rep.append((line+"\n","data"))
        rep.append(("  "+"-"*58+"\n\n","data"))
        rep.append(("  Allocated cells:\n","head"))
        for i in range(m):
            for j in range(n):
                if alloc[i][j] > 0:
                    cost_ij = alloc[i][j]*costs[i][j]
                    rep.append((f"    S{i+1} → C{j+1}:  {alloc[i][j]:.1f} units  × {costs[i][j]:.1f}  = {cost_ij:.1f}\n","ok"))
        rep.append(("\n",""))
        rep.append((f"  ► Initial Basic Feasible Solution Cost = {total:.4f}\n","value"))
        rep.append(("\n  NOTE: This is a starting solution. Use MODI / stepping-stone\n","warn"))
        rep.append(("        method to optimise further.\n","warn"))
        rep.append(("\n"+"═"*64+"\n","data"))
        self.show_report(rep)

# ──────────────────────────────────────────────────────────────────────────────
# 8. LEAST COST METHOD
# ──────────────────────────────────────────────────────────────────────────────
class LeastCostScreen(AlgoScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Least Cost — Transportation", "#ec4899")

    def _build_body(self):
        self.section(self.body, "Transportation Problem Input")
        self.tip = TransportInputPanel(self.body)
        self.tip.pack(fill="x")
        self.section(self.body, "Run")
        styled_btn(self.body, "▶  Run Least Cost", self._run, "#ec4899", 24).pack(pady=8)

    def _run(self):
        m, n, costs, supply, demand, (S, D) = self.tip.balance()
        s = supply[:]
        d = demand[:]
        alloc = [[0.0]*n for _ in range(m)]
        steps = []

        while True:
            # find min cost cell among remaining
            min_c = float('inf')
            best = None
            for i in range(m):
                for j in range(n):
                    if s[i] > 0 and d[j] > 0:
                        if costs[i][j] < min_c:
                            min_c = costs[i][j]
                            best = (i, j)
            if best is None:
                break
            i, j = best
            amt = min(s[i], d[j])
            alloc[i][j] = amt
            s[i] -= amt
            d[j] -= amt
            steps.append((i, j, amt, costs[i][j]))

        total = sum(alloc[i][j]*costs[i][j] for i in range(m) for j in range(n))

        rep = []
        rep.append(("═"*64+"\n","data"))
        rep.append(("  LEAST COST METHOD — TRANSPORT REPORT\n","head"))
        rep.append(("═"*64+"\n\n","data"))
        rep.append((f"  Total Supply={S:.1f}   Total Demand={D:.1f}\n\n","data"))
        if abs(S-D) > 1e-6:
            rep.append(("  (Dummy added to balance)\n\n","warn"))
        rep.append(("  Allocation Steps (lowest cost first):\n","head"))
        rep.append(("  "+"-"*50+"\n","data"))
        for step, (i,j,amt,c) in enumerate(steps,1):
            rep.append((f"  Step {step}: Allocate {amt:.1f} to S{i+1}→C{j+1}  (cost={c:.1f})\n","ok"))
        rep.append(("  "+"-"*50+"\n\n","data"))
        rep.append(("  Final Allocation Table:\n","head"))
        rep.append(("  "+"-"*54+"\n","data"))
        header = "  " + " "*6 + "".join(f"   C{j+1:>2}  " for j in range(n)) + "\n"
        rep.append((header,"warn"))
        rep.append(("  "+"-"*54+"\n","data"))
        for i in range(m):
            line = f"  S{i+1:>2} "
            for j in range(n):
                a = alloc[i][j]
                c = costs[i][j]
                cell = f" {a:>3.0f}×{c:<3.0f}" if a > 0 else "   —    "
                line += cell
            rep.append((line+"\n","data"))
        rep.append(("  "+"-"*54+"\n\n","data"))
        for i in range(m):
            for j in range(n):
                if alloc[i][j] > 0:
                    rep.append((f"    S{i+1} → C{j+1}: {alloc[i][j]:.1f} × {costs[i][j]:.1f} = {alloc[i][j]*costs[i][j]:.1f}\n","data"))
        rep.append(("\n",""))
        rep.append((f"  ► Initial BFS Cost (Least Cost) = {total:.4f}\n","value"))
        rep.append(("\n  NOTE: Least Cost gives a better starting point than North-West.\n","warn"))
        rep.append(("        Optimise with MODI/Vogel if needed.\n","warn"))
        rep.append(("\n"+"═"*64+"\n","data"))
        self.show_report(rep)

# ──────────────────────────────────────────────────────────────────────────────
# 9. SIMPLEX  (max  cᵀx  s.t.  Ax ≤ b,  x ≥ 0)
# ──────────────────────────────────────────────────────────────────────────────
class SimplexScreen(AlgoScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Simplex — Linear Programming", "#a78bfa")

    def _build_body(self):
        self.section(self.body, "Problem Setup")
        note = ("Maximise:  c₁x₁ + c₂x₂ + … + cₙxₙ\n"
                "Subject to:  Aᵢ·x ≤ bᵢ  (all constraints ≤ form)\n"
                "             x ≥ 0")
        lbl(self.body, note, 9, color=TEXT_SEC).pack(anchor="w", pady=4)

        ctrl = tk.Frame(self.body, bg=BG_DARK)
        ctrl.pack(fill="x")
        lbl(ctrl, "Variables (n):", color=TEXT_SEC).pack(side="left")
        self.nvar_v = tk.IntVar(value=2)
        tk.Spinbox(ctrl, from_=1, to=8, textvariable=self.nvar_v, width=4,
                   bg=BG_INPUT, fg=TEXT_PRI, relief="flat").pack(side="left",padx=4)
        lbl(ctrl, "  Constraints (m):", color=TEXT_SEC).pack(side="left")
        self.ncon_v = tk.IntVar(value=3)
        tk.Spinbox(ctrl, from_=1, to=8, textvariable=self.ncon_v, width=4,
                   bg=BG_INPUT, fg=TEXT_PRI, relief="flat").pack(side="left",padx=4)
        styled_btn(ctrl, "Resize", self._resize, "#a78bfa", 10).pack(side="left",padx=4)
        styled_btn(ctrl, "Example", self._example, ACCENT3, 10).pack(side="left",padx=4)

        self.form_frame = tk.Frame(self.body, bg=BG_DARK)
        self.form_frame.pack(fill="x", pady=6)
        self._resize()
        self.section(self.body, "Run")
        row = tk.Frame(self.body, bg=BG_DARK)
        row.pack()
        self.obj_var = tk.StringVar(value="max")
        tk.Radiobutton(row, text="Maximise", variable=self.obj_var, value="max",
                       bg=BG_DARK, fg=TEXT_PRI, selectcolor=BG_INPUT,
                       font=("Segoe UI",9)).pack(side="left",padx=6)
        tk.Radiobutton(row, text="Minimise", variable=self.obj_var, value="min",
                       bg=BG_DARK, fg=TEXT_PRI, selectcolor=BG_INPUT,
                       font=("Segoe UI",9)).pack(side="left",padx=6)
        styled_btn(self.body, "▶  Run Simplex", self._run, "#a78bfa", 24).pack(pady=8)

    def _resize(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        n = self.nvar_v.get()
        m = self.ncon_v.get()
        var_lbls = [f"x{i+1}" for i in range(n)]
        con_lbls = [f"C{i+1}" for i in range(m)]

        lbl(self.form_frame, "Objective coefficients  c:", 9, bold=True, color=ACCENT2).pack(anchor="w")
        self.c_mat = MatrixInput(self.form_frame, 1, n,
                                  labels=["c"], col_labels=var_lbls)
        self.c_mat.pack(anchor="w", pady=4)

        lbl(self.form_frame, "Constraint matrix  A  (m × n):", 9, bold=True, color=ACCENT2).pack(anchor="w")
        self.A_mat = MatrixInput(self.form_frame, m, n,
                                  labels=con_lbls, col_labels=var_lbls)
        self.A_mat.pack(anchor="w", pady=4)

        lbl(self.form_frame, "Right-hand side  b:", 9, bold=True, color=ACCENT2).pack(anchor="w")
        self.b_mat = MatrixInput(self.form_frame, m, 1,
                                  labels=con_lbls, col_labels=["b"])
        self.b_mat.pack(anchor="w", pady=4)

    def _example(self):
        self.nvar_v.set(2); self.ncon_v.set(3); self._resize()
        self.c_mat.set_matrix([[5, 4]])
        self.A_mat.set_matrix([[6,4],[1,2],[1,0]])
        self.b_mat.set_matrix([[24],[6],[4]])

    def _run(self):
        n = self.nvar_v.get()
        m = self.ncon_v.get()
        mode = self.obj_var.get()

        c_raw = self.c_mat.get_float_matrix()
        A_raw = self.A_mat.get_float_matrix()
        b_raw = self.b_mat.get_float_matrix()

        c = c_raw[0]
        A = A_raw
        b = [b_raw[i][0] for i in range(m)]

        if any(bv < 0 for bv in b):
            messagebox.showerror("Error","All b values must be ≥ 0 for standard Simplex.")
            return

        # Minimise: negate objective
        if mode == "min":
            c = [-ci for ci in c]

        # Build tableau (m × n+m+1)
        tot = n + m  # decision + slack
        tableau = []
        for i in range(m):
            row = A[i][:n] + [0.0]*m + [b[i]]
            row[n+i] = 1.0   # slack variable
            tableau.append(row)
        # objective row (negated for max)
        obj_row = [-ci for ci in c] + [0.0]*(m+1)
        tableau.append(obj_row)

        iterations = []
        MAX_ITER = 200
        for it in range(MAX_ITER):
            obj = tableau[-1]
            # pivot column: most negative in obj row (excluding RHS)
            pivot_col = min(range(tot), key=lambda j: obj[j])
            if obj[pivot_col] >= -1e-9:
                break  # optimal

            # pivot row: min ratio test
            min_ratio = float('inf')
            pivot_row = -1
            for i in range(m):
                if tableau[i][pivot_col] > 1e-9:
                    ratio = tableau[i][-1] / tableau[i][pivot_col]
                    if ratio < min_ratio:
                        min_ratio = ratio
                        pivot_row = i
            if pivot_row == -1:
                messagebox.showinfo("Simplex","Problem is unbounded.")
                return

            pivot_val = tableau[pivot_row][pivot_col]
            iterations.append((it+1, pivot_row, pivot_col, pivot_val, min_ratio))

            # row reduce
            tableau[pivot_row] = [x/pivot_val for x in tableau[pivot_row]]
            for i in range(m+1):
                if i != pivot_row:
                    factor = tableau[i][pivot_col]
                    tableau[i] = [tableau[i][k] - factor*tableau[pivot_row][k]
                                  for k in range(tot+1)]

        # extract solution
        solution = [0.0]*tot
        for j in range(tot):
            col = [tableau[i][j] for i in range(m)]
            obj_c = tableau[-1][j]
            if col.count(1.0) == 1 and col.count(0.0) == m-1 and abs(obj_c) < 1e-9:
                row_idx = col.index(1.0)
                solution[j] = tableau[row_idx][-1]

        z = tableau[-1][-1]
        if mode == "min":
            z = -z

        var_lbls = [f"x{i+1}" for i in range(n)]
        slack_lbls = [f"s{i+1}" for i in range(m)]

        rep = []
        rep.append(("═"*60+"\n","data"))
        rep.append(("  SIMPLEX — LINEAR PROGRAMMING REPORT\n","head"))
        rep.append(("═"*60+"\n\n","data"))
        obj_str = ("Maximise" if mode=="max" else "Minimise")
        c_disp = c if mode=="max" else [-ci for ci in c]
        rep.append((f"  Objective: {obj_str}  Z = "+" + ".join(f"{c_disp[i]:.2f}·{var_lbls[i]}" for i in range(n))+"\n\n","data"))
        rep.append(("  Pivot Iterations:\n","head"))
        rep.append(("  "+"-"*48+"\n","data"))
        rep.append((f"  {'Iter':>5}  {'Row':>5}  {'Col':>5}  {'Pivot':>8}  {'Ratio':>8}\n","warn"))
        rep.append(("  "+"-"*48+"\n","data"))
        for it, pr, pc, pv, ratio in iterations:
            lbl_c = var_lbls[pc] if pc < n else slack_lbls[pc-n]
            rep.append((f"  {it:>5}  {pr+1:>5}  {lbl_c:>5}  {pv:>8.4f}  {ratio:>8.4f}\n","data"))
        rep.append(("  "+"-"*48+"\n\n","data"))
        rep.append(("  Optimal Solution:\n","head"))
        for i in range(n):
            rep.append((f"    {var_lbls[i]} = {solution[i]:.6f}\n","ok"))
        rep.append(("\n",""))
        rep.append((f"  ► Optimal Value  Z = {z:.6f}\n","value"))
        rep.append(("\n  Slack Variables:\n","head"))
        for i in range(m):
            rep.append((f"    {slack_lbls[i]} = {solution[n+i]:.6f}\n","data"))
        rep.append(("\n"+"═"*60+"\n","data"))
        self.show_report(rep)

# ──────────────────────────────────────────────────────────────────────────────
# WELCOME SCREEN (New Landing Page)
# ──────────────────────────────────────────────────────────────────────────────
class WelcomeScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_DARK)
        self.app = app
        self._build()

    def _build(self):
        # A master wrapper to keep everything perfectly centered vertically
        wrapper = tk.Frame(self, bg=BG_DARK)
        wrapper.pack(expand=True, fill="both", pady=50)

        # 1. Title Block
        title_text = ("Development of a Desktop Python Application Integrating Graph Algorithms:\n"
                      "Optimizing Scheduling & Improving Production Flows in an Automated Factory\n"
                      "Industry 4.0: Sector of electrical & Electronic systems engineering")
        tk.Label(wrapper, text=title_text, bg=BG_DARK, fg="#79c0ff",
                 font=("Segoe UI", 16, "bold"), justify="center").pack(pady=(20, 30))

        # 2. Subtitle Block
        tk.Label(wrapper, text="Mohammadia School of Engineers (EMI)",
                 bg=BG_DARK, fg=ACCENT, font=("Segoe UI", 15, "bold")).pack(pady=(0, 40))

        # 3. Central Start Button (Following the red arrow from the doodle)
        btn_frame = card_frame(wrapper, padx=40, pady=30)
        btn_frame.pack(pady=(0, 60))

        tk.Label(btn_frame, text="Operational Research", bg=BG_CARD, fg=TEXT_PRI,
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))
        styled_btn(btn_frame, "▶ START", self.app.show_home, ACCENT2, 20).pack()

        # 4. Footer Layout (Student and Professor side-by-side)
        footer = tk.Frame(wrapper, bg=BG_DARK)
        footer.pack(fill="x", padx=40)

        # Student Profile Box (Left)
        frm_student = card_frame(footer, padx=20, pady=15)
        frm_student.pack(side="left")
        tk.Label(frm_student, text="Mohammed Amine SABBARI", bg=BG_CARD, fg=RED_ACC,
                 font=("Segoe UI", 12, "bold")).pack()

        # Professor Profile Box (Right)
        frm_prof = card_frame(footer, padx=20, pady=15)
        frm_prof.pack(side="right")
        tk.Label(frm_prof, text="Dr. EL MKHALET MOUNA", bg=BG_CARD, fg=RED_ACC,
                 font=("Segoe UI", 12, "bold")).pack()

# ──────────────────────────────────────────────────────────────────────────────
# HOME SCREEN
# ──────────────────────────────────────────────────────────────────────────────
class HomeScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_DARK)
        self.app = app
        self._build()

    def _build(self):
        # ── Hero ──────────────────────────────────────────────────────────────
        hero = tk.Frame(self, bg="#0d1f3c", pady=24)
        hero.pack(fill="x")
        tk.Label(hero,
                 text="Operational Research Toolkit",
                 bg="#0d1f3c", fg="#79c0ff",
                 font=("Segoe UI", 20, "bold")).pack()
        tk.Label(hero,
                 text="Mohammadia School of Engineers (EMI)  ·  Dr. EL MKHALET MOUNA",
                 bg="#0d1f3c", fg=TEXT_SEC,
                 font=("Segoe UI", 10)).pack(pady=(4,0))

        # ── Subtitle ──────────────────────────────────────────────────────────
        sub = tk.Frame(self, bg=BG_DARK, pady=8)
        sub.pack(fill="x")
        tk.Label(sub,
                 text="Select an algorithm to begin",
                 bg=BG_DARK, fg=TEXT_SEC,
                 font=("Segoe UI", 11)).pack()

        # ── Algorithm grid ────────────────────────────────────────────────────
        grid = tk.Frame(self, bg=BG_DARK, pady=10)
        grid.pack(expand=True)

        for idx, (name, key, color) in enumerate(BTN_ALGOS):
            r, c = divmod(idx, 3)
            card = card_frame(grid, padx=2, pady=2)
            card.grid(row=r, column=c, padx=10, pady=8, sticky="nsew")

            tk.Label(card, text=_algo_icon(key), bg=BG_CARD,
                     fg=color, font=("Segoe UI", 22)).pack(pady=(14,2))
            tk.Label(card, text=name, bg=BG_CARD, fg=TEXT_PRI,
                     font=("Segoe UI", 11, "bold")).pack()
            tk.Label(card, text=_algo_desc(key), bg=BG_CARD, fg=TEXT_SEC,
                     font=("Segoe UI", 8), wraplength=160).pack(pady=(2,10))
            btn = tk.Button(card, text="Open →",
                            command=lambda k=key: self.app.show_algo(k),
                            bg=color, fg="white", relief="flat",
                            font=("Segoe UI", 9, "bold"),
                            cursor="hand2", width=12, pady=4,
                            activebackground=color)
            btn.pack(pady=(0,12))

def _algo_icon(key):
    icons = {
        "welsh_powell":"🎨","kruskal":"🌲","dijkstra":"🗺️",
        "bellman_ford":"⚡","ford_fulkerson":"🌊","potentiel":"📅",
        "northwest":"🧭","leastcost":"💰","simplex":"📐",
    }
    return icons.get(key, "🔧")

def _algo_desc(key):
    d = {
        "welsh_powell": "Graph coloring with minimum colors",
        "kruskal":      "Minimum spanning tree (greedy)",
        "dijkstra":     "Shortest path (non-negative weights)",
        "bellman_ford": "Shortest path (negative weights OK)",
        "ford_fulkerson":"Maximum flow in a network",
        "potentiel":    "Critical path / project scheduling",
        "northwest":    "Initial transport solution (NW)",
        "leastcost":    "Initial transport solution (Least Cost)",
        "simplex":      "Linear programming optimisation",
    }
    return d.get(key, "")

# ──────────────────────────────────────────────────────────────────────────────
# SPLASH SCREEN
# ──────────────────────────────────────────────────────────────────────────────
class SplashScreen(tk.Toplevel):
    def __init__(self, parent, on_done):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(bg="#0d1f3c")
        w, h = 480, 300
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        tk.Label(self, text="⚙", bg="#0d1f3c", fg=ACCENT2,
                 font=("Segoe UI", 48)).pack(pady=(30,4))
        tk.Label(self, text="Operational Research Toolkit",
                 bg="#0d1f3c", fg="#79c0ff",
                 font=("Segoe UI", 16, "bold")).pack()
        tk.Label(self, text="Mohammadia School of Engineers",
                 bg="#0d1f3c", fg=TEXT_SEC,
                 font=("Segoe UI", 10)).pack(pady=2)
        tk.Label(self, text="Dr. EL MKHALET MOUNA",
                 bg="#0d1f3c", fg=ACCENT3,
                 font=("Segoe UI", 10, "italic")).pack()

        self.pb_var = tk.DoubleVar(value=0)
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Splash.Horizontal.TProgressbar",
                        background=ACCENT2,
                        troughcolor="#1c2128",
                        bordercolor="#1c2128",
                        thickness=6)
        pb = ttk.Progressbar(self, variable=self.pb_var,
                             maximum=100, length=300,
                             style="Splash.Horizontal.TProgressbar")
        pb.pack(pady=20)
        self.status = tk.Label(self, text="Loading…", bg="#0d1f3c", fg=TEXT_SEC,
                                font=("Segoe UI",8))
        self.status.pack()

        self.on_done = on_done
        self._progress(0)

    def _progress(self, val):
        msgs = {0:"Initializing…",30:"Loading algorithms…",
                60:"Building interface…",85:"Almost ready…",100:"Done!"}
        self.pb_var.set(val)
        if val in msgs:
            self.status.config(text=msgs[val])
        if val < 100:
            self.after(30, self._progress, val+2)
        else:
            self.after(400, self._finish)

    def _finish(self):
        self.destroy()
        self.on_done()

# ──────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ──────────────────────────────────────────────────────────────────────────────
class App:
    SCREENS = {
        "welsh_powell": WelshPowellScreen,
        "kruskal":      KruskalScreen,
        "dijkstra":     DijkstraScreen,
        "bellman_ford": BellmanFordScreen,
        "ford_fulkerson":FordFulkersonScreen,
        "potentiel":    PotentielScreen,
        "northwest":    NorthWestScreen,
        "leastcost":    LeastCostScreen,
        "simplex":      SimplexScreen,
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Operational Research Toolkit — EMI")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1050x760")
        self.root.minsize(900, 650)

        # Main scrollable container
        self.main_canvas = tk.Canvas(self.root, bg=BG_DARK, highlightthickness=0)
        self.scrollbar   = tk.Scrollbar(self.root, orient="vertical",
                                         command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)

        self.container = tk.Frame(self.main_canvas, bg=BG_DARK)
        self.canvas_win = self.main_canvas.create_window(
            (0, 0), window=self.container, anchor="nw")
        self.container.bind("<Configure>", self._on_frame_config)
        self.main_canvas.bind("<Configure>", self._on_canvas_config)
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.current_screen = None
        # Show splash then transition straight to Welcome Screen
        SplashScreen(self.root, self._show_welcome_after_splash)

    def _on_frame_config(self, e):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def _on_canvas_config(self, e):
        self.main_canvas.itemconfig(self.canvas_win, width=e.width)

    def _on_mousewheel(self, e):
        self.main_canvas.yview_scroll(int(-1*(e.delta/120)), "units")

    def _show_welcome_after_splash(self):
        self.root.deiconify()
        self.show_welcome()

    def show_welcome(self):
        self._clear()
        self.current_screen = WelcomeScreen(self.container, self)
        self.current_screen.pack(fill="both", expand=True)
        self.main_canvas.yview_moveto(0)

    def show_home(self):
        self._clear()
        self.current_screen = HomeScreen(self.container, self)
        self.current_screen.pack(fill="both", expand=True)
        self.main_canvas.yview_moveto(0)

    def show_algo(self, key):
        cls = self.SCREENS.get(key)
        if not cls:
            return
        self._clear()
        self.current_screen = cls(self.container, self)
        self.current_screen.pack(fill="both", expand=True)
        self.main_canvas.yview_moveto(0)

    def _clear(self):
        if self.current_screen:
            self.current_screen.destroy()
        for w in self.container.winfo_children():
            w.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
