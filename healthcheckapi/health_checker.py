import networkx as nx
import aiohttp
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from collections import deque

class HealthChecker:
    def __init__(self, system_data):
        self.graph = nx.DiGraph()
        self.build_graph(system_data)

    def build_graph(self, system_data):
        for component in system_data['components']:
            self.graph.add_node(component['name'], url=component['health_check_url'])

        for relationship in system_data['relationships']:
            self.graph.add_edge(relationship['from'], relationship['to'])

    async def check_component_health(self, component):
        url = self.graph.nodes[component]['url']
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return component, "Healthy"
                    else:
                        return component, "Unhealthy"
            except:
                return component, "Unreachable"

    async def check_system_health(self):
        visited = set()
        results = {}
        queue = deque()

        # Start from nodes with no incoming edges (roots)
        roots = [n for n in self.graph.nodes if self.graph.in_degree(n) == 0]
        queue.extend(roots)

        while queue:
            current = queue.popleft()
            if current in visited:
                continue

            component, status = await self.check_component_health(current)
            results[component] = status
            visited.add(current)

            for neighbor in self.graph.successors(current):
                if neighbor not in visited:
                    queue.append(neighbor)

        return results

    def get_system_health_table(self, health_results):
        table = "| Component | Status |\n|-----------|--------|\n"
        for component, status in health_results.items():
            table += f"| {component} | {status} |\n"
        return table

    def get_system_graph_image(self):
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue',
                node_size=3000, font_size=10, font_weight='bold')

        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()

        return img_base64
