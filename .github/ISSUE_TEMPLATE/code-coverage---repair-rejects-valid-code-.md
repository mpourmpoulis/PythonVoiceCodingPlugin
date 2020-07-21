---
name: 'Code Coverage : Repair Rejects Valid Code '
about: This concerns bugs where valid code is rejected after being repaired
title: ''
labels: bug, code coverage
assignees: mpourmpoulis

---

<!--In a nutshell what is going on under the hood is

- the plug-in tries first to parse your code Without making any modification. If The ASD module does not complain, we are good to go!
- however if there are errors, it will tokenize your code and will deploy various heuristics in order to fix as many problems as possible
Unfortunately, it will occasionally make Mistakes and Intervene in a way that may break some piece of syntactically correct code. If you're facing such a problem( for instance getting the pop-up message within the invalid syntax warning in a correct line), Is the correct issue type for you!

Please note that for the reasons explained above these bugs can be very subtle, appearing only when there is another error somewhere in the code!
-->




# Description

<!-- enter  a short description of the problem And What ever information You'd like to include but does not become apparent from the examples below-->



<!-- providing the snippet of Syntactically correct code for which repair produces an invalid output Could be helpful Or you can upload to gif if you prefer instead-->

**Your Code**


```python

```

<!-- Optionally providing the corrected code as output in the console (Ctr + \`l) Could also be helpful

**Repair Output**

```python

```
-->
