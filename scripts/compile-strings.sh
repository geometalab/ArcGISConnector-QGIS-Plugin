#!/bin/bash
LOCALES=$*

for LOCALE in ${LOCALES}
do
    echo "Processing: ${LOCALE}.ts"
    # Note we don't use pylupdate with qt .pro file approach as it is flakey
    # about what is made available.
    lrelease i18n/${LOCALE}.ts
done
