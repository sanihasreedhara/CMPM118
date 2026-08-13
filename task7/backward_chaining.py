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


def backward_chain(goal):
    for fact in facts:
        bindings = match(goal, fact)

        if bindings is not None:
            return True

    for conclusion, condition in rules:
        bindings = match(conclusion, goal)

        if bindings is not None:
            condition = condition

            for fact in facts:
                new_condition = condition

                for var, value in bindings.items():
                    new_condition = new_condition.replace(var, value)

                if match(new_condition, fact) is not None:
                    return True

    return False


while True:
    question = input("Query: ")

    if question == "quit":
        break

    print(backward_chain(question))
    