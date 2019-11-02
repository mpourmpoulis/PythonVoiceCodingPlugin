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


I want to be honest. This is not exactly the best code ever written. It is far from it:) And it is far from the full functionality i would want it to offer. Nonetheless, I still think that PythonVoiceCodingPlugin is a tool that :

* will give you a first taste of AST navigation of your code using abstractions such as :
"smart if condition" or "below argument one"

* is easy to use and learn. Commands for the most part maintain a relatively clear structural pattern and sound pretty natural. 

* takes a first , though  addmittedly small, step towards reducing your dependency on the quality of speech recognition and your struggle with unspeakable words. 

* is designed on the realization that flexibility is key. I really want a lot of functionality available to you without the need to master the tool. To that end:

    - the tool will go to great lengths to try and decode what you meant from incomplete or insufficient or ambiguous descriptions and suggest meaningful , color highlighted alternatives:) 

   - even if you fail to get what you wanted as the main result , certain operations such as paste back can work with those alternatives instead, minimizing command overhead:)
   
   - as a side effect there are often more than one ways to select the same region so you can use whichever you think first:)


  
* is partly customizable. If you find yourself using certain commands with some given parameters often and want a shorthand smaller command, you can always follow my commented banana example:)



## Release and Version 

Currently in preparation of the initial 0.0.0 release , probably between 5-10/11 :)
 



## Limitations

There are of course certain limitations: 

* Currently I do not fully support python > 3.3 (Still, you can work on code that contains some new features such as async and await keywords, f-strings). That's because Sublime uses python 3.3.6 and I rely on the standard library´s ast module to parse the code. An alternative could have been astroid but it itself uses typed_ast, which contains C code, something which I wanted to avoid. The plugin will most likely eventually change to a client server architecture and simply use an up to date ast module from python 3.7 or the new 3.8.

[](gif/l1.gif)

* Furthermore, to be usable in practice it needs to be able to handle incomplete code(code where stuff is missing and thus cannot be parsed). It does so by "repairing" various common cases. Unfortunately it cannot handle everything you throw at it and in such cases most commands cannot run. Nonetheless, it can manage code like the one below:

[](gif/l2.gif)

## Installation 

Currently you can download the plugin directly from github and place it in sublime package folder

To install dependencies, run from inside the folder:
```bash
python3 -m pip install --target third_party -r requirements.txt
```

Be sure to check instructions to install the [bundles as well](bundles/README.md)


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


Probably by far the most convenient way is via sublime comand line interface. This is the default method used. For example after a command of the form 

```python
"[smart] [<adjective>] argument <argument_index>"
```
like

```
"first argument 2"
```

The script invokes the subl cli tool with a command like that:

``` bash
subl --command python_voice_coding_plugin { "arg" : {
	"command":"argument",
	"format":1,
	"adjective":"first",
	"argument_index":2,
	}
}
```
So effectively we trigger the command our plugin provides in its top file and pass information about the type of query we want and the parameters we used as a dict encoded as a json string. 

Of course this does not work across virtual machine barriers:) 



For the time being I have bundles for 0.5.11 release of Caster that work as expected on Windows 10 64bit.



## License

All code is licensed under 2-clause BSD License.

## Dependencies

Many thanks to the contributors and maintainers of the following pypi packages:

* [asttokens](https://github.com/gristlabs/asttokens)

* [astmonkey](https://github.com/mutpy/astmonkey)

* [segment_tree](https://github.com/evgeth/segment_tree)

For specific versions be sure to check the requirements.txt

## Acknowledgements

### Resources

The following resources proved very helpfull for the success of the project. Many thanks to all the authors!

* [Green Tree Snakes](https://greentreesnakes.readthedocs.io/en/latest/nodes.html) an truly invaluable for this project tutorial of the python ast

* this [tutorial for python tokens](https://www.asmeurer.com/brown-water-python/tokens.html)

* [sublime 3 api documentation]( https://www.sublimetext.com/docs/3/api_reference.html#sublime.View )

* [sublime 3 unofficial documentation]( http://docs.sublimetext.info/en/latest/index.html  )

* the python [grammar]() specification