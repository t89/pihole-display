#!/bin/bash

##
# I _think_ core has to be first, because it seems to automatically
# update everything else to the _newest_ version. Therefore we have to
# enforce the other versions afterwards
bash "./version/core-update.sh"
bash "./version/admin-update.sh"
bash "./version/ftl-update.sh"
