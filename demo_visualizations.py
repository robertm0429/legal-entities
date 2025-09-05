#!/usr/bin/env python3
"""
Demo script for Corporate Structure Graph Visualizations
========================================================

This script demonstrates the visualization capabilities of the Corporate Graph Visualizer
by creating sample plots for each corporate structure type.

Usage:
    python demo_visualizations.py
"""

from corporate_graph_visualizer import CorporateGraphVisualizer
import os

def main():
    """Run demonstration visualizations."""
    print("Corporate Structure Visualization Demo")
    print("=" * 50)
    
    # Initialize the visualizer
    visualizer = CorporateGraphVisualizer()
    visualizer.load_all_companies()
    
    # Create output directory for HTML files
    output_dir = "visualization_outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nCreating visualizations in {output_dir}/")
    print("-" * 40)
    
    # 1. Ownership Hierarchy Plots for Each Company
    print("1. Creating ownership hierarchy plots...")
    for company_name in visualizer.companies.keys():
        try:
            fig = visualizer.create_ownership_hierarchy_plot(company_name)
            filename = f"{output_dir}/{company_name}_ownership_hierarchy.html"
            fig.write_html(filename)
            print(f"   ✓ {company_name} ownership hierarchy → {filename}")
        except Exception as e:
            print(f"   ✗ Error creating {company_name} ownership hierarchy: {e}")
    
    # 2. Financial Flow Networks
    print("\n2. Creating financial flow networks...")
    for company_name in visualizer.companies.keys():
        try:
            fig = visualizer.create_financial_flow_plot(company_name)
            filename = f"{output_dir}/{company_name}_financial_flows.html"
            fig.write_html(filename)
            print(f"   ✓ {company_name} financial flows → {filename}")
        except Exception as e:
            print(f"   ✗ Error creating {company_name} financial flows: {e}")
    
    # 3. Multi-Layer Network Visualizations  
    print("\n3. Creating multi-layer network visualizations...")
    for company_name in visualizer.companies.keys():
        try:
            fig = visualizer.create_multilayer_network_plot(company_name)
            filename = f"{output_dir}/{company_name}_multilayer_network.html"
            fig.write_html(filename)
            print(f"   ✓ {company_name} multi-layer network → {filename}")
        except Exception as e:
            print(f"   ✗ Error creating {company_name} multi-layer network: {e}")
    
    # 4. Specialized Corporate Model Visualizations
    print("\n4. Creating specialized corporate model visualizations...")
    for company_name in visualizer.companies.keys():
        try:
            fig = visualizer.create_specialized_model_visualization(company_name)
            filename = f"{output_dir}/{company_name}_specialized_model.html"
            fig.write_html(filename)
            print(f"   ✓ {company_name} specialized model → {filename}")
        except Exception as e:
            print(f"   ✗ Error creating {company_name} specialized model: {e}")
    
    # 5. Advanced Analytics and Metrics
    print("\n5. Creating advanced analytics...")
    
    # Corporate Metrics Dashboard
    try:
        fig = visualizer.create_corporate_metrics_dashboard()
        filename = f"{output_dir}/corporate_metrics_dashboard.html"
        fig.write_html(filename)
        print(f"   ✓ Corporate metrics dashboard → {filename}")
    except Exception as e:
        print(f"   ✗ Error creating metrics dashboard: {e}")
    
    # Business Model Analysis (Radar Chart)
    try:
        fig = visualizer.create_business_model_analysis()
        filename = f"{output_dir}/business_model_analysis.html"
        fig.write_html(filename)
        print(f"   ✓ Business model analysis → {filename}")
    except Exception as e:
        print(f"   ✗ Error creating business model analysis: {e}")
    
    # 6. Comparative Overview
    print("\n6. Creating comparative overview...")
    try:
        fig = visualizer.create_comparative_overview()
        filename = f"{output_dir}/corporate_structures_comparison.html"
        fig.write_html(filename)
        print(f"   ✓ Comparative overview → {filename}")
    except Exception as e:
        print(f"   ✗ Error creating comparative overview: {e}")
    
    # 7. Summary Report
    print("\n" + "=" * 50)
    print("VISUALIZATION SUMMARY")
    print("=" * 50)
    
    total_files = 0
    for filename in os.listdir(output_dir):
        if filename.endswith('.html'):
            total_files += 1
            file_path = os.path.join(output_dir, filename)
            file_size = os.path.getsize(file_path) / 1024  # Size in KB
            print(f"📊 {filename:<35} ({file_size:.1f} KB)")
    
    print(f"\n✓ Generated {total_files} interactive HTML visualizations")
    print(f"📁 All files saved in: {os.path.abspath(output_dir)}")
    
    # 8. Network Analysis Summary
    print("\n" + "=" * 50)
    print("NETWORK ANALYSIS SUMMARY")
    print("=" * 50)
    
    analysis_data = []
    
    for company_name, graph in visualizer.graphs.items():
        nodes = graph.number_of_nodes()
        edges = graph.number_of_edges()
        
        # Basic metrics
        density = graph.number_of_edges() / (nodes * (nodes - 1)) if nodes > 1 else 0
        
        # Find root nodes (no incoming ownership edges)
        ownership_edges = [(u, v) for u, v, d in graph.edges(data=True) 
                          if d.get('relationship_type') == 'ownership']
        ownership_graph = graph.edge_subgraph(ownership_edges)
        root_nodes = [n for n in ownership_graph.nodes() if ownership_graph.in_degree(n) == 0]
        
        # Find leaf nodes (no outgoing ownership edges)
        leaf_nodes = [n for n in ownership_graph.nodes() if ownership_graph.out_degree(n) == 0]
        
        # Transaction analysis
        transaction_edges = [(u, v) for u, v, d in graph.edges(data=True) 
                           if d.get('relationship_type') == 'transaction']
        
        analysis_data.append({
            'company': company_name,
            'nodes': nodes,
            'edges': edges,
            'density': density,
            'root_nodes': len(root_nodes),
            'leaf_nodes': len(leaf_nodes),
            'transaction_edges': len(transaction_edges),
            'ownership_edges': len(ownership_edges)
        })
    
    # Print analysis table
    print(f"{'Company':<15} {'Nodes':<6} {'Edges':<6} {'Density':<8} {'Roots':<6} {'Leafs':<6} {'Txns':<6}")
    print("-" * 65)
    
    for data in analysis_data:
        print(f"{data['company']:<15} "
              f"{data['nodes']:<6} "
              f"{data['edges']:<6} "
              f"{data['density']:<8.3f} "
              f"{data['root_nodes']:<6} "
              f"{data['leaf_nodes']:<6} "
              f"{data['transaction_edges']:<6}")
    
    print("\nLegend:")
    print("  Nodes: Total legal entities")
    print("  Edges: Total relationships (ownership + transactions)")  
    print("  Density: Network connectedness (0-1 scale)")
    print("  Roots: Ultimate parent companies")
    print("  Leafs: Subsidiary entities with no children")
    print("  Txns: Financial transaction relationships")
    
    print("\n🎯 Next Steps:")
    print("  • Open the HTML files in your browser to explore interactive graphs")
    print("  • Use zoom, pan, and hover features to examine entity details")
    print("  • Compare different corporate models side-by-side")
    print("  • Analyze financial flows and ownership percentages")

if __name__ == "__main__":
    main()