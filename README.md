# CLASSFLOW 
###  Help students plan their courses by generating flow maps of UC Riverside major paths.
###### (Designed at [Cutie Hack 2018](https://www.cutiehack.io/).)

Course scheduling has frustrated me for a while. To think about your academic plans at a high level, you have to be aware of all of the classes available in your major and related majors, and the proscriptive guides given by the university usually say something like "if you're a major, be sure to take CS100" without it being clear what classes you need to do before getting there.

To deal with this before this project, I spent about an hour per major exhaustively searching all classes of a major on Banner (our course scheduler) and tying them together in [XMind](https://www.xmind.net/). You can see an example of this here with Computer Science:

![handmade cs course graph](https://github.com/OrderFromChaos/classflow/blob/master/handmade/compsci_v2.png)

While it looks nice (and deals with the frustrations mentioned above), it is an uphill battle to generate these. Each year, the department will usually shift courses around a little bit, and sometimes new courses will be added or fail to be offered that year. I wanted to come up with a robust way to create these based on new offerings each year.

We did it! [William Shiao](https://github.com/willshiao) made this repo's git submodule ucr-course-graph, which allows us to use JS to scan Banner for courses and their prerequisites, and I wrote a program using graphviz and dot to replicate the handmade results. See here:

![generated cs course graph](https://github.com/OrderFromChaos/classflow/blob/master/smallphys.png)

Some caveats:
1. The data pull only worked properly for one quarter, so this ignores two quarters of series classes. This is why you only see Phys135A, for example. We're working on partnering with UCR IT and Special Projects to get limited access to the Banner database, and this repo will be updated accordingly as the project proceeds.
2. Some prerequisites are "AND" groups, which means you have to complete each of them, and some are "OR" groups, which means you have the option of completing a couple different courses, each of which satisfy the requirements. This program deals with these by drawing dotted lines for the OR groups, and solid lines for the AND groups. You can see OR groups in the same node as a class.
3. There is, of course, more graphic work to go. There are some fairly complicated rules I used as a human to make the chart nicer looking (ignore honors courses - assume people understand that, etc.), so these still need to be implemented. [You can track our progress on our Trello here](https://trello.com/b/R8BMbjK5).

Note that this system works quickly for generating large graphs - this combination of `{'PHYS','CS','MATH','ECON','BIOL'}` generated in about a second:

![{'PHYS','CS','MATH','ECON','BIOL'} graph](https://github.com/OrderFromChaos/classflow/blob/master/hugegraph.png)

Some extension ideas we have:
1. Pull the UCR catalog for that year, and grab the prerequisites from it. Unfortunately, we can't guarantee the catalog will be regularly structured, but we did come up with a decent regex for this: `^[A-Z]{3,4}\s?[0-9]{3}[A-Z]?\s.+\n?.+\([12345]\)`
2. Reduce graph crossing as much as possible. [This might be an NP-hard problem](https://cs.stackexchange.com/questions/14901/how-to-reduce-the-number-of-crossing-edges-in-a-diagram), or we could use other data, like when people tend to take classes (this would let us deal with series classes elegantly).
3. Combine lecture and lab sections that are meant to be taken concurrently.

Thanks to everyone else who helped out in the project (G. Mata, J. Shin).