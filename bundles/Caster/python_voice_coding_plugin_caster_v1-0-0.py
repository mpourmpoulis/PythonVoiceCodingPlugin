from dragonfly import (MappingRule, Choice, Dictation, Grammar, Repeat, StartApp, Function,RunCommand,FocusWindow)

from castervoice.lib import control
from castervoice.lib import settings
from castervoice.lib.actions import Key, Text
from castervoice.lib.context import AppContext
from castervoice.lib.merge.additions import IntegerRefST
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails


######################################################################################### 

import json
import os
import platform
import subprocess

#########################################################################################

local_settings = {
    "show_command":False,
    "force_rpc":False,
}

######################################################################################### 

if settings.SETTINGS["miscellaneous"]["use_aenea"] or local_settings["force_rpc"]:
    try:
        import aenea
        from jsonrpclib import ProtocolError
        using_rpc = True
    except:
        using_rpc = False
else:
    using_rpc = False 

######################################################################################### 

GRAMMAR_VERSION = (0,1,2)

######################################################################################### 

def create_arguments(command,format,**kwargs):
    p = {x:kwargs[x] for x in kwargs.keys() if x not in ['_node','_rule','_grammar']}
    p["format"] = format  
    p["command"] = command
    p["grammar_version"] = GRAMMAR_VERSION
    return {"arg":p}



