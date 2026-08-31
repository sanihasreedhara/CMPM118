from typing import TypedDict
from langgraph.graph import StateGraph, START, END

import sys
sys.path.append("task7")

from kb import facts, rules


# State passed between LangGraph nodes
class State(TypedDict):
    query: str
    context: list
    relevant: bool
    result: bool
    trace: list


# Match a query to a fact
def match(pattern, fact):
    p = pattern.split("(")
    f = fact.split("(")

    if p[0] != f[0]:
        return None

    p_args = p[1].rstrip(")").split(",")
    f_args = f[1].rstrip(")").split(",")

    bindings = {}

    for x, y in zip(p_args, f_args):
        x = x.strip()
        y = y.strip()

        if x.isupper():
            bindings[x] = y
        elif x != y:
            return None

    return bindings


# RAG: retrieve relevant facts and rules
def retrieve(state):
    query = state["query"]
    predicate = query.split("(")[0]

    context = []

    for fact in facts:
        if fact.startswith(predicate):
            context.append(fact)

    for rule in rules:
        if rule[0].startswith(predicate):
            context.append(rule)

    return {"context": context}


# Judge whether the retrieved context is relevant
def judge(state):
    if len(state["context"]) > 0:
        return {"relevant": True}

    return {"relevant": False}


# Run logical inference
def infer(state):
    goal = state["query"]
    trace = []

    # Check facts
    for fact in facts:
        if match(goal, fact) is not None:
            trace.append(f"{fact} [FACT]")

            return {
                "result": True,
                "trace": trace
            }

    # Check rules
    for conclusion, condition in rules:

        bindings = match(conclusion, goal)

        if bindings is not None:

            new_condition = condition

            for var, value in bindings.items():
                new_condition = new_condition.replace(var, value)

            trace.append(f"{goal}")
            trace.append(f"  <- {new_condition}")

            for fact in facts:

                if match(new_condition, fact) is not None:

                    trace.append(f"  <- {fact} [FACT]")

                    return {
                        "result": True,
                        "trace": trace
                    }

    return {
        "result": False,
        "trace": trace
    }


# Final refinement/check
def refine(state):

    if state["result"]:
        state["trace"].append("Inference verified.")
    else:
        state["trace"].append("No valid deduction found.")

    return state


# Create the LangGraph
graph = StateGraph(State)

graph.add_node("retrieve", retrieve)
graph.add_node("judge", judge)
graph.add_node("infer", infer)
graph.add_node("refine", refine)

graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "judge")
graph.add_edge("judge", "infer")
graph.add_edge("infer", "refine")
graph.add_edge("refine", END)

app = graph.compile()


# Ask the user for a query
query = input("Query: ")

result = app.invoke({
    "query": query,
    "context": [],
    "relevant": False,
    "result": False,
    "trace": []
})


# Print results
print("\nQuery:", result["query"])
print("Result:", result["result"])

print("\nRetrieved Context:")
for item in result["context"]:
    print(item)

print("\nInference Trace:")
for step in result["trace"]:
    print(step)
    