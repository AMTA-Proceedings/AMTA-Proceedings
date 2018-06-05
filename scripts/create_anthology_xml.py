#!/usr/bin/env python3

import errno
import os
import re
import sys

class Author:

    def __init__(self, full_name):
        self.full_name = full_name.strip()
        self.parts = self.full_name.split(" ")
        self.first_name = self.parts[0]
        self.last_name  = self.parts[-1]

    def xml_string(self, leading_tabs=2):
        tabs="\t"*leading_tabs
        s = tabs + "<author>\n" + \
            tabs + "\t<first>" + self.first_name + "</first>\n" + \
            tabs + "\t<last>"  + self.last_name  + "</last>\n" + \
            tabs + "</author>\n"
        return s
    
    def bib_string(self):
        return self.last_name + ", " + self.first_name
    
    def __repr__(self):
        return "Author(" + self.first_name + " " + self.last_name + ")"
    
class Entry:

    @staticmethod
    def from_line(acronym, line):
        parts=line.rstrip("\n").split("\t")
        if len(parts) == 11:
            bibtype   = parts[0]
            if bibtype=="none" or bibtype.strip()=="":
                bibtype=""
            authors   = [Author(name) for name in parts[1].split(";")] if parts[1] and len(parts[1].strip()) > 0 else []
            title     = parts[2]
            booktitle = parts[3]
            month     = parts[4]
            year      = parts[5]
            address   = parts[6]
            publisher = parts[7]
            pages     = parts[8]
            url       = parts[9]
            paperID   = re.sub("^.*-", "", url)
            note      = parts[10]
            if note=="none" or note.strip()=="":
                note=""
            return Entry(bibtype, authors, title, booktitle, month, year, address, publisher, pages, url, note, paperID, acronym)
        else:
            raise(ValueError("WARNING:\tLine should contain 10 columns, but contains " + len(parts)+"\t"+line))
            
    def __init__(self, bibtype, authors, title, booktitle, month, year, address, publisher, pages, url, note, paperID, acronym):
        self.bibtype   = bibtype
        self.authors   = authors
        self.title     = title
        self.booktitle = booktitle
        self.month     = month
        self.year      = year
        self.address   = address
        self.publisher = publisher
        self.pages     = pages
        self.url       = url
        self.note      = note
        self.paperID   = paperID
        self.acronym   = acronym
        if self.authors and len(self.authors) > 0:
            self.bibkey = "-".join([author.last_name for author in authors]) + ":"
        else:
            self.bibkey = ""
        self.bibkey += year + ":" + acronym

    def xml_string(self, leading_tabs=1):
        tabs="\t"*leading_tabs
        s=tabs+'<paper id="'+self.paperID+'">\n'
        if self.title and len(self.title) > 0:
            s += tabs+'\t<title>'+self.title+'</title>\n'
        if self.authors and len(self.authors) > 0:
            s += ''.join([author.xml_string(leading_tabs=leading_tabs+1) for author in self.authors])
        if self.booktitle and len(self.booktitle) > 0:
            s += tabs+"\t<booktitle>" + self.booktitle + "</booktitle>\n"
        if self.publisher and len(self.publisher) > 0:
            s += tabs+"\t<publisher>" + self.publisher + "</publisher>\n"
        if self.pages and len(self.pages) > 0:
            s += tabs+"\t<pages>"     + self.pages     + "</pages>\n"
        if self.url and len(self.url) > 0:
            s += tabs+"\t<url>"       + self.url       + "</url>\n"
        if self.bibtype and len(self.bibtype) > 0:
            s += tabs+"\t<bibtype>"   + self.bibtype   + "</bibtype>\n"
        if self.bibkey and len(self.bibkey) > 0:
            s += tabs+"\t<bibkey>"     + self.bibkey    + "</bibkey>\n"
        s += tabs+"</paper>\n"
        return s

    def bib_string(self):
        s='@' + self.bibtype + "{" + self.bibkey + ",\n"
        if self.authors and len(self.authors) > 0:
            s += "\tauthor = {" + ' and '.join([author.bib_string() for author in self.authors]) + "}\n"
        if self.title and len(self.title) > 0:
            s += '\ttitle = {'+self.title+'},\n'
        if self.booktitle and len(self.booktitle) > 0:
            s += "\tbooktitle = {" + self.booktitle + "},\n"
        if self.publisher and len(self.publisher) > 0:
            s += "\tpublisher = {" + self.publisher + "},\n"
        if self.pages and len(self.pages) > 0:
            s += "\tpages = {"     + self.pages     + "},\n"
        if self.address and len(self.address) > 0:
            s += "\taddress = {"     + self.address     + "},\n"
        if self.year and len(self.year) > 0:
            s += "\tyear = {"     + self.year     + "},\n"
        if self.month and len(self.month) > 0:
            s += "\tmonth = {"     + self.month     + "},\n"
        if self.url and len(self.url) > 0:
            s += "\turl = {"       + self.url       + "},\n"
        s += "}\n"
        return s
          
          
class Volume:

    @staticmethod
    def from_tsv(volumeID, acronym, filename):
        entries = []
        with open(tsv_filename) as tsv_file:
            read_header=False
            for line in tsv_file:
                if not read_header:
                    read_header=True
                else:
                    entry = Entry.from_line(acronym, line)
                    entries.append(entry)
        return Volume(volumeID, entries)

    def __init__(self, volumeID, entries):
        self.volumeID = volumeID
        self.entries  = entries

    def __iter__(self):
        return self.entries.__iter__()

    def __len__(self):
        return len(self.entries)

    def xml_string(self):
        s  = '<volume id="' + self.volumeID + '">\n'
        for entry in self.entries:
            s += entry.xml_string(leading_tabs=1)
        s += '</volume>\n'
        return s

    def bib_string(self):
        s = "\n".join([entry.bib_string() for entry in self.entries])
        return s


if __name__=="__main__":


    if len(sys.argv) != 6:
        print("Usage:\t"+sys.argv[0]+" 20XX/your.tsv volumeID output.xml output_bib_dir acronym", file=sys.stderr)
        exit(-1)

    tsv_filename = sys.argv[1]
    volumeID = sys.argv[2]
    output_xml_filename = sys.argv[3]
    output_bibdir = sys.argv[4]
    acronym = sys.argv[5]

    volume = Volume.from_tsv(volumeID, acronym, tsv_filename)
    print("Read " + str(len(volume)) + " entries from " + tsv_filename, file=sys.stderr)

    print("Writing XML file data to " + output_xml_filename, file=sys.stderr)
    with open(output_xml_filename, "w") as output_xml_file:
        print(volume.xml_string(), file=output_xml_file)
    
    try:
        os.makedirs(output_bibdir)    
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
    
    prefix = re.sub("-.*$", "", volumeID)
    for entry in volume:
        output_bib_filename=os.path.join(output_bibdir, prefix + "-" + entry.paperID + ".bib")
        with open(output_bib_filename , "w") as output_bib_file:
            print("Writing bibTeX file data to " + output_bib_filename, file=sys.stderr)
            print(entry.bib_string(), file=output_bib_file)

    output_bib_filename=os.path.join(output_bibdir, volumeID + ".bib")
    with open(output_bib_filename , "w") as output_bibs_file:
        print("Writing bibTeX file data to " + output_bib_filename, file=sys.stderr)
        print(volume.bib_string(), file=output_bibs_file)
