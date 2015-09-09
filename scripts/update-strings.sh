#!/bin/bash
LOCALES=$*

  # Get newest .py files so we don't update strings unnecessarily
PYTHON_FILES=`ls . | grep -E '.py$|.ui$'`
echo ${PYTHON_FILES}
# update .ts
echo "Please provide translations by editing the translation files below:"
for LOCALE in ${LOCALES}
do
  echo "i18n/"${LOCALE}".ts"
  # Note we don't use pylupdate with qt .pro file approach as it is flakey
  # about what is made available.
  pylupdate4 -noobsolete ${PYTHON_FILES} -ts i18n/${LOCALE}.ts
done
