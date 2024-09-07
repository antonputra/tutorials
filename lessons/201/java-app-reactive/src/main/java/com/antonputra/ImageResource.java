package com.antonputra;

import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.Timer.Sample;
import io.smallrye.mutiny.Uni;
import io.micrometer.core.instrument.MeterRegistry;

import io.vertx.mutiny.sqlclient.PreparedQuery;
import io.vertx.mutiny.sqlclient.Row;
import io.vertx.mutiny.sqlclient.RowSet;
import io.vertx.mutiny.sqlclient.Tuple;
import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import java.util.concurrent.atomic.AtomicInteger;

import org.eclipse.microprofile.config.inject.ConfigProperty;

import software.amazon.awssdk.core.async.AsyncRequestBody;
import software.amazon.awssdk.services.s3.S3AsyncClient;
import io.vertx.mutiny.core.Vertx;
import io.vertx.mutiny.pgclient.PgPool;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;


@Path("/api/images")
public class ImageResource {

    private AtomicInteger counter = new AtomicInteger(0);

    @ConfigProperty(name = "bucket.name")
    String bucketName;

    @ConfigProperty(name = "image.path")
    String imgPath;

    private final Vertx vertx;
    private final MeterRegistry registry;
    private final S3AsyncClient s3Async;
    private final PreparedQuery<RowSet<Row>> st;

    private static Timer s3Timer;
    private static Timer dbTimer;

    @Inject
    public ImageResource(Vertx vertx, PgPool dbClient, S3AsyncClient s3Async, MeterRegistry registry) {
        this.vertx = vertx;
        this.registry = registry;
        this.s3Async = s3Async;
        this.st = dbClient.preparedQuery("INSERT INTO java_image VALUES ($1, $2, $3)");

        s3Timer = Timer.builder("myapp_request_duration_seconds")
                .publishPercentiles(0.9, 0.99)
                .tags("op", "s3")
                .description("S3 request duration.").register(registry);

        dbTimer = Timer.builder("myapp_request_duration_seconds")
                .publishPercentiles(0.9, 0.99)
                .tags("op", "db")
                .description("DB request duration.").register(registry);
    }

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public Uni<String> getImages() {
        String imgKey = "java-thumbnail-" + counter.getAndIncrement() + ".png";

        Image img = new Image(imgKey);

        return upload(imgPath, imgKey)
                .flatMap(v -> save(img))
                .replaceWith("Saved!");
    }

    private Uni<Void> upload(String path, String key) {
        Sample sample = Timer.start(registry);

        PutObjectRequest putOb = PutObjectRequest.builder()
                .bucket(bucketName)
                .key(key)
                .build();

        return vertx.fileSystem().readFile(path)
                .flatMap(buffer -> {
                    return Uni.createFrom().completionStage(
                            s3Async.putObject(putOb, AsyncRequestBody.fromBytes(buffer.getBytes())));
                })
                .onItem().ignore().andContinueWithNull()
                .onItem().invoke(() -> sample.stop(s3Timer));
    }

    private Uni<Void> save(Image img) {
        Sample sample = Timer.start(registry);

        return st.execute(Tuple.of(img.imageId(), img.objKey(), img.createdAt()))
                .onItem().ignore().andContinueWithNull()
                .onItem().invoke(() -> sample.stop(dbTimer));
    }
}
