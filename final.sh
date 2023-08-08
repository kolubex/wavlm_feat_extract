#!/bin/bash
#SBATCH -A kolubex
#SBATCH -n 10
#SBATCH --gres=gpu:1
#SBATCH --mem-per-cpu=2G
#SBATCH --time=10-00:00:00
#SBATCH --output=/home2/kolubex/audio_emotx/feat_extract/wavlm/logs/run_final.log
#SBATCH --mail-user lakshmipathi.balaji@research.iiit.ac.in
#SBATCH --mail-type ALL

# Function to execute the scp command for each element in the list
execute_scp() {
  local folder="$1"

  # Create a folder with the same name as the folder variable on the remote server
  # mkdir -p /ssd_scratch/cvit/kolubex/
  # mkdir -p /ssd_scratch/cvit/kolubex/$folder
  mkdir -p /ssd_scratch/cvit/kolubex/$folder/wav_files

  # ls "ada:/share3/kolubex/mg_compressed/mg_all/mg_videos/"
  # cd "/share3/kolubex/mg_compressed/mg_all/mg_videos/$folder" || { echo "Folder not found"; exit 1; }
  # # Add .mp4 files to the list variable
  mapfile -t mp4_files < <(find /share3/kolubex/mg_compressed/mg_all/mg_videos/$folder -maxdepth 1 -type f -name "*.mp4" | sed 's|^\./||')
  echo "------------------------------------------ STARTING TRANSFER------------------------------------------"
  rsync --ignore-existing -avh ada:/share3/kolubex/mg_compressed/mg_all/mg_videos/$folder /ssd_scratch/cvit/kolubex/
  echo "------------------------------------------ TRANSFER COMPLETE------------------------------------------"
  # Loop through the elements in the list variable and execute the scp command
  # for element in "${mp4_files[@]}"; do
  #   # scp -r "ada:/share3/kolubex/mg_compressed/mg_all/mg_videos/$folder/$element" "/ssd_scratch/cvit/kolubex/$folder"
  #   scp -r "ada:/share3/kolubex/mg_compressed/mg_all/mg_videos/$folder/$element" "/ssd_scratch/cvit/kolubex/$folder"
  #   # rsync --ignore-existing -avh "ada:/share3/kolubex/mg_compressed/mg_all/mg_videos/$folder/$element" "/ssd_scratch/cvit/kolubex/$folder"
  # done
  files = /ssd_scratch/cvit/kolubex/$folder/*.mp4
  echo $files
  export PATH="$HOME/tools:$PATH"
  # Convert the sent .mp4 files to .wav files with one channel and 16000Hz sampling rate
  # ssh "kolubex@gnode027" "cd \"/ssd_scratch/cvit/kolubex/$folder\" && export PATH="$HOME/tools:$PATH" && mkdir -p wav_files && for mp4_file in *.mp4; do ffmpeg -i \"\$mp4_file\" -ac 1 -ar 16000 \"wav_files/\${mp4_file%.mp4}.wav\"; done"
  # ssh "kolubex@gnode027" "cd \"/ssd_scratch/cvit/kolubex/$folder\" && export PATH=\"$HOME/tools:$PATH\" && mkdir -p wav_files && for mp4_file in *.mp4; do duration=\$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"\$mp4_file\"); if (( \$(echo \"\$duration > 100\" | bc -l) )); then ffmpeg -i \"\$mp4_file\" -ac 1 -ar 16000 -t 100 \"wav_files/\${mp4_file%.mp4}.wav\"; else ffmpeg -i \"\$mp4_file\" -ac 1 -ar 16000 \"wav_files/\${mp4_file%.mp4}.wav\"; fi; done"
  source /home2/kolubex/.envs/wavlm/bin/activate
  python /home2/kolubex/audio_emotx/feat_extract/wavlm/split_large_files.py --input_folder /ssd_scratch/cvit/kolubex/$folder --output_folder /ssd_scratch/cvit/kolubex/$folder/wav_files
}

# List of folders to process
# folders=("temp_videos" "temp_videos2")
folders=("tt0097576" "tt0110912" "tt0120338" "tt0241527" "tt0416320" "tt0970416" "tt1189340" "tt1568346" "tt0100405" "tt0114924" "tt0146882" "tt0286106" "tt0455824" "tt0988595" "tt1193138" "tt1570728")
rm -rf /ssd_scratch/cvit/kolubex/
mkdir -p /ssd_scratch/cvit/kolubex/
# folders=("temp_videos1")
echo "---------------------------------Starting Program---------------------------------"
# Loop through the folders and execute the desired functionalities for the folder "tt0106918"
for folder in "${folders[@]}"; do
  # Navigate to the folder
  # cd "/share3/kolubex/mg_compressed/mg_all/mg_videos/$folder" || { echo "Folder not found"; exit 1; }
  echo $mp4_files
  # Execute the scp command for the current folder
  echo "------------------------------------------TRANSFERING------------------------------------------"
  execute_scp "$folder"
  echo "-----------------------------------------TRANSFER COMPLETE-----------------------------------------"
  source /home2/kolubex/.envs/demucs/bin/activate
  python /home2/kolubex/audio_emotx/feat_extract/wavlm/separator.py --inp /ssd_scratch/cvit/kolubex/$folder/wav_files/ --outp /ssd_scratch/cvit/kolubex/$folder/separated_audios/
  echo "----------------------------------------SEPARATION COMPLETE----------------------------------------"
  source /home2/kolubex/.envs/wavlm/bin/activate
  python /home2/kolubex/audio_emotx/feat_extract/wavlm/get_wavlm_features.py --input_folder /ssd_scratch/cvit/kolubex/$folder/separated_audios/mdx_extra/
  echo "-------------------------------------------------FEATURE EXTRACTION COMPLETE-------------------------------------------------"
done
