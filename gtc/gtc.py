# You can find all notation charts in the notation_systems directory next to this script.
# There, you can just copy one of them and modify it to your heart's content.
# Don't rename any keys. The script works by assigning the same key to different values.
# Keys are the first words on each line, for the uninitiated.

# You can add your own keys, although in translation,
#   if it doesn't detect a matching key in the output chart,
#   you will be prompted to handle it.

# For further functionality, either modify this script,
# make a pull request or contact Oxity on Discord (.oxity).

import enum
import os, json, random

script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, "notation_systems")

quit_words = ["exit", "close", "quit"]
# You can quit the program at any time by typing one of these words.

# make a pull request or contact Oxity on Discord (.oxity).

import os, json, random
from typing import Optional

script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, "notation_systems")

quit_words = ["exit", "close", "quit"]
# You can quit the program at any time by typing one of these words.

header = """
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
    
"""


# I think you should be able to use this script as a module
#   and then use these functions in your own scripts. If it doesn't work,
#   ¯\_(ツ)_/¯
def load_charts() -> dict[str]:
    """
    Loads charts from the /notation_systems directory.
    """

    # Load charts from json
    json_list = []
    # List all files in directory
    for file_name in os.listdir(folder_path):
        # Filter only JSON files
        if file_name.endswith('.json'):
            try:
                # Get fullpath
                file_path = os.path.join(folder_path, file_name)
                # Open filepath and manipulate
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Load and read data into the list
                    data = json.load(file)  
                    json_list.append(data)
            except Exception as e:
                # Print our error messsage
                print(f"Error reading {file_name}: {e}")
    # Return the finalized list
    return json_list

def dict_find_key_by_value(system: dict[str], value) -> str:
    """
    Searches for key in a dict. Utility function.
    """
    # > Oops! Forgot that dict_values don't have .index() function. Returned.
    return list(system.keys())[list(system.values()).index(value)]

def find_system_by_name(systems: list[dict[str]], name: str) -> Optional[dict[str]]:
    try:
        for obj in systems:
            # For (Current system) in (Range of systems)
            for element in range(len(obj["name"]) + 1):
                # If (Get name from Dict containing JSON data) = (Name I'm looking for)
                if obj["name"][element-1] == name:
                    return obj
    except:
        return None

def input_valid_system(systems: dict, prompt: str) -> Optional[str]:
    user_input = input(prompt)
    # Quit if in quit words
    if user_input in quit_words:
        return "exit"
    # Find system
    system = find_system_by_name(systems, user_input)
    # Iff system is None (not found), say nothing
    if system == None: print("Invalid system.")
    # > Changed to return None instead of "invalid" due to edge case of there being a notation system named "invalid"
    # Return system
    return system

def find_instances_in_system(system: dict[str], symbol: str) -> list[str]:
    # Initialize variables
    # all_values = []
    all_instances = []
    # For each value in values
    # > Redid this so that it's shorter 
    """
    for value in system.values():
        # Append values
        all_values.append(value)"""
    c = [(type(x).__name__ == dict.__name__) for x in system.values()]
    for instance in [*system.values()]:
        if instance[:len(symbol)] == symbol:
            all_instances.append(instance)
    return all_instances

class INVALID_VALUE_OPTIONS(enum.Enum):
    REMOVE = 1
    CHANGE = 2
    ASSIGN = 3
    INCLUDE = 4
    IGNORE = 5

def handle_invalid_value(symbol) -> str:
    # Prompt for user input.
    user_input = input(f'''
    "{symbol}" is not a valid value in the input system. How would you like to handle it?
    (1) Remove it.
    (2) Change it.
    (3) Assign it. (will replace existing value of the key)
    (4) Include the next # characters and ask again.
    (5) Ignore it.

    > ''')
    # If in quit_words, quit.
    if user_input in quit_words:
        return "exit"
    # Else, match to provided input (self-explanatory)
    match user_input:
        case "1"|"remove":
            return "remove"
        case "2"|"change":
            return "change"
        case "3"|"assign":
            return "assign"
        case "4"|"include":
            return "include"
        case "5"|"ignore":
            return "ignore"
        case _:
            print("\nInvalid option.\n")

