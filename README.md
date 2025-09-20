# General Transcript Converter [GTC]
A python script that translates between RUMBLE VR notations.

> [IMPORTANT!]
> STATUS UPDATE: This is the result of several months of offline work on the project. Thank you for your patience!

## How does this work?
The script splits the lines of the inputs and determines whether a line is notation or a note.
If there are symbols with tokens inside the notation, the notation in the place of the tokens will be translated first.
For every line of notation, it recursively scans all the characters of the line and if it matches a symbol from the input chart, it stores its ID. In the case where characters do not match a valid symbol, either the user will be asked to handle the error, or it will select a default solution, depending on the value of `converter.fast`.
The IDs are then processed according to the properties of the output chart.
The IDs are turned back into notation according to the output chart.
Tokens are then replaced with the notation stored at the beginning.
Tags determine which tokens can replace a symbol, alongside additional logic, such as modifier reordering.

## What tags are there?
- `note_symbol` — Makes the symbol act as a note indicator.
- `token` — Tokens take the place of other symbols inside a symbol. To use said tokens, this tag needs to be used.
- `indicator` — Makes the symbol act as a positional indicator.
- `shiftstone` — Makes the symbol act as a shiftstone.
- `shiftstone_separator` — Makes the symbol act as a separator between shiftstones and notation.
- `modifier` — Makes the symbol act as a modifier.
- `number` — Makes the symbol act as a digit.
- `structure` — Makes the symbol act as a structure.
- `structure_state` — Makes the symbol act as a structure state.
- `space` — Only used for whitespace, which is automatically added to every chart. Not meant to be used for other symbols.

## What tokens are there?
- **#STRUCTURE#** — Symbols with `structure` tag.
- **#MODIFIER#** — Symbols with `modifier` tag.
- **#MIRROR#** — Symbols with `mirror` tag.
- **#NUMBER#** — Symbols with `number` tag.
- **#INDICATORS#** — Symbols with `indicator` tag.
- **#SYMBOL#** — A singular instance of any symbol.
- **#NOTATION#** — Any valid notation.
- **#TEXT#** — Any string of text.
> [WARNING!]
> Using **#NOTATION#** and **#TEXT#** without surrounding it in other characters will lead to everything after its usage to be considered part of the symbol it's used in.

## How to add custom system/modify existing one?
You can copy and/or modify a .json file from `gtc/notation_systems2/`. The script will automatically detect the new system.
*Don't rename any keys. The script works by assigning the same key to different values.*
