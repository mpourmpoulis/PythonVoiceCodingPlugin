---
name: Commands Functionality Bug Report
about: Report core functionality bugs like a command not running or yielding wrong
  result
title: ''
labels: bug
assignees: mpourmpoulis

---

## Description

<!-- here you can provide your description of the bug. 

Providing the screenshot or GIF could be helpful if things are complicated. Furthermore,there follows a small questionnaire to help you summarize information about some important aspects you may have noticed about the issue
To complete you can fill the checkboxes with "x" or click them after you submit the issue.
Zero,one or more answers may be applicable for each question!

-->

**General Information**
<!-- which version are you using? for instance v0.1.0, v0.1.2  or develop -->

Plug-In Version: 

**Queries Affected**

<!-- what types of queries are affected (there may be multiple) -->

- [ ] Argument

- [ ] Big Roi

- [ ] Sub Indexing
	- [ ] only dedicated Subindexing commands
	- [ ] also affect suffixes

- [ ] Operations
	- [ ] Paste
	- [ ] Delete
	- [ ] Swap
	- [ ] Edit
	- [ ] Prefix

- [ ] Collections


**Response To Command**

<!-- okay what is actually happening? -->

- [ ] the command fails/nothing happens at all

- [ ] the command select/operates on a wrong result,
	- [ ] that did not match your positional description (e.g. grabs an ROI one line above or below the one you wanted)
	- [ ] did not match the type of result you are looking for(e.g. you wanted an assertion message but you got assertion condition)
	- [ ] or maybe the result was of the correct type and position but it was selected improperly(e.g. you asked for the parameter list of function but the last parameter was not selected)
	- [ ] or maybe things are working fine when trying to select a region as a whole but start breaking when you try access smaller pieces of it
	- [ ] or perhaps the command did find the correct result but perhaps the alternatives included regions they should not or vice versa. (for instance because the command searched the entire code instead of just the current function or vice versa)

- [ ] somehow the whole preserving the current state(alternatives,origin,initial_origin and so on) was messed up by the command! For instance,
	- [ ] track was lost of initial originand things were pasted back onto the wrong position
	- [ ] alternatives were changed when they were supposed not to!(for instance prefix operations are not supposed to do this)


- [ ] the command seems to select/operates on a random result

- [ ] the command has some other unintended behavior




**Context In Which It Appears**

<!--
Unfortunately, bugs can sometimes appear only in a specific context making them harder to reproduce and debug. There is no need for you to scratch your head and go through over every scenario presented here but if you have noticed any of the below it could help me narrow things down!
-->

Does the problem seem to appear or disappear only some of the time? Does there seem to be

- [ ] spatial context/correlation with the cursor? for instance
	- [ ] is it affected by adjustments to the cursor position?()
	- [ ] does it make a difference whether you have selected some text or not?
	- [ ] does the problem appear only when you're going in one direction?
	- [ ] does it have to only do with multiple cursors?
	- [ ] or perhaps when switching back-and-forth between single and multiple cursors?



- [ ] a temporal context?
	- [ ] does it appear only right after selection query was executed?
	- [ ] does it appear only if no one other selection query was executed since the last edit?
	- [ ] does it appear only after executing an operation(paste,delete,swap)?
	- [ ] does it appear when you perform manual editing between commands?

- [ ] correlation with a pattern in the code? a strong indicator for such a case . In case you have identified this pattern, does the error occure when it appears
	- [ ] on the target of the query? (For instance there was a bug at some point that sometimes prevented you from selecting arguments from function calls inside with statements)
	- [ ] on the origin of the query?
	- [ ] in between them perhaps?
	- [ ] somewhere inside to the current function/class/indentation block/...
	- [ ] anywhere in the code :)

<!-- if none of the above satisfies you can describe the contextas you wish -->

<!-- I did some examples(like providing gifs, code snippets, command series) where things work versus when they don't could sometimes be helpful especially when you're not really sure what is wrong. -->

**Error Message**

- [ ] error message appears in a pop-up

- [ ] an exception trace back is printed in the sublime console(Ctrl + \`)

- [ ] the command fails silently

<!-- If possible, sharing the error message might be helpful
```
error message
```
-->
