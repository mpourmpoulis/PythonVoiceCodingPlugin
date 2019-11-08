from PythonVoiceCodingPlugin.queries.abstract import *
from PythonVoiceCodingPlugin.queries.argument import SelectArgument
from PythonVoiceCodingPlugin.queries.alternatives import SelectAlternative
from PythonVoiceCodingPlugin.queries.big_roi import SelectBigRoi
from PythonVoiceCodingPlugin.queries.paste_back import PasteBack
from PythonVoiceCodingPlugin.queries.collect_variable import CollectVariable
from PythonVoiceCodingPlugin.queries.collect_parameter import CollectParameter
from PythonVoiceCodingPlugin.queries.collect_module import CollectModule
from PythonVoiceCodingPlugin.queries.collect_function_name import CollectFunctionName
from PythonVoiceCodingPlugin.queries.collect_imported_value import CollectImportedValue
from PythonVoiceCodingPlugin.queries.insert_item import InsertItem




def get_query(query_description):
	index = query_description["command"]
	if index in ["collect_indexable"]:
		index = {
			"variable":"collect_variable",
			"parameter":"collect_parameter",
			"module":"collect_module",
			"import value":"collect_imported_value",
			"function name":"collect_function_name",

		}[query_description["collectable"]]
	h = {
		"argument": SelectArgument,
		"alternative": SelectAlternative,
		"big_roi": SelectBigRoi,
		"paste_back": PasteBack,
		"collect_variable": CollectVariable,
		"collect_parameter":CollectParameter,
		"collect_module":CollectModule,
		"collect_imported_value": CollectImportedValue,
		"collect_function_name": CollectFunctionName,
		"insert_item": InsertItem,
	}
	return h[index]
	




