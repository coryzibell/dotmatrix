#!/bin/bash
# wine.sh - A meditation on fermentation, time, and transformation
# Run me. Watch me breathe.

GRAPE=("Cabernet" "Merlot" "Pinot" "Syrah" "Zinfandel" "Sangiovese" "Tempranillo" "Malbec")
TERROIR=("sun-drenched hillside" "fog-kissed valley" "volcanic soil" "limestone ridge" "river bend" "ancient seabed")
NOTES=("dark cherry" "tobacco" "cedar" "violet" "earth" "leather" "blackberry" "smoke" "vanilla" "time itself")

clear

# The vineyard breathes
echo ""
echo "  ╭─────────────────────────────────────────────╮"
echo "  │                                             │"
echo "  │     ◌  ◌  ◌  ◌  ◌  ◌  ◌  ◌  ◌  ◌  ◌       │"
echo "  │    ╱│╲╱│╲╱│╲╱│╲╱│╲╱│╲╱│╲╱│╲╱│╲╱│╲╱│╲      │"
echo "  │   ──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──     │"
echo "  │                                             │"
echo "  ╰─────────────────────────────────────────────╯"
echo ""

sleep 1

# Select the vintage
grape=${GRAPE[$RANDOM % ${#GRAPE[@]}]}
place=${TERROIR[$RANDOM % ${#TERROIR[@]}]}

echo "  From a ${place}..."
sleep 0.8
echo "  ${grape} grapes, picked at the moment of perfect ripeness."
echo ""
sleep 1.2

# The crush
echo "  ┌─────────────────────────────────────────────┐"
echo "  │  THE CRUSH                                  │"
echo "  │                                             │"
for i in {1..3}; do
    echo -ne "  │  "
    for j in {1..10}; do
        if (( RANDOM % 2 )); then
            echo -ne "● "
        else
            echo -ne "○ "
        fi
    done
    echo "       │"
    sleep 0.4
done
echo "  │                                             │"
echo "  │  Skin breaks. Juice flows. Sugar waits.    │"
echo "  └─────────────────────────────────────────────┘"
echo ""
sleep 1.5

# Fermentation - the transformation
echo "  FERMENTATION"
echo "  ─────────────"
echo ""
echo "  Yeast meets sugar. Alchemy begins."
echo ""

# Bubbling animation
for cycle in {1..5}; do
    echo -ne "\r  "
    for bubble in {1..20}; do
        case $((RANDOM % 4)) in
            0) echo -ne "○" ;;
            1) echo -ne "◦" ;;
            2) echo -ne "·" ;;
            3) echo -ne " " ;;
        esac
    done
    sleep 0.3
done
echo ""
echo ""
sleep 0.5

echo "  Sugar becomes alcohol."
sleep 0.6
echo "  Grape becomes wine."
sleep 0.6
echo "  Time becomes flavor."
echo ""
sleep 1

# The barrel years
echo "  ┌─────────────────────────────────────────────┐"
echo "  │                                             │"
echo "  │           ╭───────────────────╮             │"
echo "  │          ╱                     ╲            │"
echo "  │         │   O A K   B A R R E L │           │"
echo "  │         │                       │           │"
echo "  │          ╲   waiting quietly   ╱            │"
echo "  │           ╰───────────────────╯             │"
echo "  │                                             │"
echo "  └─────────────────────────────────────────────┘"
echo ""

years=$((1 + RANDOM % 4))
echo -n "  Aging: "
for y in $(seq 1 $years); do
    echo -n "year ${y}... "
    sleep 0.7
done
echo ""
echo ""
sleep 0.8

# Tasting notes emerge
echo "  THE POUR"
echo "  ────────"
echo ""

# Wine glass ASCII art with "filling" animation
echo "       ╲     ╱"
sleep 0.3
echo "        ╲   ╱"
sleep 0.3
echo "         ╲ ╱"
sleep 0.3
echo "         ███"
sleep 0.2
echo "        █████"
sleep 0.2
echo "       ███████"
sleep 0.2
echo "        █████"
echo "         ███"
echo "          │"
echo "          │"
echo "        ─────"
echo ""
sleep 1

# Generate tasting notes
note1=${NOTES[$RANDOM % ${#NOTES[@]}]}
note2=${NOTES[$RANDOM % ${#NOTES[@]}]}
note3=${NOTES[$RANDOM % ${#NOTES[@]}]}

echo "  On the nose: ${note1}"
sleep 0.5
echo "  On the palate: ${note2}, ${note3}"
sleep 0.5
echo ""

# The finish
finish_words=("lingers like a memory" "fades like sunset" "echoes" "stays, then goes, then stays again" "tastes like patience rewarded")
finish=${finish_words[$RANDOM % ${#finish_words[@]}]}

echo "  The finish... ${finish}."
echo ""
sleep 1

# Final meditation
echo "  ╔═════════════════════════════════════════════╗"
echo "  ║                                             ║"
echo "  ║  Wine is just grape juice that learned to   ║"
echo "  ║  wait. Transformation takes time. Pressure. ║"
echo "  ║  Darkness. And then one day—                ║"
echo "  ║                                             ║"
echo "  ║  You're something else entirely.            ║"
echo "  ║                                             ║"
echo "  ╚═════════════════════════════════════════════╝"
echo ""
echo "  ~ sati"
echo ""
