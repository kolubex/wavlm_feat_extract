#!/bin/bash
#SBATCH -A kolubex
#SBATCH -n 10
#SBATCH --gres=gpu:1
#SBATCH --mem-per-cpu=2G
#SBATCH --time=10-00:00:00
#SBATCH --output=/home2/kolubex/audio_emotx/feat_extract/wavlm/logs/pad_pool.log
#SBATCH --mail-user lakshmipathi.balaji@research.iiit.ac.in
#SBATCH --mail-type ALL

echo "========================================TRANSFERRING FILES========================================"
rsync --ignore-existing -avh ada:/share3/kolubex/emotx/audio_feats/wavlm_feats/total_npy.tar.gz /ssd_scratch/cvit/kolubex/
echo "========================================TRANSFER COMPLETE========================================"
echo "========================================EXTRACTING FILES========================================"
tar -xvzf /ssd_scratch/cvit/kolubex/total_npy.tar.gz -C /ssd_scratch/cvit/kolubex/
echo "========================================EXTRACTION COMPLETE========================================"
# call python script
source /home2/kolubex/.envs/wavlm/bin/activate
python /home2/kolubex/audio_emotx/feat_extract/wavlm/pooling/pad_pool.py --input_path /ssd_scratch/cvit/kolubex/total_npy_files --output_path /ssd_scratch/cvit/kolubex/total_npy_pooled