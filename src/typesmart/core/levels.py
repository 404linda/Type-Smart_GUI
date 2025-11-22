BEGINNER_LEVEL = [
    "asdf jkl qwe rty",
    "zxcv bn m po iu",
    "qaz wsx edc rfv",
] + [f"wordset {i}" for i in range(10)]

INTERMEDIATE_LEVEL = [
    "The quick brown fox jumps over the lazy dog.",
    "Typing improves focus and muscle memory.",
] + [f"Intermediate sentence {i}" for i in range(10)]

EXPERT_LEVEL = [
    "Expert typing requires endurance, precision, and mental stamina.",
    "Long-form typing helps develop high sustained WPM.",
] + [f"Expert paragraph {i}" for i in range(10)]

LEVELS = {
    1: BEGINNER_LEVEL,
    2: INTERMEDIATE_LEVEL,
    3: EXPERT_LEVEL
}
