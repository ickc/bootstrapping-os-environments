macOS/gnuize.sh: submodule/gnuize.sh
	ln -s $< $@

# Submodule
init:
	git submodule update --init --recursive
update:
	git submodule update --recursive --remote

clean:
	rm -f macOS/gnuize.sh
