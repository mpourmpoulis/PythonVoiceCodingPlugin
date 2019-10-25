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


## Documentation

Documentation is available here [Documentation](doc/README.md)

## Support for voice coding framework

### Short version:

For the time being the full system has been tested with Caster 0.5.11 on a Windows 10 machine. I plan better support for aenea in the near future and would love to (if possible) provide bundles for more systems on the long run:) The plugin code itself is intentionally pure python so it should probably run fine on other OS that sublime supports (tp be updated after linux test)

### Long version:

Ok this can get a little bit  complicated because there is a variety of operating systems, speech recognition backends, macro systems and toolkits built upon them which may or may not introduce complications. To give you an example lets see a few cases of how Caster with Dragon Naturally Speaking can be used: 

- everything native in Windows 

- in combination with aenea on linux host with windows guest where dragon is running and keystrokes are send to the host via rpc commands 

- linux guest receiving keystrokes from pure dragonfly windows host 

- oh and what about that linux guest receiving aenea rpc from windows host?:)



To understand why all this may become an issue, we need to take a look at how communication between dragonfly and the plugin works. 


Probably by far the most convenient way is via sublime comand line interface. This is the default method used. The script invokes the subl cli tool with 

Of course this does not work across virtual machine barriers:)

I have limited myself to pure python so odds are it should work on all sublime supported operatings systems. For the time being it has been tested on Windows 10 64 bit.

For the time being I have bundles for 0.5.11 release of Caster that work as expected



## License

The code is licensed under 2-clause BSD License.

## Dependencies

Many thanks to the contributors and maintainers of the following pypi packages:

* [asttokens](https://github.com/gristlabs/asttokens)

* [astmonkey](https://github.com/mutpy/astmonkey)

* [segment_tree](https://github.com/evgeth/segment_tree)

For specific versions be sure to check the requirements.txt

## Acknowledgements

### Resources

The following resources proved very helpfull for the success of the project. Many thanks to anypne involved!

* [Green Tree Snakes](https://greentreesnakes.readthedocs.io/en/latest/nodes.html) an awesome and invaluable for this project tutorial of the python ast

* [tutorial for python tokens](https://www.asmeurer.com/brown-water-python/tokens.html)

* [sublime 3 api documentation]( https://www.sublimetext.com/docs/3/api_reference.html#sublime.View )

* [sublime 3 unofficial documentation]( http://docs.sublimetext.info/en/latest/index.html  )
