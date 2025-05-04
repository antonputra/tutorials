package com.antonputra;

import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.Timer.Sample;
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

import org.eclipse.microprofile.config.inject.ConfigProperty;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;

import io.vertx.mutiny.pgclient.PgPool;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

import java.io.File;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Objects;

@Path("/api/images")
public class ImageResource {
    @Inject
    S3Client s3;

    private int counter = 0;

    @ConfigProperty(name = "bucket.name")
    String bucketName;

    @ConfigProperty(name = "image.path")
    String imgPath;

    private final MeterRegistry registry;
    private static Timer s3Timer;
    private static Timer dbTimer;
    private final PgPool dbClient;

    public ImageResource(PgPool dbClient, MeterRegistry registry) {
        this.registry = registry;
        this.dbClient = dbClient;

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
    public String getImages() {
        String imgKey = "java-thumbnail-" + counter++ + ".png";
        Image img = new Image(imgKey);

        upload(imgPath, imgKey);
        save(img);

        return "Saved!";
    }

    private void upload(String path, String key) {
        Sample sample = Timer.start(registry);

        PutObjectRequest putOb = PutObjectRequest.builder().bucket(bucketName).key(key).build();
        s3.putObject(putOb, RequestBody.fromFile(new File(path)));

        sample.stop(s3Timer);
    }

    private void save(Image img) {
        Sample sample = Timer.start(registry);

        PreparedQuery<RowSet<Row>> st = dbClient.preparedQuery("INSERT INTO java_image VALUES ($1, $2, $3)");
        st.executeAndAwait(Tuple.of(img.imageId, img.objKey, img.createdAt));

        sample.stop(dbTimer);
    }
}
