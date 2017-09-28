#!/usr/bin/env bash
python test.py \
--dataroot ./datasets/tiny_test_set \
--name train_pix2pix_render_standeview_daytime_9000samples \
--model pix2pix \
--which_model_netG unet_1024 \
--which_direction BtoA \
--dataset_mode aligned \
--gpu_ids -1 \
--fineSize 1024 \
--loadSize 1024 \
--batchSize 1 \
--how_many 4 \
--results_dir ./out/