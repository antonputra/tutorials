# How To Install and Use PyTorch

[YouTube Tutorial](https://youtu.be/zInhP5xg96o)

## Create a virtual environment (Optionally)
```bash
$ python3 -m venv .venv
```

## Activate virtual environment
```bash
$ source .venv/bin/activate
```

## Install PyTorch pip package (macOS)
```bash
$ pip install torch torchvision
```

## On Linux and Windows, use the following commands for a CPU-only build
```bash
$ pip install torch==1.7.1+cpu torchvision==0.8.2+cpu -f https://download.pytorch.org/whl/torch_stable.html
```

## Create a JSON file to convert neural network output to a human-readable class name

## Create Python script to classify an image

## Run classifier
```
# python classify.py dog.jpg
```
