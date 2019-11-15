from dragonfly import (Choice, Dictation, Grammar, Repeat, StartApp, Function)

from caster.lib import control
from caster.lib import settings
from caster.lib.actions import Key, Text
from caster.lib.context import AppContext
from caster.lib.dfplus.additions import IntegerRefST
from caster.lib.dfplus.merge import gfilter
from caster.lib.dfplus.merge.mergerule import MergeRule
from caster.lib.dfplus.state.short import R



import os
import subprocess
import json

def create_arguments(command,format,**kwargs):
    p = {x:kwargs[x] for x in kwargs.keys() if x not in ['_node','_rule','_grammar']}
    p["format"] = format  
    p["command"] = command
    return {"arg":p}


def send_sublime(c,data):
    x =  json.dumps(data).replace('"','\\"')
    y = "subl --command \"" + c + "  " + x + "\""
    subprocess.call(y, shell = True)
    # subprocess.call("subl --command \"argument {\\\"arg\\\":[1,\\\"None\\\", \\\"argument\\\", 1]}\"",shell = True)
    subprocess.call("subl", shell = True)

def noob_send(command,format,**kwargs):
    data = create_arguments(command,format,**kwargs)
    send_sublime("python_voice_coding_plugin", data)

def lazy_value(c,f,**kwargs):
    return  R(Function(noob_send, command = c, format = f,**kwargs))


class NoobRule(MergeRule):
    pronunciation = "python voice coding plugin"
    mapping = {
        # alternative rule
        "[smart] alternative <alternative_index>":
            lazy_value("alternative",1),
        "smart <color> [alternative]":
            lazy_value("alternative",2),

        # paste back rule
        "[smart] paste back [<paste_back_index>]":
            lazy_value("paste_back",1),
        "[smart] paste <color> back":
            lazy_value("paste_back",2),

        # argument rule
        "[smart] [<adjective>] argument <argument_index>":
            lazy_value("argument",1),
        "[smart] <vertical_direction> [<ndir>] [<adjective>] argument <argument_index>":
            lazy_value("argument",2),
        "[smart] [<adjective>] <level> [<level_index>]  argument <argument_index>": 
            lazy_value("argument",3),
        "[smart] <level> [<level_index>] <adjective> argument <argument_index>": 
            lazy_value("argument",4),

        # big roi rule
        "smart <big_roi> [<big_roi_sub_index>]":
            lazy_value("big_roi",1),
        "[smart] <adjective> <big_roi> [<big_roi_sub_index>]":
            lazy_value("big_roi",2),
        "[smart] <vertical_abstract_only_direction> [<ndir>] <big_roi> [<big_roi_sub_index>]":
            lazy_value("big_roi",3),
        "[smart] <vertical_abstract_only_direction> [<ndir>] <block> [<adjective>] <big_roi> [<big_roi_sub_index>]":
            lazy_value("big_roi",4),

           
        # insert rule
        "(smart insert|insert item) <item_index>":
            lazy_value("insert_item",1),

        # collect rule
        "[smart] collect <collectable>":
            lazy_value("collect_indexable",1),
        "[smart] variable <collect_index>":
            lazy_value("collect_variable",2),
        "[smart] parameter <collect_index>":
            lazy_value("collect_parameter",2),
        "[smart] module <collect_index>":
            lazy_value("collect_module",2),
        "[smart] imported (value|object) <collect_index>":
            lazy_value("collect_imported_value",2),


 
        # banana example
        # "banana [<adjective>] <big_roi> [<big_roi_sub_index>]":
            # lazy_value("big_roi",4,vertical_abstract_only_direction = "above",
                # ndir = 1,block = "function"),
 
    }
    extras = [  
        IntegerRefST("argument_index", 1, 10),  
        IntegerRefST("alternative_index", 1, 10), 
        IntegerRefST("ndir",1,20),
        IntegerRefST("level_index",1,10),                                                                                                                                                       
        IntegerRefST("big_roi_sub_index",0,10), 
        IntegerRefST("paste_back_index",0,10),
        IntegerRefST("collect_index",1,30),
        IntegerRefST("item_index",1,30) ,                                                                                                                                                     
        Choice("adjective",{
                "first" : "first",
                "second": "second",
                "third": "third",
                "fourth": "fourth",
                "fifth": "fifth",
                "sixth": "sixth",
                "seventh": "seventh",
                "eighth": "eighth",
                "ninth":"ninth",
                "last":"last",
                "second last": "second last",
                "third last": "third last",
                "fourth last": "fourth last",
            }
        ) , 
        Choice("vertical_direction",{
                "up":"up",
                "down":"down",
                "above":"above",
                "below":"below",
            }
        ),
        Choice("vertical_abstract_only_direction",{
                "above":"above",
                "below":"below",
            }
        ),
        Choice("color",{
                "red":1,
                "blue":2, 
                "green":3,
                "yellow":4,
                "orange":5,
            }
        ),
        Choice("level",{
                "inside":"inside",
            }
        ),
        Choice("big_roi",{
                "if condition" : "if condition",
                "else if condition" : "else if condition",
                "while condition" : "while condition",
                "if expression condition" : "if expression condition",
                "if expression body" : "if expression body",
                "if expression":"if expression",
                "comprehension condition" : "comprehension condition",
                "return value" : "return value",
                "pass":"pass",
                "break" : "break",
                "continue" : "continue",
                "assertion message" : "assertion message",
                "assertion condition" : "assertion condition",
                "(assignment right| right)" : "assignment right",
                "(assignment left| left)" : "assignment left",
                "assignment full" : "assignment full",
                "import statement":"import statement",
                #"(import|imported) (value|item|object|element)":"import value",
                #"module" : "module", 
                "(expression statement|expression)" : "expression statement",
                "iterator" : "iterator",
                "iterable" : "iterable",

            }
        ),
        Choice("block",{
                "(function|functions)" :"function",
            }
        ),
        Choice("collectable",{
                "(variable|variables)":"variable",
                "( parameter | parameters)":"parameter",
                "(module|modules)":"module",
                "(import|imported) (value|item|object|element)":"import value",
                "function ( name |names)":"function name",
            }
        ),

   
    ]
    defaults = {
        "adjective":"None",
        "ndir":1,
        "level_index":1,
        "big_roi_sub_index":0,
        "paste_back_index":0,

    }


#---------------------------------------------------------------------------

context = AppContext(executable="sublime_text")
grammar = Grammar("pvcp", context=context)

if settings.SETTINGS["apps"]["sublime"]:
    if settings.SETTINGS["miscellaneous"]["rdp_mode"]:
        control.nexus().merger.add_global_rule(NoobRule())
    else:
        rule = NoobRule(name="python voice coding plugin")
        gfilter.run_on(rule)
        grammar.add_rule(rule)
        grammar.load()
