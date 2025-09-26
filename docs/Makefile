#
# Makefile for Sphinx docs generation
#

SPHINXBUILD = sphinx-build
BUILDDIR = ./_build
HTMLDIR = ${BUILDDIR}/html

# Internal variables
ALLSPHINXOPTS = -d $(BUILDDIR)/doctrees .

.PHONY: html
html:
	@rm -rf $(BUILDDIR)
	@$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(HTMLDIR)
	@sh munge_links.sh $(HTMLDIR)
	@echo
	@echo "Build finished. HTML pages available at docs/$(HTMLDIR)."