"""Finite sanity checks only; not a proof assistant or an in-model NFA simulator.

verify_with_guess scans its read-only input once and stores a guessed index.
The test harness enumerates guesses externally; that harness is NOT claimed
as a deterministic logspace decider for INDEX.
"""

def encode_index(word, position):
    width = max(1, len(word).bit_length())
    return word + "#" + format(position, f"0{width}b")


def verify_with_guess(stream, guess):
    m = 0
    selected_one = False
    separated = False
    value = 0
    width = 0
    invalid = False
    for ch in stream:
        if not separated:
            if ch == "#":
                separated = True
            elif ch in "01":
                m += 1
                if m == guess:
                    selected_one = ch == "1"
            else:
                invalid = True
        elif ch in "01":
            # Saturate both numeric value and length, so invalid suffixes
            # cannot silently consume linear working memory.
            value = min(m + 1, 2 * value + int(ch))
            width = min(m.bit_length() + 1, width + 1)
        else:
            invalid = True
    return (not invalid and separated and m >= 1 and selected_one and
            width == m.bit_length() and 1 <= value <= m and value == guess)


def harness_accepts(text):
    # Deliberately outside the restricted model: finite test branch enumeration.
    m = text.find("#")
    return any(verify_with_guess(iter(text), position) for position in range(1, max(m, 0)+1))
