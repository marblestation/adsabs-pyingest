#!/usr/bin/env python

import sys
import json
import codecs
from adsputils import u2asc
from jats import JATSParser

class NoSchemaException(Exception):
    pass

class WrongSchemaException(Exception):
    pass

class UnparseableException(Exception):
    pass


class APSJATSParser(JATSParser):

    def get_author_init(self,namestring):
        output = u2asc(namestring)
        for c in output:
            if c.isalpha():
                return c
        return u'.'

    def aps_journals(self, pid):
#       mapping journal-meta/journal-id/publisher-id to bibstems
        publisher_ids = {'PRL': 'PhRvL', 'PRX': 'PhRvX', 'RMP': 'RvMP',
                         'PRA': 'PhRvA', 'PRB': 'PhRvB', 'PRC': 'PhRvC',
                         'PRD': 'PhRvD', 'PRE': 'PhRvE', 'PRAB': 'PhRvS',
                         'PRSTAB': 'PhRvS', 'PRAPPLIED': 'PhRvP',
                         'PRFLUIDS': 'PhRvF', 'PRMATERIALS': 'PhRvM', 
                         'PRPER': 'PRPER', 'PRSTPER': 'PRSTP', 'PR': 'PhRv',
                         'PRI': 'PhRvI','PHYSICS': 'PhyOJ'}
        try:
            bibstem = publisher_ids[pid]
        except KeyError:
            return 'XSTEM'
        else:
            return bibstem

#   def make_journal_field

    def doi_parse(self, doi):
        doi_string = doi[4:].split('/')[1]
        doi_array = doi_string.split('.')
        vol , idsix = doi_array[1], doi_array[2]
        vol = vol.rjust(4,'.')
        if len(idsix) == 6:
            idtwo = chr(96+int(idsix[0:2]))
            idfour = idsix[2:]
        else:
            idtwo = ''
            idfour = idsix.rjust(5,'.')
        return vol, idtwo + idfour
        

    def parse(self, fp, **kwargs):

        output_metadata = super(self.__class__, self).parse(fp, **kwargs)


# Bibcode
        try:
            j_bibstem = self.aps_journals(output_metadata['pub-id'])
        except KeyError:
            pass
        else:
            year = output_metadata['pubdate'][0:4]
            bibstem = j_bibstem.ljust(5,'.')
            volume, idno = self.doi_parse(output_metadata['properties']['DOI'])
            try:
                author_init = self.get_author_init(output_metadata['authors'][0])
            except:
                author_init = '.'
            output_metadata['bibcode'] = year + bibstem + volume + idno + author_init
            del output_metadata['pub-id']


# Publication +
        try:
            pubstring = output_metadata['publication']
        except:
            pass
        else:
            try:
                output_metadata['volume']
            except:
                pass
            else:
                pubstring = pubstring +', Volume '+ output_metadata['volume']
            
            try:
                pubstring = pubstring +', Issue '+ output_metadata['issue']
            except TypeError:
                pass
            
            try:
                output_metadata['page']
            except:
                pass
            else:
                pubstring = pubstring +', id.'+ output_metadata['page']

            output_metadata['publication'] = pubstring
            
# Return
        return output_metadata
# 
# 
#if __name__ == "__main__":
# 
#    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
#    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
# 
#    jatsx = APSJATSParser()
# 
#    with open('/Users/mtempleton/adsaps.work/fulltext.xml','rU') as fp:
#        woo = jatsx.parse(fp)
# 
#    print(woo)
