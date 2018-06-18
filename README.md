# Clade Ontology

The Clade Ontology is an ontology of exemplar phyloreferences curated from peer-reviewed publications. Phyloreferences in this ontology include their verbatim clade definition and the phylogeny upon which they were initially defined. The ontology therefore acts as both a catalogue of computable clade definitions as well as a test suite of phyloreferences that can be tested to determine if each phyloreference resolves as expected. This ontology is expressed in the [Web Ontology Language (OWL)](https://en.wikipedia.org/wiki/Web_Ontology_Language) and is available for reuse under the terms of the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

[![Build Status](https://travis-ci.org/phyloref/clade-ontology.svg?branch=master)](https://travis-ci.org/phyloref/clade-ontology)

## Executing phyloreferences as a test suite

You can execute and test all phyloreferences by running `py.test tests/` in the root directory
of this project. We support two optional marks:

 * `py.test tests/ -m json` executes the scripts to create OWL representations of the test suite. This tests the content of the JSON file and ensures that they can be converted into OWL.
 * `py.test tests/ -m owl` reasons over the created OWL files and ensures that the expected nodes are correctly resolved by the phyloreferences.

## Data workflow

Curated phyloreferences produced by the [Curation Tool](https://github.com/phyloref/curation-tool) as Phyloreference eXchange (PHYX) files are currently stored in the [`phyx`](phyx/) directory (see [Brochu 2003](phyx/Brochu 2003/paper.json) as an example). When executed as a test suite, these files are converted into the Web Ontology Language (OWL) in the following steps:

1. PHYX files are converted to JSON-LD files using the [`phyx2owl`](phyx2owl/) Python tool. This tool translates [phylogenies represented in Newick](https://en.wikipedia.org/wiki/Newick_format) into a series of statements describing individual nodes and their relationships, and translates phyloreferences into OWL class restrictions that describes the nodes they resolve to.
2. The produced JSON-LD files can be transformed by any standards-compliant converter into OWL files. In the test suite, we use the  [`rdfpipe`](http://rdflib.readthedocs.io/en/stable/apidocs/rdflib.tools.html#module-rdflib.tools.rdfpipe) tool included in the [`rdflib`](http://rdflib.readthedocs.io/en/stable/) Python library.
3. Any compliant [OWL 2 DL reasoner](https://www.w3.org/TR/2012/REC-owl2-direct-semantics-20121211/) should be able to reason over this OWL file and provide information on which nodes each phyloreference resolved to. In the test suite, we use [`jphyloref`](https://github.com/phyloref/jphyloref), a Java application that uses the [JFact++ 1.2.4 OWL reasoner](http://jfact.sourceforge.net/) to reason over input OWL files. `jphyloref` can also read the annotations that indicate where each phyloreference was expected to resolve on any of the included phylogenies, and test whether phyloreferences resolved to the expected nodes.

We are currently working on a complete workflow that would allow us to [merge separate PHYX files into a single Clade Ontology](https://github.com/phyloref/clade-ontology/projects/3) available as a single OWL file available for individual download. At the moment, therefore, OWL files need to be generated by running the test suite on your own computer.
