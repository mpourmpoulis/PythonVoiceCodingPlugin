from noob.queries.abstract import *
from noob.queries.argument import SelectArgument
from noob.queries.alternatives import SelectAlternative
from noob.queries.big_roi import SelectBigRoi
from noob.queries.paste_back import PasteBack
from noob.queries.collect_variable import CollectVariable
from noob.queries.collect_parameter import CollectParameter
from noob.queries.collect_module import CollectModule
from noob.queries.collect_function_name import CollectFunctionName
from noob.queries.collect_imported_value import CollectImportedValue
from noob.queries.insert_item import InsertItem




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
	




