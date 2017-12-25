#RM = del
PYTHON2 = python2
MAKE = make

APPL = dug.py

PY_FILES = \
	__main__.py \
	__init__.py \
	update.py \
	scan.py \
	ansi.py

all: $(APPL)

clean:
	rm -f $(APPL) *.pyc

$(APPL): $(PY_FILES) 
	$(PYTHON2) -c "import zipfile; zipfile.PyZipFile('$(APPL).tmp', 'w').writepy('.')"
	echo "#!/usr/bin/env python2" > $(APPL)
	cat $(APPL).tmp >> $(APPL)
	chmod +x $(APPL)
	rm $(APPL).tmp

.PHONY: all clean 
