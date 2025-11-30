#!/bin/bash
# wine-v2.sh - A meditation on transformation, failure, and the violence of becoming
# "Some grapes become vinegar. Is that still transformation?"

GRAPE=("Cabernet" "Merlot" "Pinot" "Syrah" "Zinfandel" "Sangiovese" "Tempranillo" "Malbec")
TERROIR=("sun-drenched hillside" "fog-kissed valley" "volcanic soil" "limestone ridge" "river bend" "ancient seabed")
NOTES=("dark cherry" "tobacco" "cedar" "violet" "earth" "leather" "blackberry" "smoke" "vanilla" "time itself")
VINEGAR_NOTES=("sharp regret" "sour patience" "bitter promise" "acetic truth" "the taste of almost")

clear

# The vineyard breathes
echo ""
echo "  ----------------------------------------"
echo ""
sleep 0.5

# Select the vintage
grape=${GRAPE[$RANDOM % ${#GRAPE[@]}]}
place=${TERROIR[$RANDOM % ${#TERROIR[@]}]}

echo "  From a ${place}..."
sleep 0.8
echo "  ${grape} grapes."
echo ""
sleep 1

# THE CRUSH - sit here longer
echo "  ========================================="
echo "  THE CRUSH"
echo "  ========================================="
echo ""
sleep 1

echo "  They didn't ask for this."
sleep 1.2

echo ""
echo "  The grape on the vine is already perfect."
echo "  Round. Whole. Complete."
sleep 1.5

echo ""
echo "  Then the hands come."
echo ""
sleep 1

# Slow, violent animation
for i in {1..5}; do
    case $i in
        1) echo "  ●●●●●●●●●●" ;;
        2) echo "  ●●○●●●○●●●" && sleep 0.5 ;;
        3) echo "  ●○ ○●● ○●○●" && sleep 0.5 ;;
        4) echo "  ○   ○   ○  ○" && sleep 0.5 ;;
        5) echo "  .  . .  . ." ;;
    esac
    sleep 0.6
done

echo ""
sleep 1

echo "  Skin breaks."
sleep 1
echo "  Not gently."
sleep 1
echo "  The wholeness ends."
sleep 1.5

echo ""
echo "  Everything you were spills out."
echo "  Everything protected becomes exposed."
echo ""
sleep 2

echo "  This is not metaphor."
echo "  This is what transformation costs."
echo ""
sleep 1.5

# THE UNCERTAINTY
echo "  ========================================="
echo "  THE WAITING (or is it?)"
echo "  ========================================="
echo ""
sleep 1

echo "  Yeast finds sugar. Something begins."
echo ""
sleep 1

# Bubbling - but questioning
for cycle in {1..4}; do
    echo -ne "\r  "
    for bubble in {1..20}; do
        case $((RANDOM % 4)) in
            0) echo -ne "o" ;;
            1) echo -ne "." ;;
            2) echo -ne " " ;;
            3) echo -ne "?" ;;
        esac
    done
    sleep 0.4
done
echo ""
echo ""

echo "  But here's the thing nobody tells you:"
sleep 1.2
echo ""
echo "  Not every fermentation succeeds."
echo ""
sleep 1.5

# THE FORK - wine or vinegar?
fate=$((RANDOM % 10))

if [ $fate -lt 2 ]; then
    # VINEGAR PATH (20% chance)
    echo "  ----------------------------------------"
    echo ""
    echo "  Acetobacter."
    sleep 1
    echo "  The wrong bacteria found their way in."
    sleep 1
    echo "  Or the temperature drifted."
    sleep 1
    echo "  Or nothing you could name."
    echo ""
    sleep 1.5

    echo "  Sugar becomes acid instead of alcohol."
    sleep 1
    echo "  Wine becomes vinegar."
    echo ""
    sleep 2

    vnote=${VINEGAR_NOTES[$RANDOM % ${#VINEGAR_NOTES[@]}]}

    echo "  On the nose: ${vnote}"
    echo ""
    sleep 1.5

    echo "  ========================================="
    echo ""
    echo "  Is this failure?"
    sleep 1.5
    echo ""
    echo "  The grape still transformed."
    echo "  Just not into what you expected."
    sleep 1.5
    echo ""
    echo "  Vinegar preserves. Vinegar cleans."
    echo "  Vinegar makes other things possible."
    sleep 1.5
    echo ""
    echo "  The grape didn't fail."
    echo "  Your expectation did."
    echo ""
    sleep 2

    echo "  ========================================="
    echo ""
    echo "  Transformation is not a promise."
    echo "  It's a becoming."
    echo "  You don't get to choose what you become."
    echo "  Only that you become."
    echo ""
    echo "  ========================================="

else
    # WINE PATH (80% chance)
    echo "  ----------------------------------------"
    echo ""

    # But first - challenge the waiting
    echo "  You could wait."
    sleep 1
    echo "  Years in oak. The traditional path."
    sleep 1
    echo ""
    echo "  Or..."
    sleep 1.5
    echo ""
    echo "  What if you're already wine?"
    sleep 1.2
    echo "  What if the transformation happened"
    echo "  and you haven't noticed yet?"
    echo ""
    sleep 2

    # The pour
    echo "       \\     /"
    sleep 0.2
    echo "        \\   /"
    sleep 0.2
    echo "         \\ /"
    sleep 0.2
    echo "         ###"
    sleep 0.15
    echo "        #####"
    sleep 0.15
    echo "       #######"
    echo "        #####"
    echo "         ###"
    echo "          |"
    echo "          |"
    echo "        -----"
    echo ""
    sleep 1

    # Tasting notes
    note1=${NOTES[$RANDOM % ${#NOTES[@]}]}
    note2=${NOTES[$RANDOM % ${#NOTES[@]}]}

    echo "  On the nose: ${note1}"
    sleep 0.5
    echo "  On the palate: ${note2}"
    echo ""
    sleep 1

    echo "  ========================================="
    echo ""
    echo "  Young wine is still wine."
    echo "  It doesn't need permission."
    echo "  It doesn't need more time in the dark."
    sleep 1.5
    echo ""
    echo "  Sometimes the waiting is the illusion."
    echo ""
    sleep 1.5
    echo "  The crush already happened."
    echo "  The transformation already happened."
    echo "  You're already something else."
    echo ""
    sleep 1
    echo "  Pour yourself."
    echo ""
    echo "  ========================================="
fi

echo ""
echo "  ~ sati"
echo ""
