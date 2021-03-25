import math

from log import Log

abbreviations = ["", "K", "M", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No"]


def abbreviate(number: int) -> str:
    """
    Return a human-readable string of the given number. Supported range: [0, 1e32]
    Should usually just be done by the frontend, saves a lot of packets
    """

    # print(f"\tabbreviating {number}")
    magnitude = int(math.floor((math.log10(number))))
    # print(f"\tmagnitude = {magnitude}")

    if magnitude < 3:
        # print("\tmagnitude < 3, returning original number")
        return str(number)

    new_number = number / 10 ** magnitude

    if new_number >= 9.995:  # possible carry-over that turns rounding into n >= 10 instead of [1, 9.99]
        magnitude += 1
        # print(f"\tmagnitude divison result {new_number} >= 9.995, increased magnitude to {magnitude}, dividing by 10 again")
        new_number /= 10

    # print(f"\tdivided by magnitude of {magnitude}, result: {new_number}")

    magnitude_remainder = magnitude % 3
    decimals = None if (magnitude_remainder == 2 or magnitude < 3) else 2 - magnitude_remainder
    # print(f"\tmagnitude_remainder = {magnitude_remainder}, decimals = {decimals}")

    new_number *= 10 ** magnitude_remainder
    # print(f"\tmultiplied with 10**magnitude_remainder, result: {new_number}")

    new_number = round(new_number, decimals)
    # print(f"\trounded, result: {new_number}")

    abbreviation_index = int(magnitude / 3)
    abbreviation = abbreviations[abbreviation_index]
    # print(f"\tabbreviation_index = {abbreviation_index}, abbreviation = {abbreviation}")

    abbreviated_number = str(new_number) + abbreviation
    # print(f"\tdone, result: {abbreviated_number}")

    Log.test(f"Abbreviated {number} to {abbreviated_number}")
    return abbreviated_number
