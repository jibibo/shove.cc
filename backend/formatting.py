import math

from log import Log


abbreviations_dict = {  # number: (abbreviation, digits_after_comma, denominator)
    1e3: ("K", 2, 1e3),
    1e4: ("K", 1, 1e3),
    1e5: ("K", 0, 1e3),
    1e6: ("M", 2, 1e6),
    1e7: ("M", 1, 1e6),
    1e8: ("M", 0, 1e6),
    1e9: ("B", 2, 1e9),
    1e10: ("B", 1, 1e9),
    1e11: ("B", 0, 1e9),
    1e12: ("T", 2, 1e12),
    1e13: ("T", 1, 1e12),
    1e14: ("T", 0, 1e12),
    1e15: ("Qa", 2, 1e15),
    1e16: ("Qa", 1, 1e15),
    1e17: ("Qa", 0, 1e15),
    1e18: ("Qi", 2, 1e18),
    1e19: ("Qi", 1, 1e18),
    1e20: ("Qi", 0, 1e18),
    1e21: ("Sx", 2, 1e21),
    1e22: ("Sx", 1, 1e21),
    1e23: ("Sx", 0, 1e21),
    1e24: ("Sp", 2, 1e24),
    1e25: ("Sp", 1, 1e24),
    1e26: ("Sp", 0, 1e24),
    1e27: ("Oc", 2, 1e27),
    1e28: ("Oc", 1, 1e27),
    1e29: ("Oc", 0, 1e27),
    1e30: ("No", 2, 1e30),
    1e31: ("No", 1, 1e30),
    1e32: ("No", 0, 1e30)
}


# todo possible solution to this mess: get log of input, lookup how many digits/abbreviation
# just round the number to at most 3 significant digits, and then times 10 or 100 if required
# 13579 -> 1.36 -> 13.6 -> 13.6K
# 999999 -> 10.0 -> is equal to 10 so -> 1.00 -> etc
# 998999 -> 9.99 -> 999K
# 999899 -> 9.99899 -> 10.0
# the 10.0 problem is caused by rounding if the 3rd digit w.xyz (y) is a 9, and (z) >= 5
# 9.994444 -> 9.99
# 9.995555 -> 10.00
def abbreviate_number(n: int) -> str:
    """Return a human-readable string of the given number. Supported range: [0, 1e32]"""

    Log.test(f"INPUT: {n}")

    selected_v = None
    continued_0 = False
    for k, potential_v in abbreviations_dict.items():
        if n < k or continued_0:
            if not selected_v:  # number is too small (n<1000)
                Log.test(f"OUTPUT: {n}")
                return str(n)

            abbreviation, digits_after_comma, denominator = selected_v  # get the settings to abbreviate with
            Log.test(f"--- den: {denominator}, after comma: {digits_after_comma}, abbrev: {abbreviation}, ")

            new_number = n / denominator  # divide the number
            Log.test(f"--- divided to: {new_number}")

            if digits_after_comma:
                new_number = round(new_number, digits_after_comma)  # specific amount of digits after the comma
                Log.test(f"--- dac: yes, rounded to: {new_number}{abbreviation}")
                # if digits_after_comma in [0, 1] and str(new_number)[-1] == "0":
                #     new_number = str(new_number)[:-digits_after_comma + 1]
                #     Log.test(f"dac AND last digit zero: {new_number}")

            else:
                new_number = round(new_number)  # no digits after the comma
                Log.test(f"--- dac: no, rounded to: {new_number}{abbreviation}")

            new_number_str = str(new_number)
            new_number_len = len(new_number_str)
            if not continued_0 \
                    and new_number_str[-1] == "0" \
                    and ((new_number_len > 3 and digits_after_comma == 0)
                         or (new_number_len > 4 and digits_after_comma == 1)):
                continued_0 = True
                selected_v = potential_v
                Log.test("--- round problem, continuing")
                continue

            Log.test(f"OUTPUT: {new_number}{abbreviation}")
            return f"{new_number}{abbreviation}"

        selected_v = potential_v
