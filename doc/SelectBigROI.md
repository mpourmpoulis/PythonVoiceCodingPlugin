# Select Big Region of Interest Command

These commands are responsible for selecting "big" regions of interest. By "big" we refer to things like "if condition" or "assignment right" in contrast to say the first entry of a dictionary, though we will see later, by means of subindexes we can select [smaller stuff!](./SubIndexes.md)

![](./gif/big2.gif)


In particular, the currently offered "big roi´s" are :

```python
Choice("big_roi",{ 
"if condition" : "if condition", 
"else if condition" : "else if condition", 
"while condition" : "while condition", 

"if expression condition" : "if expression condition", 
"if expression body" : "if expression body", 
"if expression":"if expression",

"return value" : "return value", 

"pass":"pass", 
"break" : "break", 
"continue" : "continue", 

"assertion message" : "assertion message",
 "assertion condition" : "assertion condition", 
 
"(assignment right| right)" : "assignment right",
"(assignment left| left)" : "assignment left", 
"assignment full" : "assignment full",

 "import statement":"import statement", 

"(expression statement|expression)" : "expression statement", 

"iterator" : "iterator", "iterable" : "iterable",
 } ),
```

I hope most of them should be  self explanatory  and  you can find examples [below](#Selectable).

There are four syntaxes for you find the location of those regions of interest:




```python 
"smart <big_roi> [<big_roi_sub_index>]"

"[smart] <nth> <big_roi> [<big_roi_sub_index>]"

"[smart] <vertical_direction> [<ndir>] <big_roi> [<big_roi_sub_index>]"

"[smart] <vertical_direction> [<ndir>] <block> [<nth>] <big_roi> [<big_roi_sub_index>]"
```


technically the rules you're going to see in my grammar bundles also have the prefix 

# Case one 

Ok lets start with the simple one, namely queries of the form: 

```python 
"smart <big_roi>"
``` 

As you might expect, the plugin will try to find matches to big roi description , prioritizing ones "nearer" in the AST with respect to the current selection.

![](./gif/big1.gif)

t is also important to note that with exception of the import statements, all other queries search only within the current function.


# Case two 

another alternative are commands of the types:

```python 
"[smart] <adjective> <big_roi> [<big_roi_sub_index>]"
```
you should probably be already familiar with adjectives, so here is an example of how you can use them:

![](./gif/big3.gif)

as with case one, only the current function searched. ( pay attention to my last example where alternatives are only offered from the nested function definition!)




# Case three 

Another alternative you can use is to provide information about the relative vertical position of your ROI with a command like that:

```python
"[smart] <vertical_abstract_only_direction> [<ndir>] <big_roi> [<big_roi_sub_index>]"
```
The only difference compared to argument selection is that you can only use the more "abstract", 'above' and 'below' keywords:

```python 
Choice("vertical_abstract_only_direction",{ 
	"above":"above",
 	"below":"below", 
 } ),
```
As an example:

![](./gif/big4.gif)

Another important detail is that these types of queries are not limited to searching only the current function like the adjective ones! 

![](./gif/big11.gif)


# Case four 

Ok this is a bit different:)
This variant combines vertical and positional order information. 

```python
"[smart] <vertical_abstract_only_direction> [<ndir>] <block> [<adjective>] <big_roi> [<big_roi_sub_index>]"
```
What on earth is that "block" thing over there? Well for the time being there is only one option available:

```python 
Choice("block",{ 
		"(function|functions)" :"function",
	 } 
),
```

So essentially, we can specify a function using a relative vertical desciption with the above/below keywords!

```python 
"<vertical_abstract_only_direction> [<ndir>] <block>"
```


Once we have established which function we are to search, the command will then work more or less like cases one and two

```python
"[<adjective>] <big_roi> [<big_roi_sub_index>]"
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
"pass"
"break" 
"continue" 
```
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















