# Docker: the full lab

The full lab for my video "Docker Explained: How Containers Actually Work": thirteen missions, about 90 minutes, on a Linux server of your own. You put a small status page app in a container by hand, with plain Linux commands and no Docker, then build the same container with Docker and open it to compare. The missions are on the lab's page, https://antonputra.com/labs/docker/; this folder is everything they use. Short on time? The 10-minute exercise is one folder up, in [../README.md](../README.md), with its page at https://antonputra.com/exercises/docker-explained/.

## Run it

You need a fresh Ubuntu 26.04 server with no Docker on it, where you can use `sudo`: the lab changes it as root. A free VM from [Multipass](https://canonical.com/multipass/install) is just right:

```bash
multipass launch 26.04 --name server-1 --cpus 2 --memory 4G --disk 20G
multipass shell server-1
```

On the server, after you clone this repository (the lab's page has the command), put the app where the video has it:

```bash
cd tutorials/lessons/284/lab
sudo mkdir -p /app /data
sudo cp app/status.py app/message.txt /app/
sudo chown $USER /data
```

The missions type every command one at a time, with the errors left in, because the video teaches from them. The scripts are the clean result: the 28 commands of the hand build, and a check. Run the app in one terminal, and everything else in a second one:

```bash
./build.sh          # the first 27 commands: the app's files, the folder we keep and its user, the stacked folders, the network, the limits
./launch.sh         # the 28th: starts the app inside all of it; it stays in the foreground, so run it in terminal 1
./check.sh          # in terminal 2, while the app runs: 14 checks of the five rows of the card
./clean.sh          # takes the hand-built container apart again
```

## What is here

| file | what it is |
|---|---|
| `app/status.py`, `app/message.txt` | the status app, with Python's standard library only. `--listen` sets the address it listens on, and `--leak-mb N` turns on a memory leak of N MB a request |
| `build.sh` | the clean hand build, missions 2 to 8: 27 commands |
| `launch.sh` | the 28th command: the app in its own folder, process list and network, in its control group, as its own user |
| `check.sh` | 14 checks that the hand-built container is what the video shows |
| `clean.sh` | takes the hand-built container apart: seven commands |
| `Dockerfile` | the video's image: five lines, from our own files (mission 9) |
| `install-docker.sh` | Docker Engine from Docker's own apt repository, as Docker's install page says (mission 9) |

I tested the lab on Ubuntu 26.04 in a Multipass VM on a Mac with Apple silicon (arm64), with Docker Engine 29.10.
