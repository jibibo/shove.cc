const abbreviations = ["", "K", "M", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No"];

function abbreviate(number) {
    // convert a big number to a human-readable abbreviated number
    // converted to JS from backend/formatting.py

    if (number === undefined) {
        console.warn("abbreviate(undefined) called, ignoring");
        return;
    }

    let magnitude = Math.floor(Math.log10(number));

    if (magnitude < 3) {
        // number is too small to abbreviate
        return `${number}`;
    }

    let newNumber = number / Math.pow(10, magnitude);

    if (newNumber >= 9.995) {
        magnitude += 1;
        newNumber /= 10;
    }

    let magnitudeRemainder = magnitude % 3;
    // decimals = ... // decimals can be ignored in JS using toPrecision method
    newNumber *= Math.pow(10, magnitudeRemainder);
    newNumber = newNumber.toPrecision(3); // python doesn't have this

    let abbreviationIndex = Math.floor(magnitude / 3);
    let abbreviation = abbreviations[abbreviationIndex];
    // console.log(number, newNumber, abbreviation, abbreviationIndex);

    return `${newNumber}${abbreviation}`;
}

function thousandsSeperatorFull(x) {
    // https://stackoverflow.com/a/2901298/13216113
    var parts = x.toString().split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return parts.join(".");
}

export { abbreviate, thousandsSeperatorFull };
