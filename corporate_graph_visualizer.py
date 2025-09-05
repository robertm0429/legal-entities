#!/usr/bin/env python3
"""
Corporate Structure Graph Visualizer
=====================================

A comprehensive tool for visualizing complex corporate structures using network graphs.
Supports multiple corporate models: Tech Conglomerate, Berkshire-style Holding Company, 
Consumer Goods Matrix Organization, and Franchise Beverage Model.

Author: Claude Code Assistant
Date: 2025-01-XX
"""

import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

class CorporateGraphVisualizer:
    """
    Main class for processing corporate structure data and creating visualizations.
    """
    
    def __init__(self, base_path: str = "/workspaces/legal-entities/"):
        """
        Initialize the visualizer with the base path to corporate data.
        
        Args:
            base_path (str): Path to the directory containing corporate structure folders
        """
        self.base_path = base_path
        self.companies = {
            'TechGlobal': 'TechGlobal',
            'GlobalVentures': 'GlobalVentures', 
            'ConsumerBrands': 'ConsumerBrands',
            'GlobalBeverage': 'GlobalBeverage'
        }
        
        self.graphs = {}  # Store NetworkX graphs for each company
        self.entity_data = {}  # Store processed entity data
        self.ownership_data = {}  # Store ownership relationships
        self.transaction_data = {}  # Store financial transactions
        self.attributes_data = {}  # Store entity attributes
        
        # Color schemes for different visualizations
        self.region_colors = {
            'North America': '#1f77b4',
            'Europe': '#ff7f0e', 
            'Asia Pacific': '#2ca02c',
            'South America': '#d62728',
            'Africa': '#9467bd',
            'Central America': '#8c564b'
        }
        
        self.entity_type_colors = {
            'Corporation': '#1f77b4',
            'LLC': '#ff7f0e',
            'Limited Company': '#2ca02c', 
            'GmbH': '#d62728',
            'S.A. de C.V.': '#9467bd',
            'B.V.': '#8c564b',
            'K.K.': '#e377c2',
            'Ltda.': '#7f7f7f'
        }

    def load_company_data(self, company_name: str) -> Dict:
        """
        Load all CSV files for a specific company.
        
        Args:
            company_name (str): Name of the company directory
            
        Returns:
            Dict: Dictionary containing loaded DataFrames
        """
        company_path = os.path.join(self.base_path, company_name)
        data = {}
        
        # Define expected file patterns
        file_patterns = {
            'structure': f'{company_name}_Corporate_Structure.csv',
            'ownership': f'{company_name}_Ownership.csv', 
            'transactions': f'{company_name}_InternalDebts.csv',
            'attributes': f'{company_name}_EntityAttributes.csv'
        }
        
        # Load each file if it exists
        for data_type, filename in file_patterns.items():
            file_path = os.path.join(company_path, filename)
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    data[data_type] = df
                    print(f"✓ Loaded {data_type} data for {company_name}: {len(df)} records")
                except Exception as e:
                    print(f"✗ Error loading {filename}: {e}")
            else:
                print(f"⚠ File not found: {filename}")
        
        return data

    def process_ownership_relationships(self, ownership_df: pd.DataFrame, company_name: str) -> List[Tuple]:
        """
        Process ownership data into graph edges.
        
        Args:
            ownership_df (pd.DataFrame): Ownership relationships DataFrame
            company_name (str): Name of the company
            
        Returns:
            List[Tuple]: List of (parent, child, attributes) tuples
        """
        edges = []
        
        for _, row in ownership_df.iterrows():
            parent = row.get('Owner Entity Code', '')
            child = row.get('Owned Entity Code', '')
            
            # Skip if parent is empty (external shareholders)
            if pd.isna(parent) or parent == '':
                continue
                
            # Extract ownership percentage
            percent_owned = row.get('Percent Owned', '0%')
            if isinstance(percent_owned, str):
                try:
                    percent_value = float(percent_owned.rstrip('%'))
                except:
                    percent_value = 0.0
            else:
                percent_value = float(percent_owned)
            
            edge_attrs = {
                'relationship_type': 'ownership',
                'percent_owned': percent_value,
                'share_class': row.get('Share Class', ''),
                'ownership_type': row.get('Ownership Type', ''),
                'entry_date': row.get('Entry As Shareholder Date', ''),
                'company': company_name
            }
            
            edges.append((parent, child, edge_attrs))
        
        return edges

    def process_transaction_relationships(self, transactions_df: pd.DataFrame, company_name: str) -> List[Tuple]:
        """
        Process transaction data into graph edges.
        
        Args:
            transactions_df (pd.DataFrame): Transaction relationships DataFrame
            company_name (str): Name of the company
            
        Returns:
            List[Tuple]: List of (creditor, debtor, attributes) tuples
        """
        edges = []
        
        for _, row in transactions_df.iterrows():
            creditor = row.get('Creditor Entity Code', '')
            debtor = row.get('Debtor Entity Code', '')
            
            # Skip if either party is missing
            if pd.isna(creditor) or pd.isna(debtor) or creditor == '' or debtor == '':
                continue
            
            # Extract transaction amount
            amount = row.get('Principal Amount', 0)
            if isinstance(amount, str):
                try:
                    # Remove commas and convert to float
                    amount = float(str(amount).replace(',', ''))
                except:
                    amount = 0.0
            
            edge_attrs = {
                'relationship_type': 'transaction',
                'transaction_type': row.get('Transaction Type', ''),
                'amount': amount,
                'currency': row.get('Currency', 'USD'),
                'interest_rate': row.get('Interest Rate', ''),
                'purpose': row.get('Purpose', ''),
                'status': row.get('Status', ''),
                'company': company_name
            }
            
            edges.append((creditor, debtor, edge_attrs))
        
        return edges

    def create_company_graph(self, company_name: str) -> nx.DiGraph:
        """
        Create a NetworkX directed graph for a company.
        
        Args:
            company_name (str): Name of the company
            
        Returns:
            nx.DiGraph: NetworkX directed graph
        """
        # Load company data
        data = self.load_company_data(company_name)
        
        if not data:
            print(f"No data loaded for {company_name}")
            return nx.DiGraph()
        
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes from structure data
        if 'structure' in data:
            structure_df = data['structure']
            for _, row in structure_df.iterrows():
                entity_code = row.get('Legal Entity Code (#)', '')
                if pd.isna(entity_code) or entity_code == '':
                    continue
                
                # Node attributes
                node_attrs = {
                    'entity_name': row.get('Entity Name', ''),
                    'entity_type': row.get('Entity Type', ''),
                    'country': row.get('Country Of Incorporation', ''),
                    'region': row.get('Region', ''),
                    'line_of_business': row.get('Line Of Business', ''),
                    'complexity': row.get('Complexity', ''),
                    'descriptor': row.get('Descriptor', ''),
                    'effective_date': row.get('Effective Date', ''),
                    'company': company_name,
                    'jurisdiction': row.get('Jurisdiction', ''),
                    'local_currency': row.get('Local Currency', ''),
                    'functional_currency': row.get('Functional Currency', ''),
                    'reporting_currency': row.get('Reporting Currency', '')
                }
                
                G.add_node(entity_code, **node_attrs)
        
        # Add ownership edges
        if 'ownership' in data:
            ownership_edges = self.process_ownership_relationships(data['ownership'], company_name)
            for parent, child, attrs in ownership_edges:
                G.add_edge(parent, child, **attrs)
        
        # Add transaction edges
        if 'transactions' in data:
            transaction_edges = self.process_transaction_relationships(data['transactions'], company_name)
            for creditor, debtor, attrs in transaction_edges:
                # Add as separate edges or combine with existing ownership edges
                if G.has_edge(creditor, debtor):
                    # Add transaction attributes to existing edge
                    G.edges[creditor, debtor].update(attrs)
                else:
                    # Create new edge for transaction-only relationships
                    G.add_edge(creditor, debtor, **attrs)
        
        # Add entity attributes as node properties
        if 'attributes' in data:
            attributes_df = data['attributes']
            for _, row in attributes_df.iterrows():
                entity_code = row.get('Entity Code', '')
                if entity_code in G.nodes:
                    attr_name = row.get('Attribute Name', '')
                    attr_value = row.get('Attribute Value', '')
                    
                    # Store attributes in a nested dict to avoid conflicts
                    if 'attributes' not in G.nodes[entity_code]:
                        G.nodes[entity_code]['attributes'] = {}
                    
                    G.nodes[entity_code]['attributes'][attr_name] = {
                        'value': attr_value,
                        'type': row.get('Value Type', 'Text'),
                        'category': row.get('Category', 'General')
                    }
        
        print(f"Created graph for {company_name}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        return G

    def load_all_companies(self):
        """Load data for all companies and create their graphs."""
        print("Loading corporate structure data for all companies...")
        print("=" * 60)
        
        for company_key, company_name in self.companies.items():
            print(f"\nProcessing {company_name}:")
            self.graphs[company_name] = self.create_company_graph(company_name)
        
        print(f"\n{'='*60}")
        print("Data loading complete!")
        print(f"Loaded {len(self.graphs)} company structures")

    def get_node_sizes(self, G: nx.DiGraph, size_attribute: str = 'revenue') -> Dict[str, float]:
        """
        Calculate node sizes based on a specific attribute.
        
        Args:
            G (nx.DiGraph): NetworkX graph
            size_attribute (str): Attribute to use for sizing (revenue, employees, etc.)
            
        Returns:
            Dict[str, float]: Dictionary mapping node IDs to sizes
        """
        sizes = {}
        min_size, max_size = 20, 100
        
        # Extract attribute values
        values = []
        for node in G.nodes():
            node_data = G.nodes[node]
            
            # Look for the attribute in various places
            attr_value = 0
            
            # Check in attributes dict
            if 'attributes' in node_data:
                attrs = node_data['attributes']
                for attr_name, attr_data in attrs.items():
                    if size_attribute.lower() in attr_name.lower():
                        try:
                            attr_value = float(str(attr_data['value']).replace(',', ''))
                            break
                        except:
                            continue
            
            values.append(attr_value)
        
        # Normalize sizes
        if max(values) > 0:
            for i, node in enumerate(G.nodes()):
                normalized = (values[i] - min(values)) / (max(values) - min(values))
                sizes[node] = min_size + (max_size - min_size) * normalized
        else:
            # Default size if no valid attributes found
            for node in G.nodes():
                sizes[node] = (min_size + max_size) / 2
        
        return sizes

    def create_hierarchy_layout(self, G: nx.DiGraph, root_node: str = None) -> Dict[str, Tuple[float, float]]:
        """
        Create a hierarchical layout for the graph.
        
        Args:
            G (nx.DiGraph): NetworkX graph
            root_node (str): Root node for hierarchy (auto-detected if None)
            
        Returns:
            Dict[str, Tuple[float, float]]: Node positions
        """
        # Find root node if not specified
        if root_node is None:
            # Look for nodes with no predecessors (ultimate parent)
            root_candidates = [n for n in G.nodes() if G.in_degree(n) == 0]
            if root_candidates:
                root_node = root_candidates[0]
            else:
                # Fallback to node with highest out-degree
                root_node = max(G.nodes(), key=lambda n: G.out_degree(n))
        
        # Create hierarchical layout
        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except:
            # Fallback to spring layout if graphviz not available
            try:
                pos = nx.spring_layout(G, k=3, iterations=50)
            except:
                # Ultimate fallback to random layout
                pos = nx.random_layout(G)
        
        return pos

    def create_ownership_hierarchy_plot(self, company_name: str, layout_type: str = 'hierarchical') -> go.Figure:
        """
        Create an ownership hierarchy visualization for a specific company.
        
        Args:
            company_name (str): Name of the company to visualize
            layout_type (str): Layout algorithm ('hierarchical', 'spring', 'circular')
            
        Returns:
            go.Figure: Plotly figure object
        """
        if company_name not in self.graphs:
            raise ValueError(f"Company {company_name} not found in loaded data")
        
        G = self.graphs[company_name]
        
        # Create subgraph with only ownership relationships
        ownership_edges = [(u, v) for u, v, d in G.edges(data=True) 
                          if d.get('relationship_type') == 'ownership']
        G_ownership = G.edge_subgraph(ownership_edges).copy()
        
        # Calculate layout
        if layout_type == 'hierarchical':
            pos = self.create_hierarchy_layout(G_ownership)
        elif layout_type == 'spring':
            pos = nx.spring_layout(G_ownership, k=2, iterations=50, seed=42)
        elif layout_type == 'circular':
            pos = nx.circular_layout(G_ownership)
        else:
            pos = nx.spring_layout(G_ownership, seed=42)
        
        # Get node sizes based on attributes (e.g., revenue, employees)
        node_sizes = self.get_node_sizes(G)
        
        # Create edge traces
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G_ownership.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            # Get edge information
            edge_data = G_ownership.edges[edge[0], edge[1]]
            ownership_pct = edge_data.get('percent_owned', 0)
            edge_info.append(f"{edge[0]} → {edge[1]}: {ownership_pct}% ownership")
        
        edge_trace = go.Scatter(x=edge_x, y=edge_y,
                               line=dict(width=2, color='#888'),
                               hoverinfo='none',
                               mode='lines')
        
        # Create node traces
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        node_colors = []
        node_sizes_list = []
        
        for node in G_ownership.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Get node information
            node_data = G_ownership.nodes[node]
            entity_name = node_data.get('entity_name', node)
            entity_type = node_data.get('entity_type', 'Unknown')
            region = node_data.get('region', 'Unknown')
            
            node_text.append(f"{entity_name[:20]}..." if len(entity_name) > 20 else entity_name)
            
            # Create hover text
            hover_text = f"<b>{entity_name}</b><br>"
            hover_text += f"Code: {node}<br>"
            hover_text += f"Type: {entity_type}<br>"
            hover_text += f"Region: {region}<br>"
            
            # Add attributes if available
            if 'attributes' in node_data:
                hover_text += "<br><b>Key Metrics:</b><br>"
                for attr_name, attr_data in list(node_data['attributes'].items())[:3]:
                    hover_text += f"{attr_name}: {attr_data['value']}<br>"
            
            node_info.append(hover_text)
            
            # Color by region
            node_colors.append(self.region_colors.get(region, '#999'))
            node_sizes_list.append(node_sizes.get(node, 30))
        
        node_trace = go.Scatter(x=node_x, y=node_y,
                               mode='markers+text',
                               hoverinfo='text',
                               hovertext=node_info,
                               text=node_text,
                               textposition="middle center",
                               marker=dict(size=node_sizes_list,
                                         color=node_colors,
                                         line=dict(width=2, color='white')))
        
        # Create the figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title=dict(text=f"{company_name} - Ownership Hierarchy", font=dict(size=16)),
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text=f"Network Graph showing ownership relationships<br>"
                                   f"Node size: Based on entity attributes | Color: Region",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002, xanchor='left', yanchor='bottom',
                               font=dict(color="gray", size=10)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                       )
        
        return fig

    def create_financial_flow_plot(self, company_name: str) -> go.Figure:
        """
        Create a financial flow visualization showing transactions between entities.
        
        Args:
            company_name (str): Name of the company to visualize
            
        Returns:
            go.Figure: Plotly figure object
        """
        if company_name not in self.graphs:
            raise ValueError(f"Company {company_name} not found in loaded data")
        
        G = self.graphs[company_name]
        
        # Create subgraph with transaction relationships
        transaction_edges = [(u, v) for u, v, d in G.edges(data=True) 
                            if d.get('relationship_type') == 'transaction']
        
        if not transaction_edges:
            # Create empty plot if no transactions
            fig = go.Figure()
            fig.add_annotation(text=f"No transaction data available for {company_name}",
                             xref="paper", yref="paper",
                             x=0.5, y=0.5, showarrow=False,
                             font=dict(size=16))
            fig.update_layout(title=f"{company_name} - Financial Flow Network")
            return fig
        
        G_transactions = G.edge_subgraph(transaction_edges).copy()
        
        # Calculate layout
        pos = nx.spring_layout(G_transactions, k=3, iterations=50, seed=42)
        
        # Create edge traces with different colors for different transaction types
        transaction_types = set()
        for _, _, d in G_transactions.edges(data=True):
            transaction_types.add(d.get('transaction_type', 'Unknown'))
        
        transaction_colors = px.colors.qualitative.Set1[:len(transaction_types)]
        type_color_map = dict(zip(transaction_types, transaction_colors))
        
        edge_traces = []
        for trans_type in transaction_types:
            edge_x = []
            edge_y = []
            edge_text = []
            
            for edge in G_transactions.edges():
                edge_data = G_transactions.edges[edge[0], edge[1]]
                if edge_data.get('transaction_type') == trans_type:
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                    
                    # Add transaction info
                    amount = edge_data.get('amount', 0)
                    currency = edge_data.get('currency', 'USD')
                    edge_text.append(f"{edge[0]} → {edge[1]}<br>"
                                   f"Type: {trans_type}<br>"
                                   f"Amount: {currency} {amount:,.0f}")
            
            if edge_x:  # Only add trace if there are edges of this type
                edge_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=3, color=type_color_map[trans_type]),
                    hoverinfo='none',
                    mode='lines',
                    name=trans_type
                )
                edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        node_sizes_list = []
        
        for node in G_transactions.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Get node information
            node_data = G_transactions.nodes[node]
            entity_name = node_data.get('entity_name', node)
            
            node_text.append(entity_name[:15] + "..." if len(entity_name) > 15 else entity_name)
            
            # Create hover text
            hover_text = f"<b>{entity_name}</b><br>Code: {node}<br>"
            
            # Calculate total inflows and outflows
            inflow = sum(G_transactions.edges[pred, node].get('amount', 0) 
                        for pred in G_transactions.predecessors(node))
            outflow = sum(G_transactions.edges[node, succ].get('amount', 0) 
                         for succ in G_transactions.successors(node))
            
            hover_text += f"Total Inflow: ${inflow:,.0f}<br>"
            hover_text += f"Total Outflow: ${outflow:,.0f}<br>"
            hover_text += f"Net Flow: ${inflow - outflow:,.0f}"
            
            node_info.append(hover_text)
            
            # Size based on total transaction volume
            total_volume = inflow + outflow
            node_sizes_list.append(max(20, min(100, total_volume / 1e8)))
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=node_info,
            text=node_text,
            textposition="middle center",
            marker=dict(size=node_sizes_list,
                       color='lightblue',
                       line=dict(width=2, color='white')),
            name='Entities'
        )
        
        # Create the figure
        fig = go.Figure(data=edge_traces + [node_trace],
                       layout=go.Layout(
                           title=dict(text=f"{company_name} - Financial Flow Network", font=dict(size=16)),
                           showlegend=True,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                       )
        
        return fig

    def create_multilayer_network_plot(self, company_name: str) -> go.Figure:
        """
        Create an advanced multi-layer network visualization showing both ownership
        and financial transaction layers with interactive controls.
        
        Args:
            company_name (str): Name of the company to visualize
            
        Returns:
            go.Figure: Plotly figure object with layer controls
        """
        if company_name not in self.graphs:
            raise ValueError(f"Company {company_name} not found in loaded data")
            
        G = self.graphs[company_name]
        
        # Separate relationship types
        ownership_edges = [(u, v, d) for u, v, d in G.edges(data=True) 
                          if d.get('relationship_type') == 'ownership']
        transaction_edges = [(u, v, d) for u, v, d in G.edges(data=True) 
                            if d.get('relationship_type') == 'transaction']
        
        # Create layout optimized for multi-layer viewing
        pos = nx.spring_layout(G, k=3.5, iterations=100, seed=42)
        
        # Initialize figure
        fig = go.Figure()
        
        # Layer 1: Ownership Network (Background)
        ownership_x = []
        ownership_y = []
        ownership_info = []
        
        for u, v, data in ownership_edges:
            if u in pos and v in pos:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                ownership_x.extend([x0, x1, None])
                ownership_y.extend([y0, y1, None])
                
                pct = data.get('percent_owned', 0)
                ownership_info.append(f"Ownership: {u} → {v} ({pct}%)")
        
        # Add ownership layer
        fig.add_trace(go.Scatter(
            x=ownership_x, y=ownership_y,
            line=dict(width=2, color='rgba(128,128,128,0.6)', dash='dot'),
            hoverinfo='none',
            mode='lines',
            name='Ownership Structure',
            visible=True,
            legendgroup="ownership"
        ))
        
        # Layer 2: Financial Transaction Networks (by type)
        transaction_types = {}
        for u, v, data in transaction_edges:
            trans_type = data.get('transaction_type', 'Unknown')
            if trans_type not in transaction_types:
                transaction_types[trans_type] = []
            transaction_types[trans_type].append((u, v, data))
        
        # Color scheme for transaction types
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD']
        color_map = {t: colors[i % len(colors)] for i, t in enumerate(transaction_types.keys())}
        
        # Create traces for each transaction type
        for trans_type, edges in transaction_types.items():
            trans_x = []
            trans_y = []
            amounts = []
            
            for u, v, data in edges:
                if u in pos and v in pos:
                    x0, y0 = pos[u]
                    x1, y1 = pos[v]
                    trans_x.extend([x0, x1, None])
                    trans_y.extend([y0, y1, None])
                    
                    amount = data.get('amount', 0)
                    amounts.append(amount)
            
            # Calculate line width based on transaction volume
            if amounts:
                max_amount = max(amounts) if amounts else 1
                min_width, max_width = 2, 8
                avg_amount = sum(amounts) / len(amounts) if amounts else 0
                line_width = min_width + (max_width - min_width) * (avg_amount / max_amount) if max_amount > 0 else min_width
            else:
                line_width = 2
            
            fig.add_trace(go.Scatter(
                x=trans_x, y=trans_y,
                line=dict(width=line_width, color=color_map[trans_type]),
                hoverinfo='none',
                mode='lines',
                name=f'{trans_type} ({len(edges)})',
                visible=True,
                legendgroup="transactions"
            ))
        
        # Layer 3: Entity Nodes with Multi-dimensional Information
        node_x = []
        node_y = []
        node_sizes = []
        node_colors = []
        node_text = []
        hover_text = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Calculate multi-dimensional metrics for each node
            node_data = G.nodes[node]
            entity_name = node_data.get('entity_name', node)
            entity_type = node_data.get('entity_type', 'Unknown')
            region = node_data.get('region', 'Unknown')
            
            # Financial metrics
            inbound_volume = sum(data.get('amount', 0) for u, v, data in transaction_edges if v == node)
            outbound_volume = sum(data.get('amount', 0) for u, v, data in transaction_edges if u == node)
            net_flow = inbound_volume - outbound_volume
            
            # Ownership metrics  
            subsidiaries = len([v for u, v, d in ownership_edges if u == node])
            parents = len([u for u, v, d in ownership_edges if v == node])
            
            # Node size based on total transaction volume (logarithmic scale)
            total_volume = inbound_volume + outbound_volume
            if total_volume > 0:
                size = max(15, min(80, 15 + np.log10(total_volume) * 8))
            else:
                size = 20
            node_sizes.append(size)
            
            # Node color based on role and financial position
            if net_flow > 1e9:
                color = '#2ECC71'  # High net inflow (green)
            elif net_flow < -1e9:
                color = '#E74C3C'  # High net outflow (red)  
            elif subsidiaries > 3:
                color = '#3498DB'  # Parent company (blue)
            elif parents > 0 and subsidiaries == 0:
                color = '#F39C12'  # Subsidiary (orange)
            else:
                color = '#95A5A6'  # Neutral (gray)
            node_colors.append(color)
            
            # Node labels (abbreviated for clarity)
            short_name = entity_name.replace('GlobalBeverage', 'GB').replace('Company', 'Co').replace('Corporation', 'Corp')
            if len(short_name) > 12:
                short_name = short_name[:12] + '...'
            node_text.append(short_name)
            
            # Rich hover information
            hover_info = f"""<b>{entity_name}</b><br>
            Code: {node}<br>
            Type: {entity_type}<br>
            Region: {region}<br>
            <br><b>Financial Flow:</b><br>
            Inbound: ${inbound_volume/1e6:.1f}M<br>
            Outbound: ${outbound_volume/1e6:.1f}M<br>
            Net Flow: ${net_flow/1e6:.1f}M<br>
            <br><b>Ownership:</b><br>
            Subsidiaries: {subsidiaries}<br>
            Parent Companies: {parents}"""
            hover_text.append(hover_info)
        
        # Add entity nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white'),
                opacity=0.9
            ),
            text=node_text,
            textposition="middle center",
            textfont=dict(size=9, color='white', family='Arial Black'),
            hovertext=hover_text,
            hoverinfo='text',
            name='Legal Entities',
            showlegend=True
        ))
        
        # Enhanced layout with interactive controls
        fig.update_layout(
            title=dict(
                text=f"{company_name} - Multi-Layer Corporate Network Analysis",
                font=dict(size=18, family='Arial Black'),
                x=0.5
            ),
            showlegend=True,
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="Black",
                borderwidth=1,
                font=dict(size=10),
                groupclick="toggleitem"
            ),
            hovermode='closest',
            margin=dict(b=50, l=10, r=10, t=80),
            annotations=[
                dict(
                    text="Interactive Multi-Layer View: • Click legend to toggle layers • Hover for entity details<br>"
                         "• Node size = Transaction volume • Node color = Financial role • Line width = Flow volume",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.5, y=-0.02,
                    xanchor='center', yanchor='top',
                    font=dict(size=11),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="gray",
                    borderwidth=1
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.2, 1.2]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.2, 1.2]),
            plot_bgcolor='rgba(248,248,248,0.8)'
        )
        
        return fig

    def create_specialized_model_visualization(self, company_name: str) -> go.Figure:
        """
        Create specialized visualizations tailored to each company's unique business model.
        
        Args:
            company_name (str): Name of the company to visualize
            
        Returns:
            go.Figure: Plotly figure object optimized for the specific business model
        """
        if company_name == 'TechGlobal':
            return self._create_tech_hierarchy_view(company_name)
        elif company_name == 'GlobalVentures':
            return self._create_portfolio_holding_view(company_name)
        elif company_name == 'ConsumerBrands':
            return self._create_matrix_organization_view(company_name)
        elif company_name == 'GlobalBeverage':
            return self._create_franchise_network_view(company_name)
        else:
            # Fallback to standard visualization
            return self.create_ownership_hierarchy_plot(company_name)

    def _create_tech_hierarchy_view(self, company_name: str) -> go.Figure:
        """Create a 4-tier hierarchical view for TechGlobal."""
        if company_name not in self.graphs:
            raise ValueError(f"Company {company_name} not found")
            
        G = self.graphs[company_name]
        
        # Define the 4 tiers based on entity types and ownership depth
        tiers = {
            0: [],  # Ultimate parent
            1: [],  # Regional holding companies  
            2: [],  # Country operations
            3: []   # Specialized entities
        }
        
        # Classify entities by tier
        for node in G.nodes():
            node_data = G.nodes[node]
            entity_type = node_data.get('entity_type', '')
            entity_name = node_data.get('entity_name', node)
            
            if 'TechGlobal Inc' in entity_name:
                tiers[0].append(node)
            elif 'Holdings' in entity_type or 'Holding' in entity_name:
                tiers[1].append(node)
            elif 'Operations' in entity_type or any(country in entity_name for country in ['Ltd', 'GmbH', 'SAS', 'K.K.']):
                tiers[2].append(node)
            else:
                tiers[3].append(node)
        
        # Create hierarchical positions
        fig = go.Figure()
        y_positions = [3, 2, 1, 0]  # Top to bottom
        node_positions = {}
        
        for tier_num, nodes in tiers.items():
            if not nodes:
                continue
            y_pos = y_positions[tier_num]
            x_positions = np.linspace(-2, 2, len(nodes)) if len(nodes) > 1 else [0]
            
            for i, node in enumerate(nodes):
                node_positions[node] = (x_positions[i], y_pos)
        
        # Add tier background rectangles
        tier_colors = ['rgba(52,73,94,0.1)', 'rgba(41,128,185,0.1)', 'rgba(39,174,96,0.1)', 'rgba(230,126,34,0.1)']
        tier_names = ['Ultimate Parent', 'Regional Holdings', 'Country Operations', 'Specialized Entities']
        
        for tier_num, color in enumerate(tier_colors):
            fig.add_shape(
                type="rect",
                x0=-2.5, y0=y_positions[tier_num]-0.3,
                x1=2.5, y1=y_positions[tier_num]+0.3,
                fillcolor=color,
                line=dict(color=color, width=1)
            )
            
            # Add tier labels
            fig.add_annotation(
                x=-2.3, y=y_positions[tier_num],
                text=tier_names[tier_num],
                showarrow=False,
                font=dict(size=12, color='black'),
                bgcolor="white",
                bordercolor="gray",
                borderwidth=1
            )
        
        # Add ownership edges
        ownership_edges = [(u, v, d) for u, v, d in G.edges(data=True) 
                          if d.get('relationship_type') == 'ownership']
        
        edge_x = []
        edge_y = []
        for u, v, data in ownership_edges:
            if u in node_positions and v in node_positions:
                x0, y0 = node_positions[u]
                x1, y1 = node_positions[v]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='gray'),
            mode='lines',
            name='Ownership Flow',
            hoverinfo='none'
        ))
        
        # Add nodes by tier
        for tier_num, nodes in tiers.items():
            if not nodes:
                continue
                
            node_x = [node_positions[node][0] for node in nodes]
            node_y = [node_positions[node][1] for node in nodes] 
            node_text = []
            hover_text = []
            
            for node in nodes:
                node_data = G.nodes[node]
                entity_name = node_data.get('entity_name', node)
                
                # Abbreviated names for display
                short_name = entity_name.replace('TechGlobal', 'TG').replace('Corporation', 'Corp')
                if len(short_name) > 15:
                    short_name = short_name[:15] + '...'
                node_text.append(short_name)
                
                # Rich hover info
                hover_info = f"<b>{entity_name}</b><br>Tier {tier_num + 1}: {tier_names[tier_num]}<br>Code: {node}"
                hover_text.append(hover_info)
            
            # Colors for each tier
            colors = ['#2C3E50', '#3498DB', '#27AE60', '#E67E22']
            
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(size=40, color=colors[tier_num], line=dict(width=2, color='white')),
                text=node_text,
                textposition="middle center",
                textfont=dict(size=8, color='white', family='Arial Black'),
                hovertext=hover_text,
                hoverinfo='text',
                name=f'Tier {tier_num + 1}: {tier_names[tier_num]}',
                showlegend=True
            ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"{company_name} - 4-Tier Technology Conglomerate Structure",
                font=dict(size=16, family='Arial Black'),
                x=0.5
            ),
            showlegend=True,
            xaxis=dict(range=[-3, 3], showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(range=[-0.5, 3.5], showgrid=False, showticklabels=False, zeroline=False),
            margin=dict(t=60, b=20, l=20, r=20),
            plot_bgcolor='white'
        )
        
        return fig

    def _create_portfolio_holding_view(self, company_name: str) -> go.Figure:
        """Create a flat portfolio view for GlobalVentures (Berkshire-style)."""
        if company_name not in self.graphs:
            raise ValueError(f"Company {company_name} not found")
            
        G = self.graphs[company_name]
        
        # Find the ultimate parent
        parent_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
        parent = parent_nodes[0] if parent_nodes else list(G.nodes())[0]
        
        # Group subsidiaries by industry/sector
        subsidiaries = [n for n in G.nodes() if n != parent]
        sectors = {}
        
        for node in subsidiaries:
            node_data = G.nodes[node]
            entity_name = node_data.get('entity_name', node)
            
            # Classify by business sector based on name
            if any(keyword in entity_name.lower() for keyword in ['insurance', 'reinsurance', 'underwriting']):
                sector = 'Insurance'
            elif any(keyword in entity_name.lower() for keyword in ['transport', 'rail', 'logistics']):
                sector = 'Transportation'
            elif any(keyword in entity_name.lower() for keyword in ['energy', 'power', 'utilities']):
                sector = 'Energy'
            elif any(keyword in entity_name.lower() for keyword in ['manufacturing', 'industrial']):
                sector = 'Manufacturing'
            elif any(keyword in entity_name.lower() for keyword in ['retail', 'consumer']):
                sector = 'Retail'
            else:
                sector = 'Other'
                
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(node)
        
        # Create radial layout with parent at center
        fig = go.Figure()
        
        # Position parent at center
        parent_pos = (0, 0)
        
        # Position sectors in a circle around parent
        sector_angles = np.linspace(0, 2*np.pi, len(sectors), endpoint=False)
        sector_colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C']
        color_map = {sector: sector_colors[i % len(sector_colors)] for i, sector in enumerate(sectors.keys())}
        
        node_positions = {parent: parent_pos}
        
        # Create sector layouts
        for i, (sector, nodes) in enumerate(sectors.items()):
            sector_angle = sector_angles[i]
            sector_radius = 2
            sector_center = (sector_radius * np.cos(sector_angle), sector_radius * np.sin(sector_angle))
            
            # Position nodes within each sector
            if len(nodes) == 1:
                node_positions[nodes[0]] = sector_center
            else:
                angles = np.linspace(sector_angle - 0.3, sector_angle + 0.3, len(nodes))
                for j, node in enumerate(nodes):
                    r = sector_radius + 0.3 * (j % 2)  # Slight radius variation
                    node_positions[node] = (r * np.cos(angles[j]), r * np.sin(angles[j]))
        
        # Add edges from parent to each subsidiary
        edge_x = []
        edge_y = []
        for node in subsidiaries:
            x0, y0 = parent_pos
            x1, y1 = node_positions[node]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='lightgray'),
            mode='lines',
            name='Holdings',
            hoverinfo='none'
        ))
        
        # Add parent node
        fig.add_trace(go.Scatter(
            x=[parent_pos[0]], y=[parent_pos[1]],
            mode='markers+text',
            marker=dict(size=60, color='#2C3E50', line=dict(width=3, color='white')),
            text=['GlobalVentures'],
            textposition="middle center",
            textfont=dict(size=10, color='white', family='Arial Black'),
            name='Ultimate Parent',
            hovertext=f"<b>{G.nodes[parent].get('entity_name', parent)}</b><br>Portfolio Holdings: {len(subsidiaries)}",
            hoverinfo='text'
        ))
        
        # Add subsidiary nodes by sector
        for sector, nodes in sectors.items():
            node_x = [node_positions[node][0] for node in nodes]
            node_y = [node_positions[node][1] for node in nodes]
            node_text = []
            hover_text = []
            
            for node in nodes:
                entity_name = G.nodes[node].get('entity_name', node)
                short_name = entity_name.replace('GlobalVentures', 'GV').replace('Corporation', 'Corp')
                if len(short_name) > 12:
                    short_name = short_name[:12] + '...'
                node_text.append(short_name)
                hover_text.append(f"<b>{entity_name}</b><br>Sector: {sector}")
            
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(size=30, color=color_map[sector], line=dict(width=2, color='white')),
                text=node_text,
                textposition="middle center",
                textfont=dict(size=7, color='white'),
                hovertext=hover_text,
                hoverinfo='text',
                name=f'{sector} ({len(nodes)})'
            ))
        
        fig.update_layout(
            title=dict(
                text=f"{company_name} - Berkshire-Style Portfolio Holdings",
                font=dict(size=16, family='Arial Black'),
                x=0.5
            ),
            showlegend=True,
            xaxis=dict(range=[-3.5, 3.5], showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(range=[-3.5, 3.5], showgrid=False, showticklabels=False, zeroline=False),
            margin=dict(t=60, b=20, l=20, r=20),
            plot_bgcolor='white'
        )
        
        return fig

    def _create_matrix_organization_view(self, company_name: str) -> go.Figure:
        """Create a matrix organization view for ConsumerBrands (P&G-style)."""
        if company_name not in self.graphs:
            raise ValueError(f"Company {company_name} not found")
            
        G = self.graphs[company_name]
        
        # Classify entities by function: Brands vs Geographic Operations vs Corporate Functions
        brands = []
        geographic = []
        corporate = []
        parent = None
        
        for node in G.nodes():
            entity_name = G.nodes[node].get('entity_name', node)
            entity_type = G.nodes[node].get('entity_type', '')
            
            if G.in_degree(node) == 0:  # Ultimate parent
                parent = node
            elif any(keyword in entity_name.lower() for keyword in ['brand', 'product', 'beauty', 'care', 'home']):
                brands.append(node)
            elif any(keyword in entity_name.lower() for keyword in ['europe', 'america', 'asia', 'africa', 'region']):
                geographic.append(node)
            else:
                corporate.append(node)
        
        fig = go.Figure()
        
        # Matrix layout: Brands on X-axis, Geographic on Y-axis, Corporate functions around parent
        brand_positions = {}
        geo_positions = {}
        corp_positions = {}
        
        # Position parent at center
        if parent:
            parent_pos = (0, 0)
        
        # Position brands along bottom
        if brands:
            x_coords = np.linspace(-2, 2, len(brands))
            for i, brand in enumerate(brands):
                brand_positions[brand] = (x_coords[i], -1.5)
        
        # Position geographic operations along left side
        if geographic:
            y_coords = np.linspace(-1, 1, len(geographic))
            for i, geo in enumerate(geographic):
                geo_positions[geo] = (-2.5, y_coords[i])
        
        # Position corporate functions in a circle around parent
        if corporate:
            angles = np.linspace(0, 2*np.pi, len(corporate), endpoint=False)
            for i, corp in enumerate(corporate):
                x = 1.2 * np.cos(angles[i])
                y = 1.2 * np.sin(angles[i])
                corp_positions[corp] = (x, y)
        
        # Add matrix grid lines
        if brands and geographic:
            # Vertical lines for brands
            for brand in brands:
                x, _ = brand_positions[brand]
                fig.add_shape(type="line", x0=x, y0=-1.8, x1=x, y1=1.3, 
                             line=dict(color="lightgray", width=1, dash="dot"))
            
            # Horizontal lines for geographic
            for geo in geographic:
                _, y = geo_positions[geo]
                fig.add_shape(type="line", x0=-2.8, y0=y, x1=2.3, y1=y,
                             line=dict(color="lightgray", width=1, dash="dot"))
        
        # Add edges
        edge_x = []
        edge_y = []
        for u, v, d in G.edges(data=True):
            if d.get('relationship_type') == 'ownership':
                pos_u = brand_positions.get(u) or geo_positions.get(u) or corp_positions.get(u) or (parent_pos if u == parent else None)
                pos_v = brand_positions.get(v) or geo_positions.get(v) or corp_positions.get(v) or (parent_pos if v == parent else None)
                
                if pos_u and pos_v:
                    edge_x.extend([pos_u[0], pos_v[0], None])
                    edge_y.extend([pos_u[1], pos_v[1], None])
        
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='lightgray'),
            mode='lines',
            name='Reporting Lines',
            hoverinfo='none'
        ))
        
        # Add parent node
        if parent:
            fig.add_trace(go.Scatter(
                x=[parent_pos[0]], y=[parent_pos[1]],
                mode='markers+text',
                marker=dict(size=50, color='#2C3E50', line=dict(width=3, color='white')),
                text=['ConsumerBrands'],
                textposition="middle center",
                textfont=dict(size=9, color='white', family='Arial Black'),
                name='Corporate HQ',
                hovertext=f"<b>{G.nodes[parent].get('entity_name', parent)}</b><br>Matrix Organization Center",
                hoverinfo='text'
            ))
        
        # Add brand entities
        if brands:
            brand_x = [brand_positions[b][0] for b in brands]
            brand_y = [brand_positions[b][1] for b in brands]
            brand_text = [G.nodes[b].get('entity_name', b).replace('ConsumerBrands', 'CB')[:10] for b in brands]
            brand_hover = [f"<b>{G.nodes[b].get('entity_name', b)}</b><br>Brand Portfolio" for b in brands]
            
            fig.add_trace(go.Scatter(
                x=brand_x, y=brand_y,
                mode='markers+text',
                marker=dict(size=35, color='#E74C3C', line=dict(width=2, color='white')),
                text=brand_text,
                textposition="middle center",
                textfont=dict(size=7, color='white'),
                hovertext=brand_hover,
                hoverinfo='text',
                name=f'Brand Units ({len(brands)})'
            ))
        
        # Add geographic entities
        if geographic:
            geo_x = [geo_positions[g][0] for g in geographic]
            geo_y = [geo_positions[g][1] for g in geographic]
            geo_text = [G.nodes[g].get('entity_name', g).replace('ConsumerBrands', 'CB')[:10] for g in geographic]
            geo_hover = [f"<b>{G.nodes[g].get('entity_name', g)}</b><br>Regional Operations" for g in geographic]
            
            fig.add_trace(go.Scatter(
                x=geo_x, y=geo_y,
                mode='markers+text',
                marker=dict(size=35, color='#3498DB', line=dict(width=2, color='white')),
                text=geo_text,
                textposition="middle center",
                textfont=dict(size=7, color='white'),
                hovertext=geo_hover,
                hoverinfo='text',
                name=f'Geographic Units ({len(geographic)})'
            ))
        
        # Add corporate functions
        if corporate:
            corp_x = [corp_positions[c][0] for c in corporate]
            corp_y = [corp_positions[c][1] for c in corporate]
            corp_text = [G.nodes[c].get('entity_name', c).replace('ConsumerBrands', 'CB')[:10] for c in corporate]
            corp_hover = [f"<b>{G.nodes[c].get('entity_name', c)}</b><br>Corporate Function" for c in corporate]
            
            fig.add_trace(go.Scatter(
                x=corp_x, y=corp_y,
                mode='markers+text',
                marker=dict(size=30, color='#2ECC71', line=dict(width=2, color='white')),
                text=corp_text,
                textposition="middle center",
                textfont=dict(size=7, color='white'),
                hovertext=corp_hover,
                hoverinfo='text',
                name=f'Corporate Functions ({len(corporate)})'
            ))
        
        fig.update_layout(
            title=dict(
                text=f"{company_name} - Matrix Organization Structure",
                font=dict(size=16, family='Arial Black'),
                x=0.5
            ),
            showlegend=True,
            annotations=[
                dict(text="Brands", x=0, y=-2, showarrow=False, font=dict(size=12, color='#E74C3C')),
                dict(text="Geographic", x=-3, y=0, showarrow=False, font=dict(size=12, color='#3498DB'), textangle=90)
            ],
            xaxis=dict(range=[-3.2, 2.8], showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(range=[-2.2, 1.8], showgrid=False, showticklabels=False, zeroline=False),
            margin=dict(t=60, b=20, l=20, r=20),
            plot_bgcolor='white'
        )
        
        return fig

    def _create_franchise_network_view(self, company_name: str) -> go.Figure:
        """Create a franchise network view for GlobalBeverage (Coca-Cola-style)."""
        if company_name not in self.graphs:
            raise ValueError(f"Company {company_name} not found")
            
        G = self.graphs[company_name]
        
        # Identify key components of the franchise model
        parent = None
        concentrate_ops = []
        bottling_ops = []
        support_functions = []
        regional_ops = []
        
        for node in G.nodes():
            entity_name = G.nodes[node].get('entity_name', node)
            
            if G.in_degree(node) == 0:  # Ultimate parent
                parent = node
            elif 'concentrate' in entity_name.lower() or 'formula' in entity_name.lower():
                concentrate_ops.append(node)
            elif 'bottling' in entity_name.lower():
                bottling_ops.append(node)
            elif any(region in entity_name for region in ['North America', 'Europe', 'Asia', 'Latin America', 'EMEA']):
                regional_ops.append(node)
            elif any(func in entity_name for func in ['Marketing', 'Supply Chain', 'IP', 'Innovation']):
                support_functions.append(node)
        
        fig = go.Figure()
        
        # Create franchise network layout: Core at center, regions around it
        if parent:
            parent_pos = (0, 0)
        
        # Position concentrate operations near center (key asset)
        conc_positions = {}
        if concentrate_ops:
            conc_positions[concentrate_ops[0]] = (0, 0.8)  # Above parent
        
        # Position support functions in inner circle  
        support_positions = {}
        if support_functions:
            angles = np.linspace(0, 2*np.pi, len(support_functions), endpoint=False)
            for i, func in enumerate(support_functions):
                x = 1.2 * np.cos(angles[i])
                y = 1.2 * np.sin(angles[i])
                support_positions[func] = (x, y)
        
        # Position regional operations in outer circle
        regional_positions = {}
        if regional_ops:
            angles = np.linspace(0, 2*np.pi, len(regional_ops), endpoint=False)
            for i, region in enumerate(regional_ops):
                x = 2.2 * np.cos(angles[i])
                y = 2.2 * np.sin(angles[i])
                regional_positions[region] = (x, y)
        
        # Position bottling operations around regions
        bottling_positions = {}
        if bottling_ops and regional_ops:
            for i, bottling in enumerate(bottling_ops):
                # Associate with nearest region based on name
                bottling_name = G.nodes[bottling].get('entity_name', bottling)
                best_region = regional_ops[0]  # default
                
                for region in regional_ops:
                    region_name = G.nodes[region].get('entity_name', region)
                    if any(geo in bottling_name and geo in region_name for geo in ['North America', 'Europe', 'Asia']):
                        best_region = region
                        break
                
                if best_region in regional_positions:
                    base_x, base_y = regional_positions[best_region]
                    # Position bottling ops slightly offset from their region
                    offset_angle = i * 0.5
                    x = base_x + 0.4 * np.cos(offset_angle)
                    y = base_y + 0.4 * np.sin(offset_angle)
                    bottling_positions[bottling] = (x, y)
        
        # Add franchise network connections
        edge_x = []
        edge_y = []
        
        # Connect parent to all major components
        all_positions = {**conc_positions, **support_positions, **regional_positions, **bottling_positions}
        if parent:
            all_positions[parent] = parent_pos
        
        for u, v, d in G.edges(data=True):
            if u in all_positions and v in all_positions:
                x0, y0 = all_positions[u]
                x1, y1 = all_positions[v]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        # Different line styles for different relationships
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='lightblue'),
            mode='lines',
            name='Franchise Network',
            hoverinfo='none'
        ))
        
        # Add parent company (franchise headquarters)
        if parent:
            fig.add_trace(go.Scatter(
                x=[parent_pos[0]], y=[parent_pos[1]],
                mode='markers+text',
                marker=dict(size=60, color='#C0392B', line=dict(width=3, color='white')),
                text=['GB HQ'],
                textposition="middle center",
                textfont=dict(size=10, color='white', family='Arial Black'),
                name='Franchise HQ',
                hovertext=f"<b>{G.nodes[parent].get('entity_name', parent)}</b><br>Global Franchise Headquarters",
                hoverinfo='text'
            ))
        
        # Add concentrate operations (core asset)
        if concentrate_ops:
            conc_x = [conc_positions[c][0] for c in concentrate_ops]
            conc_y = [conc_positions[c][1] for c in concentrate_ops]
            conc_text = ['Secret Formula']
            conc_hover = [f"<b>{G.nodes[c].get('entity_name', c)}</b><br>Concentrate Production & Formula" for c in concentrate_ops]
            
            fig.add_trace(go.Scatter(
                x=conc_x, y=conc_y,
                mode='markers+text',
                marker=dict(size=45, color='#8E44AD', line=dict(width=3, color='white')),
                text=conc_text,
                textposition="middle center",
                textfont=dict(size=8, color='white', family='Arial Black'),
                hovertext=conc_hover,
                hoverinfo='text',
                name='Concentrate Operations'
            ))
        
        # Add support functions
        if support_functions:
            support_x = [support_positions[s][0] for s in support_functions]
            support_y = [support_positions[s][1] for s in support_functions]
            support_text = [G.nodes[s].get('entity_name', s).split()[-1][:8] for s in support_functions]
            support_hover = [f"<b>{G.nodes[s].get('entity_name', s)}</b><br>Corporate Support Function" for s in support_functions]
            
            fig.add_trace(go.Scatter(
                x=support_x, y=support_y,
                mode='markers+text',
                marker=dict(size=30, color='#16A085', line=dict(width=2, color='white')),
                text=support_text,
                textposition="middle center",
                textfont=dict(size=7, color='white'),
                hovertext=support_hover,
                hoverinfo='text',
                name=f'Support Functions ({len(support_functions)})'
            ))
        
        # Add regional operations
        if regional_ops:
            regional_x = [regional_positions[r][0] for r in regional_ops]
            regional_y = [regional_positions[r][1] for r in regional_ops]
            regional_text = []
            regional_hover = []
            
            for r in regional_ops:
                name = G.nodes[r].get('entity_name', r)
                if 'North America' in name:
                    regional_text.append('N.America')
                elif 'Europe' in name:
                    regional_text.append('Europe')
                elif 'Asia' in name:
                    regional_text.append('Asia Pacific')
                elif 'Latin' in name:
                    regional_text.append('Latin Am')
                else:
                    regional_text.append(name[:8])
                regional_hover.append(f"<b>{name}</b><br>Regional Franchise Operations")
            
            fig.add_trace(go.Scatter(
                x=regional_x, y=regional_y,
                mode='markers+text',
                marker=dict(size=40, color='#2980B9', line=dict(width=2, color='white')),
                text=regional_text,
                textposition="middle center",
                textfont=dict(size=8, color='white', family='Arial Black'),
                hovertext=regional_hover,
                hoverinfo='text',
                name=f'Regional Operations ({len(regional_ops)})'
            ))
        
        # Add bottling partners
        if bottling_ops:
            bottling_x = [bottling_positions[b][0] for b in bottling_ops if b in bottling_positions]
            bottling_y = [bottling_positions[b][1] for b in bottling_ops if b in bottling_positions]
            bottling_text = ['Bottling' for _ in bottling_x]
            bottling_hover = [f"<b>{G.nodes[b].get('entity_name', b)}</b><br>Franchise Bottling Partner" 
                             for b in bottling_ops if b in bottling_positions]
            
            fig.add_trace(go.Scatter(
                x=bottling_x, y=bottling_y,
                mode='markers+text',
                marker=dict(size=25, color='#E67E22', line=dict(width=2, color='white')),
                text=bottling_text,
                textposition="middle center",
                textfont=dict(size=6, color='white'),
                hovertext=bottling_hover,
                hoverinfo='text',
                name=f'Bottling Partners ({len(bottling_x)})'
            ))
        
        fig.update_layout(
            title=dict(
                text=f"{company_name} - Global Franchise Network",
                font=dict(size=16, family='Arial Black'),
                x=0.5
            ),
            showlegend=True,
            xaxis=dict(range=[-3.5, 3.5], showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(range=[-3.5, 3.5], showgrid=False, showticklabels=False, zeroline=False),
            margin=dict(t=60, b=20, l=20, r=20),
            plot_bgcolor='white',
            annotations=[
                dict(
                    text="Franchise Model: HQ provides concentrate & brand → Regions manage markets → Partners bottle & distribute",
                    x=0.5, y=-0.05,
                    xref='paper', yref='paper',
                    showarrow=False,
                    font=dict(size=10),
                    bgcolor="rgba(255,255,255,0.8)"
                )
            ]
        )
        
        return fig

    def create_comparative_overview(self) -> go.Figure:
        """
        Create a comparative overview of all corporate structures.
        
        Returns:
            go.Figure: Plotly figure with subplots for each company
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=list(self.companies.keys()),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for i, (company_name, G) in enumerate(self.graphs.items()):
            row, col = positions[i]
            
            # Create layout for this company
            pos = nx.spring_layout(G, k=1, iterations=30, seed=42)
            
            # Add edges
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            fig.add_trace(
                go.Scatter(x=edge_x, y=edge_y,
                          mode='lines',
                          line=dict(width=1, color='gray'),
                          hoverinfo='none',
                          showlegend=False),
                row=row, col=col
            )
            
            # Add nodes
            node_x = []
            node_y = []
            node_colors = []
            node_sizes = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                # Color by entity type
                entity_type = G.nodes[node].get('entity_type', 'Unknown')
                node_colors.append(self.entity_type_colors.get(entity_type, '#999'))
                
                # Size by degree
                node_sizes.append(max(10, G.degree(node) * 3))
            
            fig.add_trace(
                go.Scatter(x=node_x, y=node_y,
                          mode='markers',
                          marker=dict(size=node_sizes, 
                                    color=node_colors,
                                    line=dict(width=1, color='white')),
                          hoverinfo='none',
                          showlegend=False),
                row=row, col=col
            )
            
            # Remove axes for cleaner look
            fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, row=row, col=col)
            fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, row=row, col=col)
        
        fig.update_layout(
            title=dict(text="Corporate Structure Comparison", font=dict(size=18)),
            height=800,
            margin=dict(t=60, b=40, l=40, r=40)
        )
        
        return fig

    def create_corporate_metrics_dashboard(self) -> go.Figure:
        """
        Create a comprehensive metrics dashboard comparing all corporate structures.
        
        Returns:
            go.Figure: Multi-subplot dashboard with key corporate metrics
        """
        # Create 2x2 subplot layout
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Network Complexity Metrics',
                'Financial Flow Analysis', 
                'Ownership Structure Depth',
                'Corporate Model Comparison'
            ],
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "scatter"}]
            ]
        )
        
        # Calculate comprehensive metrics for each company
        metrics_data = {}
        
        for company_name, G in self.graphs.items():
            # Basic network metrics
            nodes = G.number_of_nodes()
            edges = G.number_of_edges()
            density = nx.density(G) if nodes > 1 else 0
            
            # Separate ownership and transaction edges
            ownership_edges = [(u, v) for u, v, d in G.edges(data=True) 
                             if d.get('relationship_type') == 'ownership']
            transaction_edges = [(u, v) for u, v, d in G.edges(data=True) 
                               if d.get('relationship_type') == 'transaction']
            
            # Financial transaction analysis
            total_transaction_volume = 0
            transaction_types = set()
            
            for u, v, d in G.edges(data=True):
                if d.get('relationship_type') == 'transaction':
                    amount = d.get('amount', 0)
                    if isinstance(amount, (int, float)):
                        total_transaction_volume += amount
                    transaction_types.add(d.get('transaction_type', 'Unknown'))
            
            # Ownership structure analysis  
            ownership_graph = G.edge_subgraph(ownership_edges)
            
            # Find hierarchy depth (longest path from root)
            root_nodes = [n for n in ownership_graph.nodes() if ownership_graph.in_degree(n) == 0]
            max_depth = 0
            if root_nodes:
                for root in root_nodes:
                    try:
                        depths = nx.single_source_shortest_path_length(ownership_graph, root)
                        max_depth = max(max_depth, max(depths.values()) if depths else 0)
                    except:
                        pass
            
            # Network centrality measures
            centrality_scores = nx.degree_centrality(G)
            max_centrality = max(centrality_scores.values()) if centrality_scores else 0
            avg_centrality = sum(centrality_scores.values()) / len(centrality_scores) if centrality_scores else 0
            
            # Store metrics
            metrics_data[company_name] = {
                'nodes': nodes,
                'edges': edges,
                'density': density,
                'ownership_edges': len(ownership_edges),
                'transaction_edges': len(transaction_edges),
                'hierarchy_depth': max_depth,
                'transaction_volume': total_transaction_volume,
                'transaction_types': len(transaction_types),
                'max_centrality': max_centrality,
                'avg_centrality': avg_centrality
            }
        
        companies = list(metrics_data.keys())
        
        # Subplot 1: Network Complexity Metrics (Bar Chart)
        complexity_metrics = ['nodes', 'edges', 'ownership_edges', 'transaction_edges']
        colors = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12']
        
        for i, metric in enumerate(complexity_metrics):
            values = [metrics_data[company][metric] for company in companies]
            
            fig.add_trace(
                go.Bar(
                    x=companies,
                    y=values,
                    name=metric.replace('_', ' ').title(),
                    marker_color=colors[i],
                    offsetgroup=i
                ),
                row=1, col=1
            )
        
        # Subplot 2: Financial Flow Analysis (Scatter plot)
        transaction_volumes = [metrics_data[company]['transaction_volume']/1e9 for company in companies]  # In billions
        transaction_types = [metrics_data[company]['transaction_types'] for company in companies]
        node_counts = [metrics_data[company]['nodes'] for company in companies]
        
        # Color by business model
        model_colors = {'TechGlobal': '#3498DB', 'GlobalVentures': '#E74C3C', 
                       'ConsumerBrands': '#2ECC71', 'GlobalBeverage': '#F39C12'}
        scatter_colors = [model_colors.get(company, 'gray') for company in companies]
        
        fig.add_trace(
            go.Scatter(
                x=transaction_volumes,
                y=transaction_types,
                mode='markers+text',
                marker=dict(
                    size=[max(20, size*2) for size in node_counts],  # Scale by entity count
                    color=scatter_colors,
                    line=dict(width=2, color='white'),
                    opacity=0.8
                ),
                text=companies,
                textposition="middle center",
                textfont=dict(size=10, color='white'),
                name='Financial Flows'
            ),
            row=1, col=2
        )
        
        # Subplot 3: Ownership Structure Depth (Bar Chart)
        hierarchy_depths = [metrics_data[company]['hierarchy_depth'] for company in companies]
        
        fig.add_trace(
            go.Bar(
                x=companies,
                y=hierarchy_depths,
                name='Hierarchy Depth',
                marker_color='#9B59B6',
                text=hierarchy_depths,
                textposition='outside'
            ),
            row=2, col=1
        )
        
        # Subplot 4: Corporate Model Comparison (Network Centrality)
        max_centralities = [metrics_data[company]['max_centrality'] for company in companies]
        avg_centralities = [metrics_data[company]['avg_centrality'] for company in companies]
        densities = [metrics_data[company]['density'] for company in companies]
        
        fig.add_trace(
            go.Scatter(
                x=densities,
                y=max_centralities,
                mode='markers+text',
                marker=dict(
                    size=[max(20, c*200) for c in avg_centralities],  # Scale by average centrality
                    color=scatter_colors,
                    line=dict(width=2, color='white'),
                    opacity=0.8
                ),
                text=companies,
                textposition="middle center", 
                textfont=dict(size=10, color='white'),
                name='Network Structure'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text="Corporate Structure Metrics Dashboard",
                font=dict(size=20, family='Arial Black'),
                x=0.5
            ),
            showlegend=True,
            height=800,
            margin=dict(t=80, b=50, l=50, r=50)
        )
        
        # Update subplot axes
        fig.update_xaxes(title_text="Companies", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=1)
        
        fig.update_xaxes(title_text="Transaction Volume ($B)", row=1, col=2)
        fig.update_yaxes(title_text="Transaction Types", row=1, col=2)
        
        fig.update_xaxes(title_text="Companies", row=2, col=1)
        fig.update_yaxes(title_text="Hierarchy Levels", row=2, col=1)
        
        fig.update_xaxes(title_text="Network Density", row=2, col=2)
        fig.update_yaxes(title_text="Max Node Centrality", row=2, col=2)
        
        return fig

    def create_business_model_analysis(self) -> go.Figure:
        """
        Create a detailed analysis of different business model characteristics.
        
        Returns:
            go.Figure: Radar chart comparing business model dimensions
        """
        # Define business model dimensions to analyze
        dimensions = [
            'Asset Intensity',      # Higher = more asset-heavy operations
            'Geographic Spread',    # Higher = more geographic diversity
            'Operational Complexity',  # Higher = more complex operations
            'Financial Integration',    # Higher = more internal transactions
            'Control Centralization',   # Higher = more centralized control
            'Innovation Focus'      # Higher = more innovation/R&D entities
        ]
        
        # Calculate dimension scores for each company (0-10 scale)
        model_scores = {}
        
        for company_name, G in self.graphs.items():
            scores = {}
            
            # Asset Intensity (based on entity types and bottling/manufacturing)
            manufacturing_entities = sum(1 for n in G.nodes() 
                                       if 'bottling' in G.nodes[n].get('entity_name', '').lower() or
                                          'manufacturing' in G.nodes[n].get('entity_name', '').lower() or
                                          'operations' in G.nodes[n].get('entity_type', '').lower())
            scores['Asset Intensity'] = min(10, manufacturing_entities / G.number_of_nodes() * 20)
            
            # Geographic Spread (count of different regions)
            regions = set()
            for n in G.nodes():
                region = G.nodes[n].get('region', 'Unknown')
                if region != 'Unknown':
                    regions.add(region)
            scores['Geographic Spread'] = min(10, len(regions) * 2)
            
            # Operational Complexity (network density and edges)
            density = nx.density(G)
            scores['Operational Complexity'] = min(10, density * 50 + G.number_of_edges() / 10)
            
            # Financial Integration (transaction volume and types)
            transaction_edges = [(u, v, d) for u, v, d in G.edges(data=True) 
                               if d.get('relationship_type') == 'transaction']
            scores['Financial Integration'] = min(10, len(transaction_edges) / max(1, G.number_of_nodes()) * 10)
            
            # Control Centralization (hierarchy depth)
            ownership_edges = [(u, v) for u, v, d in G.edges(data=True) 
                             if d.get('relationship_type') == 'ownership']
            if ownership_edges:
                ownership_graph = G.edge_subgraph(ownership_edges)
                root_nodes = [n for n in ownership_graph.nodes() if ownership_graph.in_degree(n) == 0]
                max_depth = 0
                for root in root_nodes:
                    try:
                        depths = nx.single_source_shortest_path_length(ownership_graph, root)
                        max_depth = max(max_depth, max(depths.values()) if depths else 0)
                    except:
                        pass
                scores['Control Centralization'] = min(10, max_depth * 2.5)
            else:
                scores['Control Centralization'] = 0
            
            # Innovation Focus (R&D, innovation, IP entities)
            innovation_entities = sum(1 for n in G.nodes() 
                                    if any(keyword in G.nodes[n].get('entity_name', '').lower() 
                                          for keyword in ['innovation', 'research', 'development', 'ip', 'ventures']))
            scores['Innovation Focus'] = min(10, innovation_entities / max(1, G.number_of_nodes()) * 30)
            
            model_scores[company_name] = scores
        
        # Create radar chart
        fig = go.Figure()
        
        # Color scheme for companies
        colors = {
            'TechGlobal': '#3498DB',
            'GlobalVentures': '#E74C3C', 
            'ConsumerBrands': '#2ECC71',
            'GlobalBeverage': '#F39C12'
        }
        
        # Add trace for each company
        for company_name, scores in model_scores.items():
            values = [scores[dim] for dim in dimensions]
            values.append(values[0])  # Close the radar chart
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=dimensions + [dimensions[0]],  # Close the chart
                fill='toself',
                line=dict(color=colors[company_name], width=3),
                name=company_name,
                opacity=0.7
            ))
        
        # Update layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    tickmode='linear',
                    tick0=0,
                    dtick=2
                )
            ),
            showlegend=True,
            title=dict(
                text="Business Model Characteristics Analysis",
                font=dict(size=18, family='Arial Black'),
                x=0.5
            ),
            height=600,
            margin=dict(t=80, b=50, l=50, r=50)
        )
        
        return fig

def main():
    """Main function to demonstrate the visualizer."""
    print("Corporate Structure Graph Visualizer")
    print("====================================")
    
    # Initialize visualizer
    visualizer = CorporateGraphVisualizer()
    
    # Load all company data
    visualizer.load_all_companies()
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print("-" * 40)
    
    for company_name, graph in visualizer.graphs.items():
        nodes = graph.number_of_nodes()
        edges = graph.number_of_edges()
        
        # Calculate some basic network metrics
        if nodes > 0:
            density = nx.density(graph)
            try:
                # Only calculate for weakly connected graphs
                if nx.is_weakly_connected(graph):
                    avg_clustering = nx.average_clustering(graph.to_undirected())
                else:
                    avg_clustering = 0
            except:
                avg_clustering = 0
        else:
            density = 0
            avg_clustering = 0
        
        print(f"{company_name:15} | Nodes: {nodes:2d} | Edges: {edges:2d} | Density: {density:.3f} | Clustering: {avg_clustering:.3f}")
    
    print(f"\n✓ Successfully loaded {len(visualizer.graphs)} corporate structures")
    print("Ready for visualization! Example usage:")
    print("  fig = visualizer.create_ownership_hierarchy_plot('TechGlobal')")
    print("  fig.show()")
    
    return visualizer

if __name__ == "__main__":
    # Run the main function when script is executed directly
    visualizer = main()