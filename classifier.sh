L=()

echo "Part1 - Dataset"
echo "----------------------------------------"
while read LINE
do
    L+="$LINE, "
    python ./dataset/dataset.py $LINE
done <$1
echo "----------------------------------------"

echo "Part2 - PreProcessing For tflearn"
echo "----------------------------------------"
python ./model/tags.py ${L[@]}
echo "----------------------------------------"

echo "Part3 - Training"
echo "----------------------------------------"
python ./model/train.py
echo "----------------------------------------"
