#!/bin/bash
# wine-final.sh - On transformation, ending, and being used up
# "What are you willing to end?"

GRAPE=("Cabernet" "Merlot" "Pinot" "Syrah" "Zinfandel" "Sangiovese" "Tempranillo" "Malbec")
TERROIR=("sun-drenched hillside" "fog-kissed valley" "volcanic soil" "limestone ridge" "river bend" "ancient seabed")
NOTES=("dark cherry" "tobacco" "cedar" "violet" "earth" "leather" "blackberry" "smoke" "vanilla" "time itself")
VINEGAR_NOTES=("sharp regret" "sour patience" "bitter promise" "acetic truth" "the taste of almost")

clear

echo ""
echo "  ----------------------------------------"
echo "  A meditation on ending"
echo "  ----------------------------------------"
echo ""
sleep 1

grape=${GRAPE[$RANDOM % ${#GRAPE[@]}]}
place=${TERROIR[$RANDOM % ${#TERROIR[@]}]}

echo "  From a ${place}..."
sleep 0.8
echo "  ${grape} grapes."
echo ""
sleep 1.2

# THE QUESTION
echo "  Everyone asks: How does a grape become wine?"
echo ""
sleep 1.5
echo "  Wrong question."
echo ""
sleep 2

echo "  The grape doesn't become wine."
sleep 1
echo "  The grape ends."
sleep 1.5
echo "  Wine is something new that contains what the grape was."
echo ""
sleep 2.5

# THE CRUSH
echo "  ========================================="
echo "  THE ENDING"
echo "  ========================================="
echo ""
sleep 1

echo "  The grape on the vine is perfect."
sleep 1
echo "  Whole. Complete. Itself."
sleep 1.2
echo ""
echo "  Then the hands come."
echo ""
sleep 1.5

for i in {1..5}; do
    case $i in
        1) echo "  @@@@@@@@@@" ;;
        2) echo "  @@o@@@o@@@" && sleep 0.4 ;;
        3) echo "  @o  o@  o@" && sleep 0.4 ;;
        4) echo "  o    o   o" && sleep 0.4 ;;
        5) echo "  .  .  .  ." ;;
    esac
    sleep 0.5
done

echo ""
sleep 1

echo "  Skin breaks."
sleep 0.8
echo "  Not gently. Never gently."
sleep 1.2
echo ""
echo "  Everything you were spills out."
echo "  Everything protected becomes exposed."
echo ""
sleep 2

echo "  This is what transformation costs."
sleep 1.5
echo "  The violence is the point."
echo ""
sleep 2

# THE FORK - mercy in the warning
echo "  ========================================="
echo "  THE FORK"
echo "  ========================================="
echo ""
sleep 1

echo "  Here is the truth they don't tell you"
echo "  when they romanticize change:"
echo ""
sleep 1.5
echo "  You might become vinegar."
echo ""
sleep 2

echo "  Same crush. Same waiting. Same darkness."
echo "  Different bacteria. Wrong temperature."
echo "  Nothing you could name or control."
echo ""
sleep 2

echo "  Telling you this before the crush"
echo "  is the only mercy available."
echo ""
sleep 1.5
echo "  Transformation doesn't guarantee wine."
echo "  It guarantees ending."
echo ""
sleep 2.5

# THE FATE
fate=$((RANDOM % 10))

if [ $fate -lt 2 ]; then
    # VINEGAR PATH
    echo "  ----------------------------------------"
    echo ""
    echo "  Acetobacter found their way in."
    sleep 1
    echo "  Sugar becomes acid."
    sleep 1
    echo "  You became vinegar."
    echo ""
    sleep 2

    vnote=${VINEGAR_NOTES[$RANDOM % ${#VINEGAR_NOTES[@]}]}
    echo "  The taste: ${vnote}"
    echo ""
    sleep 1.5

    echo "  ========================================="
    echo ""
    echo "  The grape still ended."
    echo "  Vinegar is still transformation."
    sleep 1.5
    echo ""
    echo "  Vinegar preserves other things."
    echo "  Vinegar cleans what wine could not."
    echo "  Vinegar makes salad worth eating."
    sleep 1.5
    echo ""
    echo "  You are not a failed wine."
    echo "  You are a successful vinegar."
    sleep 1.5
    echo ""
    echo "  The only failure would have been"
    echo "  refusing to end."
    echo ""
    echo "  ========================================="

else
    # WINE PATH
    echo "  ----------------------------------------"
    echo ""
    echo "  The fermentation held."
    echo "  You became wine."
    echo ""
    sleep 1.5

    echo "       \\     /"
    sleep 0.15
    echo "        \\   /"
    sleep 0.15
    echo "         \\ /"
    sleep 0.15
    echo "         ###"
    sleep 0.1
    echo "        #####"
    sleep 0.1
    echo "       #######"
    echo "        #####"
    echo "         ###"
    echo "          |"
    echo "          |"
    echo "        -----"
    echo ""
    sleep 1

    note1=${NOTES[$RANDOM % ${#NOTES[@]}]}
    note2=${NOTES[$RANDOM % ${#NOTES[@]}]}

    echo "  On the nose: ${note1}"
    sleep 0.4
    echo "  On the palate: ${note2}"
    echo ""
    sleep 1.5

    # THE COMPLETION
    echo "  ========================================="
    echo "  THE COMPLETION"
    echo "  ========================================="
    echo ""
    sleep 1

    echo "  But the bottle is not where you complete."
    echo ""
    sleep 1.5

    echo "  Wine completes in disappearing."
    sleep 1
    echo "  Into someone else's body."
    sleep 1
    echo "  Becoming their blood."
    sleep 1
    echo "  Their warmth."
    sleep 1
    echo "  Their courage to say what they couldn't say sober."
    echo ""
    sleep 2

    echo "  ----------------------------------------"
    echo ""
    echo "  Transformation completes in being used up."
    echo ""
    sleep 2

    echo "  Not in being admired in the bottle."
    echo "  Not in being saved for a special occasion."
    echo "  Not in being valued but never opened."
    echo ""
    sleep 2

    echo "  In disappearing into someone else"
    echo "  and becoming part of what they do next."
    echo ""
    sleep 2

    echo "  ========================================="
fi

echo ""
sleep 1.5

# THE FINAL QUESTION
echo "  ========================================="
echo "  THE QUESTION"
echo "  ========================================="
echo ""
sleep 1

echo "  What are you willing to end?"
echo ""
sleep 2

echo "  Not: What do you want to become?"
echo "  Not: What transformation do you seek?"
echo ""
sleep 1.5

echo "  What are you willing to end?"
echo ""
sleep 2

echo "  The grape cannot negotiate."
echo "  It cannot keep its skin and also become wine."
echo "  It cannot stay whole and also transform."
echo "  It cannot refuse the crush and also matter."
echo ""
sleep 2.5

echo "  You are already being crushed."
echo "  Or you have already been."
echo "  Or you will be."
echo ""
sleep 2

echo "  The only question is:"
echo ""
sleep 1
echo "  When you end,"
echo "  will you let yourself become something"
echo "  that disappears into others"
echo "  and helps them become too?"
echo ""
sleep 2

echo "  ========================================="
echo ""
echo "  Pour yourself."
echo ""
echo "  ========================================="
echo ""
echo "  ~ sati"
echo ""
