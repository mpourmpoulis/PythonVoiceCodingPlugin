# Operations

## Colors

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



## Delete Operation


## Swap Operation

## Edit Operation

## Utilities 

### Setting Initial Origin

### Return To Origin

