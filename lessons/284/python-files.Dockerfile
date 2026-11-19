# The files our app needs, collected the way the video collects them by hand on the server: Python, the loader
# and the four libraries that ldd names, Python's own code, BusyBox (a small toolbox), and an empty /data that
# belongs to the app's user, 10001. They come out as python-files.tar, in this folder:
#
#   docker build -f python-files.Dockerfile -o . .
#
# The video's own Dockerfile then builds the image from that archive and the app.
FROM ubuntu:26.04 AS collect
RUN apt-get update && apt-get install -y --no-install-recommends python3 busybox-static
RUN F=/srv/status-files \
 && mkdir -p $F/data $F/proc $F/usr/bin $F/bin \
 && cp /usr/bin/python3.14 $F/usr/bin/python3 \
 && for f in $(ldd /usr/bin/python3.14 | grep -o '/[^ ]*'); do mkdir -p $F$(dirname $f) && cp -L $f $F$f; done \
 && mkdir -p $F/usr/lib/python3.14 \
 && cp -a /usr/lib/python3.14/. $F/usr/lib/python3.14/ \
 && cp /usr/bin/busybox $F/bin/ \
 && chroot $F /bin/busybox --install -s /bin \
 && chown 10001:10001 $F/data \
 && tar -C $F -cf /python-files.tar .

FROM scratch
COPY --from=collect /python-files.tar /
