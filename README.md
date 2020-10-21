# Supervised SC2

This project aims to reproduce Deepmind's initial results of their supervised agent by similarly training a Convolutional Neural Network (CNN) in a supervised fashion from players Diamond 1 and better. 

## Requirements
1. Install SDL
   - Ubuntu: `apt install SDL`
   - Mac: `brew install SDL`
   - Arch Linux: [SDL2](https://www.archlinux.org/packages/extra/x86_64/sdl2/)  is on the AUR. `yay -S SDL2`

2. Install the rest of the requirements requirements `pip install -r requirements.txt`

## Steps
2. Download Starcraft II
   - Linux: Downlaod and unzip StarCraft II Linux Package [4.10.0](https://github.com/Blizzard/s2client-proto#downloads) into `~/StarCraftII`
   - Windows: Downlaod StarCraft II as you regularly would
3. Acquire replays for the game version of your choice via the `download_replays.py` script supplied. See the [replay](replay_api/README.md) for a detailed explaination for how to use this provided script.
4. Preprocess the replays
5. Parse the replays
6. Extract the features

## Dataset Overview

`todo!()`

## Dataset Usage Guide

`todo!()`
