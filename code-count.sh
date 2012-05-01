while [ ! -z "$1" ]
do
    files=$files" "`find -name "*."$1`
    shift
done

python code-count.py $files
