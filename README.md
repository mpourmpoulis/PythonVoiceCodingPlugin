# PythonVoiceCodingPlugin

[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

<!-- ![](https://img.shields.io/static/v1?label=Version&message=0.1.0&color=green) -->

[![](https://img.shields.io/badge/documentation-here-green)](https://github.com/dictation-toolbox/Caster)

<!-- ![](https://img.shields.io/static/v1?label=Caster&message=0.5.11|0.6.11|1.0.0&color=blue) -->

[![](https://img.shields.io/badge/Caster-v0_5_11|v0_6_14|v1_0_0-blue)](https://github.com/dictation-toolbox/Caster)

<!-- ![](https://img.shields.io/static/v1?label=Aenea&message=supported&color=red) -->

[![](https://img.shields.io/badge/Aenea-supported-red)](https://github.com/dictation-toolbox/aenea)

<!-- ![](https://img.shields.io/static/v1?label=Platform&message=Windows|Linux&color=yellow) -->

![](https://img.shields.io/badge/Platform-Windows%7CLinux-yellow)


[![](https://img.shields.io/gitter/room/mpourmpoulis/PythonVoiceCodingPlugin.svg)](https://gitter.im/PythonVoiceCodingPlugin/community)

![](https://img.shields.io/github/v/release/mpourmpoulis/PythonVoiceCodingPlugin.svg)

PythonVoiceCodingPlugin is a Sublime Text 3 plugin meant to enhance user experience 
when coding python 3 by voice. It ships with  an integrated [Caster](https://github.com/dictation-toolbox/Caster)  grammar bundle containing voice commands that provide you with syntactical navigation capabilities!

![](doc/gif/big37.gif)


## Contents

<!-- MarkdownTOC  autolink="true" -->

- [Documentation](#documentation)
- [Motivation](#motivation)
- [Release and Version](#release-and-version)
- [Limitations](#limitations)
- [Installation](#installation)
  - [Package Control](#package-control)
    - [note for those who installed between 0.0.4 and 0.0.5](#note-for-those-who-installed-between-004-and-005)
  - [Git Install](#git-install)
- [Support for voice coding framework](#support-for-voice-coding-framework)
- [License](#license)
- [Dependencies](#dependencies)
- [Acknowledgements](#acknowledgements)
  - [Useful Learning Resources](#useful-learning-resources)
  - [Development tools](#development-tools)
  - [People](#people)

<!-- /MarkdownTOC -->





## Documentation

Documentation is available [here](doc/README.md)  you can also find links to documentation under

```
Preferences > Package Settings  > PythonVoiceCodingPlugin
```

![](doc/gif/sub11.gif)

## Motivation

The project was inspired by [Gustav Wengel's article](https://medium.com/bambuu/state-of-voice-coding-2017-3d2ff41c5015) on the state of voice coding  and my personal experiences
with  [Caster](https://github.com/dictation-toolbox/Caster). Despite the excellent work put behind this trully awesome [dragonfly](https://github.com/t4ngo/dragonfly) based toolkit, I felt there were cases we could do slightly better:)

In particular, navigation through the code sometimes felt a little bit too mechanistic. Say for instance you want to go to some location or select some text. For the most part ,you are  describing what actions 
need to be taken to get there. What if you could instead simply describe (syntactically)  what you want to select? 

![](doc/gif/arg17.gif)

PythonVoiceCodingPlugin tries to enable you to do just that!
To provide this functionality, it ships with bundles the implement a grammar, hopefully expressive enough for describing regions of interest, while running on the voice coding macro system side. These bundles
cooperate with the core plugin, running on the editor side, arguably the more suitable of the two environments
for analyzing source code and decoding the meaning of queries within the given context. 

![](doc/gif/op2.gif)


I want to be honest. This is not exactly the best code ever written. It is far from it:) And it is far from the full functionality i would want it to offer. Nonetheless, I still think that PythonVoiceCodingPlugin is a tool that :

* will give you a first taste of AST navigation of your code using abstractions such as :
"smart if condition" or "below argument one"

* is easy to use and learn. Commands for the most part maintain a relatively clear structural pattern and sound pretty natural. 

* takes a first , though  addmittedly small, step towards reducing your dependency on the quality of speech recognition and your struggle with unspeakable words. 

* is designed on the realization that flexibility is key. I really want a lot of functionality available to you without the need to master the tool. To that end:

    - the tool will go to great lengths to try and decode what you meant from incomplete or insufficient or ambiguous descriptions and suggest meaningful , color highlighted alternatives:) 

   - even if you fail to get what you wanted as the main result , certain operations such as paste back can work with those alternatives instead without command overhead:)
   
   - as a side effect there are often more than one ways to select the same region so you can use whichever you think first:)


  
* is partly customizable. If you find yourself using certain commands with some given parameters often and want a shorthand smaller command, you can always follow my commented banana example:)


![](doc/gif/op37.gif)

As I said, far (really far) from perfect but nonetheless an out-of-the-box solution which I hope to be helpful ,especially for beginners to get up to speed , and a step towards the right direction. I hope you enjoy using it as much as I have enjoyed coding it:)

Needless to say, while coding PythonVoiceCodingPlugin , PythonVoiceCodingPlugin was used :)

## Release and Version 

The code is available on [github](https://github.com/mpourmpoulis/PythonVoiceCodingPlugin)

The latest release  is  0.1.0!


## Limitations

There are of course certain limitations which I would like to make clear from the start: 

* Currently I do not fully support python > 3.3 (Still, you can work on code that contains some new features such as async and await keywords, f-strings). That's because Sublime uses python 3.3.6 and I rely on the standard library´s ast module to parse the code. An alternative could have been astroid but it itself uses typed_ast, which contains C code, something which I wanted to avoid. The plugin will most likely eventually change to a client server architecture and simply use an up to date ast module from python 3.7 or the new 3.8. please note that this restriction only concerns the users of new syntactical features. There is no problem , for instance, if you use a new standard library function.


* Furthermore, to be usable in practice it needs to be able to handle incomplete code(code where stuff is missing and thus cannot be parsed). It does so by "repairing" various common cases. Unfortunately it cannot handle everything you throw at it and in such cases most commands cannot run. Nonetheless, it can manage code like the one below:

![](doc/gif/l2.gif)

## Installation 

In order to install, you must install both the plugging as well as the corresponding [grammar](bundles/README.md). 


There are currently two installation methods for performing the first task 


### Package Control

Release 0.0.5 fixed the errors that prevented 0.0.4 from installing directly from package control. You can now install the package simply by 

- open Command Palette

- execute

```
Package Control:Install Package
```

And then simply

```
PythonVoiceCodingPlugin
```



#### note for those who installed between 0.0.4 and 0.0.5 

previously the installation of plug-in included running

```
Package Control:Add Repository
```

and then entering a URL to my repository

```
https://github.com/mpourmpoulis/PythonVoiceCodingPlugin
```


which enabled you to install directly from a master branch rather than my releases and you should be seing a fake version like v2020.01.05.( and so on ) instead of v0.0.4.

This was only temporary solution  and I recommend that you ran 
```
Package Control:Remove Repository
```

so was only install/upgrade from releasees.




For the time being be warned, that the plug-in has not been tested with portable versions of sublime!


For any further installation questions, feel free to ask [here](https://github.com/mpourmpoulis/PythonVoiceCodingPlugin/issues/5)



### Git Install

Currently you can download the plugin directly from github and place it in sublime package folder

for windows users this should be:

```
C:\Users\Admin\AppData\Roaming\Sublime Text 3\Packages
```

and on Ubuntu it is :
```
~/.config/sublime-text-3/Packages/
```

Currently the Master Branch  and the releases  0.0.5 ships with its dependencies so the next step is not really necessary.

To install dependencies,using your installation of python (this worked for me with 3.7.4 and 3.5.2) run from inside the plug-in folder (PythonVoiceCodingPlugin):
```bash
python3 -m pip install --target third_party -r requirements.txt
```






## Support for voice coding framework



they are available grammars for Caster 0.5.11,0.6.11 as well as >=1.0.0  with many thanks to [LexiconCode](https://github.com/LexiconCode)!

It is my highest recommendation if you are using older versions of Caster that you upgrade to the latest one. Sooner or later the plug-in is going to drop support for those older versions and either way the newer version has a lot of improvements!

Regarding operating system support, the plug-in has been tested both on Windows 10 and  on Ubuntu 16.04 as release 0.0.4 introduced support for [aenea](https://github.com/mpourmpoulis/PythonVoiceCodingPlugin/blob/master/bundles/Aenea/README.md)!


Also note that if you are using the latest version of Caster, you must also enable the grammar by saying

```
enable python voice coding plugin
```




## License

All code (grammar bundles and plugin) is licensed under 2-clause BSD License.

```
BSD 2-Clause License

Copyright (c) 2019, Kitsios Panagiotis
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

## Dependencies

Many thanks to the contributors and maintainers of the following pypi packages:

* [asttokens](https://github.com/gristlabs/asttokens)

* [astmonkey](https://github.com/mutpy/astmonkey)

* [segment_tree](https://github.com/evgeth/segment_tree)

For specific versions be sure to check the requirements.txt

For their licensees check out the dedicated [file](https://github.com/mpourmpoulis/PythonVoiceCodingPlugin/blob/master/DEPENDENCES_LICENSE.md)

## Acknowledgements

### Useful Learning Resources

The following resources proved to be very helpfull for the completion of the project. Many thanks to all the authors!

* [Green Tree Snakes](https://greentreesnakes.readthedocs.io/en/latest/nodes.html) an truly invaluable for this project tutorial of the python ast

* this [tutorial for python tokens](https://www.asmeurer.com/brown-water-python/tokens.html)

* sublime 3 [api documentation]( https://www.sublimetext.com/docs/3/api_reference.html#sublime.View )

* sublime 3 [unofficial documentation]( http://docs.sublimetext.info/en/latest/index.html  )

* the python 3.7 [grammar](https://docs.python.org/3.7/reference/grammar.html) specification

* of course [the sublime forum](https://forum.sublimetext.com/)



### Development tools


Many thanks to all of the developers that have put their time and effort behind projects such as

* Natlink

* Dragonfly  and [Dragonfly2](https://github.com/dictation-toolbox/dragonfly)

* Caster


also some of the other tools I found useful developing this project

* TabNine 

* Quoda

* Automatic Package Reloader

* MarkdownTOC 

* ScreenToGif 

* Jedi 


### People

Last but not least many things to

* LexiconCode, for porting the grammar from 0.5 to 0.6 and 1.0 versions of Caster

* FichteFoll, for pointing out various errors during package review



