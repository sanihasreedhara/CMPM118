from langchain_core.runnables import RunnableLambda

import sys
sys.path.append("task7")

from kb import facts, rules


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


def infer(goal):
    trace = []

    # Check facts
    for fact in facts:
        bindings = match(goal, fact)

        if bindings is not None:
            trace.append(f"{fact} [FACT]")
            return True, trace

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
                    return True, trace

    return False, trace


# RAG: retrieve relevant facts/rules
def retrieve(query):
    relevant = []

    predicate = query.split("(")[0]

    for fact in facts:
        if fact.startswith(predicate):
            relevant.append(fact)

    for rule in rules:
        if rule[0].startswith(predicate):
            relevant.append(rule)

    return relevant


# LangChain pipeline
def run(query):
    context = retrieve(query)
    result, trace = infer(query)

    return {
        "query": query,
        "context": context,
        "result": result,
        "trace": trace
    }


chain = RunnableLambda(run)


query = input("Query: ")

result = chain.invoke(query)

print("\nQuery:", result["query"])
print("Result:", result["result"])

print("\nRetrieved Context:")
for item in result["context"]:
    print(item)

print("\nInference Trace:")
for step in result["trace"]:
    print(step)
