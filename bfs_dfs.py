import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class InteractivePlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Robot Path Planner: BFS vs DFS")
        self.root.geometry("1100x750")

        # --- State Variables ---
        self.grid_size = 7
        self.start_node = None
        self.goal_node = None
        self.blocks = set()
        self.path = []
        
        # --- UI Layout ---
        self.control_panel = tk.Frame(root, width=280, bg="#2c3e50", padx=20, pady=20)
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(self.control_panel, text="CONTROL PANEL", font=("Helvetica", 16, "bold"), 
                 bg="#2c3e50", fg="#ecf0f1").pack(pady=(0, 20))

        # Dynamic Instruction Label
        self.instr_var = tk.StringVar(value="Step 1: Click for START (Green)")
        tk.Label(self.control_panel, textvariable=self.instr_var, justify=tk.LEFT, 
                 font=("Helvetica", 11), bg="#2c3e50", fg="#f1c40f").pack(pady=10)

        # Algorithm Selection
        self.algo_var = tk.StringVar(value="BFS")
        tk.Label(self.control_panel, text="Select Algorithm:", font=("Helvetica", 12, "bold"), 
                 bg="#2c3e50", fg="#ecf0f1").pack(anchor=tk.W, pady=(20, 5))
        
        for text, mode in [("BFS (Shortest Path)", "BFS"), ("DFS (Long Path)", "DFS")]:
            tk.Radiobutton(self.control_panel, text=text, variable=self.algo_var, value=mode, 
                           font=("Helvetica", 10), bg="#2c3e50", fg="#ecf0f1", selectcolor="#34495e",
                           command=self.calculate_and_refresh).pack(anchor=tk.W)

        # Buttons
        tk.Button(self.control_panel, text="RESET GRID", command=self.reset_all, 
                  bg="#e74c3c", fg="white", font=("Helvetica", 11, "bold"), width=20).pack(pady=30)

        # --- Plotting Area ---
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Connect click event
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        self.init_graph()
        self.refresh_plot()

    def init_graph(self):
        self.G = nx.grid_2d_graph(self.grid_size, self.grid_size)
        # Flip coordinates for visual grid alignment (0,0 at top-left)
        self.pos = {(x, y): (y, -x) for x, y in self.G.nodes()}

    def on_click(self, event):
        if event.xdata is None or event.ydata is None: return
        
        # Find closest node to click coordinate
        clicked_node = min(self.G.nodes(), key=lambda n: (self.pos[n][0]-event.xdata)**2 + (self.pos[n][1]-event.ydata)**2)

        # Left Click Logic: Start -> Goal -> Blocks
        if event.button == 1: 
            if self.start_node is None:
                self.start_node = clicked_node
                self.instr_var.set("Step 2: Click for GOAL (Red)")
            elif self.goal_node is None and clicked_node != self.start_node:
                self.goal_node = clicked_node
                self.instr_var.set("Step 3: Click to add/remove BLOCKS")
            elif clicked_node not in [self.start_node, self.goal_node]:
                if clicked_node in self.blocks:
                    self.blocks.remove(clicked_node)
                else:
                    self.blocks.add(clicked_node)
        
        self.calculate_and_refresh()

    def calculate_and_refresh(self):
        self.calculate_path()
        self.refresh_plot()

    def reset_all(self):
        self.start_node = None
        self.goal_node = None
        self.blocks = set()
        self.path = []
        self.instr_var.set("Step 1: Click for START (Green)")
        self.refresh_plot()

    def calculate_path(self):
        if not self.start_node or not self.goal_node:
            self.path = []
            return

        # Create a temporary graph excluding blockages
        temp_G = self.G.copy()
        temp_G.remove_nodes_from(self.blocks)

        try:
            if self.algo_var.get() == "BFS":
                # BFS always finds the shortest path
                self.path = nx.shortest_path(temp_G, self.start_node, self.goal_node)
            else:
                # DFS finds a path by exploring deep branches (not necessarily shortest)
                self.path = list(nx.dfs_edges(temp_G, source=self.start_node))
                # Reconstruction: Filter the DFS edges to find the specific path to goal
                full_dfs = nx.dfs_tree(temp_G, source=self.start_node)
                self.path = nx.shortest_path(full_dfs, self.start_node, self.goal_node)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            self.path = []

    def refresh_plot(self):
        self.ax.clear()
        self.ax.set_facecolor('#ecf0f1')
        
        # Draw the base grid
        nx.draw_networkx_nodes(self.G, self.pos, ax=self.ax, node_color='white', 
                               edgecolors='#bdc3c7', node_size=700)
        nx.draw_networkx_edges(self.G, self.pos, ax=self.ax, edge_color='#bdc3c7', alpha=0.4)

        # Draw Blocks (Obstacles)
        if self.blocks:
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=list(self.blocks), 
                                   node_color='#2c3e50', node_size=700, ax=self.ax)

        # Draw Computed Path
        if self.path:
            path_edges = list(zip(self.path, self.path[1:]))
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.path, 
                                   node_color='#3498db', node_size=700, ax=self.ax)
            nx.draw_networkx_edges(self.G, self.pos, edgelist=path_edges, 
                                   edge_color='#2980b9', width=4, ax=self.ax)

        # Draw Start and Goal with high visibility
        if self.start_node:
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=[self.start_node], 
                                   node_color='#27ae60', node_size=900, ax=self.ax)
        if self.goal_node:
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=[self.goal_node], 
                                   node_color='#c0392b', node_size=900, ax=self.ax)

        # Bold labels for coordinates
        nx.draw_networkx_labels(self.G, self.pos, font_size=9, font_weight="bold", 
                                font_family="sans-serif", ax=self.ax)

        # Visual feedback in Title
        status = f"ALGORITHM: {self.algo_var.get()}"
        if self.path:
            status += f"  |  PATH STEPS: {len(self.path)-1}"
        elif self.start_node and self.goal_node:
            status += "  |  PATH: UNREACHABLE"
            
        self.ax.set_title(status, fontsize=14, fontweight='bold', color='#2c3e50', pad=20)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = InteractivePlanner(root)
    root.mainloop()