def handle_doubled(symbol, keys):
    
    options = ""
    for key in keys:
        options += f"({keys.index(key) + 1}) {key}\n    "
    # Prompt for user input.
    user_input = input(f'''
    "{symbol}" belongs to multiple keys.
    Which one would you like to insert?
    (0) None (will handle "{symbol}" as an invalid value)
    {options}
    > ''')
    # If in quit_words, quit.
    if user_input in quit_words:
        return "exit"
    # Match to options. Dynamic insertion means we need to use "raise" to quit.
    try:
        match user_input:
            case "0":
                return "ignore"
            case _:
                # > Added "raise" clause to trigger invalid option to appear.
                if keys[abs(int(user_input)) - 1] == None: raise Exception.add_note("Self-raised")
                return keys[abs(int(user_input)) - 1]
    except:
        print("\nInvalid option.\n")
        return "invalid"

def handle_invalid_key(key):
    # Prompt for user input.
    user_input = input(f'''
    "{key}" doesn't have a value in the output system. How would you like to handle it?
    (1) Remove it.
    (2) Change it.
    (3) Assign a value to it.
    (4) Turn it into a note.
    
    > ''')
    
    # Quit if in quit words.
    if user_input in quit_words:
        return "exit"
    # Otherwise, match to user input (self explanatory)
    match user_input:
        case "1"|"remove":
            return "remove"
        case "2"|"change":
            return "change"
        case "3"|"assign":
            return "assign"
        case "4"|"note":
            return "note"
        case _:
            print("\nInvalid option.\n")
            return "invalid"

# Renamed to flatten_system from process_system for less ambiguous code.

def flatten_system(system: dict[str, dict[str]|bool]) -> dict[str, str]:
    # Initiate variables
    processed_system = {}
    # Get processed systems
    for obj in list(system.values()):
        # Sort for dict objects
        if type(obj) == dict:
            # Get keys from dict, form compound key, and add compound key directly to processed_system
            # > Apparently I'm an idiot and don't know how list comprehensions work, returned longer form code
            for child_key in list(obj.keys()):
                # Get compound key from system
                parent_key = dict_find_key_by_value(system, obj)
                processed_key = f"{parent_key}/{child_key}"
                # Add these compound keys to the system
                processed_system.update({processed_key: obj[child_key]})
    # Return finalized system
    return processed_system

def yoink_bools(system:dict[str]) -> dict[str, bool]:
    # > Replaced system_bools with a dict for consistency's sake. Having a list of dicts is insane IMO.
    system_bools = {}
    # Sort for boolean values
    # > Replaced name of iterant "bools" with "key" as not all iterants were, in fact, bools - that's the point of this function
    for key in list(system.keys()):
        # Iff the key is boolean, append it to the system_bools list.
        if type(system[key]) == bool:
            system_bools.update({key: system[key]})
    return system_bools


