# Argument Selection Command

This is a SelectionQuery that enables you to select an argument from a function call.
It supports the following syntaxes: 

```python
"[smart] [<adjective>] argument <argument_index>"

"[smart] <vertical_direction> [<ndir>] [<adjective>] argument <argument_index>"

"[smart] [<adjective>] <level> [<level_index>] argument <argument_index>"

"[smart] <level> [<level_index>] <adjective> argument <argument_index>"
```

Let´s start with the first one and clarify some terms. 

## "[smart] [<adjective>] argument <argument_index>"

argument_index is an integer

```python 
IntegerRefST("argument_index", 1, 10),
```
specifying which argument you want to select.

[](gif/arg1.gif)

adjective is one or two adjectives such as first, second , last

```python
Choice("adjective",{ 

"first" : "first", "second": "second", "third": "third",

 "fourth": "fourth", "fifth": "fifth", "sixth": "sixth",
 
  "seventh": "seventh", "eighth": "eighth", "ninth":"ninth", 
  
"last":"last", "second last": "second last", "third last": "third last", "fourth last": "fourth last", } )
```

specifying from which function call we want to select an argument 

[](gif/arg3.gif)

Of course code can be much more complicated so the plugin tries to interpret "second" in a variety of ways as illustrated below:

[](gif/arg4.gif)

