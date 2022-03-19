# \ var
MODULE  = $(notdir $(CURDIR))
OS      = $(shell uname -o|tr / _)
NOW     = $(shell date +%d%m%y)
REL     = $(shell git rev-parse --short=4 HEAD)
BRANCH  = $(shell git rev-parse --abbrev-ref HEAD)
PEPS    = E26,E302,E305,E401,E402,E701,E702
# / var

# \ tool
CURL    = curl -L -o
CF      = clang-format-11 -style=file -i
PY      = $(shell which python3)
PIP     = $(shell which pip3)
PEP     = $(shell which autopep8) --ignore=$(PEPS) --in-place
# / tool

# \ src
Y += $(MODULE).py
S += $(Y)
# / src

# \ all
all: $(PY) $(MODULE).py
	$^
	$(MAKE) tmp/format_py
# / all

# \ format
tmp/format_py: $(Y)
	$(PEP) $? && touch $@
# / format

# \ merge
MERGE  = Makefile README.md .gitignore apt.txt $(S)
MERGE += .vscode bin doc lib src tmp

dev:
	git push -v
	git checkout $@
	git pull -v
	git checkout shadow -- $(MERGE)
#	$(MAKE) doxy ; git add -f docs

shadow:
	git push -v
	git checkout $@
	git pull -v

ZIP = tmp/$(MODULE)_$(BRANCH)_$(NOW)_$(REL).src.zip
zip:
	git archive --format zip --output $(ZIP) HEAD
	$(MAKE) doxy ; zip -r $(ZIP) docs
