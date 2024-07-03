from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # TODO

    # Exclusive OR indicating that A is either a knight or a knave but not both.
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    # A says "I am both a knight and a knave. That is true if and only if A is a knight.
    Implication(AKnight, And(AKnight, AKnave)),
    Implication(And(AKnight, AKnave), AKnight),
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # TODO

    # Exclusive OR indicating that A is either a knight or a knave but not both.
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    # Exclusive OR indicating that B is either a knight or a knave but not both.
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    # A says "We are both knaves.". That is true if and only if A is a knight.
    Implication(AKnight, And(AKnave, BKnave)),
    Implication(And(AKnave, BKnave), AKnight)
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # TODO

    # Exclusive OR indicating that A is either a Knight or a knave but not both.
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    # Exclusive OR indicating that B is either a Knight or a knave but not both.
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    # A says "We are the same kind.". That is true if and only if A is a knight.
    Implication(AKnight, And(Or(And(AKnight, BKnight), And(AKnave, BKnave)), Not(And(And(AKnight, BKnight),And(AKnave, BKnave))))),
    Implication(And(Or(And(AKnight, BKnight), And(AKnave, BKnave)), Not(And(And(AKnight, BKnight), And(AKnave, BKnave)))), AKnight),

    # B says "We are of different kinds.". That is true if and only if B is a knight.
    Implication(BKnight, And(Or(And(AKnight, BKnave), And(AKnave, BKnight)), Not(And(And(AKnight, BKnave), And(AKnave, BKnight))))),
    Implication(And(Or(And(AKnight, BKnave),And(AKnave, BKnight)),Not(And(And(AKnight, BKnave),And(AKnave, BKnight)))), BKnight)

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # TODO

    # Exclusive OR indicating that A is either a Knight or a knave but not both.
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    # Exclusive OR indicating that B is either a Knight or a knave but not both.
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    # Exclusive OR indicating that C is either a Knight or a knave but not both.
    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),

    # A says either "I am a knight." or "I am a knave.", Exclusive OR because either one is true.
    Or(
        And(
            Implication(AKnight,AKnight),Implication(AKnight,AKnight))
        ,
        And(
            Implication(AKnight,AKnave),Implication(AKnave,AKnight))
      ),

    Not(
        And(
            And(
                Implication(AKnight,AKnight),Implication(AKnight,AKnight))
                ,
            And(Implication(AKnight,AKnave),Implication(AKnave,AKnight))
            )
        ),

    # B says "A said 'I am a knave'.". That is true if and only if B is a knight.
    Implication(BKnight,And(Implication(AKnight,AKnave),Implication(AKnave,AKnight))),
    Implication(And(Implication(AKnight,AKnave),Implication(AKnave,AKnight)),BKnight),

    # B says "C is a knave.". That is true if and only if B is a knight.
    Implication(BKnight,CKnave),
    Implication(CKnave,BKnight),

    # C says "A is a knight.". That is true if and only if C is a knight.
    Implication(CKnight,AKnight),
    Implication(AKnight,CKnight)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
