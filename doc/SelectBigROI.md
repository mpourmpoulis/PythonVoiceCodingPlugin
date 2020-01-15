# Select Big Region of Interest Command

These commands are responsible for selecting "big" regions of interest. By "big" we refer to things like "if condition" or "assignment right" in contrast to say the first entry of a dictionary, though we will see later, by means of subindexes we can select [smaller stuff!](./SubIndexing.md)

![](./gif/big2.gif)

Regarding the available big regions of interest, you can find more details [below](#Selectable) , but I hope most of them are sufficiently self-explanatory. Now if for any reason you do not like the names I have given, you can always customize as you see fit. Remember only change the spoken part, that is the key of each key value pair , so as not to break the plug-in backened!



```python
Choice("big_roi",{

                "if condition" : "if condition",
                "else if condition" : "else if condition",
                "while condition" : "while condition",
                "with item" : "with clause",

                "exception":"exception",
                "exception name":"exception name",
                "handler":"handler",

                "if expression condition" : "if expression condition",
                "if expression value" : "if expression body",
                "if expression":"if expression",
                "if expression else" : "if expression else",

                "comprehension condition" : "comprehension condition",
                "comprehension value" : "comprehension value",

                "return value" : "return value",
                "pass":"pass",
                "break" : "break",
                "continue" : "continue",

                "assertion message" : "assertion message",
                "assertion condition" : "assertion condition",
                "exception raised" : "exception raised",
                "raised cause": "raised cause",

                "(assignment right| right)" : "assignment right",
                "(assignment left| left)" : "assignment left",
                "assignment [full]" : "assignment full",
                "(expression statement|expression)" : "expression statement",


                "import statement":"import statement",
                "import value" : "import value",
                "module" : "import module",
                
                

                "iterator" : "iterator",
                "iterable" : "iterable",

                "function name": "definition name",
                "function parameter": "definition parameter",
                "parameter list": "definition parameter list",
                "default value": "default value",
                

                "lambda":"lambda",
                "lambda body":"lambda body",

                
                "class name": "class name",
                "decorator":"decorator",
                "base class":"base class",

    }
)
```

now the full syntax, looks like

```python
"(smart|<operation>) <big_roi> [<sub_index>]"
"[(smart|<operation>)] <nth> <big_roi> [<sub_index>]"
"[(smart|<operation>)] <vertical_direction> [<ndir>] <big_roi> [<sub_index>]"
"[smart] <vertical_direction> [<ndir>] <block> [<nth>] <big_roi> [<sub_index>]"
```


As with the other selection queries,  the whole "operation" thing you see at the start of each command, is not really a part of the big ROI queries themselves but rather a prefix , which causes some action to be taken with the result of the query instead of selecting it and can accompany virtually all selection queries in general. as an example,

![](./gif/big36.gif)

Please note that in the fourth case, this prefix is missing. If you wish, nothing stops you from editing the definition to match the other three rules, I just chose it not to enable by default because I fear it might make the spoken queries too long and unnecessarily increase grammar complexity.


There are four syntaxes for you find the location of those regions of interest:




```python 
"smart <big_roi> [<sub_index>]"

"[smart] <nth> <big_roi> [<sub_index>]"

"[smart] <vertical_direction> [<ndir>] <big_roi> [<sub_index>]"

"[smart] <vertical_direction> [<ndir>] <block> [<nth>] <big_roi> [<sub_index>]"
```


technically the rules you're going to see in my grammar bundles also have the prefix 

# Case one 

Ok lets start with the simple one, namely queries of the form: 

```python 
"smart <big_roi>"
``` 

As you might expect, the plugin will try to find matches to big roi description , prioritizing ones "nearer" in the AST with respect to the current selection. Some random examples:

![](./gif/big1.gif)

One thing that is really important to note and is not made clear by the above gif, is what region are these queries  actually searching in order to retrieve results and alternatives? 

* a select few are always searching the entire code, for instance `import statement` or `class name` 

* most of them behave in their little bit more "contained" manner 

	- if invoked from the global scope the entire code will be searched, prioritizing things that are global in scope but providing alternatives that are inside functions as well.

	- If you invoked from inside say a function, then only that function will be searched

To illustrate this:

![](./gif/big35.gif)



# Case two 

If you will have a little bit more control over what select, one of the ways to achieve that is through the command

```python 
"[smart] <nth> <big_roi> [<big_roi_sub_index>]"
```

where nth is an ordinal nth adjective and can take the following values

```python
"first"             "second"
"third"             "fourth"
"fifth"             "sixth"
"seventh"           "eighth"
"ninth"             "last"
"second last"       "third last"
"fourth last"
```

As a first remark, their region searched is the same with case one,and for most queries that means the current function( pay attention to my last example where alternatives are only offered from the nested function definition!)


![](./gif/big3.gif)

Please also note that the plug-in is going to try a variety of ways to interpret this adjective. I hope the below example might give you a hint about the heuristics employed:

![](./gif/big34.gif) 



# Case three 

Another,more preferable for short distances if you ask me, alternative you can use is to provide information about the relative vertical position of your ROI with a command like that:

```python
"[smart] <vertical_direction> [<ndir>] <big_roi> [<big_roi_sub_index>]"
```

vertical_direction can belong to one of the two following families and as the name suggests enables you to specify whether you want something that is above or below your current cursor position.

```python
"(up|sauce|above)":"upwards"

"(down|dunce|below)":"downwards"
```

and ndir is an interger specifying how many "interesting"(!) lines relative to the current line up or down your roi is. if omitted it has a default value of one

```python
defaults = {
    "ndir":1,
}
```

As an example:

![](./gif/big4.gif)

A very important detail is that these types of queries are not limited to searching only the current function like the nth adjective ones or the ones from the first case! 

![](./gif/big11.gif)



# Case four 


This variant combines vertical and positional order information. 

```python
"[smart] <vertical_direction> [<ndir>] <block> [<nth>] <big_roi> [<big_roi_sub_index>]"
```
For the time being there is only one option available:

```python 
Choice("block",{ 
		"(function|functions)" :"function",
	 } 
),
```

So essentially, we can specify a function using a relative vertical desciption with the above/below keywords!

```python 
"<vertical_direction> [<ndir>] <block>"
```


Once we have established which function we are to search, the command will then work more or less like cases one and two

```python
"[<nth>] <big_roi> [<big_roi_sub_index>]"
```

 but will search inside that function!

![](./gif/big5.gif)

# Selectable



### Assignment And Expression Statements

probably one of the most basic examples and one of the most frequently used ones as well

```python
"(assignment right| right)" 
"(assignment left| left)" 
"assignment [full]" 
"(expression statement|expression)" 
```

![](./gif/big20.gif)

and because I forgot one rather important case

![](./gif/big31.gif)

### If conditions While loops With clauses

```python
"if condition" 
"else if condition" 
"while condition" 
"with item" 
```

![](./gif/big21.gif)


### If expressions

```python
"if expression"
"if expression condition" 
"if expression value" 
"if expression else" 
```

![](./gif/big22.gif)

### Return Value

```python
"return value" 
```
 
Please note 

* that empty return values can be selected and must be taken into account when counting ndir

* yield is also covered under this case

![](./gif/big32.gif)

### Iterator  and Iterable

```python
"iterator" 
"iterable" 
```
![](./gif/big23.gif)

### Comprehensions

```python
"comprehension condition" 
"comprehension value" 
```
![](./gif/big24.gif)

### Exception Handling

```python
"exception"
"exception name"
"handler"
```

![](./gif/big25.gif)

Please note that empty handlers are supported as well and that some examples with some indexing are included.

### Assertions And Exceptions Raising

```python
"assertion message" 
"assertion condition" 

"exception raised" 
"raised cause"
```

![](./gif/big26.gif)


### Functional Definitions

```python
"function name"
"function parameter"
"default value"
"parameter list"
```

![](./gif/big27.gif)


### Class Definitions

```python
"class name"
"decorator"
"base class"
```

![](./gif/big28.gif)

### Import 

```python
"import statement"
"import value" 
"module" 
```

![](./gif/big29.gif)

please do pay attention, the sub indexing import statement has the same effect as import  value!

### Lambda

```python
"lambda"
"lambda body"
```

![](./gif/big30.gif)

please do pay attention, the sub indexing Lambda has the same effect as Lambda Body!

### Continue Break Pass

Nothing really special about them

```python
"lambda"
"lambda body"
```

![](./gif/big33.gif)















