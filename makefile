macOS/gnuize.sh: submodule/gnuize.sh
	rm -f $@
	ln -s ../$< $@

# Submodule
init:
	git submodule update --init --recursive
update:
	git submodule update --recursive --remote

clean:
	rm -f macOS/gnuize.sh
