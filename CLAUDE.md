# Purpose
We are building an ontology that will guide development of an open data format platform where common data classes can be leveraged by different stakeholders to build applications

## How it is used
The vocabulary will be primarily imported into protege ontology editor to get the structure right

we are also using our code editor (neovim in our example) to edit the ontology by hand so feel free to use that to review and make structured edits

# Overview
We are using OWL 2 with a scoping for a productivity app

the intention is that we will use this ontology as well as the SHACL structure to generate scaffolding such as:
- tree sitter parsers
- database schemas
- data schema for json
- class generation on static typing languages

to this point we are trying to capture semantic meaning here while also importing enough context that the implementors can take this work one at a time

## Key Files
- README.md covers the concepts in a plaintext format
- actions-vocabulary.ttl is the ontology itself and is the primary unit of work
- action-shapes.ttl is a SHACL file that actually holds the complimentary SHACL constraints needed to function properly

# Testing
Constraints testing is done with the `pySHACL` library where we have a few example tests that can be run with the bash script inside of the `tests` folder
