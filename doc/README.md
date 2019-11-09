# User Guide 

## Quick Command Overview

Here we will briefly go over the commands offered. 

Before we get started, a small general remark: 
```
tip: if you do not know what to say, say smart :P
```

because virtually every command starts with the keyword smart! 

```python
"smart <big_roi> [<big_roi_sub_index>]"

"smart <color> [alternative]"
```

This was chosen in order to minimize chances of collision with other commands on your system. However, because for a variety of commands, ommitting the keyword smart makes them more convenient and easier to speak
you may find the smart keyword in brackets

```python
"[smart] alternative <alternative_index>"

"[smart] paste back [<paste_back_index>]"

"[smart] paste <color> back"
```

if there are conflicts with other commands, try to remove those brackets (making smart not optional). Furthermore, I I think it is best not to put brackets in cases where I haven't.  

After the small remark let's get started!


### Selection Queries

The most simple thing you can do is to select some text. This can be done by Selection Queries/Commands. One example of such a command is [Select Argument](SelectArgument.md) command :

![](./gif/arg0.gif)

Another example is [Select Big ROI](SelectBigROI.md) command :

![](./gif/big0.gif)

For more specifics you can view the correspondong documentation but I would like to note a couple of things about two methods that both commands more or less share in order to specify which canditate you are interested in:

* if you wish to specify the order of your region of interest, then you probably need an adjective :

```python
Choice("adjective",{ 

"first" : "first", "second": "second", "third": "third",

"fourth": "fourth", "fifth": "fifth", "sixth": "sixth",
 
"seventh": "seventh", "eighth": "eighth", "ninth":"ninth", 
  
"last":"last", "second last": "second last",

"third last": "third last", "fourth last": "fourth last", 


} )
```
![](./gif/big3.gif)

and 

* if you want to  specify the relative vertical position with respect to your current selection, probably you need one of these keywords: 

```
Choice("vertical_direction",{ 

"up":"up", "down":"down",

"above":"above", "below":"below", 

} )
```

usually followed by an integer. Beware the difference between up and above! As a rule of thumb, above only takes "interesting" lines into consideration:)

![](./gif/arg5.gif)



* in certain cases you can combine these two approaches:)

![](./gif/big5.gif)

Details vary but that is the. spirit! Ok , what else?


### Alternatives

As you can see, these commands select some ROI (region of interest) and generate alternatives. These alternatives are shown to the user in an output panel on the bottom of the screen and the top ones get highlighted in the code as well. 

We can select one of those alternatives with the alternative rule which comes in two variations:

```python
"[smart] alternative <alternative_index>"

"smart <color> [alternative]"
```
![](./gif/d1.gif)

alternative_index is an integer
```python
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

![](./gif/d2.gif)

As you can see it comes in two formats: 
```python
"[smart] paste back [<paste_back_index>]"

"[smart] paste <color> back"
```

If no alternative is specified the main result is pasted back!

Please also pay attention to the following:

![](./gif/d3.gif)

That is you can use successive selection queries and paste back will insert in your original starting position!


So we can select some basic stuff and we can insert it where we are writing. What elae can we do?

### Collection Queries 

Imagine a case where you have a variable or parameter name or an expression with perhaps many atoms that are hard to dictate. 

If you dont want to rely on autocompletion you can for instance select it and paste it back:) But what if you need to write it several times in dofferent locations? Or what if it is so far away in the code you cannot really describe it?(say an imported item whose full name you dont even remember)


Collection Queries try to address this issue. These collect the text of interesting regions and display it on the bottom panel.


![](./gif/d4.gif)

you can collect a variety of things:

```python
Choice("index_collectable",{
	"(variable|variables)":"variable",
	"( parameter | parameters)":"parameter",
	"(module|modules)":"module",
	"imported (value|object)":"import value",
	"function ( name |names)":"function name",
} 
```
please note that these items are collected from the whole source code.

### Insert Item

These "items" can then be inserted in the current cursor position by means of the 

```python
"(smart insert|insert item) <item_index>"
```
command. Item_index specifies which item from the collection you want

![](./gif/d5.gif)

### index collectible

certain collectible items such as variables and parameters can be index collected by means of a query like

```python
"[smart] variable <collect_index>"
```
In such a case, items will only be collected from the current function  and in item will be inserted
based on the index specified and their order of appearance

![](./gif/d6.gif)




