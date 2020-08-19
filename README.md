# gutenberg_nlp
nlp project looking at works in the public domain


## Downloading


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