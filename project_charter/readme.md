# Project 4 Proposal

Brendan Lafferty

## Idea

### Main 

 - Compare writing styles across the entire english corpus of Project Gutenberg
 
### Backup
 - Compare the differences of a shortlist of authors
  - Sheakespear, William
  - Dickens, Charles
  - Austin, Jane
  - etc.
  
### Bonuses/stretch goals
 - Recommendation system that recommends books based books read/like that are either similar or 
   different 
 - Text generation mimicking an author (lol, I don't think I will actually do this :) 
 
## Data Source:
 - [Project Gutenberg](https://www.gutenberg.org/)\
   -[info](https://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages) on downloading files 

## Workflow

 - Download English Corpus from Project Gutenberg
 - Clean text
   - Found a python module to help remove the project gutenberg headers and footers
   - Also found a nice module to keep track of the metadata (author, title, etc.)
 - Probably will have to subsample each text
 - See what I can learn about the corpus through topic modeling

## References
 - Python Package: [gutenberg](https://github.com/c-w/gutenberg)