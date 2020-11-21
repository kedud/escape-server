#!/bin/bash

CURRENT_GIT_DIRECTORY=`git rev-parse --show-toplevel`
cd $CURRENT_GIT_DIRECTORY/frontend;
npm run build;