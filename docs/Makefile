#
# Makefile for Sphinx docs generation
#

BUILDDIR = ./_build
HTMLDIR = ${BUILDDIR}/html
ZIPFILE = ${BUILDDIR}/splunk-sdk-python-docs.zip

.PHONY: html zip
html:
	rm -rf $(BUILDDIR)
	sphinx-build -b html -d $(BUILDDIR)/doctrees . $(HTMLDIR)
	sh munge_links.sh $(HTMLDIR)
	@echo "[splunk-sdk] ---"
	@echo "[splunk-sdk] Build finished. HTML pages available at docs/$(HTMLDIR)."

zip: html
	cd $(HTMLDIR) && zip -r $(abspath $(ZIPFILE)) .
	@echo "[splunk-sdk] Zip available at docs/$(ZIPFILE)."
