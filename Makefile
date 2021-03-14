all: out/mbat out/mbat.1

out/mbat: src/main.sh src/init.sh src/prepare.py process_includes.sh
	test -d out || mkdir out
	cd src; ../process_includes.sh < main.sh \
		| grep -v '#!DEBUG-ONLY' \
		> ../out/mbat
	chmod +x out/mbat

out/mbat.1: readme.md
	test -d out || mkdir out
	cat readme.md \
		| awk '/## Usage/ {output=1}; output {print}' \
		| sed 's,^## ,# ,g' \
		| pandoc -f markdown -t man --standalone \
			-M title=mbat -M section=1 \
		> out/mbat.1

.PHONY: clean
clean:
	rm -r out
