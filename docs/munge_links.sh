#!/bin/bash

TARGET=$1

for file in $TARGET/*.html; do
    echo ${file}
    # we use perl instead of sed - macOS sed -i creates backup files, but -i '' makes it not work on Linux
    perl -i -pe 's/class="reference external"/class="reference external" target="_blank"/g' "${file}"
done
