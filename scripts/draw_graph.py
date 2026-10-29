"""Save a picture of the answer graph to outputs/graph.png (and the Mermaid text to graph.mmd).

    uv run python scripts/draw_graph.py

The PNG is rendered by the mermaid.ink web service, so it needs internet. The .mmd file is
made locally; if the PNG fails, paste it into https://mermaid.live to see the picture.
"""

from pathlib import Path

from income_tax_agent.graph.build import build_graph
from income_tax_agent.llm import FakeLLM

OUT_DIR = Path(__file__).resolve().parents[1] / "outputs"


def main() -> None:
    # Drawing only reads the wiring; nodes never run, so no real retriever or Gemini is needed.
    graph = build_graph(retriever=None, llm=FakeLLM()).get_graph(xray=True)
    OUT_DIR.mkdir(exist_ok=True)

    mmd_path = OUT_DIR / "graph.mmd"
    mmd_path.write_text(graph.draw_mermaid())
    print(f"Saved {mmd_path}")

    png_path = OUT_DIR / "graph.png"
    try:
        png_path.write_bytes(graph.draw_mermaid_png())
        print(f"Saved {png_path}")
    except Exception as e:  # mermaid.ink down or no internet: the .mmd file is still there
        print(f"Could not render PNG ({e}). Open {mmd_path.name} in https://mermaid.live instead.")


if __name__ == "__main__":
    main()
