# Changelog


## [0.1.1]

### Added

- a bunch of preliminary versions for small regions of interest were added in the unofficial features.

- recommendation has been updated to include links to the gitter chanell

- the sublime menu has been edited accordingly as well!



### Fixed

- fixed a nasty bug in the argument queries, which prevented  above/below queries to select parts of calls inside with clauses and for loops( it did not affect counting though)

- fixed a bug regarding empty definition parameter lists, where the initial "def" keyword would be selected. Now the cursor is correct placed between the empty brackets

- documentation fix, the documentation for the same keyword was pointing to the unofficial small regions of interest

### Changed

- the escaping problems faced with quotes and other special characters were lifted( see below for details )

- the repair module now supports correcting cases where the return keyword is followed by invalid code

- changes in the code for the sublime grammar communication on the grammar side, issues with escaping characters and occasionally losing focus have been lifted via RunCommand ( custom solution  0.5.11 )






## [0.0.5 and 0.1.0 are not really change loged properly]

### Added

* upgrades in the  paste back query where it can now support surrounded punctuation.

* the module delete alternatives has been added.

* View information now also exposes they get regions sublime API

* The interface module now has a clear_actions methods to flush the already pushed actions.

### Fixed

* fixed an important bug in the insertion query module. the writing positions were sorted, but on an ascending order which simply broke everything when there are multiple of them. Fix this to sort them in descending order, so the changes that are executed first do not affect the others.

### Changed

* the application module has been adopted, sought after selection queries we do not only store that arraigns corresponding to the main result in the alternative but we also keep the corresponding text.

*  the  paste back query now reads the corresponding text directly from the state instead of getting their location and obtaining from the code as it did in the past

## [0.0.4] - 2019-11-27

### Added

* aenea support has been added by means of the server plug-ins,  available	in the bundles aenea folder. this includes both the PythonVoiceCodingPluginAeneaServer.py  and the corresponding yapsy-plugin file. 

* in the tiebreak module function tiebreak_on_visual has been added, to enable more coherent tie-breaking

* PopUpErrorAction has been added in order to inform the user in  cases where to cannot parse the source code.

* Sublime settings file has been added, from which you can turn on or off, showing the main result when it is not visible as well as the pop-ups with error information.

### Fixed

* fixed the empty brackets bug in the repair modulebugs with ":" addressed, needs more testing and a subsequent bug

* also in the repair module, we can now handle  consecutive space separated name tokens( and some mixing with error tokens) like the ones that can occur after a misrecognition, for instance "x = gibberish words " is now parsable!

* fixed  one error in vertical direction + big_roi queries, which appeared when a region of interest spanned across multiple physical lines and was the selection origin of a query searching for a region of interest of the same kind and was causing an off by one error when going upwards.

* Fixed error in big_roi module , where when trying to select something in global scope with vertical direction big_roi_queries ,not checking definition_node for Nonetype object caused error

* Fixed error in the preliminary function of the big regions of interest, where if the cursor was at the last empty line of the function, selections would be given from the next function!

* Fixed old name of my output panel:)

* Fixed a bug in the argument module where not forwarding/backwarding selections could cause errors  for the above below keywords.

* fixed a bug in the above/below argument command, which occasionally caused of by one  errors. 

* in the info module, fixed a bug in the get_body function where ast.IfExp was missing for some reason

* Yet another forwarding bug in the argument module:(

*  fix a bug in the big region of interest  module which caused off by one error in the above below command, when the original selection was in an empty line.

### Changed

* The Caster bundles have been modified to be usable with aenea! both the 0.5 and 0.6 versions have been tested, with PythonVoiceCodingPlugin running on Ubuntu 16.04.

* collection queries  now have labels(names) and they display them on the output panel.

* a global state was added the application module, enabling insertion from the results of collection queries from other files

* collecting modules now also collects subparts of the import paths. For example if you importfrom x.y.z, all three [x.y.z,x.y,x] paths are collected!

* In the actions module, the SelectionAction now also shows the main result if it is not visible! works both for selection queries and paste back operations! 

* sub indexing moved from big_roi to info  module! 



* furthermore , you can now sub index strings, arithmetical operations and more! Regarding strings, you can now get words of the sentenceseparated by space or by   full stop, but you can also  pick up parts of the snake or camel case words  individual letters , as well as parts of a URL( little more work is needed for the latter)! 

* the abstract_vertical and big_roi modules have been modified so as to offer alternatives when there are multiple logical lines in the same physical line. 

* argument,adjective_strategy,primitives have been mortified in order to standardize the behavior of the grammar when the target logical line response over multiple physical ones. 

* furthermore, the issue with alternatives common from wrong direction and not close to the main result has been resolved when used with  above/ below keyword by means of tiebreak_on_visual function!

* additionally, even in case of ties when tie-breaking on the lowest common ancestor, the visual proximity is now taken into account!

* in the partial module, the function partially_parse has been modified in order to accept one more optional Boolean parameter which when True causes the function to raise the initial syntax error it captured instead of returning None objects. By default the parameter is set to False.

* In the same spirit, the query module has been modified and has a new attribute in order to store the above exception. The application module checks if this attribute HUD stored exception and displays an error through the PopUpErrorAction!

* The interface module has been modified to accept settings in its constructor.

## [0.0.3] - 2019-11-18

important patch

### Fixed

* The third  party folder was not in the Python path, so imports from the dependencies asking for other dependencies failed!

### Added

once again, thanks to thanks to @LexiconCode there are bundles for the upcoming 1.0.0 release of Caster

- python_voice_coding_plugin_caster_v1-0-0

## [0.0.2] - 2019-11-15

Caster 0.6.11 support many thanks to @LexiconCode

### Added

In the grammar section there are now two scripts:

- python_voice_coding_plugin_caster_v0-6-11
- python_voice_coding_plugin_caster_v0-5-11

## [0.0.1] - 2019-11-14

I think these are the most important changes , I hope I didn't forget  any!

### Added

* Improvements in the sub indexing of big  regions of interest , among others the ability to select parts of comparisons and slicing/indexes

### Fixed

Various bug fixes most importantly in the following modules:

* big_roi

* repair: repaired the bug about repairing ".", empty compounds and more

* obtain, fixed the bug where the main result could appear in the alternatives!

* higher, correct error regarding await but not sure yet need to revisit!

