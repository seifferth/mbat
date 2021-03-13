all: out/mailbatch

out/mailbatch: src/main.sh src/init.sh src/prepare.py process_includes.sh
	test -d out || mkdir out
	cd src; ../process_includes.sh < main.sh \
		| grep -v '#!DEBUG-ONLY' \
		> ../out/mailbatch
	chmod +x out/mailbatch

.PHONY: clean
clean:
	rm -r out
