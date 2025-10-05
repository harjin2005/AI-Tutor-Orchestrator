import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from agents.langgraph_agent import LangGraphTutorAgent

def visualize_graph():
    """Generate LangGraph visualization without pygraphviz"""
    print("🎨 Generating LangGraph visualization...")
    
    try:
        # Create agent instance
        agent = LangGraphTutorAgent()
        
        print("\n✅ Method 1: ASCII Visualization (Always Works)")
        print("=" * 60)
        
        # Generate ASCII visualization
        ascii_graph = agent.graph.get_graph().draw_ascii()
        
        # Save to file
        output_path = "docs/graph_ascii.txt"
        os.makedirs("docs", exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# AI Tutor Orchestrator - LangGraph Architecture\n\n")
            f.write(ascii_graph)
        
        print(ascii_graph)
        print(f"\n✅ ASCII graph saved to: {output_path}")
        
        print("\n✅ Method 2: Mermaid Code (For Online Visualization)")
        print("=" * 60)
        
        # Generate Mermaid code
        mermaid_code = agent.graph.get_graph().draw_mermaid()
        
        # Save Mermaid code
        mermaid_path = "docs/graph_mermaid.md"
        with open(mermaid_path, "w", encoding="utf-8") as f:
            f.write("# LangGraph StateGraph Visualization\n\n")
            f.write("## Architecture Diagram\n\n")
            f.write("```mermaid\n")
            f.write(mermaid_code)
            f.write("\n```\n\n")
            f.write("## How to View\n\n")
            f.write("1. Copy the mermaid code above\n")
            f.write("2. Go to: https://mermaid.live\n")
            f.write("3. Paste and view the interactive diagram\n\n")
            f.write("## Graph Description\n\n")
            f.write("- START: Entry point for all queries\n")
            f.write("- Classifier Node: Analyzes query type\n")
            f.write("- Groq Agent Node: Processes academic queries\n")
            f.write("- OpenRouter Agent Node: Processes coding queries\n")
            f.write("- END: Exit point after processing\n")
        
        print(f"✅ Mermaid code saved to: {mermaid_path}")
        
        # Create HTML visualization file
        html_path = "docs/graph_visualization.html"
        create_html_visualization(mermaid_code, html_path)
        print(f"✅ HTML visualization saved to: {html_path}")
        
        print("\n" + "=" * 60)
        print("📂 Files Created:")
        print(f"   • {output_path} (ASCII diagram)")
        print(f"   • {mermaid_path} (Mermaid code)")
        print(f"   • {html_path} (Interactive HTML)")
        print("=" * 60)
        
        print("\n💡 Quick Actions:")
        print(f"   1. Open {html_path} in browser")
        print(f"   2. Take screenshot for demo")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_html_visualization(mermaid_code, output_path):
    """Create standalone HTML file with Mermaid visualization"""
    
    html_parts = []
    
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html lang="en">')
    html_parts.append('<head>')
    html_parts.append('    <meta charset="UTF-8">')
    html_parts.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html_parts.append('    <title>AI Tutor Orchestrator - LangGraph</title>')
    html_parts.append('    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>')
    html_parts.append('    <style>')
    html_parts.append('        body { font-family: Arial; max-width: 1200px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }')
    html_parts.append('        .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }')
    html_parts.append('        h1 { color: #667eea; text-align: center; }')
    html_parts.append('        .mermaid { text-align: center; background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }')
    html_parts.append('        .info { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3; }')
    html_parts.append('        .legend { background: #fff3e0; padding: 15px; border-radius: 8px; margin: 20px 0; }')
    html_parts.append('        .legend h3 { color: #ff9800; margin-top: 0; }')
    html_parts.append('        .legend ul { list-style-type: none; padding-left: 0; }')
    html_parts.append('        .legend li { padding: 5px 0; }')
    html_parts.append('    </style>')
    html_parts.append('</head>')
    html_parts.append('<body>')
    html_parts.append('    <div class="container">')
    html_parts.append('        <h1>🎓 AI Tutor Orchestrator</h1>')
    html_parts.append('        <p style="text-align:center;color:#666;">LangGraph StateGraph Architecture</p>')
    html_parts.append('        <div class="info"><strong>Architecture:</strong> LangGraph StateGraph with Conditional Routing</div>')
    html_parts.append('        <div class="mermaid">')
    html_parts.append(mermaid_code)
    html_parts.append('        </div>')
    html_parts.append('        <div class="legend">')
    html_parts.append('            <h3>📊 Graph Components</h3>')
    html_parts.append('            <ul>')
    html_parts.append('                <li><strong>START:</strong> Entry point for all queries</li>')
    html_parts.append('                <li><strong>Classifier:</strong> Analyzes query type</li>')
    html_parts.append('                <li><strong>Groq Agent:</strong> Processes academic queries</li>')
    html_parts.append('                <li><strong>OpenRouter Agent:</strong> Processes coding queries</li>')
    html_parts.append('                <li><strong>END:</strong> Exit point</li>')
    html_parts.append('            </ul>')
    html_parts.append('        </div>')
    html_parts.append('        <div class="info"><strong>Demo:</strong> http://localhost:8000/docs</div>')
    html_parts.append('    </div>')
    html_parts.append('    <script>')
    html_parts.append('        mermaid.initialize({ startOnLoad: true, theme: "default" });')
    html_parts.append('    </script>')
    html_parts.append('</body>')
    html_parts.append('</html>')
    
    html_content = '\n'.join(html_parts)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 LangGraph Visualization Generator")
    print("=" * 60)
    
    result = visualize_graph()
    
    if result:
        print("\n✅ SUCCESS! Open docs/graph_visualization.html")
    else:
        print("\n❌ Failed")
