#!/usr/bin/python
# -*- coding: latin-1 -*-

import configparser
import xml.etree.ElementTree as ET, os, sys, glob, re
import logging
from optparse import OptionParser
from datetime import datetime
from datetime import timedelta
import csv
from xml_config import *

# Get script current directory
scriptDir = os.path.dirname(os.path.abspath(__file__))


# Parse command line arguments
parser = OptionParser()
parser.add_option("-i", "--input", dest="infile",
                  help="Input file containing NAME,WID,Drill-down path", metavar="FILE")
parser.add_option("-n", "--name", dest="outfile",
                  help="Specify output xml file name, default name: gen-lib", metavar="FILE", default="gen-lib.xml")
parser.add_option("-m", "--mode", dest="mode", default="normal",
                  help="Specify mode : normal or temporal, default: normal")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="debug", default=False,
                  help="Enable debug mode")


(options, args) = parser.parse_args()


#Initiate logger
logging.basicConfig(filename='adhoc_generator.log', format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logging.info('Starting adhoc_generator...')


# MAIN
if __name__ == '__main__':
    # Enable debug if option -v is specified
    if ( options.debug ) : debug = True
    else : debug = False

    if options.outfile == "gen-lib.xml":
        libname = options.outfile.split(".")[0]
    else:
        libname = options.outfile
        outfile = options.outfile+".xml"

    logging.info('Building XML tree root...')
    tree = gen_xml_tree_root(libname)
    logging.info('Building XML header...')

    gen_xml_tree_header(tree)
    # Generate the adhoc header and return root tag <AdhocModel>
    logging.info('Building XML adhoc header...')
    col_root = gen_adhoc_header(tree)

    col_ct = 1
    succ_ct = 0
    with open(options.infile) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        logging.info('Building XML columns...')
        cmt_regex = ['^#.*', '^\ *$', '^\*', '^\*+']
        j = 0
        logging.info('Reading input file...')
        for row in readCSV:
            comment = False
            if len(row) == 0:
                j += 1
                comment = True
            else:
                for reg in cmt_regex:
                    if re.match(reg, row[0]):
                        if debug:
                            logging.debug("CSV Row "+str(j)+"skipped")
                        j += 1
                        comment = True
                        break
            if comment:
                continue
            else:
                order = "none"
                try:
                    try:
                        order = row[4]
                        threshold_list = []
                        pos = 5
                        threshold_list.append(row[pos])
                        while True:
                            try:
                                threshold_list.append(row[pos+1])
                                pos += 1
                            except IndexError:
                                if debug:
                                    logging.debug(str(pos-4)+" threshold processed")
                                break
                    except IndexError:
                        if debug: logging.debug("No threshold for line: " + row[0])
                    if order != "none" and len(threshold_list) > 0:
                        gen_xml_column_data(col_root, col_ct, row[0], row[1], row[2], row[3], order, threshold_list)
                    else:
                        gen_xml_column_data(col_root, col_ct, row[0], row[1], row[2], row[3])
                    succ_ct += 1
                except IndexError:
                    logging.error("Wrong number of columns on row: "+row[0])
                except:
                    logging.error("Unknown exception while reading line")
                    sys.exit(0)
                col_ct += 1

    logging.info('Successfully generated columns: '+str(succ_ct*100/(col_ct-1))+"% ("+str(succ_ct)+"/"+str(col_ct-1)+") on total processed lines: "+str(col_ct-1))

    logging.info('Building XML footer...')
    gen_xml_footer(tree)
    logging.info('Writing XML to file: '+outfile)
    ET.ElementTree(tree).write(outfile, encoding="utf-8", xml_declaration=True)

