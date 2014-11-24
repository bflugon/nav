mkfile_dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
top_srcdir := $(mkfile_dir)../..
name := navtest:$(shell hg parent --template '{node|short}')

.PHONY: build check

build: runtime-requirements.txt test-requirements.txt
	docker build -t $(name) $(mkfile_dir)

check: build
# Running in privileged mode because Google Chrome apparently requires it
	/usr/bin/env
	docker run --privileged -v $(top_srcdir):/source $(name) /source/tests/docker/test.sh

shell:
	docker run -t -i --privileged -v $(top_srcdir):/source $(name) /bin/bash

runtime-requirements.txt: $(top_srcdir)/requirements.txt
	cp $< $@

test-requirements.txt: $(top_srcdir)/tests/requirements.txt
	cp $< $@

name:
	echo Image name: $(name)

clean:
	rm -f runtime-requirements.txt test-requirements.txt