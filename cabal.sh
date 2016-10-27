#!/bin/bash

cabal install --force-reinstalls pandoc
cabal install --force-reinstalls pandoc-citeproc
cabal install --force-reinstalls --allow-newer=base pandoc-csv2table
cabal install --force-reinstalls -f inlineMarkdown pandoc-placetable
