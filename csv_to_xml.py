##### TODO: 
	# use xml or json to store data
	# instead of 'M' or 'F' as the binary- write function/class to enable user to indicate
	# which variable they want as the binary
	# ALSO: what if instead of having discrete values such as 'M', 'F', we have continuous
	# values (i.e. score)

# Convert excel file to xml
import csv, sys, os
from lxml import etree

def convert_file(csv_name, xml_name):
    csvFile = csv_name
    xmlFile = open(xml_name, 'w')
    csvData = csv.reader(open(csvFile), delimiter=',')

    header = csvData.next()
    counter = 0
    root = etree.Element('root')

    for row in csvData:
        prod = etree.SubElement(root,'prod')
        for index in range(0, len(header)):
            child = etree.SubElement(prod, header[index])
            child.text = row[index].decode('utf-8')
            prod.append(child)

    result = etree.tostring(root, pretty_print=True)
    xmlFile.write(result)

if __name__ == '__main__':
    convert_file('data/brain_data.csv', 'data/brain_data.xml')