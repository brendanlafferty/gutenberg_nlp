# gutenberg_nlp
nlp project looking at works in the public domain

by Brendan Lafferty

## Project Charter
For the proposal see [Project Charter](./project_charter/readme.md)

## Outcome
Sucessfully created a recommendation system for the english works in project gutenberg
however the size of the corpus of project gutenbern is large enough to render the system too slow 
for practical use.

### todos for improvement
 - Further demensionality reduction
 - Better storage methods i.e. a db 


## Setup

### Setting up gutenberg python module
the gutenberg python module depends on berkeley db and requires you to download the metadata to use
please see the [project repo](https://github.com/c-w/gutenberg)

### Downloading the Corpus


#### Process for downloading the corpus:
```bash
wget -m -H -nd "http://www.gutenberg.org/robot/harvest?filetypes[]=txt&langs[]=en"
```
FYI: ~2hr in 2020 with a 5 year old laptop

#### Filtering or Deleting the extras:
```bash
rm harvest*  # these are the HTML files that host the links
rm robots*  # there are a couple robots.txt files

mkdir odds  # non texts
mkdir encoding-8  # filter by encoding
mkdir encoding-0  # filter by encoding

# filter method:
find . -name "*-*.zip" -print0 | xargs -0 -I {} mv {} ./odds/
find . -name "*-8.zip" -print0 | xargs -0 -I {} mv {} ./encoding-8/
find . -name "*-0.zip" -print0 | xargs -0 -I {} mv {} ./encoding-0/
```

#### Unzipping:
```bash
python unzipper.py ./path/to/donwload/ ../unzipped/
```
If no arguments are specified it will default to current working directory


#### Isolate .txt files:
```bash
mkdir texts
find . -name "*.txt" -print0 | xargs -0 -I {} mv {} ./texts/
find . -name "*.TXT" -print0 | xargs -0 -I {} mv {} ./texts/

python clean_dir.py
```

#### Remove Gutenberg headers and footers:
```bash
python strip_headers.py ./texts
```






## References

Project Gutenberg
 - [Main Page](https://www.gutenberg.org/wiki/Main_Page)
 - [Download Reference](https://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages)
 
 Gutenberg Python Package
 - [gutenberg](https://github.com/c-w/gutenberg) this need setting up see the readme here for info on setting up