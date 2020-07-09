## Installation 

As this is a two-part system, in order to install, you must

- install the main plugin

- install the corresponding [grammar](../bundles/README.md) for the version of caster you are using

- put the `subl` executable which enables the communication of those two into the Windows path(from 0.1.2 and above optionally) 


### Install the main plugin

There are currently two installation (Package Control and git) methods for performing the first task,I highly recommend using Package Control.


#### Package Control

- Firstly make sure you have Package Control installed. If not, please follow the instructions [here](https://packagecontrol.io/installation)

- open Command Palette(Control+Shift+P)

- execute

```
Package Control:Install Package
```

And then simply

```
PythonVoiceCodingPlugin
```



##### Note for those who installed between 0.0.4 and 0.0.5 

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



#### Git Install

Alternatively you can download the plugin directly from github and place it in sublime package folder

for windows users this should be:

```
C:\Users\Admin\AppData\Roaming\Sublime Text 3\Packages
```

and on Ubuntu it is :
```
~/.config/sublime-text-3/Packages/
```

Currently the Master Branch ships with its dependencies so you're good to go!

Just in case something is wrong and you want to manually install dependencies,using your installation of python (this worked for me with 3.7.4 and 3.5.2) run from inside the plug-in folder (PythonVoiceCodingPlugin):

```bash
python3 -m pip install --target third_party -r requirements.txt
```


### Install Grammar 

Furthermore, in order to use the plug-in, you must also install the grammar! You can find additional information [here](../bundles/Caster/README.md) if you intend to use this on Linux via [Aenea](../bundles/Aenea/README.md) you will need a few extra steps but in a nutshell:

- Make sure you have [Caster](https://caster.readthedocs.io/en/latest/) installed

- Copy the grammar files to the appropriate user directory,depending on the version of caster these should be either `C:\Users\%USERNAME%\AppData\Local\caster\rules` or `C:\Users\%USERNAME%\.caster\rules
`

- Reboot/launch Caster  and if you are using 1.0 and above do not forget to enable the rule by saying `enable python voice coding plugin`

in order to make this process easier, under `Preferences > Package Settings  > PythonVoiceCodingPlugin
` you will find utilities

- To retrieve those grammar files and then manually copy paste them

![](doc/gif/install1.gif)

- or to automatically install them to the appropriate directory if you are using Caster 1.x.x

![](doc/gif/install2.gif)

### Subl Path

The communication between the main plugin and the grammar happens via the sublime command line interface through the `subl` executable. Up to and including version 0.1.1, it was expected that this executable is in your Windows path but as pointed out by LexiconCode the corresponding documentation was missing! these was a big blunder on my part and may have prevented you from using the project altogether! 

now you can find more information about how you can add this executable to the Windows path [here](https://stackoverflow.com/questions/9440639/sublime-text-from-command-line), but in order to work around this issue without adding an additional installation step for you, release 0.1.2 implements the following scheme:

* If `subl` is already in the path, it will use normally

* Otherwise, it will try to fall back to `C:\Program Files\Sublime Text 3\subl` which is where it should be if you have installed sublime in the classical way! In such a case, no extra steps are needed on your part!

if sublime is installed in another directory, you must unfortunately add it to the path yourself!

Please note that this does not affect Linux!


