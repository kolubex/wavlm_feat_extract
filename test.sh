#!/bin/bash

# Function to execute the scp command for each element in the list
execute_scp() {
  local folder="$1"

  # Create a folder with the same name as the folder variable on the remote server
  ssh "kolubex@gnode027" "mkdir -p \"/ssd_scratch/cvit/kolubex/$folder\""

  # Loop through the elements in the list variable and execute the scp command
  for element in "${mp4_files[@]}"; do
    # scp -r "ada:/share3/kolubex/mg_compressed/mg_all/mg_videos/$folder/$element" "kolubex@gnode027:/ssd_scratch/cvit/kolubex/$folder"
    scp -r "ada:/home2/kolubex/audio_emotx/feat_extract/wavlm/$folder/$element" "kolubex@gnode027:/ssd_scratch/cvit/kolubex/$folder"
  done

  # Convert the sent .mp4 files to .wav files with one channel and 16000Hz sampling rate
  # ssh "kolubex@gnode027" "cd \"/ssd_scratch/cvit/kolubex/$folder\" && export PATH="$HOME/tools:$PATH" && mkdir -p wav_files && for mp4_file in *.mp4; do ffmpeg -i \"\$mp4_file\" -ac 1 -ar 16000 \"wav_files/\${mp4_file%.mp4}.wav\"; done"
  # ssh "kolubex@gnode027" "cd \"/ssd_scratch/cvit/kolubex/$folder\" && export PATH=\"$HOME/tools:$PATH\" && mkdir -p wav_files && for mp4_file in *.mp4; do duration=\$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"\$mp4_file\"); if (( \$(echo \"\$duration > 100\" | bc -l) )); then ffmpeg -i \"\$mp4_file\" -ac 1 -ar 16000 -t 100 \"wav_files/\${mp4_file%.mp4}.wav\"; else ffmpeg -i \"\$mp4_file\" -ac 1 -ar 16000 \"wav_files/\${mp4_file%.mp4}.wav\"; fi; done"
  source /home2/kolubex/.envs/wavlm/bin/activate
  python /home2/kolubex/audio_emotx/feat_extract/wavlm/split_large_files.py --input_folder /home2/kolubex/audio_emotx/feat_extract/wavlm/$folder --output_folder /ssd_scratch/cvit/kolubex/$folder/wav_files
}

# List of folders to process
folders=("temp_videos2")
# folders=("temp_videos1")

# Loop through the folders and execute the desired functionalities for the folder "tt0106918"
for folder in "${folders[@]}"; do
  # Navigate to the folder
  # cd "/share3/kolubex/mg_compressed/mg_all/mg_videos/$folder" || { echo "Folder not found"; exit 1; }
  cd /home2/kolubex/audio_emotx/feat_extract/wavlm/$folder
  # Add .mp4 files to the list variable
  mapfile -t mp4_files < <(find . -maxdepth 1 -type f -name "*.mp4" | sed 's|^\./||')

  # Execute the scp command for the current folder
  execute_scp "$folder"

  source /home2/kolubex/.envs/demucs/bin/activate
  python /home2/kolubex/audio_emotx/feat_extract/wavlm/separator.py --inp /ssd_scratch/cvit/kolubex/$folder/wav_files/ --outp /ssd_scratch/cvit/kolubex/$folder/separated_audios/
  source /home2/kolubex/.envs/wavlm/bin/activate
  python /home2/kolubex/audio_emotx/feat_extract/wavlm/get_wavlm_features.py --input_folder /ssd_scratch/cvit/kolubex/$folder/separated_audios/mdx_extra/
done
