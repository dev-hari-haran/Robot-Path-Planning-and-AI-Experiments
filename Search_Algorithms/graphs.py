import tkinter as tk
from tkinter import ttk, messagebox
import random, math, heapq
from collections import deque

# ================= GRAPH DATA STRUCTURE =================
class Graph:
    def __init__(self):
        self.nodes = {}  # {name: (x, y, heuristic)}
        self.edges = {}  # {name: [[neighbor, cost]]}
        self.directed = False

    def add_node(self, n, x, y, h=0):
        self.nodes[n] = [x, y, h]
        self.edges.setdefault(n, [])

    def add_edge(self, u, v, c):
        self.edges[u].append([v, c])
        if not self.directed:
            self.edges.setdefault(v, [])
            self.edges[v].append([u, c])

# ================= SEARCH ALGORITHMS =================
def get_h(g, n): return g.nodes[n][2]

def run_algorithm(g, s, t, mode):
    """
    Unified search engine for different pathfinding strategies.
    """
    # --- Priority Queue Based Algorithms ---
    if mode in ["A*", "Dijkstra", "Greedy"]:
        pq = [(get_h(g, s), 0, s, [s])]
        visited = {}
        
        while pq:
            f, g_cost, n, p = heapq.heappop(pq)
            if n == t: return p
            
            if n in visited and visited[n] <= g_cost: continue
            visited[n] = g_cost
            
            for nb, w in g.edges.get(n, []):
                new_g = g_cost + w
                if mode == "A*": 
                    priority = new_g + get_h(g, nb)
                elif mode == "Dijkstra": 
                    priority = new_g
                else: # Greedy Best-First Search
                    priority = get_h(g, nb)
                
                heapq.heappush(pq, (priority, new_g, nb, p + [nb]))

    # --- Breadth-First Search (Queue) ---
    elif mode == "BFS":
        queue = deque([(s, [s])])
        visited = {s}
        while queue:
            n, p = queue.popleft()
            if n == t: return p
            for nb, w in g.edges.get(n, []):
                if nb not in visited:
                    visited.add(nb)
                    queue.append((nb, p + [nb]))

    # --- Depth-First Search (Stack) ---
    elif mode == "DFS":
        stack = [(s, [s])]
        visited = set()
        while stack:
            n, p = stack.pop()
            if n == t: return p
            if n not in visited:
                visited.add(n)
                # Reversed neighbors for a more standard left-to-right exploration
                for nb, w in reversed(g.edges.get(n, [])):
                    if nb not in visited:
                        stack.append((nb, p + [nb]))
    return None

