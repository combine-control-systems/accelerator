SHELL := /bin/bash
FIGURES    := $(wildcard *.fig)
FIGSVG     := $(patsubst %.fig,%.svg,$(FIGURES))

.PHONY: .fig

fig:    $(FIGSVG)

%.svg:	%.fig
	fig2dev -L svg  $< $@

clean:
	rm *.svg
