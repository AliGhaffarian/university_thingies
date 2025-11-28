source ./variables.sh

cd $(dirname $(pwd))

add_to_lables_file(){
    lables_filename=$1
    file_names="$2"
    label_value=$3

    for file in $file_names; do
        #get the filename out of pathname
        file=$(echo $file | rev | cut -f 1 -d '/' | rev)

        echo $file, $label_value >> $lables_filename
    done
}

split_between_training_and_test(){
    dir="$1"
    dest="$2"
    label="$3"

    echo processing $dir
    total_trace_number=$(ls $dir | wc -l)
    number_of_test_data=$(( ($total_trace_number / $TRAINING_TO_TEST_DATA_RATIO) ))
    number_of_training_data=$(( $total_trace_number - $number_of_test_data )) 

    training_data="$(find $dir/ -mindepth 1 -type f | head -n $number_of_training_data)"
    cp $training_data $dest/"training"
    add_to_lables_file $TRAINING_LABELS "$training_data" $label

    testing_data=$(find $dir/ -mindepth 1 -type f | tail -n $number_of_test_data)
    cp $testing_data $dest/"testing"
    add_to_lables_file $TESTING_LABELS "$testing_data" $label
}

filename_from_path(){
    echo $1 | rev | cut -f1 -d'/' | rev
}

rm -rf $DEST_DIR
mkdir -p $DEST_DIR/{"training","testing"}

echo processing attack dir
for dir in $(find $DATASET_DIR/$ATTACK_SUBDIR -mindepth 1 -type d); do
    split_between_training_and_test $dir $DEST_DIR $ATTACK_CLASS_VALUE
done
split_between_training_and_test $DATASET_DIR/$TRAINING_SUBDIR $DEST_DIR $NORMAL_CLASS_VALUE

# echo making lables.csv
# echo > lables.csv
# #make lables.csv
# for file in $(find $DATASET_DIR/$ATTACK_SUBDIR/ -mindepth 1 -type f); do
#     echo "$(filename_from_path $file), $ATTACK_CLASS_VALUE" >> "lables.csv"
# done
# #make lables.csv
# for file in $(find $DATASET_DIR/$TRAINING_SUBDIR/ -mindepth 1 -type f); do
#     echo "$(filename_from_path $file), $NORMAL_CLASS_VALUE" >> "lables.csv"
# done
