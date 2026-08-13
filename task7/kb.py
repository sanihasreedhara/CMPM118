facts = [
    "house(harry, gryffindor)",
    "house(draco, slytherin)",
    "house(cedric, hufflepuff)",
    "parent(harry, pureblood)",
    "parent(draco, pureblood)"
]

rules = [
    ("brave(X)", "house(X, gryffindor)"),
    ("cunning(X)", "house(X, slytherin)"),
    ("loyal(X)", "house(X, hufflepuff)")
]
