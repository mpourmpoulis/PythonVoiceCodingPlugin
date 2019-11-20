from dragonfly import (Choice, Dictation, Grammar, Repeat, StartApp, Function)

from castervoice.lib import control
from castervoice.lib import settings
from castervoice.lib.actions import Key, Text
from castervoice.lib.context import AppContext
from castervoice.lib.dfplus.additions import IntegerRefST
from castervoice.lib.dfplus.merge import gfilter
from castervoice.lib.dfplus.merge.mergerule import MergeRule
from castervoice.lib.dfplus.state.short import R



import os
import subprocess
import json

def create_arguments(command,format,**kwargs):
    p = {x:kwargs[x] for x in kwargs.keys() if x not in ['_node','_rule','_grammar']}
    # this looks a little bit ugly and  it is only temporary as in this way both grammars
    # can work with the same plug-in
    p["level_index"] = p["inside_index"] if p["inside_index"] else ""
    x = p["vertical_direction"] if "vertical_direction" in p else ""
    p["vertical_abstract_only_direction"]  = "above" if x == "up" else "below"
    p["vertical_direction"]  = "above" if x == "up" else "below"
    p["adjective"] = p["nth"] if "nth" in p else ""
    p["ndir"] = p["nsteps"] if "nsteps" in p else ""
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




class SublimeRulePlugin(MergeRule):
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
        "[smart] [<nth>] argument <argument_index>":
            lazy_value("argument",1),
        "[smart] <vertical_direction> [<nsteps>] [<nth>] argument <argument_index>":
            lazy_value("argument",2),
        "[smart] [<nth>] inside [<inside_index>]  argument <argument_index>": 
            lazy_value("argument",3,level = "inside"),
        "[smart] inside [<inside_index>] <nth> argument <argument_index>": 
            lazy_value("argument",4,level = "inside"),

        # big roi rule
        "smart <big_roi> [<big_roi_sub_index>]":
            lazy_value("big_roi",1),
        "[smart] <nth> <big_roi> [<big_roi_sub_index>]":
            lazy_value("big_roi",2),
        "[smart] <vertical_direction> [<nsteps>] <big_roi> [<big_roi_sub_index>]":
            lazy_value("big_roi",3),
        "[smart] <vertical_direction> [<nsteps>] (function|functions) [<nth>] <big_roi> [<big_roi_sub_index>]":
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
        # "banana [<nth>] <big_roi> [<big_roi_sub_index>]":
            # lazy_value("big_roi",4,vertical_direction = "above",
                # nsteps = 1,block = "function"),
 
    }
    extras = [  
        IntegerRefST("argument_index", 1, 10),  
        IntegerRefST("alternative_index", 1, 10), 
        IntegerRefST("nsteps",1,20),
        IntegerRefST("inside_index",1,10),                                                                                                                                                       
        IntegerRefST("big_roi_sub_index",0,10), 
        IntegerRefST("paste_back_index",0,10),
        IntegerRefST("collect_index",1,30),
        IntegerRefST("item_index",1,30) ,                                                                                                                                                     
        Choice("nth",{
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
                "(sauce|up)":"up",
                "(dunce|down)":"down",
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
                "(expression statement|expression)" : "expression statement",
                "iterator" : "iterator",
                "iterable" : "iterable",

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
        "nth":"None",
        "nsteps":1,
        "inside_index":1,
        "big_roi_sub_index":0,
        "paste_back_index":0,

    }


#---------------------------------------------------------------------------

context = AppContext(executable="sublime_text", title="Sublime Text")
control.non_ccr_app_rule(SublimeRulePlugin(), context=context)
