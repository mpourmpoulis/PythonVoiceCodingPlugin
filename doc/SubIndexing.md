
# SubIndexes

So far we have seen cases where we can select an entire region of interest.
However,there are cases where you are interested in only a portion of this whole ROI. For instance there may be multiple targets in the left hand of an assignment and you want to select only one of them. Or your function may return multiple values. or your right hand side contains a dictionary and you want a specific key-value pair. In those cases the 

```python 
IntegerRefST("big_roi_sub_index",0,10),
```
comes in useful:


![](./gif/big2.gif)

Okay , can we do something similar for other cases? like select only a portion of an if condition?

![](./gif/big6.gif)

As illustrated above, you need to pay attention to how the various conditions are bound together
(or binds weaker causing it to be higher in the AST) in the can only select smaller conditions  from the outermost level!

This feature existed ever since the initial release but was only documented on 0.0.1 . This release also expanded the feature from applying only to ast.BoolOp nodes to encompass ast.Compare nodes as well! in plain English:

![](./gif/big7.gif)  

furthermore, big_roi_sub_index can make our lives easier even in cases like the one below:

![](./gif/big8.gif)  

where we want to play with the indexes of a subscript!

### new with 0.0.4

Sub indexing functionality has been expanded to include picking up parts of strings :

![](./gif/big10.gif)  

We can pick up parts from the URL, individual words or letters, or part of a camel or snake case. this feature is still immatur  and needs more work, but I am planning to improve and also expand it with the ability to select a whole range.

Also something that was kind of missing,you can now select a subset of an arithmetic expression :

![](./gif/big12.gif)  

Once again you need to pay attention to operator precedence and as you can see there are some edge cases that need to be fixed.

Finally, we clarify one more thing! What about relative vertical offsets when using above? We know that these abstract vertical keywords only count interesting lines, but what do we count as interesting here? To stay compatible with all of the above, we count all lines containing our desired big region of interest regardless of whether we can extract or not from them information with the sub index! As an example:

![](./gif/big9.gif)  


please note however that there are limitations  and sub indexes are more of a solution to make the simplest case faster
rather than a systematic way of handling complex code!
