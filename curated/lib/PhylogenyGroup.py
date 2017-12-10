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


class PhylogenyGroup(object):
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
        additional_node_properties = dict()
        if 'additional_node_properties' in json:
            additional_node_properties = phylogeny_group.read_additional_node_properties(json['additional_node_properties'])

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

            phylogeny_group.phylogenies.append(Phylogeny(phylogeny_id, tree, additional_node_properties))

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

    def read_additional_node_properties(self, node_properties):
        """ Read labeled node data with phylogenies in this phylogeny group. """

        labeled_node_data = dict()

        for label in node_properties:
            labeled_node_data[label] = node_properties[label]

        return labeled_node_data
