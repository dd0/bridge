all: docs/index.html docs/ehaa.html docs/defence.html docs/transfer.html docs/weaktwo.html docs/ubc.html

docs/%.html: src/%.md
	pandoc $< --filter bridge.py -H base.html -o $@

clean:
	rm docs/*.html
