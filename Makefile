.PHONY: check clean dist test

# List of Constants #
DS.PY = data_structures.py
EXEC = main
MAIN.PY = main.py
PIP = pip3
PY = python3


# For clean and dist target convenience
FILES = README Makefile $(MAIN.PY) $(DS.PY)


# Targets #
default: $(EXEC)

$(EXEC):
	echo './main.py "$$@"' > main
	chmod +x main

check:
	bash check.sh Makefile
	bash check.sh README
	bash check.sh $(MAIN.PY)
	bash check.sh $(DS.PY)

clean:
	rm -f $(EXEC) $(DIST)
