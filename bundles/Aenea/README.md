# aenea support

In order to use the custom RPC you need to copy both the py script and the yapsy-plugin inside aenea plug-ins folder.

This should be inside aenea/server/linux_x11/plugins if you are on a Linux machine.

```console
foo@bar:~/aenea/server/linux_x11/plugins$ ls
example.py   example.yapsy-plugin                   PythonVoiceCodingPluginAeneaServer.pyc
example.pyc  PythonVoiceCodingPluginAeneaServer.py  PythonVoiceCodingPluginAeneaServer.yapsy-plugin
```

When you  boot the server, you should see something like:

```console
foo@bar:~/aenea/server/linux_x11$ python server_x11.py 
2019-12-01 02:55:23,914 [DEBUG ] [aenea] Loading plugin "Example plugin"
<yapsy.PluginInfo.PluginInfo object at 0x7fd4d6de3350>
2019-12-01 02:55:23,914 [DEBUG ] [aenea] Loading plugin "PythonVoiceCodingPluginAeneaServer plugin"
<yapsy.PluginInfo.PluginInfo object at 0x7fd4d46b83d0>
2019-12-01 02:55:23,914 [DEBUG ] [aenea] using XdotoolPlatformRpcs for input emulation
2019-12-01 02:55:23,914 [DEBUG ] [aenea] starting server on 10.0.2.15:8240
```

The system has been tested on Ubuntu 16.04. If you face any problems, please let me know in the issues with the aenea label!
