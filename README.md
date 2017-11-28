# mkaptrepo
Create an apt repository at the specified directory

# Requirements
This script has been written to run with Python 3 (3.6, to be exact)
I may refractor it to be Python 2 compatible.  It also requires the
```pydpkg``` package

# Installation
This is a very rudimentary repository and does not include
any installation instrumentation.  Just copy the python script
to a directory in your PATH and run

```shell
git clone https://github.com/gwojtak/mkaptrepo
sudo pip3 install -r requirements.txt
```

# Usage
Copy your .deb packages to a directory accessible by your web server and run the script
```shell
sudo mkaptrepo.py /path/to/repo
```

# Issues
Open in the issue tracker!

# Contributing
Fork, edit, commit, PR - pretty standard stuff!
