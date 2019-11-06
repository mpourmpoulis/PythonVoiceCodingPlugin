# Select Big Region of Interest Command

These commands are responsible for selecting "big" regions of interest. By "big" we refer to things like "if condition" or "assignment right" in contrast to say the first entry of a dictionary.

In particular, the currently offered "big roi´s" are :

```python
Choice("big_roi",{ 
"if condition" : "if condition", 
"else if condition" : "else if condition", 
"while condition" : "while condition", 

"if expression condition" : "if´´ expression condition", 
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
"(import|imported) (value|item|object|element)":"import value", 
"module" : "module",

"(expression statement|expression)" : "expression statement", 

"iterator" : "iterator", "iterable" : "iterable",
 } ),
```

I think most of them are pretty aelf explanatory, 