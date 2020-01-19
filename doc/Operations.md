# Operations

## Introduction

### Colors

as a small notice before we get started, because you are going to see colors a lot , you should be aware of the values it can take are

```python
"colors":{
            "main":0,
            "red":1,
            "blue":2, 
            "green":3,
            "yellow":4,
            "orange":5,
},
```

with colors red until orange corresponding to alternatives and the word main to the main result.

### Introduction To Prefix Operations

the format of the operations we are going to discuss in this page, are queries that are executed after some selection query which has yielded some results  and  some alternatives. By using the color keyword, we are able to specify if we want these queries to operate using the main result or one of the alternatives. 

This of course gives us great flexibility but it does come with cost of having to perform everything in 2 steps. 
A cost which is completely unnecessary in cases where

* We are optimistic/confident what the main result of our selection query is going to be

* We are only interested in operating on the main result

And situations like those actually come up very often in day-to-day coding.

As a workaround to both retain this nice flexibility and enable quick tasks to get done in a single query, alongside with the traditional operation queries version 0.1.0 introduced prefix operations. In particular , selection queries can have a "operation" prefix which can take one of the following values

```python
Choice("operation",{
        "paste": "paste",
        "delete":"delete",
        "swap": "swap",
        "edit": "edit",
    }
),
```

what is going to happen after your single spoken command is that the plug-in will be interpreted as a "double" query

- The selection queries going to get executed firstly 

- And is then followed by a secondary operation query operating on the main result

but an important technicality is that the selection query is going to get executed "silently"






## Select Alternatives 


Arguably one of the queries that will become the bread-and-butter for your daily usage

```python
"smart <color>"
```

As they enable you to select an alternative describing it with its color

![](./gif/op4.gif)

### Multiple Colors

But that these type of queries are notlimited to only one color. Instead you can specify more to grab them all under multiple cursors!

```python
"smart <color> [<color2> [<color3> [[and] <color4>]]]"
```

![](./gif/op5.gif)


### Multiple Cursors

But things go one step ahead, and this query can also be executed even in cases where you have multiple results each with its own alternatives! 

![](./gif/op6.gif)

As you can see in the last example the color you specified has to be available for all different cursors!

### Legacy Syntax

This is a little bit of legacy code to address the need to be able to work with more than colored five alternatives.

```python
"[smart] alternative <alternative_index>"
```

As usual `<alternative_index>` is an integer.


## Delete Operation

But except selecting alternatives you can also do all the things with them. For example you can delete an alternative
simply by specifying its color and the cursor we will then be placed at its position,ready for editing.

![](./gif/op8.gif)

```python
"[smart] delete <color> [<color2> [<color3> [[and] <color4>]]]"
```

### Alternatives Persist

One thing that is important to note, is not unlike the previews alternative selection, the delete alternatives query does not make the other alternatives disappear! That is because it is NOT a selection query and even though it does change the current selection , it does so WITHOUT creating a new result/alternatives/origin/initial_origin. the old ones are still there! 

This can be convenient when you want to delete one alternative, write some new code there and then proceed to do the same on another  alternative and so on... though you need to be careful because the current implementation does not track down any code  added  to a deleted alternative, hence no color on the deleted ones

![](./gif/op9.gif)

### Multiple Colors

Furthermore, similarly to selecting alternatives, you can simultaneously delete more than one alternatives! you just need to specify more than one colors!

![](./gif/op10.gif)


### Multiple Cursors 

And of course cursors are also supported

![](./gif/op7.gif)


### Delete Prefix Operation 

As mentioned [earlier](#Introduction-To-Prefix-Operations) , prefix operations are also available

![](./gif/op11.gif)

also please note that the  delete operation can handle overlapping results

![](./gif/op12.gif)


## Pasting Operation

### Pasting To Initial Origin



![](./gif/op1.gif)

#### Surrounding Punctuation

![](./gif/op2.gif)

#### Note For 0.0.4 Users



### Pasting Between Alternatives

but you are not limited to basting only the initial origin. By means of

```python
"[smart] paste <color> on <color2> [<color3> [ [and] <color4>]]"
```

you are able to paste one of the colored alternatives/result on one or multiple other alternative/result!

![](./gif/op3.gif)

### Pasting Prefix Operation


### Multiple Cursors

#### Multiple Origins Single Result

#### Multiple Origins Multiple Results

#### Single Origin Multiple Results






## Swap Operation

## Edit Operation

## Utilities 

### Setting Initial Origin

### Return To Origin

