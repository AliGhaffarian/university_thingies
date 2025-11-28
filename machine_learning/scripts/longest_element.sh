source ./variables.sh

cd $(dirname $(pwd))

for file in $(find $DATASET_DIR/ -mindepth 1 -type f); do
cat $file | tr -cd ' \t' | wc -c
done | sort -n | tail -n 1 > $LONGEST_ELEM_FILE

