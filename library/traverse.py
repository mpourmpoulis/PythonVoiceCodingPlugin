import ast 

from PythonVoiceCodingPlugin.third_party.astmonkey import transformers
from PythonVoiceCodingPlugin.third_party.asttokens import asttokens  

from PythonVoiceCodingPlugin.library import build_tree,get_source_region,nearest_node_from_offset,make_flat

def match_node(node,targets = (),exclusions = ()):
    targets  = targets if targets else ast.AST 
    return isinstance(node,targets) and not isinstance(node, exclusions)

def match_parent(node,targets = (),exclusions = ()):
    targets  = targets if targets else ast.AST 
    p = getattr(node,"parent",None)
    return match_node(p,targets,exclusions)


def match_field(node,f,targets,exclusions = ()):
    targets  = targets if targets else ast.AST 
    field_value = getattr(node,f,None)
    return match_node(field_value,targets,exclusions)



################################################################################################

def find_all_nodes(root , targets = (), exclusions = (), visit_all_levels = True, selector = None):
    targets = targets if targets else ast.AST 
    node_wanted = selector if selector else lambda node: match_node(node,targets,exclusions)
    reachable = ast.walk if visit_all_levels else ast.iter_child_nodes
    return sorted([node  for node in reachable(root) if node_wanted(node) and hasattr(node,"first_token")], 
        key=lambda s: (s.first_token.startpos))

def find_information(root, information, flatten = False, visit_all_levels = True):
    reachable = ast.walk if visit_all_levels else ast.iter_child_nodes
    initial_result = [information(node)  for node in reachable(root) if information(node) is not None]
    return make_flat(initial_result) if flatten else initial_result

def find_matching(root, information, visit_all_levels = True):
    reachable = ast.walk if visit_all_levels else ast.iter_child_nodes
    return [node  for node in reachable(root) if information(node)]   
    


def find_all_nodes_guided(root,target_list,exclusions_list):
    pass
     

################################################################################################

def search_upwards(n,targets,exclusions = ()):
    while not match_node(n, targets,exclusions):
        if not hasattr(n,"parent"):
            return None
        else:
            n=n.parent
    return n

def search_upwards_for_parent(n, targets=(), exclusions = ()):
    if not hasattr(n,"parent"):
        return None
    while not match_node(n.parent, targets,exclusions):
        n=n.parent
        if not hasattr(n,"parent"):
            return None        
    return n

def search_upwards_log(n,targets = (),exclusions = (),log_targets = (),log_exclusions=()):
    result = []
    while not match_node(n, targets,exclusions):
        if  match_node(n, log_targets,log_exclusions):
            result.append(n)
        if not hasattr(n,"parent"):
            return n,result
        else:
            n=n.parent
    return n,result


'''
    here follow variety of functions that traverse abstract syntax  upwards looking for specific target
    And extract a field of interest from the target. they all come in pairs so that they can be used
    Regardless of whether we have a node or an offset.
'''
def select_from_up(node, target, attribute, outside_level, index = None):
    destination = search_upwards(node,target)
    for i in range(0,outside_level):
        destination = search_upwards(destination.parent,target)
    if destination:
        if index:
            return getattr(destination, attribute)[index] if attribute else destination
        else:
            return getattr(destination, attribute) if attribute else None
    return None


def select_region_from_node_up(root, atok, node, target, attribute, outside_level, index = None):
    return  get_source_region(select_from_node(root, atok, node, target, attribute, outside_level, index))

