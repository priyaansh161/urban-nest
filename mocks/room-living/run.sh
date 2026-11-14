#!/bin/bash
# rebuild the single script from its parts and run a quick (no bake) build
cd "$(dirname "$0")"
cat part1b.py part2.py part3.py part4.py > build_living_v1.py
python -c "import ast;ast.parse(open('build_living_v1.py',encoding='utf8').read())" || exit 1
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b -P build_living_v1.py -- "$(pwd -W)" ${1:-quick} > quick.log 2>&1
grep -v "Deprecat\|use_nodes" quick.log | tail -${2:-15}
