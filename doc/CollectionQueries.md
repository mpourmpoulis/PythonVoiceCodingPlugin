# Collection Queries

![](./gif/collect0.gif)


## Collecting Interesting Stuff

to collect interesting stuff, the command

```python
"[smart] collect <collectable>"
```

is available. the `collectable` parameter can have one of the following values

```python
 Choice("collectable",{
                "(variable|variables)":"variable",
                "( parameter | parameters)":"parameter",                
                "imported value":"import value",
                "function (name|names)":"function name",
                "class name" : "class name",
                "decorator" : "decorator",
            }
        )
```

![](./gif/collect5.gif)


Now there are various small things to note:

* everything is collected from the entire code, so that means that the variables and parameters are collected from other functions as well

* When you are collecting modules, if you import from x.y.z, all three [x.y.z,x.y,x] paths are collected!

* When collecting decorators, both the entire decorator as well as the calling function is collected.

## Inserting Items

okay great, so we have collected all the items that you want and they are displayed on the screen. How do you insert them? up to 0.0.4 this syntax was based around `"(smart insert|insert item) <item_index>"` but with a release of 0.1.0 that `(smart insert|insert item)` has been shortened to `[smart] item`  and enhancements have been made, mostly to accommodate the need of quickly inserting multiple items.  


To that end, the new grammar allows you to

* specify a range of items 

* Individually describe multiple items in a row by their index

the corresponding syntax is

```python
"[smart] item <item_index>"

"[smart] (item|items)  (all| <item_index> until (<item_index2>| the end))"

"[smart] (item|items) <item_index>   <item_index2> [  and  <item_index3>]"
``` 

In those multiple values are pasted with commas in between them on the current selection.
To give you an example:

![](./gif/collect1.gif)

please do note, two important factors. `[smart] item` :

* Does not parse your source code, so it is going to work even if there are fatal errors which might prevent other commands from running

* because collections currently persist between tabs, you can insert items from other source files!

* Is going to use the latest  collection built, even if the display bar has been hidden because of another query/pressing escape.

* works with multiple cursors, inserting the same thing in all of them

To illustrate all of the above:

![](./gif/collect2.gif)




## Index Collectible

so far we have seen two discrete rules, one collecting items and displaying them on the bottom of the screen and pond responsible for inserting them. but for two special cases, namely variables and parameters kinda combine them :)

the core idea is to have commands based on the form

```python
"variable <item_index>"

"parameter <item_index>"
```

which are going to collect variables/parameters from the current function and insert them directly. Combined in these with the ideas developed above for inserting multiple items at once, we obtain something of the form

### Variables

```python
"[smart] variable <item_index>  [[and] <item_index2> [and <item_index3>]]"

"[smart] (variables all|variable <item_index> until (<item_index2>| the end))"
```

![](./gif/collect3.gif)

please do pay attention to the fact that variables are extracted only from the current function this time! 

### Parameters

something similar applies for parameters as well

![](./gif/collect6.gif)

however in this case we have a little bit more expressiveness available, as we can also insert barometers from other functions! 


![](./gif/collect4.gif)

```python
"[smart] [<vertical_direction> [<ndir>]] parameter <item_index>  [<item_index2> [and <item_index3>]]"


"[smart] [<vertical_direction> [<ndir>]] (parameters all| parameter <item_index> until (<item_index2>| the end))"
```

notice that the syntax is very similar after the one used by big regions of interest queries `"<vertical_direction> [<ndir>] <block>"` for selecting things from other functions, but function is optional, so it can also be used in the more simple and traditional `"<vertical_direction> [<ndir>]"` this was chosen so most makes things easier to speak into either way we are extracting from function definitions:)

#### Experimental 


In the grammar bundles you are going to to see there are some extra commented lines 

```python
"[smart] [<vertical_direction> [<ndir>]] key parameter <item_index>  [ and <item_index2> [and <item_index3>]]":
    lazy_value("collect_parameter",2,experimental = "True"),

"[smart] [<vertical_direction> [<ndir>]] key (parameters all| parameter <item_index> until (<item_index2>| the end))":
    lazy_value("collect_parameter",3,experimental = "True"),
```



this is a little bit more functionality that that the backened has been adopted to support but I am still not sure if what it offers is worth the additional grammar complexity. furthermore they are still immature and may be subject to change. As a consequence, I chose not to include them in the "official" grammar but if you want you can enable them yourself by simply commending those lines.

Essentially they look just like the previous ones but in the spoken form there is a `key`  word before the parameter( which of course you can change to what ever you wish) and an additional `experimental = "True"`, which is just a temporary way to inform the plug-in that we want experimental functionality.

where they defer is that instead of inserting

```python
parameter1,parameter2,...
```

they insert 

```python
parameter1=parameter1,parameter2=parameter2,...
```


![](./gif/collect7.gif)



