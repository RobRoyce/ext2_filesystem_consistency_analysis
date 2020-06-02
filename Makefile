#NAME: Robert Royce, Tyler Hackett
#EMAIL: robroyce1@ucla.edu, tjhackett@ucla.edu
#ID: 705357270,405180956
.PHONY: check clean dist

# List of Constants #
DIST = lab3b-705357270.tar.gz
DS.PY = data_structures.py
EXEC = lab3b
MAIN.PY = lab3b.py
PIP = pip3
PY = python3
REQ = requirements.txt
StudID = 705357270
TEST.D = test/
TEST.SH = P3B_check.sh


# For clean and dist target convenience
FILES = README Makefile $(MAIN.PY) $(DS.PY)


# Targets #
default: $(EXEC)

check:
	bash check.sh Makefile
	bash check.sh README
	bash check.sh $(MAIN.PY)
	bash check.sh $(DS.PY)

clean:
	rm -f $(EXEC) $(DIST)

dist:
	tar -czvf $(DIST) $(FILES)

lab3b: $(MAIN.C)
	$(PIP) install -r $(REQ)

test: dist
	cp $(DIST) $(TEST.D) && cd $(TEST.D) && bash $(TEST.SH) $(StudID)
