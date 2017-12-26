SRC_FILES = $(wildcard src/*.md)
OUT_HTML = $(patsubst src/%.md,docs/%.html,$(SRC_FILES))
OUT_PDF = $(patsubst src/%.md,docs/%.pdf,$(SRC_FILES))

FLAGS = --filter bridge.py
HTML_FLAGS = $(FLAGS) -H base.html
PDF_FLAGS = $(FLAGS) -H bridge-header.tex

all: web pdf

web: $(OUT_HTML)
pdf: $(OUT_PDF)

docs/%.html: src/%.md
	pandoc $< $(HTML_FLAGS) -o $@

docs/%.pdf: src/%.md
	pandoc $< $(PDF_FLAGS) -o $@

clean:
	rm -f $(OUT_HTML) $(OUT_PDF)
