#!/usr/bin/env python3.10

from os import path, listdir
from sys import stderr, exit, version_info
from json import load
from dataclasses import dataclass
from typing import Callable, Union, Any
from uuid import uuid4
from difflib import get_close_matches
from re import sub, finditer, findall

# If you're reading all this, then you're in for a ride :)
# If you wanna skip to the Converter class, line 154

header = r"""
╔═══════════════════════════════════════════════════════╗
║  ,.-</#@$>,      ,.-~=+>#$@>$#$(>*"`   ,..<&%#$       ║
║ /|$      \%$     "'`    \#$#          /%<             ║
║ |&%   ,.   '             |%|         |$?              ║
║  \#$   \$.,              $#           \$\      ,$     ║
║   `<&>,./.d             <>?             <%>#$#%/      ║
║     `'*'`               `                  ``         ║
║ G E N E R A L  T R A N S C R I P T  C O N V E R T E R ║
╚═════╤═══════════════════════════════════════════╤═════╝
      │  Made by 0xity (mostly) and BlueEyedFox_  │
      └───────────────────────────────────────────┘

"""  # Thank you BlueEyedFox_ fox this awesome header!

if version_info < (3, 10):  # Check if the python version is right
    if __name__ == "__main__":
        exit("This script requires Python 3.10 or higher.")
    else:
        exit("The GTC module requires Python 3.10 or higher.")


def _handle_invalid_symbol(symbol: str) -> Union[str, None]:
    user_input = input(f'''
"{symbol}" is not a valid symbol.
(1) `Remove` it.
(2) `Replace` it.
(3) `Assign` it. (will replace existing value of the key)
(4) `Include` the next # characters and ask again.
(5) `Ignore` it.
(6) Turn it to a `note`.

Type the number of the chosen option or the word in `backticks`.

> ''')
    match user_input.lower():  # Case insensitive.
        case "1" | "remove":
            return "remove"
        case "2" | "replace":
            return "replace"
        case "3" | "assign":
            return "assign"
        case "4" | "include":
            return "include"
        case "5" | "ignore":
            return "ignore"
        case "6" | "note":
            return "note"
        case _:
            print("\nInvalid option.\n")


def _handle_doubled(
        symbol: str,
        ids_and_descriptions: dict[str, str]
) -> Union[str, None]:
    # Number the IDs.
    # Then store tuples with the number, ID and description of the symbols.
    options = [
        (str(list(ids_and_descriptions.keys()).index(id) + 1), id, description)
        for id, description in ids_and_descriptions.items()
    ]
    
    input_prompt = f'''
"{symbol}" belongs to multiple keys.
(0) None (will handle "{symbol}" as an invalid value.
'''

    for option in options:
        input_prompt += f"({option[0]}) {option[1]} -- {option[2]}\n"
        # Would look like "(1) ID -- Explanation"
    input_prompt += "\n\nType the number or ID of chosen option.\n\n> "

    # Options was initially a dict, too lazy to recode this part,
    #   so I'll just turn the list back into a dict. - @0xity
    options = {option[0]: option[1] for option in options} # {index: ID}

    # Case insensitive.
    user_input = input(input_prompt).lower()
    if user_input in ["0", "none"]:
        return "ignore"
    elif user_input in options.keys():
        return options[user_input]
    elif user_input in options.values():
        return user_input
    else:
        print("\nInvalid option.\n")


def _handle_invalid_id(id) -> Union[str, None]:
    user_input = input(f'''
"{id}" doesn't have a value in the output system.
(1) `Remove` it.
(2) `Replace` it.
(3) `Assign` a symbol to it.
(4) Turn it into a `note`.

Type the number of the chosen option or the word in `backticks`.

> ''').lower()
    match user_input:
        case "1" | "remove":
            return "remove"
        case "2" | "replace":
            return "replace"
        case "3" | "assign":
            return "assign"
        case "4" | "note":
            return "note"
        case _:
            print("\nInvalid option.\n")


# Function to be used whenever an action needs to be confirmed
def _ask_for_confirmation(prompt: str) -> bool:
    # True is always "yes", False is always "no"

    # I wanted to make this function have only the prompt parameter
    #   so that if another function is given instead of this one
    #   that function doesn't need to support parameters it doesn't use.

    # This is how I'm handling default values
    # A website, for example, might not need this. - @0xity

    user_input = input(prompt).lower()[:1]
    if prompt[-6:] == "[Y/n] ":
        match user_input:
            case "n":
                return False
            case _:
                return True
    else:
        match user_input:
            case "y":
                return True
            case _:
                return False


