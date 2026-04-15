#
# Makefile for Sphinx docs generation
#

BUILDDIR = ./_build
HTMLDIR = ${BUILDDIR}/html

.PHONY: html
html:
	rm -rf $(BUILDDIR)
	sphinx-build -b html -d $(BUILDDIR)/doctrees . $(HTMLDIR)
	sh munge_links.sh $(HTMLDIR)
	@echo "[splunk-sdk] ---"
	@echo "[splunk-sdk] Build finished. HTML pages available at docs/$(HTMLDIR)."
