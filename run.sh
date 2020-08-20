#!/bin/bash
if [ "$( $1 )" == ""]; then
	echo 'Usage: ./run.sh <thread_url>'
else
	python3 thread_download.py $1
fi