@dataclass  # These things are so cool! They make classes so convenient! - @0xity
class Converter:
    # If True, skips prompting the user
    fast: bool = False

    # User input methods
    input_method: Callable[str, str] = input
    invalid_symbol_method: Callable[str, str] = _handle_invalid_symbol
    doubled_symbol_method: Callable[[str, dict[str, str]], str] = _handle_doubled
    invalid_id_method: Callable[str, str] = _handle_invalid_id
    confirmation_method: Callable[str, bool] = _ask_for_confirmation

    chart_folder_path: str = path.join(
        # "notation_systems2" folder next to script
        path.dirname(path.abspath(__file__)), "notation_systems2"
    )

    def load_charts(self) -> list[dict[str, Any]]:
        """
        Loads JSON files from folder_path.
        """
        json_list = []
        for file_name in listdir(self.chart_folder_path):
            if file_name.endswith(".json"):
                try:
                    file_path = path.join(self.chart_folder_path, file_name)
                    with open(file_path, "r", encoding="utf-8") as file:
                        json_list.append(load(file))
                except Exception as e:
                    stderr.write(f"Error reading {file_name}: {e}")

        return json_list

    def find_chart(
        self, chart_name: str, all_charts: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Returns the chart that matches the name given.
        """
        for chart in self.load_charts():
            if chart_name in chart["chart_names"]:
                return chart

    #      ______)          ________)
    #     (, /  /)         (, /
    #       /  (/    _       /___,    __  __
    #    ) /   / )__(/_   ) /    (_(_/ )_/ )_(_/
    #   (_/              (_/                .-/-,
    #                                      (_/

    def translate(
        self,
        input_chart: dict[str, Any],
        output_chart: dict[str, Any],
        notation: str,
        *, indicator_priority: bool = False
    ) -> str:
        """
        Translates notation from input chart to output chart.

        If self.fast is false, it prompts the user for confirmation and handling.

        PARAMETERS:
        input_chart, output_chart: Objects from JSON files.
        notation: String to be translated.

        RETURNS:
        Translated notation as string.
        """

        # TODO:  [F]eature  [A]utomation  [B]ugfix  [R]ework  -  indicate the task is finished
        #        (E)asy     (M)edium      (H)ard
        #        {L}ow   /  {H}igh Priority
        # [F] Split lines of user input, separate notes and notation (M)
        # [A] Iterate through notation and match symbols with input chart (E)
        #  - [A] Increase search range for symbols composed of multiple characters
        # [F] Convert symbols to IDs (E)
        # [A] Convert IDs to output chart symbols (E)
        # [F] Handle edge cases (M)
        #  - [F] Invalid values
        #  - [F] Doubled values
        #     - [B] Handle end of line edge case
        #  - [F] Invalid keys
        #  - [F] Incomplete symbols
        #     - [A] Split into complete ones if possible (i.e. turn ".." into two pauses)
        # [B] Fix pass by multiple matches with fast mode (E)
        # [B] Fix invalid symbol with fast mode (E)
        # [F] difflib.get_close_matches() to match user input notes to chart notes (E)
        #  - [ ] Fix note insertion order. (Index note symbol position?)
        # [ ] Macro translations (H)
        #  - [ ] Translate note to multiple IDs {L}
        #  - [ ] Translate multiple IDs to one note {H}
        # [ ] Property logic (M)
        #  - [A] Separate shiftstones
        #  - [F] Order after mods
        #  - [F] Strict numbering
        #  - [ ] Fuzzy match symbols (H) {L}
        # [F] Insert tokens (M)
        #  - [R] Support symbols with multiple tokens. {H}
        #  - [ ] Handle indicators with a more modular system.
        #  - [ ] Fix #STRWSTATE# {H}
        #  - [R] Fix #NUMBER# token to use chart digits.
        #  - [ ] Fix structure numbering after reinsertion. (Make numbering post-translation?) {L}
        #  - [ ] Include replaced notation when turning symbol to note {H}
        # [ ] Symbol overrides {H}
        # [ ] Token and tokenless symbol conversion (E) {L}
        #  - [ ] Tokenless to token
        #  - [ ] Token to tokenless

        try:

            #=======================#
            #                       #
            #      DEFINITIONS      #
            #                       #
            #=======================#

            # Translation variables.
            last_symbol_was_valid = False
            translating_shiftstones = False
            start_index, end_index = 0, 1
            translated_notation = ""
            notation = notation.splitlines()
            regex_chars = ["\\", ".", "^", "$", "*", "+", "-", "?", "(", ")", "[", "]", "{", "}", "|", "/"]
            symbols_to_ids = []
            replaced_notation = {}
            symbol_notes = {}

            # Pre-load some queries for performance and convenience.
            input_symbols = input_chart["symbols"]
            output_symbols = output_chart["symbols"]

            # Unless numbers are explicitly specified in the JSON, add them automatically.
            # If you add a number yourself, I expect you to add all numbers from 0 to 9.
            found_digits = False
            for symbol_chart in [input_symbols, output_symbols]:
                for symbol in symbol_chart.values():
                    if "tags" in symbol and "number" in symbol["tags"]:
                        found_digits = True
                        break
                if not found_digits:
                    for digit in range(10):
                        symbol_chart.update(
                            # WARN: Include macro notes here whenever they're implemented.
                            {
                                f"digit_{digit}" : {
                                    "text": str(digit),
                                    "description": f"The digit {digit}, used in numbering and reusing structures.",
                                    "tags": ["number"]
                                }
                            }
                        )
                else:
                    if missing_digits := [
                        str(d) for d in range(10)
                        if f"digit_{d}" not in symbol_chart.keys()
                    ]:
                        input_or_output = "output" if symbol_chart == output_symbols else "input"
                        print(
                            (
                                f"WARNING: Numbers are explicitly specified in {input_or_output} chart, "
                                f"but {",".join(missing_digits)} are missing.\n"
                                "They will not be autocompleted. "
                                "If you define the digits yourself, I expect you to define all of them."
                            )
                        )
                        del input_or_output

                # Some other default symbols that should be added automatically.
                # I put them in here to avoid another iteration through both charts.
                symbols_to_add = {
                    "clarity_space": {
                        "text": " ",
                        "description": "A space.",
                        "tags": ["space"]
                    }
                }
                for id, symbol in symbols_to_add.items():
                    if id not in symbol_chart:
                        symbol_chart.update({id: symbol})
            del found_digits, symbols_to_add

            input_properties = input_chart["properties"]
            output_properties = output_chart["properties"]

            def search_symbol(chars: str, chart_symbols: dict[str, Any]) -> dict[str, str]:
                # Return a dict with ID: Text pairs for every symbol that starts with `chars`.
                return {
                    id: chart_symbols[id]["text"] for id in chart_symbols
                    if chart_symbols[id]["text"].startswith(chars)
                }

            def next_chars():
                nonlocal start_index, end_index
                start_index = end_index - 1
                start_index += 1
                end_index += 1

            def store_ids(list_of_ids: list):
                symbols_to_ids.extend(list_of_ids)

            def check_if_has_tag(symbol: dict, tag: str) -> bool:
                return "tags" in symbol and tag in symbol["tags"]

            def separate_note(line: str):
                input_note_symbols = [
                    symbol["text"] for symbol in input_symbols.values()
                    if check_if_has_tag(symbol, "note_symbol")
                ]

                for symbol in input_note_symbols:
                    if line.startswith(symbol):
                        return (symbol, line[len(symbol):])
                return None

            def get_first_note_symbol(chart_symbols: dict):
                for id in chart_symbols:
                    if check_if_has_tag(chart_symbols[id], "note_symbol"):
                        return id
                return None

            def check_if_is_note(id: str) -> bool:
                try:
                    return check_if_has_tag(output_symbols[id], "note_symbol")
                except KeyError:
                    print(f"ID {id} NOT IN OUTPUT CHART")
                    return False

            # re.escape() escapes hashtags too, which I don't want. - @0xity
            def escape_regex_chars(string: str) -> str:
                output = string
                for char in regex_chars:
                    output = output.replace(char, fr"\{char}")
                return output

            def find_escaped_symbols_with_tag(tag: str) -> list:
                output = [
                    symbol["text"] for symbol in input_symbols.values()
                    if check_if_has_tag(symbol, tag)
                ]
                return [escape_regex_chars(symbol) for symbol in output]

            # Preload variables for performance and convenience, again.
            input_note_symbol = get_first_note_symbol(input_symbols)
            output_note_symbol = get_first_note_symbol(output_symbols)
            del get_first_note_symbol  # Won't need this anymore since we stored both symbols in variables.
            token_symbols = [
                symbol["text"] for symbol in input_symbols.values()
                if check_if_has_tag(symbol, "token")
            ]
            token_symbols = sorted(token_symbols, key=len, reverse=True)  # To mitigate order pritority
            print(f"TOKEN SYMBOLS: {token_symbols}")

            # Temp queries for the tokens.
            structures = find_escaped_symbols_with_tag("structure")
            structure_states = find_escaped_symbols_with_tag("structure_state")
            modifiers = find_escaped_symbols_with_tag("modifier")
            mirrorables = find_escaped_symbols_with_tag("mirrorable")
            indicators = find_escaped_symbols_with_tag("indicator")
            numbers = find_escaped_symbols_with_tag("number")
            symbols = [symbol["text"] for symbol in input_symbols.values()]
            symbols = [escape_regex_chars(symbol) for symbol in symbols]
            symbols.sort(reverse=True, key=lambda symbol: len(symbol))

            indicator_symbols = {
                id: symbol for id, symbol in input_symbols.items()
                if check_if_has_tag(symbol, "indicator")
            }
            indicator_chart = input_chart.copy()
            indicator_chart["symbols"] = indicator_symbols
            indicator_chart["chart_names"] = ["indicator chart"]
            del indicator_symbols, find_escaped_symbols_with_tag

            # WARN: Replace this with a modular system later.
            if "insanity" in input_chart["chart_names"]:
                input_symbols = {
                    id: symbol for id, symbol in input_symbols.items()
                    if not check_if_has_tag(symbol, "indicator")
                }

            # Token regex to store and replace symbols.
            regex_patterns = {
                # WARN: Replace digits with numbers from chart.
                "#STRUCTURE#": f"\\d+|{"\\d*|".join(structures)}\\d*",
                "#STRWSTATE#": f"{"|".join(structure_states)}".replace("#STRUCTURE#", f"(?:\\d+|{"\\d*|".join(structures)}\\d*)"),
                "#MODIFIER#": f"{"|".join(modifiers)}",
                "#MIRROR#": f"{"|".join(mirrorables)}",
                "#NUMBER#": f"(?:{"|".join(numbers)})+",
                "#NOTATION#": f"(?:{"+|".join(symbols)})+".replace("#STRUCTURE#", f"(?:\\d+|{"\\d*|".join(structures)}\\d*)"),
                "#SYMBOL#": f"{"|".join(symbols)}",
                "#TEXT#": r"\w+",
                "#POSITIONALINDICATORS#": f"(?:{"|".join(indicators)})+".replace("#STRWSTATE#", f"(?:{")|(?:".join(structure_states)})".replace("#STRUCTURE#", f"(?:\\d+|{"\\d*|".join(structures)}\\d*)"))
            }
            del structures, structure_states, modifiers, mirrorables
            del symbols, indicators, numbers

            input_shiftstone_separators = {
                id: symbol["text"] for id, symbol in input_symbols.items()
                if check_if_has_tag(symbol, "shiftstone_separator")
            }

            # If it can separate the note symbol, the line is a note.
            notes = [line for line in notation[1:] if separate_note(line)]

            # First line is excluded because notes always come after notation.
            # The first line being a note doesn't make sense.
            # If you're translating in bulk and there's a move starting in a note,
            #   tough luck. - @0xity

            notation = [line for line in notation if line not in notes]
            print(f"NOTATION: {repr(notation)}")
            # Remove beginning note symbols from note content.
            notes = [separate_note(line)[1] for line in notes]
            symbol_notes = {
                id: symbol["notes"] for id, symbol in output_symbols.items()
                if "notes" in symbol
            }

            #=======================#
            #                       #
            #    PRE-TRANSLATION    #
            #                       #
            #=======================#

            # Replace all tokens in all token symbols with regex patterns.
            symbols_with_tokens = [
                symbol["text"] for symbol in input_symbols.values()
                if check_if_has_tag(symbol, "token")
            ]
            symbols_with_tokens.sort(reverse=True, key=lambda token: len(token))
            symbol_expressions = symbols_with_tokens.copy()
            for index in range(len(symbol_expressions)):
                symbol = escape_regex_chars(symbol_expressions[index])
                match_spans = []
                for token in regex_patterns.keys():
                    for match in finditer(token, symbol):
                        match_spans += [(match.start(), match.end(), match.group())]
                match_spans.sort(reverse=True, key=lambda span: span[0])
                for span in match_spans:
                    symbol = symbol[:span[0]] + f"({regex_patterns[span[2]]})" + symbol[span[1]:]
                symbol_expressions[index] = symbol
            symbol_expressions = {
                symbol_expressions[index]: symbols_with_tokens[index]
                for index in range(len(symbol_expressions))
            }
            del symbols_with_tokens

            # Match regex patterns with notation, then store and translate matched groups.
            # That's right baby, we're putting a converter INSIDE the converter! - @0xity
            match_converter = Converter()
            match_converter.fast = self.fast
            matches = []
            for line_index in range(len(notation)):
                line = notation[line_index]
                for expression in symbol_expressions.keys():
                    print(symbol_expressions[expression])
                    for match in finditer(expression, line):
                        print(f"GROUP FOUND: {match.group()}\nSYMBOL: {symbol_expressions[expression]}\nEXPRESSION: {expression}\n")
                        tokens_in_order = findall(
                            f"({"|".join(regex_patterns.keys())})",
                            symbol_expressions[expression]
                        )
                        print(tokens_in_order)
                        for group_index in range(len(match.groups())):
                            if tokens_in_order[group_index] == "#POSITIONALINDICATORS#":
                                translated_match = match_converter.translate(
                                    indicator_chart,
                                    output_chart,
                                    match.group(group_index + 1),
                                    indicator_priority=True
                                )
                            else:
                                translated_match = match_converter.translate(
                                    input_chart,
                                    output_chart,
                                    match.group(group_index + 1)
                                )
                            matches.append(
                                (line_index, match.start(group_index + 1), translated_match)
                            )
                        line = line[:match.start()] + symbol_expressions[expression] + line[match.end():]
                matches.sort(key=lambda match: (match[0], match[1]))
                print(matches)
                notation[line_index] = line
            del match_converter

            # Replace notes with symbols where possible.
            # For every note, if it corresponds to a symbol, it adds the ID to note_replacements,
            #   and if it doesn't, it adds None.
            # WARN: Will probably need to be replaced with a better system
            #   that accounts for notes added after translation.
            note_replacements = []
            all_notes = []
            for id_note in symbol_notes.values():
                all_notes.extend(id_note)
            note_index = 0
            for note in notes:
                print(f"NOTE: {note}")
                # The cutoff was chosen by trial and error.
                if close_match := get_close_matches(note, all_notes, n=1, cutoff=0.611):
                    print(f"CLOSE MATCH: {close_match}")
                    matching_id = [
                        id for id in symbol_notes.keys()
                        if close_match[0] in symbol_notes[id]
                    ][0]
                    if matching_id in output_symbols:
                        note_replacements.append(matching_id)
                        notes.pop(note_index)
                    else:
                        print("MATCH DOESN'T HAVE SYMBOL IN OUTPUT CHART, NOTE PRESERVED")
                        note_replacements.append(None)
                else:
                    note_replacements.append(None)
                note_index += 1

            if indicator_priority:
                input_chart = indicator_chart
                input_symbols = indicator_chart["symbols"]

            print(f"NOTATION: {notation}\nNOTES: {notes}")

            #=======================#
            #                       #
            #   TRANSLATION TO ID   #
            #                       #
            #=======================#

            for line_index in range(len(notation)):
                line = notation[line_index]
                print(f"CURRENTLY TRANSLATING: {line}")

                # If input chart separates shiftstones
                #   and there's a separator in the notation, only translate shiftstones
                #   until it reaches the separator.
                if input_properties["separate_shiftstones"]:
                    for separator in input_shiftstone_separators.values():
                        if separator in line:
                            translating_shiftstones = True
                            break

                if translating_shiftstones:
                    input_symbols = {
                        id: symbol for id, symbol in input_symbols.items()
                        if check_if_has_tag(symbol, "shiftstone")
                        or check_if_has_tag(symbol, "shiftstone_separator")
                    }
                else:
                    input_symbols = {
                        id: symbol for id, symbol in input_symbols.items()
                        if not check_if_has_tag(symbol, "shiftstone")
                        and not check_if_has_tag(symbol, "shiftstone_separator")
                    }

                # Stores amount of previous detected symbols.
                previous_matches = 0

                while end_index <= len(line):
                    current_segment = line[start_index:end_index]
                    print(f"CURRENT SEGMENT: {current_segment}")

                    # If symbol turned to note (from invalid symbol handling),
                    #   add ID of first note symbol found, add contents to notes and move on.
                    if current_segment in symbol_notes:
                        note_symbol_id = input_note_symbol
                        if note_symbol_id:
                            store_ids([note_symbol_id])
                            notes.append(symbol_notes[current_segment])
                            next_chars()
                        else:
                            print("Input chart doesn't have note symbol.")
                        continue

                    print(
                        f"PREVIOUS MATCHES: {previous_matches}\n"
                        f"LAST SYMBOL WAS VALID: {last_symbol_was_valid}"
                    )
                    # Handle symbol based on how many IDs it could match.
                    match len(detected_symbols := search_symbol(current_segment, input_symbols)):
                        # No matches.
                        case 0:
                            print(f"NO SYMBOL FOUND FOR {current_segment}")
                            current_segment = line[start_index:end_index]
                            print(f"CURRENT SEGMENT: {current_segment}")
                            if previous_matches == 1 and not last_symbol_was_valid:
                                new_segment_start = 0
                                for char in range(len(current_segment)):
                                    if len(
                                        new_detected_symbols := [
                                            symbol
                                            for symbol in input_symbols
                                            if input_symbols[symbol]["text"] == current_segment[new_segment_start:char + 1]
                                        ]
                                    ) == 1:
                                        print("SEPARATED INCOMPLETE SYMBOL IN VALID ONES")
                                        store_ids(new_detected_symbols)
                                        print(f"STORED IDS: {new_detected_symbols}")
                                        new_segment_start += 1
                                        previous_matches = 1
                                        last_symbol_was_valid = True
                                next_chars()
                                continue
                            if previous_matches > 1:
                                print("PASSED BY MULTIPLE MATCHES, REVERTING SEARCH RANGE")
                                print(f"BEFORE END INDEX DEINCREMENT: {current_segment}")
                                if len(current_segment) > 1:
                                    end_index -= 1
                                    # Update variables with new end index.
                                    current_segment = line[start_index:end_index]
                                print(f"AFTER END INDEX DEINCREMENT: {current_segment}")
                                detected_symbols = search_symbol(current_segment, input_symbols)
                                print(f"CURRENT SEGMENT: {current_segment}")
                                print(f"DETECTED SYMBOLS: {detected_symbols}")

                                match len(
                                    possible_matches := {
                                        id: output_symbols[id]["description"] for id in detected_symbols.keys()
                                        if detected_symbols[id] == current_segment
                                    }
                                ):
                                    case 1:
                                        print(f"ONE POSSIBLE MATCH: {possible_matches}")
                                        store_ids(possible_matches)
                                        next_chars()
                                        continue

                                    case _:
                                        if self.fast:
                                            # Stores the first possible match.
                                            # Top most match in JSON file takes precedence.
                                            store_ids([list(possible_matches.keys())[0]])
                                            next_chars()
                                            continue
                                        else:
                                            print(f"POSSIBLE MATCHES: {possible_matches}")
                                            selection = self.doubled_symbol_method(
                                                current_segment,
                                                possible_matches
                                            )
                                            if not selection:
                                                continue
                                            # If selection == "ignore", skips to invalid handling due to no continue.
                                            if selection != "ignore":
                                                store_ids([selection])
                                                print(f"STORED IDS: {selection}")
                                                next_chars()
                                                continue

                            # If previous segment didn't have multiple IDs it could match,
                            #   handle it as an invalid symbol.
                            if self.fast:
                                # Not exactly sure why I need to deincrement end_index... - @0xity
                                end_index -= 1
                                next_chars()
                            else:
                                print("INVALID SYMBOL HANDLING")
                                match self.invalid_symbol_method(current_segment):
                                    case "remove":
                                        next_chars()

                                    case "replace":
                                        replacement = self.input_method(f"Replace {current_segment} with: ")
                                        if not self.confirmation_method("Replace all instances? [y/N] "):
                                            line = line.replace(current_segment, replacement, 1) # One instance
                                        else:
                                            line = line.replace(current_segment, replacement) # All instances
                                        end_index = start_index + 1

                                    case "assign":
                                        assignment = self.input_method(
                                            "WARNING -- This will override any existing ID!"
                                            f"Enter an identifier for {current_segment}: "
                                        )
                                        if assignment == "":
                                            print("Invalid input.")
                                            continue
                                        if self.confirmation_method("Apply assignment to all instances? [Y/n] "):
                                            input_symbols.update(
                                                {
                                                    assignment: {
                                                        "text": current_segment,
                                                        "description": "Symbol assigned by user."
                                                    }
                                                }
                                            )
                                        else:
                                            store_ids([assignment])

                                    case "include":
                                        try:
                                            characters_to_insert = int(
                                                self.input_method(
                                                    "Enter the amount of characters to include, negative for previous characters: "
                                                )
                                            )
                                            if characters_to_insert > len(line[end_index:]):
                                                print("AMOUNT EXCEEDED LINE LENGTH, CAPPED LENGTH")
                                                characters_to_insert = line[end_index:]
                                            if characters_to_insert <= -len(current_segment):
                                                print("AMOUNT EXCEEDED SYMBOL LENGTH, CAPPED LENGTH")
                                                characters_to_insert = -len(current_segment) + 1
                                            end_index += characters_to_insert
                                            current_segment = line[start_index:end_index]

                                            if len(
                                                new_detected_symbols := [
                                                    symbol
                                                    for symbol in input_symbols
                                                    if input_symbols[symbol]["text"] == current_segment
                                                ]
                                            ) == 1:
                                                store_ids(new_detected_symbols)
                                                next_chars()
                                                continue
                                        except ValueError:
                                            print("INVALID NUMBER")

                                    case "ignore":
                                        # Add the symbol to both charts with the same random ID.
                                        # They get treated as valid symbols, with the same properties.
                                        randomized_id = f"randomized_id_{uuid4()}"
                                        for chart in [input_symbols, output_symbols]:
                                            chart.update(
                                                {
                                                    randomized_id: {
                                                        "text": current_segment,
                                                        "description": "User prompted to ignore."
                                                    }
                                                }
                                            )
                                        continue

                                    case "note":
                                        note_contents = self.input_method(f"Enter note contents for {current_segment}: ")
                                        if self.confirmation_method("Replace all instances? [Y/n] "):
                                            symbol_notes.update({current_segment: note_contents})
                                        else:
                                            note_symbol_id = input_note_symbol
                                            if not note_symbol_id:
                                                print("Input chart doesn't have note symbol.")
                                            else:
                                                store_ids([note_symbol_id])
                                                notes.append(note_contents)
                                    case _:
                                        continue

                            last_symbol_was_valid = False
                            previous_matches = 0
                            next_chars()

                        # One match.
                        case 1:
                            print(f"FOUND EXACTLY ONE SYMBOL FOR {current_segment}")
                            id_to_match = list(detected_symbols.keys())[0]
                            if current_segment == detected_symbols[id_to_match]:
                                if id_to_match in input_shiftstone_separators.keys() and translating_shiftstones:
                                    input_symbols = {
                                        id: symbol for id, symbol in input_chart["symbols"].items()
                                        if symbol not in input_symbols.values()
                                    }
                                    translating_shiftstones = False

                                store_ids([x for x in detected_symbols])
                                next_chars()
                                last_symbol_was_valid = True
                            else:
                                print("MATCH NOT REACHED YET, INCREASING SEARCH RANGE")
                                end_index += 1
                                last_symbol_was_valid = False
                            previous_matches = 1

                        # Multiple matches.
                        case _:
                            print(f"MULTIPLE SYMBOLS FOUND FOR {current_segment}:\n{detected_symbols}")
                            print("INCREASING SEARCH RANGE")
                            previous_matches = len(detected_symbols)
                            end_index += 1
                            last_symbol_was_valid = False

            #=======================#
            #                       #
            #     ID PROCESSING     #
            #                       #
            #=======================#

                print(f"IDS: {symbols_to_ids}")

                input_symbols = input_chart["symbols"]  # Reinclude shiftstone symbols.

                # If input chart has separator and output one doesn't, remove separator.
                if (
                    input_properties["separate_shiftstones"]
                    and not output_properties["separate_shiftstones"]
                ):
                    symbols_to_ids = [
                        id for id in symbols_to_ids 
                        if id in input_symbols
                        and not check_if_has_tag(input_symbols[id], "shiftstone_separator")
                    ]

                # If input chart doesn't have separator and output one does, insert separator.
                if (
                    not input_properties["separate_shiftstones"]
                    and output_properties["separate_shiftstones"]
                ):
                    id_index = 0
                    separator = [
                        id for id, symbol in output_symbols.items()
                        if check_if_has_tag(symbol, "shiftstone_separator")
                    ][0]
                    if not separator:
                        print(
                            "WARNING: Output chart separates shiftstones, "
                            "but no separator was defined in the chart."
                        )
                        del separator
                    else:
                        for id in symbols_to_ids:
                            if not check_if_has_tag(input_symbols[id], "shiftstone"):
                                if id_index > 0:
                                    symbols_to_ids.insert(id_index, separator)
                                    del separator
                                break
                            id_index += 1

                # For every note symbol, check if it can be replaced by a symbol.
                # Recycled variables to avoid unnecessary new variables.
                # WARN: This currently doesn't work when turning a symbol into a note,
                #   unless said symbol is after every note in the notation.
                id_index = 0
                note_index = 0
                for id in symbols_to_ids:
                    if check_if_is_note(id):
                        if note_replacements[note_index]:
                            symbols_to_ids[id_index] = note_replacements[note_index]
                            note_index += 1
                    id_index += 1

                # If input chart numbers structures after mods and output doesn't, switch order.
                if (
                    input_properties["order_after_mods"]
                    and not output_properties["order_after_mods"]
                ):
                    print("OUTPUT SYSTEM ORDERS BEFORE MODS, MUST REORDER")

                    insertion_index = None
                    current_index = 0
                    digits = {}

                    # Put digits in reverse order, remove them from notation and move them before mods.
                    def reorder():
                        nonlocal digits, insertion_index
                        if len(digits) > 0 and insertion_index is not None:
                            print(f"DIGITS EXIST ({digits}), REORDERING")
                            print(symbols_to_ids)
                            # Removes digits from end to start.
                            for index, digit in tuple(digits.items())[::-1]:
                                symbols_to_ids.pop(index)

                            # Inserts them back in reverse reverse order, so the correct one essentially.
                            for index, digit in tuple(digits.items())[::-1]:
                                symbols_to_ids.insert(insertion_index, digit)
                                print(symbols_to_ids)
                        # Reset variables for the next cycle.
                        insertion_index = None
                        digits = {}

                    for current_index in range(len(symbols_to_ids)):
                        id = symbols_to_ids[current_index]
                        symbol = output_symbols[id]
                        print(f"ID: {id}")
                        match (
                            check_if_has_tag(symbol, "modifier"),
                            check_if_has_tag(symbol, "number")
                        ):
                            case (True, False):
                                # If ID is modifier, 
                                print("MODIFIER, NOT NUMBER")
                                if len(digits) > 0 and insertion_index is not None:
                                    reorder()

                                # Set insertion index to the first modifier.
                                # Digits will take up its place.
                                if insertion_index is None:
                                    insertion_index = current_index

                                print(f"INSERTION_INDEX: {insertion_index}")

                            case (False, True):
                                print("NOT MODIFIER, NUMBER")
                                digits.update({current_index: id})

                                if current_index == len(symbols_to_ids) - 1:
                                    reorder()

                            case (False, False):
                                # The check if the reorder is needed is already included in the reorder function.
                                reorder()

                    del reorder, id, symbol, digits, insertion_index

                # Same thing again, but mods get moved instead of digits.
                if (
                    not input_properties["order_after_mods"]
                    and output_properties["order_after_mods"]
                ):
                    print("OUTPUT SYSTEM ORDERS AFTER MODS, MUST REORDER")

                    insertion_index = None
                    current_index = 0
                    mods = {}

                    def reorder():
                        nonlocal mods, insertion_index
                        if len(mods) > 0 and insertion_index is not None:
                            print(f"MODS EXIST ({mods}), REORDERING")
                            print(f"INSERTION INDEX: {insertion_index}")
                            print(symbols_to_ids)
                            for index, mod in tuple(mods.items())[::-1]:
                                symbols_to_ids.pop(index)

                            for index, mod in tuple(mods.items())[::-1]:
                                symbols_to_ids.insert(insertion_index, mod)
                                print(symbols_to_ids)
                        insertion_index = None
                        mods = {}

                    for current_index in range(len(symbols_to_ids)):
                        id = symbols_to_ids[current_index]
                        symbol = output_symbols[id]
                        print(f"ID: {id}")
                        match (
                            check_if_has_tag(symbol, "modifier"),
                            check_if_has_tag(symbol, "number")
                        ):
                            case (True, False):
                                print("MODIFIER, NOT NUMBER")
                                mods.update({current_index: id})
                                if current_index == len(symbols_to_ids) - 1:
                                    reorder()

                            case (False, True):
                                print("NOT MODIFIER, NUMBER")
                                if len(mods) > 0 and insertion_index is not None:
                                    reorder()

                                if insertion_index is None:
                                    insertion_index = current_index

                                print(f"INSERTION_INDEX: {insertion_index}")

                            case (False, False):
                                reorder()

                    del reorder, id, symbol, mods, insertion_index

                # If input chart numbers structures strictly and output one doesn't,
                #   remove numbers after structures.
                if (
                    input_properties["strict_numbering"]
                    and not output_properties["strict_numbering"]
                ):
                    structure_or_number = False
                    id_index = 0
                    while id_index < len(symbols_to_ids):
                        current_id = symbols_to_ids[id_index]
                        print(f"STRUCTURE OR NUMBER: {structure_or_number}")
                        print(f"CURRENT ID: {current_id}")
                        if (
                            structure_or_number and (
                                check_if_has_tag(output_symbols[current_id], "number")
                                or check_if_has_tag(output_symbols[current_id], "space")
                            )
                        ):
                            print("NUMBER AFTER STRUCTURE, MUST REMOVE")
                            symbols_to_ids.pop(id_index)
                            print(f"IDS: {symbols_to_ids}")
                        elif check_if_has_tag(output_symbols[current_id], "structure"):
                            print("ID IS STRUCTURE")
                            structure_or_number = True
                            id_index += 1
                        else:
                            print("ID ISN'T STRUCTURE OR NUMBER")
                            structure_or_number = False
                            id_index += 1
                    del structure_or_number, current_id, id_index

                # If output chart numbers structures strictly and input one doesn't,
                #   add numbers after structures.
                if (
                    not input_properties["strict_numbering"]
                    and output_properties["strict_numbering"]
                ):
                    current_structure = 0
                    id_index = 0
                    while id_index < len(symbols_to_ids):
                        current_id = symbols_to_ids[id_index]
                        if check_if_has_tag(output_symbols[current_id], "structure"):
                            current_structure += 1
                            # If output system puts numbers before mods, add a space.
                            # This is to separate structure number from modifier number.
                            if not output_properties["order_after_mods"]:
                                symbols_to_ids.insert(id_index + 1, "clarity_space")
                            for digit in str(current_structure)[::-1]:
                                symbols_to_ids.insert(id_index + 1, f"digit_{digit}")
                        id_index += 1
                    del current_structure, id_index, current_id

                # Stores IDs that will be translated to notes.
                ids_to_notes = {}

            #=======================#
            #                       #
            # TRANSLATION TO SYMBOL #
            #                       #
            #=======================#

                print("TRANSLATING IDS TO SYMBOLS")

                # Translate ID to text from output chart and add it to output.
                id_index = 0
                while id_index < len(symbols_to_ids):
                    id = symbols_to_ids[id_index]
                    print(f"ID: {id}")

                    # Turn ID to note if it's invalid.
                    if id in ids_to_notes.keys():
                        print("ID IS IN IDS TO NOTES LIST")
                        note_symbol_id = output_note_symbol
                        translated_notation += output_symbols[note_symbol_id]["text"]
                        notes.append(ids_to_notes[id])
                        symbols_to_ids[id_index] = note_symbol_id
                        id_index += 1
                        continue

                    # Add the text of every ID to the final output.
                    if id in output_symbols:
                        translated_notation += output_symbols[id]["text"]
                        print(f"CURRENT TRANSLATED NOTATION: {translated_notation}")
                        id_index += 1
                    else:
                        # Handle invalid ID.
                        if self.fast:
                            if output_note_symbol:
                                translated_notation += output_symbols[output_note_symbol]["text"]
                                notes.append(input_symbols[id]["notes"][0])
                                symbols_to_ids[id_index] = output_note_symbol
                            else:
                                print("Output chart doesn't have note symbol")
                            id_index += 1
                        else:
                            id = symbols_to_ids[id_index]
                            match self.invalid_id_method(id):
                                case "remove":
                                    id_index += 1 # Skips invalid ID.

                                case "replace":
                                    replacement = self.input_method("Enter the ID to replace it with: ")
                                    if replacement == "":
                                        print("Invalid input.")
                                        continue
                                    else:
                                        symbols_to_ids[id_index] = replacement

                                case "assign":
                                    assignment = self.input_method("Enter the symbol to assign to the ID: ")
                                    if assignment == "":
                                        print("Invalid input.")
                                        continue
                                    else:
                                        output_symbols.update(
                                            {
                                                id: {
                                                    "text": assignment,
                                                    "description": "ID assigned by user."
                                                }
                                            }
                                        )

                                case "note":
                                    print(f"NOTE SYMBOL: {output_note_symbol}")
                                    # If output chart has a way to represent notes,
                                    if output_note_symbol:
                                        # Turn the ID to a note.
                                        if "notes" in input_symbols[id]:
                                            print("ID HAS NOTE")
                                            ids_to_notes.update({id: input_symbols[id]["notes"][0]})
                                        else:
                                            print("ID DOESN'T HAVE NOTE")
                                            note_contents = self.input_method("Input note contents: ")
                                            ids_to_notes.update({id: note_contents})
                                    else:
                                        # Otherwise skip it.
                                        print("Output chart doesn't have note symbol")
                                        id_index += 1
                                        if id_index == len(line):
                                            id_index -= 1
                del id_index

            #=======================#
            #                       #
            #    POST PROCESSING    #
            #                       #
            #=======================#

                print("POST PROCESSING")

                matches_on_current_line = [match for match in matches if match[0] == line_index]
                for match in matches_on_current_line:
                    translated_notation = sub("|".join(regex_patterns.keys()), match[2], translated_notation, count=1)
                    print(translated_notation)
                    matches.pop(0)

                print(f"NOTES: {notes}")
                # Insert note from notes list for every note symbol in line.
                for id in symbols_to_ids:
                    if check_if_is_note(id):
                        translated_notation += f"\n{output_symbols[id]["text"]}{notes[0]}"
                        notes.pop(0)

                if len(notes) > 0:
                    print(f"NOTES SKIPPED DUE TO LACK OF NOTE SYMBOLS IN NOTATION:\n{notes}")

                # Translation end, prepare for next translation.
                translated_notation += "\n"
                start_index, end_index = 0, 1
                symbols_to_ids = []

                print("TRANSLATED LINE, PREPARED FOR NEXT LINE")

            #=======================#
            #                       #
            #    POST-TRANSLATION   #
            #                       #
            #=======================#

            print("LAST LINE TRANSLATED, PROCESSING OUTPUT")

            replaced_notation = sum(replaced_notation.values(), [])
            replaced_notation = [match for index, match in replaced_notation]
            for index in range(len(replaced_notation)):
                translated_notation = sub(
                    "|".join(regex_patterns.keys()),
                    replaced_notation[index],
                    translated_notation,
                    count=1
                )

            print("\n")
            if "text" in output_chart["chart_names"] and "english" in output_chart["chart_names"]:
                return translated_notation.strip()[:-1].replace(", structure", " structure")
            return translated_notation.strip()
        except KeyboardInterrupt:
            exit("\nExiting...")


if __name__ == "__main__":
    try:
        while True:
            stderr.write(header)
            stderr.write("Press Ctrl+C to exit.\n")
            c = Converter()
            all_charts = c.load_charts()
            system1 = input("System 1: ").strip().lower()
            system2 = input("System 2: ").strip().lower()
            chart1 = c.find_chart(system1, all_charts)
            chart2 = c.find_chart(system2, all_charts)

            # c.fast = True

            notation = input("Notation: ")
            print(c.translate(chart1, chart2, notation))
    except KeyboardInterrupt:
        exit("\nExiting...")
