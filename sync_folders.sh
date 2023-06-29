source ~/.zshrc &&

source_dir="$2"
destination_dir="$1"
folder_name=$(basename "$source_dir")

if [ ! -d "$destination_dir/$folder_name" ]; then
    mkdir -p "$destination_dir/$folder_name"
fi

rsync -az --info=progress2 "$source_dir/" "$destination_dir/$folder_name" &&
if [ $? -eq 0 ]; then
    rm -r "$source_dir"
	echo "success!"
else
    echo "rsync command failed. The directory won't be removed."
fi