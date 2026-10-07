"""LangGraph coach: router -> nutritionist -> fitness -> motivation -> synthesize, re-planning on alerts."""
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END

class S(TypedDict):
    profile: dict; intent: str; notes: Annotated[list[str], operator.add]
    briefing: str; iterations: int

def router(s: S): return {"iterations": s.get("iterations", 0) + 1}
def nutritionist(s: S):
    p = s["profile"]
    return {"notes": [f"Nutrition: hit {p.get('protein_g','?')} g protein; stay under GI cap {p.get('gi_cap','?')}."]}
def fitness(s: S):
    low = s["profile"].get("sleep_h", 8) < 6
    return {"notes": ["Fitness: " + ("deload today, Zone 2 only." if low else "follow the planned session; add progressive overload.")]}
def motivation(s: S):
    return {"notes": [f"Motivation: {s['profile'].get('steps', 0)} steps so far."]}
def synthesize(s: S): return {"briefing": "\n".join(s["notes"])}
def route_after(s: S): return "replan" if s["profile"].get("alert") and s["iterations"] < 2 else END

def build():
    g = StateGraph(S)
    for n, f in [("router", router), ("nutritionist", nutritionist), ("fitness", fitness),
                 ("motivation", motivation), ("synthesize", synthesize)]:
        g.add_node(n, f)
    g.set_entry_point("router")
    g.add_edge("router", "nutritionist"); g.add_edge("nutritionist", "fitness")
    g.add_edge("fitness", "motivation"); g.add_edge("motivation", "synthesize")
    g.add_conditional_edges("synthesize", route_after, {"replan": "router", END: END})
    return g.compile()
