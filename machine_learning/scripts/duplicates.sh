# replace '.' with the desired root directory
files=( $(find . -type f) )

for ((i=0; i<${#files[@]}; i++)); do
    for ((j=i+1; j<${#files[@]}; j++)); do
        if diff -q "${files[$i]}" "${files[$j]}" &>/dev/null; then
            echo "DUPLICATE: ${files[$i]} and ${files[$j]}"
        fi
    done
done
