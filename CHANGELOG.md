# Changelog

## [Unreleased]

### Fixed
* fixed the empty brackets bug in the repair module

* fixed  one error in vertical direction + big_roi queries, which appeared when a region of interest spanned across multiple physical lines and was the selection origin of a query searching for a region of interest of the same kind.

### Changed

* a global state was added the application module, enabling insertion from the results of collection queries from other files

* collecting modules now also collects subparts of the import paths. For example if you importfrom x.y.z, all three [x.y.z,x.y,x] paths are collected!

* In the actions module, the SelectionAction now also shows the main result if it is not visible! works both for selection queries and paste back operations! 

* sub indexing moved from big_roi to info  module!

* the abstract_vertical and big_roi modules have been modified so as to offer alternatives when there are multiple logical lines in the same physical line. 

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

