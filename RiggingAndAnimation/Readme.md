# Rigging and Animation

### Dependencies Installation

1. Downloading openpose 

Download openpose from the following link: https://github.com/CMU-Perceptual-Computing-Lab/openpose/releases
Note: Choose the GPU version if compatable.

After openpose installation, move directory openpose to 'RiggingAndAnimation' directory, and the download openpose's models by following the instraction given.

2. Downloading Segmentation model

```{sh}
git clone https://github.com/Adham-M/HumanSeg.git
```

To download the model of HumanSeg:
```{sh}
cd HumanSeg
pip install paddleseg
python export_model/download_export_model.py
```
