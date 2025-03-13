# General Transcript Converter [GTC]
A python script that translates between RUMBLE VR notations.

## Features
It can translate between:
- [x] **Standard notation** (standard, normal, normnote)
- [x] **Emoji notation** (emoji, emojinote)
- [x] **English** (text, human, english)
- [ ] **Mahjong notation**
- [ ] **Insanity extension**
- [ ] **Unclarinote**
- [ ] **Yiaknote**
- [ ] **Multithread**

It automatically handles shiftstones, regardless of system.
Notes can be added individually. **Don't copy paste the notation with the notes. The script doesn't handle multi-line input** (yet),
Allows you to handle missing keys and values, as well as double values.
Designed to be as easy to extend and modify as possible.
You can use the script as a [module](https://github.com/0xity/GeneralTranscriptConverter/wiki/Using-GTC-as-a-module) in your projects.

### How to add custom system/modify existing one?
You can copy and/or modify a .json file from `gtc/notation_systems/`. The script will automatically detect the new system.
*Don't rename any keys. The script works by assigning the same key to different values.*
Keys are the first words on each line, for the uninitiated.
For further functionality, either modify this script and make a pull request or contact Oxity on Discord (.oxity).

TODO:

- [ ] **Insanity**
- [ ]   *Base System*
- [ ]   *Modifiers*
- [ ]   *Movement*
- [ ]   *Loops*
- [ ]   *Flight*
- [ ] **Multithread**
- [ ]   *Basic Multithread*
- [ ]   *Advanced TRs*
- [ ]   *Exclusions/Shorthand*
- [ ]   *Atomicization*
