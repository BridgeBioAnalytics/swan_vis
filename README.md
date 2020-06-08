# Swan

![](.gitbook/assets/swan_logo.png)

Swan is a Python library designed for the analysis and visualization of transcriptomes, especially with long-read transcriptomes in mind. Users can merge transcriptomes from different datasets and explore transcript models distict splicing and expression patterns across datasets.

## What can Swan do?

Swan can make informative plots, find differentially expressed genes and transcripts, find isoform-switching genes, and discover novel exon skipping and intron retention events.

## Installation

Swan can be installed directly from PyPi. To install Swan's most recent release, run

`pip install swan_vis`

Alternatively, the most recent commits can be installed by git cloning this repo, moving to the swan\_vis directory, and running

`pip install .`

After installation with pip, to enable visualizations using dashed edges, run the following command from anywhere in the terminal

`swan_patch_networkx`

## Tutorials

* [Getting started](tutorials/getting_started.md): how to load data into Swan
* [Visualization tools](tutorials/visualization.md): make gene and transcript-level plots to visualize the complexity of alternative splicing
* [Analysis tools](tutorials/analysis_tools.md): find differentially expressed genes and transcripts; find isoform-switching genes, discover novel intron retention and exon skipping events

## Wiki links

* [Understanding Swan visualizations](https://github.com/fairliereese/swan_vis/wiki/Understanding-Swan-visualizations)
* [Input file format specifications](https://github.com/fairliereese/swan_vis/wiki/File-format-specifications)

Logo by the wonderful [Eamonn Casey](https://www.instagram.com/designsbyeamonn/)

