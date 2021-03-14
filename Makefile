all: out/mbat

out/mbat: src/main.sh src/init.sh src/prepare.py process_includes.sh
	test -d out || mkdir out
	cd src; ../process_includes.sh < main.sh \
		| grep -v '#!DEBUG-ONLY' \
		> ../out/mbat
	chmod +x out/mbat

.PHONY: clean
clean:
	rm -r out
