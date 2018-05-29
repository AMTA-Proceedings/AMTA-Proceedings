all: W18-18.xml W18-20.xml W18-21.xml W18-22.xml 


%.xml: tsv/%.tsv scripts/create_anthology_xml.py
	scripts/create_anthology_xml.py tsv/$*.tsv $* $*.xml bib AMTA


