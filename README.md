# PythonVoiceCodingPlugin

[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

PythonVoiceCodingPlugin is a Sublime Text 3 plugin meant to enhance user experience 
when coding python 3 by voice. 

[](doc/example_5.gif)

## Motivation

The project was inspired by [Gustav Wengel's article](https://medium.com/bambuu/state-of-voice-coding-2017-3d2ff41c5015) on the state of voice coding  and my personal experiences
with  [Caster](https://github.com/dictation-toolbox/Caster). Despite the excellent work put behind this trully awesome dragonfly based toolkit, I felt there were cases we could do better:)

In particular, navigation through the code sometimes felt a little bit too mechanistic. Say for instance you want to go to some location or select some text. For the most part ,you are  describing what actions 
need to be taken to get there. What if you could instead describe what you want to select? 


I want to be honest. This is not exactly thr best code ever written. It is far from it:) But still I  think that PythonVoiceCodingPlugin is a tool that :

* will enable you to syntactically navigate your code using higher level commands

* is easy to use. Commands are relatively simple and sound natural 

* is flexible. Due to "overcomplicated" code resulting in ambiguites over ypur simple description, user error or simply because my rules are broken and make no sense, you didnt get the selection you wanted. Fear not! The plugin goes to great lengths to try and make sense of what you might mean with your wording, so there is good chance what you wanted will appear on the color highlighted alternatives:)


* focuses on flexibility and usability. 

* will hopefully somewhat reduce your dependency on the quality of speech recognition and your never ending struggle with unspeakable words.  Additionally  

## Contents
[Documentation](#documentation)

[License](#license)

## About

## Documentation

Documentation is available here [Documentation](doc/README.md)

## Support for voice coding framework



## License

The code is licensed under 2-clause BSD License.

## Dependencies

Many thanks to the contributors and maintainers of the following pypi packages:

* [asttokens](https://github.com/gristlabs/asttokens)

* [astmonkey](https://github.com/mutpy/astmonkey)

For specific versions check the requirements.txt
