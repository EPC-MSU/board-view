from json import dumps, loads
from argparse import ArgumentParser


def convert(path_from: str, path_to: str):
    """
    Convert EyePoint P10 json to EyePoint S1 json
    * squash all elements to one element
    * replace 'number_points' -> 'n_points'
    * replace 'number_charge_points' -> 'n_charge_points'
    * add "comment" field if not exists
    :param path_from: path to EyePoint P10 json
    :param path_to: Path to new EyePoint S1 json
    :return: None
    """

    replace = {
        "number_points": "n_points",
        "number_charge_points": "n_charge_points"
    }

    with open(path_from, "r", encoding="utf-8") as file:
        s = file.read()
        for f, t in replace.items():
            s = s.replace(f, t)
        _input = loads(s)

    for element in _input["elements"]:
        for pin in element["pins"]:
            if "comment" not in pin:
                pin.update({"comment": ""})

    first_element = _input["elements"][0]

    for element in _input["elements"][1:]:
        for pin in element["pins"]:
            first_element["pins"].append(pin)

    with open(path_to, "w", encoding="utf-8") as file:
        s = dumps({
            "elements": [first_element]
        })
        file.write(s)


if __name__ == "__main__":
    parser = ArgumentParser(description="Convert EyePoint P10 components json to EyePoint S1 json")
    parser.add_argument("input", help="Path to source file")
    parser.add_argument("output", help="Path to destination file")

    args = parser.parse_args()
    convert(args.input, args.output)