def validate_subl():
    if platform.system() != 'Windows':
        return "subl"
    try:
        subprocess.check_call(["subl", "-h"],stdout=subprocess.PIPE,stderr=subprocess.PIPE) # For testing purposes you can invalidate to trigger failure
        return "subl"
    except Exception as e:
        try : 
            subprocess.check_call(["C:\\Program Files\\Sublime Text 3\\subl", "-h"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            print("Resorting to C:\\Program Files\\Sublime Text 3\\subl.exe")
            return  "C:\\Program Files\\Sublime Text 3\\subl"
        except :
            print("Sublime Text 3 `subl` executable was not in the Windows path")
            if not os.path.isdir(r'C:\\Program Files\\Sublime Text 3'):
                print("And there is no C:\\Program Files\\Sublime Text 3 directory to fall back to!")
            else:
                print("And it was not found under C:\\Program Files\\Sublime Text 3")
            print("Please add `subl` to the path manually")
            return "subl"

subl = validate_subl()


def send_sublime(c,data):
    if local_settings["show_command"]:
        print(c + " " + json.dumps(data))
    RunCommand([subl,"-b", "--command",c + " " + json.dumps(data)],synchronous = True).execute()


def noob_send(command,format,**kwargs):
    data = create_arguments(command,format,**kwargs)
    if not using_rpc:
        send_sublime("python_voice_coding_plugin", data)
    else:
        aenea.communications.server.python_voice_coding_plugin_aenea_send_sublime(c="python_voice_coding_plugin",data=data)

def lazy_value(c,f,**kwargs):
    return  R(Function(noob_send, command = c, format = f,**kwargs))

######################################################################################### 

names={
    "colors":{
                "main":0,
                "red":1,
                "blue":2, 
                "green":3,
                "yellow":4,
                "orange":5,
    },
    "nth_ordinal_adjective":{
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
    },
    "vertical_direction":{
        "(up|sauce|above)":"upwards",
        "(down|dunce|below)":"downwards",
    }

}

ARGUMENT_LIKE_INFORMATION = "(argument <argument_index>|keyword <keyword_index>|keyword value <keyword_value_index>|entire keyword <entire_keyword_index>|<caller> [<sub_index>]|entire call)"


######################################################################################### 

class PythonVoiceCodingPluginRule(MappingRule):
    mapping = {
        "[smart] paste [<color>] back [with <surrounding_punctuation>]":
            lazy_value("paste_back",1),
        "[smart] paste <color> on <color2> [<color3> [ [and] <color4>]]":
            lazy_value("paste_back",2), 

        # alternative rule
        "smart alternative <alternative_index>":
            lazy_value("alternative",1),
        "smart <color>":
            lazy_value("alternative",2),
        "smart <color> [<color2> [<color3> [[and] <color4>]]]":
            lazy_value("alternative",3),

        "edit <color> [<color2> [<color3> [[and] <color4>]]]":
            lazy_value("alternative",3,operation = "edit"),

        # delete
        "[smart] delete <color> [<color2> [<color3> [[and] <color4>]]]":
            lazy_value("delete_alternatives",1),
        
        # swap
        "[smart] swap [<color>] back":
            lazy_value("swap_back",1),
        "[smart] swap <color> with <color2>":
            lazy_value("swap_back",2),

        # utilities
        "[smart] back initial":
            lazy_value("select_back",1),
        "smart back":
            lazy_value("select_back",2),
        "smart here":
            lazy_value("remember_here",1),


        # sub indexing rule
        "[(smart|<operation>)] [<nth>] part <sub_index>":
        # "[(smart|<operation>)] [<nth>] inner [<nth2>] part <sub_index>":
            lazy_value("select_part",1),
        "[(smart|<operation>)] [<nth>] part <sub_index> until (<sub_index2>|the end)":
        # "[(smart|<operation>)] [<nth>] inner [<nth2>] part <sub_index> until (<sub_index2>|the end)":
            lazy_value("select_part",2),
        "[(smart|<operation>)] ([<nth>] any|any <nth2>) part [<sub_index>]":
        # "[(smart|<operation>)] [<nth>] any [<nth2>] part [<sub_index>]":
            lazy_value("select_part",3),
        "[(smart|<operation>)] ([<nth>] every|every <nth2>) part [<sub_index>]":
        # "[(smart|<operation>)] [<nth>] every [<nth2>] part [<sub_index>]":
            lazy_value("select_part",4),


        # argument rule
        "[(smart|<operation>)] [<nth>] " + ARGUMENT_LIKE_INFORMATION:
            lazy_value("argument",1),
        "[(smart|<operation>)] <vertical_direction> [<ndir>] [<nth>] " + ARGUMENT_LIKE_INFORMATION:
            lazy_value("argument",2),
        "[(smart|<operation>)] [<nth>] inside [<level_index>] " + ARGUMENT_LIKE_INFORMATION: 
            lazy_value("argument",3),
        "[(smart|<operation>)] inside [<level_index>] <nth> " + ARGUMENT_LIKE_INFORMATION: 
            lazy_value("argument",4),
        "[(smart|<operation>)] outer [<level_index>] [<nth>] " + ARGUMENT_LIKE_INFORMATION: 
            lazy_value("argument",5),

        # big roi rule
        "(smart|<operation>) <big_roi> [<sub_index>]":
            lazy_value("big_roi",1),
        "[(smart|<operation>)] <nth> <big_roi> [<sub_index>]":
            lazy_value("big_roi",2),
        "[(smart|<operation>)] <vertical_direction> [<ndir>] <big_roi> [<sub_index>]":
            lazy_value("big_roi",3),
        "[smart] <vertical_direction> [<ndir>] <block> [<nth>] <big_roi> [<sub_index>]":
            lazy_value("big_roi",4),

           
        # item rule
        "[smart] item <item_index>":
            lazy_value("insert_item",1),
        "[smart] (item|items)  (all| <item_index> until (<item_index2>| the end))":
            lazy_value("insert_item",2),
        "[smart] (item|items) <item_index>   <item_index2> [  and  <item_index3>]":
            lazy_value("insert_item",3),


        # collect rule
        "[smart] collect <collectable>":
            lazy_value("collect_indexable",1),

        # variable rule
        "[smart] variable <item_index>  [[and] <item_index2> [and <item_index3>]]":
            lazy_value("collect_variable",2),
        "[smart] (variables all|variable <item_index> until (<item_index2>| the end))": 
            lazy_value("collect_variable",3),

        # parameter rule
        "[smart] [<vertical_direction> [<ndir>]] parameter <item_index>  [and <item_index2> [and <item_index3>]]":
            lazy_value("collect_parameter",2),
        "[smart] [<vertical_direction> [<ndir>]] (parameters all| parameter <item_index> until (<item_index2>| the end))":
            lazy_value("collect_parameter",3),
        
        # "[smart] [<vertical_direction> [<ndir>]] key parameter <item_index>  [ and <item_index2> [and <item_index3>]]":
            # lazy_value("collect_parameter",2,experimental = "True"),

        # "[smart] [<vertical_direction> [<ndir>]] key (parameters all| parameter <item_index> until (<item_index2>| the end))":
            # lazy_value("collect_parameter",3,experimental = "True"),
        
    }
    extras = [  
        IntegerRefST("argument_index", 0, 10),  
        IntegerRefST("keyword_index", 1, 10),  
        IntegerRefST("entire_keyword_index", 1, 10), 
        IntegerRefST("keyword_value_index", 1, 10), 
        IntegerRefST("alternative_index", 1, 10), 
        IntegerRefST("ndir",1,20),
        IntegerRefST("level_index",1,10),                                                                                                                                                       
        IntegerRefST("paste_back_index",0,10),
        IntegerRefST("collect_index",1,30),
        IntegerRefST("item_index",1,30),  
        IntegerRefST("item_index2",1,30),                                                                                                                                                     
        IntegerRefST("item_index3",1,30),                                                                                                                                                     
        IntegerRefST("item_index4",1,30),
        IntegerRefST("sub_index",1,10),
        IntegerRefST("sub_index2",1,10),                                                                        
        Choice("nth",names["nth_ordinal_adjective"]),
        Choice("nth2",names["nth_ordinal_adjective"]), 
        Choice("vertical_direction",names["vertical_direction"]),
        Choice("color", names["colors"]),
        Choice("color2", names["colors"]),
        Choice("color3", names["colors"]),
        Choice("color4", names["colors"]),
        Choice("big_roi",{

                "if condition" : "if condition",
                "else if condition" : "else if condition",
                "while condition" : "while condition",
                "with item" : "with clause",

                "exception":"exception",
                "exception name":"exception name",
                "handler":"handler",

                "if expression condition" : "if expression condition",
                "if expression value" : "if expression body",
                "if expression":"if expression",
                "if expression else" : "if expression else",

                "comprehension condition" : "comprehension condition",
                "comprehension value" : "comprehension value",

                "return value" : "return value",
                "pass":"pass",
                "break" : "break",
                "continue" : "continue",

                "assertion message" : "assertion message",
                "assertion condition" : "assertion condition",
                "exception raised" : "exception raised",
                "raised cause": "raised cause",

                "(assignment right| right)" : "assignment right",
                "(assignment left| left)" : "assignment left",
                "assignment [full]" : "assignment full",
                "(expression statement|expression)" : "expression statement",


                "import statement":"import statement",
                "import value" : "import value",
                "module" : "import module",
                
                

                "iterator" : "iterator",
                "iterable" : "iterable",

                "function name": "definition name",
                "function parameter": "definition parameter",
                "parameter list": "definition parameter list",
                "default value": "default value",
                

                "lambda":"lambda",
                "lambda body":"lambda body",

                
                "class name": "class name",
                "decorator":"decorator",
                "base class":"base class",

#                 "same" : "same",


#                 "string" : "string",
#                 "integer literal" : "integer literal",
#                 "dictionary" : "dictionary",
#                 "list" : "list",
#                 "tuple" : "tuple",
#                 "set" : "set",
                

#                 "subscript" : "subscript",
#                 "subscript body" : "subscript body",
#                 "key" : "key",
#                 "lower" : "lower",
#                 "upper" : "upper",
#                 "step" : "step",
                
#                 "attribute" : "attribute",

#                 "comparison" : "comparison",
#                 "arithmetic" : "arithmetic",
#                 "boolean" : "boolean",

#                 "member": "member",
#                 "container": "container",
#                 "membership" : "membership",

#                 "left side" : "left side",
#                 "right side" : "right side",
#                 "middle" : "middle",

#                 "arithmetic left"  : "arithmetic left" ,
#                 "arithmetic right" : "arithmetic right",
#                 "arithmetic middle" : "arithmetic middle",

#                 "boolean left" : "boolean left",
#                 "boolean right" : "boolean right",
#                 "boolean middle" : "boolean middle",

#                 "boolean and"  : "boolean and" ,
#                 "boolean or" : "boolean or",

            }
        ),
        Choice("block",{
                "(function|functions)" :"function",
            }
        ),
        Choice("collectable",{
                "(variable|variables)":"variable",
                "( parameter | parameters)":"parameter",                
                "imported value":"import value",
                "module" : "module",
                "function (name|names)":"function name",
                "class name" : "class name",
                "decorator" : "decorator",
            }
        ),
        Choice("surrounding_punctuation",{
                "quotes":    ("quotes","quotes"),
                "experiment":('"\t/','\n\n\n"&' + r'\s'),
                "thin quotes": ("'","'"),
                "tickris":   ("`","`"),
                "prekris":     ("(",")"),
                "brax":        ("[","]"),
                "curly":       ("{","}"),
                "angle":     ("<",">"),
                "dot":(".","."),
                "underscore": ("_","_"),
                "(comma|,)": (",",","),
                "ace":(" "," "),
                # "truth comprehension":"$$ = [x  for x in $$ if x]",
                # "force list": "$$ if isinstance($$,list) else [$$] ",
                # "truth": "$$ = $$ if $$ else ",
                # "key value":"quotes$$quotes:$$",
            }
        ),
        Choice("operation",{
                "paste": "paste",
                "delete":"delete",
                "swap": "swap",
                "edit": "edit",
            }
        ),
        Choice("caller",{
            "caller": "caller",
            }
        ),
   
    ]
    defaults = {
        "ndir":1,
        "level_index":0,

    }


#---------------------------------------------------------------------------


def get_rule():
    return PythonVoiceCodingPluginRule, RuleDetails(name="python voice coding plugin", executable="sublime_text", title="Sublime Text")

