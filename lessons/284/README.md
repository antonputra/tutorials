# Docker: Try It Yourself

You can find tutorial [here](https://youtu.be/I4GVDkxQRDI).

This is the exercise for my video about how Docker containers work. You build the status page app from the video into an image, from nothing but its own files, and run it with Docker. Then you look inside its container, row by row, and watch Linux stop it at its 64 MB limit. It takes about 10 minutes.

You need Docker (start Docker Desktop first, or the Docker service on Linux), about 1 GB of free disk space and ports 8080 and 8082 free on 127.0.0.1. Run the commands in a terminal: Terminal on a Mac, your shell on Linux, and on Windows a WSL terminal, such as Ubuntu, with Docker Desktop's WSL integration turned on. On Linux, put `sudo` in front of `docker` unless you are in the `docker` group.

The app is `app/status.py` and `app/message.txt`: a small status page in Python. On each request, it reads `message.txt`, adds a line to `/data/requests.log` and sends the message back.

## 1. Collect the app's files

In the video, the app fails in an empty folder until the folder has Python, its loader and libraries, and Python's own code. Then I pack those files into `python-files.tar`. Here, a Docker build runs the same copy commands in an Ubuntu 26.04 container and saves the archive in this folder:

```bash
docker build -f python-files.Dockerfile -o . .
ls -lh python-files.tar
```

The first build downloads Ubuntu and Python, about 80 MB, so give it a minute. The archive is about 40 MB.

## 2. Build the image

The video's recipe is five lines, in `Dockerfile`:

```text
FROM scratch
ADD python-files.tar /
COPY app/ /app/
USER 10001:10001
CMD ["python3", "/app/status.py", "--listen", "0.0.0.0"]
```

`FROM scratch` means no base image: the image starts empty, like the folder in the video. Build it, and look at its layers:

```bash
docker build -t status:1.0 .
docker image history status:1.0
```

The newest line is on top. The two lines that add files are the layers: Python's files, about 45 MB, and our app. The other two only set the user and the start command.

## 3. Run it

The same `docker run` as in the video: a name, a memory limit, half a CPU, a port on 127.0.0.1 and a volume for the log:

```bash
docker run -d --name status --memory 64m --cpus 0.5 -p 127.0.0.1:8080:8000 -v status-data:/data status:1.0
```

It prints the new container's ID. Now ask for the page, and read what the app printed:

```bash
curl http://127.0.0.1:8080/status
docker logs status
```

You get `<h1>Status: OK</h1>`, and the app's line for your request, with the time in UTC. You can open `http://127.0.0.1:8080/status` in your browser too.

## 4. Look inside

Now ask the container itself, one row of the card from the video at a time:

```bash
docker exec status ls /
docker exec status ps
docker exec status ip addr show eth0
docker exec status cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/cpu.max
docker exec status grep -E '^(Uid|CapEff)' /proc/1/status
```

- Files: the image's own folders, with `dev`, `etc` and `sys` added by Docker. On an Intel or AMD computer, `lib64` is there in place of `lib`.
- Processes: its own list, where our app is process 1.
- Network: its own interface, `eth0`, with its own address, such as `172.17.0.2`.
- Memory and CPU: `67108864` (64 MB in bytes) and `50000 100000` (50 ms of CPU time in every 100 ms: half a CPU).
- User: `10001`, and `CapEff: 0000000000000000`, none of root's powers.

## 5. Hit the limit

The app has a bug switch from the video: with `--leak-mb 10`, it keeps 10 MB more on every request and never gives it back. Start a second container from the same image with the leak on (the command after the image name replaces its start command):

```bash
docker run -d --name leaky --memory 64m --memory-swap 64m -p 127.0.0.1:8082:8000 status:1.0 python3 /app/status.py --listen 0.0.0.0 --leak-mb 10
```

Then send it eight requests:

```bash
for i in 1 2 3 4 5 6 7 8; do curl -s -o /dev/null -w "request $i: HTTP %{http_code}\n" -m 5 http://127.0.0.1:8082/status; done
```

Requests 1 to 5 get `HTTP 200`, then `HTTP 000`: at request 6, the app needed more than 64 MB, and Linux killed it. See how it ended:

```bash
docker ps -a --filter name=leaky --format '{{.Names}}: {{.Status}}'
```

Docker says `Exited (137)`: 137 means killed by force, an OOM kill, for out of memory. `--memory-swap 64m` keeps swap out of it. The server in the video has no swap, but Docker Desktop's VM has some, and without the flag Docker lets the app use 64 MB of swap on top: on my test machine, it answered 11 requests.

## Extra: a new container, the same data

Change the message inside the running container, as root, then remove the container and run a new one from the same image:

```bash
docker exec --user 0 status sh -c 'echo "Status: MAINTENANCE" > /app/message.txt'
curl http://127.0.0.1:8080/status
docker rm -f status
docker run -d --name status --memory 64m --cpus 0.5 -p 127.0.0.1:8080:8000 -v status-data:/data status:1.0
```

Ask the new container for the page, and read the log:

```bash
curl http://127.0.0.1:8080/status
docker exec status cat /data/requests.log
```

The change lived in the old container's own top layer, so the new container says `Status: OK` again. The log is in the volume, so it still has the old container's lines, with the new one's last.

## 6. Clean up

```bash
docker rm -f status leaky
docker volume rm status-data
docker image rm status:1.0
```

The builds also keep about 500 MB of cache, Ubuntu and Python included. To free it, run `docker builder prune -f`: it clears the cache of your other Docker builds too.

## The full lab

In the video, I build this container by hand first, with plain Linux commands, before Docker is even installed. The full lab does every step of it on a Linux server of your own, a free VM, then builds the same container with Docker and opens it to compare. Its files are in the [lab](lab) folder next to this README, and its steps are on https://antonputra.com/labs/docker/.
