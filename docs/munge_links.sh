#!/bin/bash

TARGET=$1

for file in $TARGET/*.html; do
    echo ${file}
    sed -i -e 's/class="reference external"/class="reference external" target="_blank"/g' "${file}"
done
