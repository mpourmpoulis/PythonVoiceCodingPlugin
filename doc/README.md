# User Guide 

 

 


### Collection Queries 

They collect the text of interesting regions.More on that later:)

### Insertion Queries 

They insert text at some location.

## Quick Command Overview


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
(Tip : index --> integer)
whereas color is an adjective:

```python
Choice("color",{ /
"red":1, "blue":2, "green":3, "yellow":4, "orange":5, 
} ),
```

### Paste Back 

But why would we want to select some text in the first place? Other than editing it, maybe to copy it and paste it somewhere? Very likely where we are currently working? Well, the paste back command allows just that! 

[](gif/d2.gif)