# I fear no commented function. But that thing? It scares me. - BlueEyedFox_
def translate(user_input:str, from_system, to_system):

    start_index = 0
    end_index = 1
    # Local function defined to increment indices
    def increment_indices():
        """
        Increment our indices.

        This advances the character window.
        """
        nonlocal start_index, end_index
        start_index += 1
        end_index += 1
    # Local function defined to reset start/end indices relative to end
    # - Interesting. I would reset it to start for a utility function, but I'll see where it's used and figure it out from there. 
    def reset_index_distance():
        """
        Resets distance to end.
        
        Whenever you see this, it just means that we're advancing our output token.
        """
        nonlocal start_index, end_index
        start_index = end_index - 1
    # Define processed user input.
    processed_user_input = user_input
    def filter_system_for_shiftstones(system: dict):
        """
        Filter out tokens before and after shiftstones. Essentially, we remove everything up to the shiftstone token.
        """

        # Make a copy of input system
        filtered_system = system.copy()
        # Iterate through each key
        for key in system.keys():
            # If this system uses shiftstoning and the first key doesn't start with shiftstones, or if it uses shiftsoning and doesn't, remove the first item.
            # > Flattened to equivalent logical statement.
            if (shiftstoning and key[:len("shiftstones/")] != "shiftstones/") or key[:len("shiftstones/")] == "shiftstones/":
                    filtered_system.pop(key)
        # Return the processed system.
        return filtered_system
    # Flatten systems.
    flattened_from_system = flatten_system(from_system)
    flattened_to_system = flatten_system(to_system)
    # If the key with identity "shiftstones/delimiter" is present in the string to translate, shiftstoning is true
    # > Flattened to an equivalent single identifier.
    shiftstoning = flattened_from_system["shiftstones/delimiter"] in processed_user_input
    
    # Instansiate tokenized and detokenized lists
    input_translated_to_keys = []
    keys_translated_to_notation = []
    
    # Instansiate exit signal boolean
    exit_signal = False

    # Instansiate previous number of instances variable
    previous_number_of_instances = 0
    
    # While we haven't processed the whole string
    while start_index < len(processed_user_input) and end_index < len(processed_user_input) + 1:
        # Get current symbol
        symbol = processed_user_input[start_index:end_index]
        
        # Filter the system for shiftstones
        filtered_from_system = filter_system_for_shiftstones(flattened_from_system)
        
        # Iff the symbol is now the delimiter, we no longer need to filter.
        # > Flattened to equivalent logical statement.
        shiftstoning = (symbol == flattened_from_system["shiftstones/delimiter"])
        
        # Begin matching symbol cases and define possible tokens.
        match len(symbol_instances := find_instances_in_system(filtered_from_system, symbol)):
        
            # If there are no possible tokens
            case 0:
        
                # If there were previously more than one possible token
                if previous_number_of_instances > 1:
                    # Move back one
                    end_index -= 1
                    
                    # Set symbol to token
                    symbol = processed_user_input[start_index:end_index]

                    # Handle doubled symbol
                    chosen_option = handle_doubled(symbol, [key for key, val in filtered_from_system.items() if val[:len(symbol)] == symbol])
                    match chosen_option:
                        # If exit, exit
                        case "exit":
                            exit_signal = True
                            break

                        # If invalid, skip and move on
                        case "invalid":
                            continue

                        # If ignore, set previous_number_of_instances to 0 to continue.
                        case "ignore":
                            previous_number_of_instances = 0
                            pass
                        
                        # Otherwise, add input (raw) to the list of tokens
                        case _:
                            input_translated_to_keys.append(chosen_option)
                            # Shrink index distance to one and increment indices.
                            reset_index_distance()
                            increment_indices()
                            # Move on
                            previous_number_of_instances = 0
                            continue
                
                # Otherwise, handle the invalid value
                match handle_invalid_value(symbol):
                    case "remove":
                        # Prompt for input
                        remove_all_instances_choice = input("All instances? [N/y] > ")

                        # > Strings are truthy, false only if completely empty. Shortened and clarified.
                        # If user says yes
                        if not remove_all_instances_choice or remove_all_instances_choice.lower()[0] != "y":
                            # Remove only this instance
                            processed_user_input = processed_user_input.replace(symbol, "", 1)
                        else:
                            # Otherwise, remove all instances
                            processed_user_input = processed_user_input.replace(symbol, "")

                        # Reset index to start
                        end_index = start_index + 1
                        continue
                    case "change":
                        # Get symbol to replace with
                        replacement_symbol = input(f"Replace {symbol} with: ")
                        
                        # Ask if all instances should be replaced
                        change_all_instances_choice = input("All instances? [N/y] > ")
                        if len(change_all_instances_choice) == 0 or change_all_instances_choice.lower()[0] != "y":
                            # > Pretty sure you meant processed_user_input since change_user_input is never used, changed
                            processed_user_input = processed_user_input.replace(symbol, replacement_symbol, 1)
                        else:
                            processed_user_input = processed_user_input.replace(symbol, replacement_symbol)
                        # * Possible shorter version, less easy to understand
                        # * processed_user_input= processed_user_input.replace(symbol, replacement_symbol, -1 if len(change_all_instances_choice) == 0 or change_all_instances_choice.lower()[0] != "y" else 1)

                        # Reset to start index to reprocess
                        end_index = start_index + 1
                        continue
                    case "assign":
                        # Get all parent keys (categories)
                        all_parent_keys = [key for key, value in from_system.items() if type(value) == dict]

                        # Get assigned parent/child key from user input
                        assigned_parent_key = input(f"Insert the category of {symbol}" + ", ".join(all_parent_keys) + "(or custom category): ")
                        assigned_child_key = input(f"Insert a key for {symbol}: ")

                        # Generated full key
                        assigned_full_key = f"{assigned_parent_key}/{assigned_child_key}"

                        # Add key
                        filtered_from_system.update({assigned_full_key: symbol})

                        # Add to tokenized input
                        input_translated_to_keys.append(assigned_full_key)
                        reset_index_distance()
                        increment_indices()
                        continue
                    case "include":
                        try:
                            # Get number of insertion characters
                            # > Added loop here so that typos can be corrected
                            while(True):
                                characters_to_insert = int(input("Number of charaters to insert: "))

                                # Assert that insertion characters don't run past string
                                if characters_to_insert > len(processed_user_input[end_index:]):
                                    if(input(f"Warning, characters would override string, limited to less than {characters_to_insert} characters. Retry? [Y/n] ").lower() == "n" or "no"):
                                        characters_to_insert = len(processed_user_input[end_index:])
                                        break
                                    else:
                                        continue
                                
                                # Assert that number of characters is more than the length of the symbol
                                if characters_to_insert <= -len(symbol):
                                    if(input(f"Warning, characters less than current limit, limited to more than {characters_to_insert} characters. Retry? [Y/n] ").lower() == "n" or "no"):
                                        characters_to_insert = -len(symbol) + 1
                                        break
                                    else:
                                        continue
                                if(input(f"Input number of {characters_to_insert} characters means that {symbol[start_index:end_index+characters_to_insert]} will be included. Are you sure? [Y/n]" == "n" or "no")):
                                    continue
                                else:
                                    break

                            # Move end_index by characters_to_insert
                            end_index += characters_to_insert
                            continue
                        except:
                            print(f"Invalid number.")
                            continue
                    case "ignore":
                        # Get a randomized key made of invisible variation selectors
                        # > Changed this to Unicode variation selectors to avoid edge cases. Apologies to any computerized notations that use these.
                        randomized_key = "".join(random.sample("\uFE00\uFE01\uFE02\uFE03\uFE04\uFE05\uFE06\uFE07\uFE08\uFE09\uFE0A\uFE0B\uFE0C\uFE0D\uFE0E\uFE0F", k=16))
                        
                        # Update with new randomized key
                        filtered_from_system.update({randomized_key: symbol})

                        # Update with new randomized key
                        flattened_to_system.update({randomized_key: symbol})
                        continue
                    case "exit":
                        exit_signal = True
                        break
            case 1:
                
                # If symbol isn't in symbol_instances
                if symbol != symbol_instances[0]:

                    # If (we aren't at end) (increment end_index) else (reset previous_number_of_instances)
                    if end_index != len(input_notation):
                        end_index += 1
                        continue
                    else:
                        previous_number_of_instances = 0
                        continue
                
                # Append token to list of tokens
                input_translated_to_keys.append(dict_find_key_by_value(filtered_from_system, symbol))

                # Set previous number of instances to 1
                previous_number_of_instances = 1

                # Move on to next character
                reset_index_distance()
                increment_indices()
                continue
            case _:
                # If there is more than one possible token
                if end_index == len(processed_user_input):

                    # Prompt for user input
                    chosen_option = handle_doubled(symbol, [key for key, val in filtered_from_system.items() if val == symbol])
                    
                    # Match to the chosen option
                    match chosen_option:
                        case "exit":
                            exit_signal = True
                            break
                        
                        # Ignore symbol (don't translate)
                        case "ignore":
                            previous_number_of_instances = 0
                            continue

                        # Else, set to chosen option
                        case _:
                            input_translated_to_keys.append(chosen_option)
                            reset_index_distance()
                            increment_indices()
                            continue
                # Set previous_number_of_instances to (number of possible tokens)
                previous_number_of_instances = len(symbol_instances)

                # Increment indexes
                end_index += 1

                # Continue
                continue
        if exit_signal:
            # If exit was provided, break
            break
    if exit_signal:
        # If exit was provided, stop function
        # > Changed from return "" to return None because "" could be interpreted as a valid translated string
        return None
    # ============================== #
    #                                #
    #   BEGIN TRANSLATION TO SYSTEM  #
    #                                #
    # ============================== #
    # Set translation_index to zero
    translation_index = 0

    # Initialize previous_was_invalid
    previous_was_invalid = False

    # While we haven't used all tokens
    while translation_index < len(input_translated_to_keys):

        # If the previous input was valid
        if not previous_was_invalid:

            # Token is current working key
            # > Changed varible name from key to working_token to clarify usage
            working_token = input_translated_to_keys[translation_index]
        try:
            # Append the equivalent token to the notation string
            keys_translated_to_notation.append(flattened_to_system[working_token])
            translation_index += 1
            previous_was_invalid = False
        except:
            print(f"Here is the currently translated portion of the notation:\n {''.join(keys_translated_to_notation)}")

            # Prompt for handling invalid key
            match handle_invalid_key(working_token):
                case "remove":
                    # Ask if should remove all instances
                    change_all_instances_choice = input("All instances? [n/Y] > ")

                    # If should remove all instances
                    if not change_all_instances_choice or change_all_instances_choice.lower()[0] != "n":
                        
                        # Iterate over all tokens
                        for instance in input_translated_to_keys:

                            # If (token is correct token for removal), remove token
                            if instance == working_token:
                                input_translated_to_keys.remove(instance)
                    else:
                        translation_index += 1
                case "change":
                    # Signal that previous token was invalid
                    previous_was_invalid = True

                    # Prompt for new key
                    changed_key = input(f"Change {working_token} to: ")

                    # Ask if should replace all instances of this token
                    change_all_instances_choice = input("All instances? [n/Y] > ")
                    if len(change_all_instances_choice) == 0 or change_all_instances_choice.lower()[0] != "n":
                        # Look for identical tokens and change
                        input_translated_to_keys = [changed_key if x == working_token else x for x in input_translated_to_keys]

                        #Signal resolved
                        previous_was_invalid = False
                        continue
                    else:
                        working_token = changed_key
                case "assign":
                    # Assign to a new translated token
                    flattened_to_system.update({working_token: f"{input(f'Assign a value to {working_token}: ')}"})
                case "note":
                    # Prompt user to ask if we should change all instances to notes
                    change_all_instances_choice = input("All instances? [n/Y] > ")
                    if len(change_all_instances_choice) == 0 or change_all_instances_choice.lower()[0] != "n":
                        # Look for identical tokens and change them
                        input_translated_to_keys = ["cadenceAndClarity/note" if x == working_token else x for x in input_translated_to_keys]
                    else:
                        # Set previous_was_invalid to True
                        previous_was_invalid = True
                        # Set the token to be a note
                        working_token = "cadenceAndClarity/note"
                case "exit":
                    # If exit, then break out of loop
                    exit_signal = True
                    break
            continue
        # If exit, then end
    if exit_signal:
        # > Changed to return None because "" could be interpreted as a valid translation string
        return None
    
    # Join all translated tokens
    translated_notation = "".join(keys_translated_to_notation)
    
    # Trim off whitespace
    if to_system["name"][0] == "text":
        if input_translated_to_keys[-1][:len("modifiers/")] != "modifiers/" and input_translated_to_keys[-1][:len("states/")] != "states/" and input_translated_to_keys[-1] != "cadenceAndClarity/note":
            translated_notation = translated_notation[:-2]
    
    # Add notes
    number_of_notes = 0
    for note_symbol in keys_translated_to_notation:
        if note_symbol == flattened_to_system["cadenceAndClarity/note"]:
            number_of_notes += 1
            translated_notation += f"\n{note_symbol}{input(f'Note {number_of_notes}: ')}"
    
    # Return fully translated notation
    return translated_notation

if __name__ == "__main__":
    all_systems = load_charts()
    print(header)
    print([a["name"] for a in all_systems])
    while True:
        try:
            input_system = input_valid_system(all_systems, "From: ")
            match input_system:
                case "exit":
                    break
                case None:
                    continue
            print("Got input system")

            output_system = input_valid_system([system for system in all_systems if system != input_system], "To: ")
            match output_system:
                case "exit":
                    break
                case None:
                    continue
            print("Got output system")

            input_notation = input(f"From {input_system['name'][0]} to {output_system['name'][0]}: ")
            print("Got input notation")
            if input_notation in quit_words:
                break
            print(f"\n{translate(input_notation, input_system, output_system)}\n")
        except Exception as e:
            print(f"ERROR: {e.with_traceback()}")
            break
