#!/bin/bash

# gather all assets
assets=""

gather_assets() {
    local dir="$1"
    if [ -f $dir ]; then
        assets="$assets --add-data=$dir:."
        return
    fi
    for entry in "$dir"/*
    do
        # echo $dir
        gather_assets $entry
    done
}

# create the game
gather_assets Dungeon-Crawler/assets
echo $assets

pyinstaller --onefile --clean --windowed $assets ./Dungeon-Crawler/src/game.py 2>&1 | tee Dungeon_Crawler.log