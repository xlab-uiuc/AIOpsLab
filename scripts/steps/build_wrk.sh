#!/bin/sh
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.


print_step 5 "Building 'wrk2' tool"
echo

WRK_DIR="$AIOPSLAB_ROOT/TargetMicroservices/wrk2"
ORIGINAL_DIR=$(pwd)

if [ -d "$WRK_DIR" ]; then
    echo "   Found wrk2 directory at $WRK_DIR"
    cd "$WRK_DIR"
    echo "   Running 'make' to build wrk2..."
    if make > /dev/null 2>&1; then
        printf "   'wrk2' built successfully."
        print_result 0

        # Export WRK_DIR to PATH
        export PATH="$WRK_DIR:$PATH"
        printf "   Exported '$WRK_DIR' to PATH."
    else
        print_result 1
        printf "${RED}   Failed to build 'wrk2'.${NC}"
        safe_exit 1
    fi
else
    print_result 1
    printf "${RED}   Directory '$WRK_DIR' does not exist.${NC}"
    safe_exit 1
fi

# Restore the original directory
cd "$ORIGINAL_DIR" || safe_exit 1
echo "   Returned to original directory: $ORIGINAL_DIR"
echo
