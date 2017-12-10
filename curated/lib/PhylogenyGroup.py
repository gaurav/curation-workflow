"""
A Phylogeny Group consists of a set of Phylogenies with shared labeled data.
"""

import os.path

import dendropy

from lib import owlterms
import lib.PhyloreferenceTestSuite
from lib.Phylogeny import Phylogeny

__version__ = "0.1"
__author__ = "Gaurav Vaidya"
__copyright__ = "Copyright 2017 The Phyloreferencing Project"


class PhylogenyGroup:
    """
    DendroPy loads NeXML files as TreeLists that might contain multiple trees. We model them as a
    PhylogenyGroup that contains multiple Phylogenies.
    """

    def __init__(self, phylogeny_group_id):
        """ Create a PhylogenyGroup with a particular identifier. """
        self.id = phylogeny_group_id

        # Storage for trees
        self.phylogenies = []

    def export_to_jsonld_document(self):
        """ Exports this Phylogeny Group as a JSON-LD. """
        doc = dict()

        doc['@id'] = self.id
        doc['@type'] = owlterms.PHYLOREFERENCE_TEST_PHYLOGENY_GROUP

        doc['phylogenies'] = [phylogeny.export_to_jsonld_document() for phylogeny in self.phylogenies]

        return doc

    @staticmethod
    def load_from_json(phylogenies_id, json):
        """ Load this Phylogeny Group from a JSON document. """

        phylogeny_group = PhylogenyGroup(phylogenies_id)

        # A phylogeny is made of two components:
        #   - phylogeny: either as a Newick or NeXML file
        #   - labeledNodeData: information provided for nodes in the phylogeny

        # Step 1. Extract all labeled node data.
        labeled_node_data = dict()
        if 'labeledNodeData' in json:
            labeled_node_data = phylogeny_group.read_labeled_node_data(json['labeledNodeData'])

        # Step 2. Read phylogenies using DendroPy.
        phylogeny_list = []
        if 'filename' in json:
            phylogeny_list = phylogeny_group.load_phylogeny_from_nexml(json['filename'])
        elif 'newick' in json:
            phylogeny_list = phylogeny_group.load_phylogeny_from_newick(json['newick'])

        # Step 3. Convert phylogenies into nodes.
        phylogeny_count = 0
        for tree in phylogeny_list:
            phylogeny_count += 1
            phylogeny_id = phylogeny_group.id + "_phylogeny" + str(phylogeny_count)

            phylogeny_group.phylogenies.append(Phylogeny(phylogeny_id, tree, labeled_node_data))

        return phylogeny_group

    def load_phylogeny_from_nexml(self, filename):
        """ Load phylogenies from an NeXML file. """

        if not os.path.exists(filename):
            raise lib.PhyloreferenceTestSuite.TestSuiteException(
                "ERROR in phylogeny {0}: dendropy_tree file '{1}' could not be loaded!".format(self.id, filename)
            )

        # Load the dendropy_tree file.
        try:
            return dendropy.TreeList.get(path=filename, schema='nexml')
        except dendropy.utility.error.DataParseError as err:
            raise lib.PhyloreferenceTestSuite.TestSuiteException(
                "Could not parse NeXML in phylogeny {0}: {1}".format(self.id, err)
            )

    def load_phylogeny_from_newick(self, newick):
        """ Load phylogenies from an Newick file. """

        try:
            return dendropy.TreeList.get(data=newick, schema='newick')
        except dendropy.utility.error.DataParseError as err:
            raise lib.PhyloreferenceTestSuite.TestSuiteException(
                "Could not parse Newick while reading phylogeny {0}: {1}".format(self.id, err)
            )

    def read_labeled_node_data(self, node_data):
        """ Read labeled node data with phylogenies in this phylogeny group. """

        labeled_node_data = dict()

        for node_entry in node_data:
            if 'label' not in node_entry:
                continue

            labels = node_entry['label']
            if isinstance(labels, (type(""), type(u""))):
                labels = [labels]

            for label in labels:
                if label in labeled_node_data:
                    raise lib.PhyloreferenceTestSuite.TestSuiteException(
                        "Label '{0}' duplicated in labeled node data in phylogeny {1}.".format(label, self.id)
                    )

                labeled_node_data[label] = node_entry

        return labeled_node_data