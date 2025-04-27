#!/bin/bash
find ./pages -type f -name "*.py" -print0 | while IFS= read -r -d '' file; do
  echo "Updating copyright in $file"
  sed -i 's/© [0-9]\{4\}.*All rights reserved./© 2025 Opulent Chikwiramakomo. All rights reserved./g' "$file"
done
