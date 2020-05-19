# math-genealogy
Generate a tree of academic ancestors of a mathematician, pulling data from the Math Genealogy Project

Downloads all the data about a mathematician from the MGP page for their ID and locates their ancestors.
Then proceeds via DFS to find all the ancestors, until the chain terminates.
Saves the data in a human readable .txt file as well as a pickled array.
