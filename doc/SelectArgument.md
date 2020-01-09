# Argument Selection Command

![](./gif/arg0.gif)

This is a SelectionQuery that was originally designed to enable you to select an argument from a function call,hence the name. With release 0.1.0, it has also been expanded so that you can pick up the calling function, below referred to as "caller", as well as the names of the keyword passed parameters.

if you open up my bundles, you will see that the corresponding rules are:

```python
"[(smart|<operation>)] [<nth>] (argument <argument_index>|keyword <keyword_index>|caller [<sub_index>])"

"[(smart|<operation>)] <vertical_direction> [<ndir>] [<nth>] (argument <argument_index>|keyword <keyword_index>|caller [<sub_index>])"

"[(smart|<operation>)] [<nth>] inside [<level_index>]  (argument <argument_index>|keyword <keyword_index>|caller [<sub_index>])"

"[(smart|<operation>)] inside [<level_index>] <nth> (argument <argument_index>|keyword <keyword_index>|caller [<sub_index>])"

"[(smart|<operation>)] outer [<level_index>] [<nth>] (argument <argument_index>|keyword <keyword_index>|caller [<sub_index>])"
```

but in essence, the full syntax comes down to:

```python
"[smart] [<nth>] argument <argument_index>"

"[smart] <vertical_direction> [<ndir>] [<nth>] argument <argument_index>"

"[smart] [<nth>] inside [<level_index>]  argument <argument_index>"

"[smart] inside [<level_index>] <nth> argument <argument_index>"

"[smart] outer [<level_index>] [<nth>] argument <argument_index>"
```

if you want find out more about what is whole "operation" thing you can find more information [here](doc/Operations.md). as far as

```python
"(argument <argument_index>|keyword <keyword_index>|caller [<sub_index>])"
```

is concerned, this is just part of the expansion I mentioned above and more on this [later](#Keywords). 

The important part is that it comes in five formats, which enable you to specify which function call you want to extract information from. We will go briefly over each of these five posibilities, clarifying all the parameters and give you an idea of how they work. 

What you should also keep in mind is that they in general search for results in a single logical line. For cases 1,3,4,5 that is the current line whereas for case 2 that is the line you indirectly specify with 

```python
"<vertical_direction> [<ndir>]"
```

### Quick note for 0.0.4 users

"nth" corresponds to what used to be "adjective",but has been seen in order to be closer to what their grammars use for ordinal adjectives and make things easier for newcomers to understand.

## Case one 

The most simple command is 

```python
"[smart] argument <argument_index>"
```
argument_index is an integer

```python 
IntegerRefST("argument_index", 1, 10),
```
specifying which argument you want to select.

![](./gif/arg1.gif)

There are of course a couple of things to note:

* your selection does not have to be inside a function call to get a result. Remember the whole line is searched!

* as with most queries alternatives will (if any found) be offered!

* take a bit of care when you6 have selected whole regions of text insted of a single point

* regions nearer your selection in the AST will get prioritized!

To illustrate all of the above :


![](./gif/arg2.gif)


But what if you want to have more control over what you select?  In that case you might need to use an nth/ordinal adjective as a positional descriptor as well. This is done by 

```python
"nth"
```

Which can take the following values:

```python
"first"
"second"
"third"
"fourth"
"fifth"
"sixth"
"seventh"
"eighth"
"ninth"
"last"
"second last"
"third last"
"fourth last"
```

specifying from which function call we want to select an argument:

![](./gif/arg3.gif)

Of course that was a trivial example and code can be much, much more complicated with lots of nested functions calls, brackets etc. The combinations of code structure, selection location and desired targets are literally dozens...

Just as an example, you might want the second call from the outermost level, the second relative to the selection from the current nested level, the second leftmost lexically appearing, the second within the list or tuple, or something matching any of the above criteria but inside your highlighted selection,etc... 

To deal with this issue without overloading you with too many rules to learn :), some designs decisions were made  >and the plugin tries to interpret your adjective description in a variety of ways:

![](./gif/arg4.gif)

The way this works is a little bit complicated but I hope you get the main idea.

## Case two 
 
What if you want to select something in a different line? Then you can use :

```python
"[smart] <vertical_direction> [<ndir>] [<nth>] argument <argument_index>"
```  

vertical_direction can belong to one of the two following families,as the name suggests enables you to specify whether you want something that these are above or below your current cursor position.

```python
"(up|sauce|above)":"upwards",

"(down|dunce|below)":"downwards",
```

and ndir is an interger specifying how many "interesting"(!) lines relative to the current line up or down your roi is. if omitted it has a default value of one

```python
defaults = {
    "ndir":1,
}
```

please do pay attention to the whole "interesting" thing!Unlike say Caster navigation rules of the form:

```python
"sauce/dunce [<n>]"
```
we only count (physical) lines containing function calls! The following example should clarify this:

![](./gif/arg5.gif)

Though if we want to be more precise, we count lines that contain the beginning of function calls! this is important because logical lines can extend over multiple "physical" lines. The last example in the gif contains such an example,but to give you a better idea:

![](./gif/arg9.gif)

so you can see that

* physical lines still determine the line to which above/below refer  

* result and  alternatives from that physical line are  being prioritized, but 

* The whole logical line is scanned for alternatives ! 

#### quick note for 0.0.4 users

In the past the keywords up and above used to have different semantics, but with 0.1.0 this has changed, we for keywords up/sauce having now the same meaning with above. This was done so us to make things more compatible with what users might be from other grammars, and either way,judging from the personal uses of my tool,up was used nowhere near as often as below/above.


#### handling edge cases

In a more complex scenario, if there are multiple functional calls in the physical line and you up for using an ordinal adjective, in order to to preserve sanity, the main result will be decided by taking into consideration the order of lexical appearance:

![](./gif/arg10.gif)


Finally, even though the argument query was originally designed to operate on a single logical line, make things more consistent, an exception was made for the case when the physical line that you are targeting contains more than one logical lines. In such a case, all the logical lines are processed in the monitor similar to the previous case, with important distinction that both the result and the alternatives must come from this physical line, where as in the previous case either one of them can come from other physical lines, if no suitable candidate is found.

![](./gif/arg11.gif)




## Case three

now let's see something different:

![](./gif/arg6.gif)

in this example we use the command:

```python
"[smart] [<adjective>] <level> [<level_index>]  argument <argument_index>"
```
For the time being, the only available option for the level parameter is

```python
Choice("level",{
		"inside":"inside",
	}
),
```
by means of the keyword inside , we can specify that we want an argument from a function call that is nested inside another function call! The level_index parameter

Specifies the index of the argument of the outer function call our desired ROI lies in. In order to specify which outer function goal we are referring to we can optionally use an adjective :

![](./gif/arg7.gif)


## Case four

This, looks very similar to the previous one. However, instead of using the adjective specify the outer function call, we use it to specify which one from the nested ones we want:

![](./gif/arg8.gif)

As you can see, the syntax looks like:

```python
"[smart] <level> [<level_index>] <adjective> argument <argument_index>"
```