# ================= APP =================
class App:
    def __init__(self, root):
        self.root = root
        root.geometry("1300x750")
        root.title("Graph Search Interactive Lab")

        self.graph = Graph()
        self.mode = "node"
        self.node_count = 0
        self.selected_node = None
        self.start_node = None
        self.goal_node = None
        self.node_radius = 20

        main = tk.Frame(root)
        main.pack(fill="both", expand=True)

        # ===== LEFT PANEL (CONTROLS) =====
        panel = tk.Frame(main, width=280, bg="#eef2f5")
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)

        tk.Label(panel, text="Graph Control", font=("Segoe UI", 16, "bold"), bg="#eef2f5").pack(pady=10)

        self.mode_var = tk.StringVar(value="Mode: Add Node")
        tk.Label(panel, textvariable=self.mode_var, font=("Segoe UI", 11, "bold"), bg="#eef2f5", fg="#2a6").pack(pady=5)

        self.dir_var = tk.BooleanVar()
        ttk.Checkbutton(panel, text="Directed Graph", variable=self.dir_var, 
                        command=self.toggle_direction).pack()

        def btn(txt, m):
            return tk.Button(panel, text=txt, height=2, command=lambda: self.set_mode(m))

        btn("➕ Add Node", "node").pack(fill="x", padx=20, pady=3)
        btn("🔗 Add Edge", "edge").pack(fill="x", padx=20, pady=3)
        btn("🟢 Set Start", "start").pack(fill="x", padx=20, pady=3)
        btn("🔴 Set Goal", "goal").pack(fill="x", padx=20, pady=3)

        tk.Button(panel, text="🎲 Random 10 Nodes", command=self.random_graph).pack(fill="x", padx=20, pady=10)

        # Updated Algorithm Dropdown
        tk.Label(panel, text="Search Strategy:", bg="#eef2f5").pack()
        self.alg = ttk.Combobox(panel, values=["A*", "Dijkstra", "Greedy", "BFS", "DFS"], state="readonly")
        self.alg.current(0)
        self.alg.pack(fill="x", padx=20, pady=5)

        tk.Button(panel, text="▶ Run Search", height=2, bg="#d1e7dd", command=self.run_search).pack(fill="x", padx=20, pady=5)
        tk.Button(panel, text="🧹 Clear All", height=2, command=self.reset_all).pack(fill="x", padx=20, pady=5)

        # ===== RIGHT PANEL (METRICS) =====
        metrics_frame = tk.Frame(main, width=320, bg="#f8f9fa", borderwidth=1, relief="sunken")
        metrics_frame.pack(side="right", fill="y")
        metrics_frame.pack_propagate(False)

        tk.Label(metrics_frame, text="Execution Log", font=("Segoe UI", 14, "bold"), bg="#f8f9fa").pack(pady=10)
        
        self.path_var = tk.StringVar(value="Total Path Cost: —")
        tk.Label(metrics_frame, textvariable=self.path_var, font=("Segoe UI", 11, "bold"), bg="#f8f9fa", fg="#0d6efd").pack(pady=5)

        self.tree = ttk.Treeview(metrics_frame, columns=("ID", "Value"), show='headings', height=15)
        self.tree.heading("ID", text="Element")
        self.tree.heading("Value", text="Cost (h/w)")
        self.tree.column("ID", width=120)
        self.tree.column("Value", width=100)
        self.tree.pack(fill="x", padx=10, pady=5)
        self.tree.bind("<Double-1>", self.on_edit_click)

        self.log_text = tk.Text(metrics_frame, height=12, font=("Consolas", 9))
        self.log_text.pack(padx=10, pady=5, fill="both", expand=True)

        # ===== CANVAS =====
        self.canvas = tk.Canvas(main, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.click)

    # ---------- LOGIC ----------
    def set_mode(self, m):
        self.mode = m
        self.mode_var.set(f"Mode: {m.capitalize()}")
        self.selected_node = None

    def toggle_direction(self):
        self.graph.directed = self.dir_var.get()
        self.refresh_canvas()

    def ask_value(self, title, prompt):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("250x120")
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text=prompt).pack(pady=5)
        entry = tk.Entry(dialog)
        entry.pack()
        res = [None]
        def ok():
            try: 
                res[0] = float(entry.get())
                dialog.destroy()
            except: pass
        tk.Button(dialog, text="OK", command=ok).pack(pady=5)
        self.root.wait_window(dialog)
        return res[0]

    def click(self, e):
        node = self.find_node(e.x, e.y)
        if self.mode == "node" and not node:
            h = self.ask_value("Heuristic", f"Enter Heuristic cost for N{self.node_count+1}:")
            if h is not None:
                self.node_count += 1
                name = f"N{self.node_count}"
                self.graph.add_node(name, e.x, e.y, h)
                self.refresh_canvas()
        elif self.mode == "edge" and node:
            if not self.selected_node: self.selected_node = node
            else:
                if node != self.selected_node:
                    w = self.ask_value("Weight", f"Path cost from {self.selected_node} to {node}:")
                    if w is not None:
                        self.graph.add_edge(self.selected_node, node, w)
                        self.refresh_canvas()
                self.selected_node = None
        elif self.mode == "start" and node:
            self.start_node = node
            self.refresh_canvas()
        elif self.mode == "goal" and node:
            self.goal_node = node
            self.refresh_canvas()

    def find_node(self, x, y):
        for n, data in self.graph.nodes.items():
            if (x - data[0])**2 + (y - data[1])**2 <= self.node_radius**2:
                return n
        return None

    def on_edit_click(self, event):
        item = self.tree.selection()
        if not item: return
        item_id = item[0]
        val = self.tree.item(item_id, "values")
        new_val = self.ask_value("Edit", f"New value for {val[0]}:")
        if new_val is not None:
            if "N" in val[0] and "->" not in val[0]:
                self.graph.nodes[val[0]][2] = new_val
            else:
                u, v = val[0].split("->")
                for e in self.graph.edges[u]:
                    if e[0] == v: e[1] = new_val
                if not self.graph.directed:
                    for e in self.graph.edges[v]:
                        if e[0] == u: e[1] = new_val
            self.refresh_canvas()

    def refresh_canvas(self):
        self.canvas.delete("all")
        for i in self.tree.get_children(): self.tree.delete(i)
        for u, neighbors in self.graph.edges.items():
            for v, w in neighbors:
                if self.graph.directed or u < v:
                    self.draw_edge(u, v, w)
                    self.tree.insert("", "end", values=(f"{u}->{v}", w))
        for n, data in self.graph.nodes.items():
            self.draw_node(n, data[0], data[1], data[2])
            self.tree.insert("", "end", values=(n, data[2]))

    def draw_node(self, n, x, y, h):
        color = "#6ec1ff"
        if n == self.start_node: color = "#2ecc71"
        elif n == self.goal_node: color = "#e74c3c"
        self.canvas.create_oval(x-20, y-20, x+20, y+20, fill=color, outline="#333", width=2)
        self.canvas.create_text(x, y-5, text=n, font=("Segoe UI", 10, "bold"))
        self.canvas.create_text(x, y+10, text=f"h:{h}", font=("Segoe UI", 8))

    def draw_edge(self, u, v, w, color="#333", width=1, tag="edge"):
        x1, y1, _ = self.graph.nodes[u]
        x2, y2, _ = self.graph.nodes[v]
        arrow = tk.LAST if self.graph.directed else None
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, arrow=arrow, tags=tag)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        length = (dx**2 + dy**2)**0.5 or 1
        ox, oy = -dy/length * 15, dx/length * 15
        self.canvas.create_text(mx + ox, my + oy, text=str(w), fill="red", font=("Arial", 9, "bold"), tags=tag)

    def random_graph(self):
        self.reset_all()
        for i in range(1, 11):
            n = f"N{i}"
            self.graph.add_node(n, random.randint(50, 600), random.randint(50, 500), random.randint(0, 40))
        nodes = list(self.graph.nodes.keys())
        for _ in range(12):
            u, v = random.sample(nodes, 2)
            self.graph.add_edge(u, v, random.randint(1, 25))
        self.node_count = 10
        self.refresh_canvas()

    def run_search(self):
        if not self.start_node or not self.goal_node:
            messagebox.showerror("Error", "Set start & goal nodes!")
            return
        
        self.canvas.delete("path")
        selected_mode = self.alg.get()
        path = run_algorithm(self.graph, self.start_node, self.goal_node, selected_mode)
        
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"Running: {selected_mode}\n\n")
        
        if path:
            cumulative = 0
            self.log_text.insert(tk.END, "Node | g(cost) | h(heur)\n" + "-"*25 + "\n")
            for i in range(len(path)):
                curr = path[i]
                h_val = self.graph.nodes[curr][2]
                if i > 0:
                    prev = path[i-1]
                    for neighbor, weight in self.graph.edges[prev]:
                        if neighbor == curr:
                            cumulative += weight
                            self.draw_edge(prev, curr, "", color="#0d6efd", width=4, tag="path")
                            break
                self.log_text.insert(tk.END, f"{curr:<5} | {cumulative:<7} | {h_val:<5}\n")
            self.path_var.set(f"Total Path Cost: {cumulative}")
        else:
            messagebox.showinfo("Fail", "No path found.")

    def reset_all(self):
        self.graph = Graph()
        self.node_count = 0
        self.start_node = self.goal_node = None
        self.path_var.set("Total Path Cost: —")
        self.refresh_canvas()
        self.log_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()