# User Guide 

## Quick Command Overview

Here we will briefly go over the commands offered.

### Selection Queries

The most simple thing you can do is to select some text. This can be done by Selection Queries/Commands. One example of such a command is [Select Argument](SelectArgument.md) command :

### Alternatives

As you can see, these commands select some ROI and generate alternatives. These alternatives are shown to the user in an output panel on the bottom of the screen and the top ones get highlighted in the code as well. 

We can select one of those alternatives with the alternative rule which comes in two variations:

```
"[smart] alternative <alternative_index>"

"smart <color> [alternative]"
```
[](gif/d1.gif)

alternative_index is an integer
```
(Tip : index --> integer)
``` 
whereas color is an adjective corresponding the color highlighting:

```python
Choice("color",{
		"red":1, "blue":2, "green":3, "yellow":4, "orange":5, 
	} 
)
```

### Paste Back 

But why would we want to select some text in the first place? Other than editing it, maybe to copy it and paste it somewhere? Very likely where we are currently working? Well, the paste back command allows just that! 

[](gif/d2.gif)

As you can see it comes in two formats: 
```
"[smart] paste back [<paste_back_index>]"

"[smart] paste <color> back"
```

If no alternative is specified the main result is pasted back!

Please also pay attention to the following:

[](gif/d3.gif)

That is you can use successive selection queries and paste back will insert in your original starting position!


So we can select some basic stuff and we can insert it where we are writing. What elae can we do?

### Collection Queries 

Imagine a case where you have a variable or parameter name or an expression with perhaps many atoms that are hard to dictate. 

If you dont want to rely on autocompletion you can for instance select it and paste it back:) But what if you need to write it several times in dofferent locations? Or what if it is so far away in the code you cannot really describe it?(say an imported item whose full name you dont even remember)


Collection Queries try to address this issue. These collect the TEXT of interesting regions and display it on the bottom panel.


[](gif/d4.gif)

### Smart Insert 

These "items" can then be inserted in the current cursor position by means of the 

```
"(smart insert|insert item) <item_index>"
```
command. Item_index specifies which item from the collection you want

[](gif/d5.gif)


