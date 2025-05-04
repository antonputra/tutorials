package com.antonputra.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.GetObjectRequest;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.util.IOUtils;
import com.amazonaws.client.builder.AwsClientBuilder.EndpointConfiguration;
import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.MongoCollection;

import org.bson.Document;

import java.util.TimeZone;
import java.util.concurrent.TimeUnit;
import java.util.Date;
import java.io.IOException;
import java.text.SimpleDateFormat;

import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.MeterRegistry;

@RestController
public class ImagesController {
    private static Timer s3RequestDuration;
    private static Timer mongoRequestDuration;

    private static String mongoDb = "lesson145";
    private static String accessKey = "admin";
    private static String secretKey = "devops123";

    private static MongoClient mongoClient;
    private static MongoDatabase database;
    private static AmazonS3 s3Client;

    public ImagesController(MeterRegistry registry) {
        s3RequestDuration = Timer.builder("javaapp_s3_request_duration").publishPercentiles(0.9, 0.99)
                .description("S3 request duration.").register(registry);
        mongoRequestDuration = Timer.builder("javaapp_mongo_request_duration").publishPercentiles(0.9, 0.99)
                .description("MongoDB request duration.").register(registry);
    }

    public static void mongodbConnect() {
        String mongoUri = System.getenv("MONGO_URI");

        mongoClient = MongoClients.create(mongoUri);
        database = mongoClient.getDatabase(mongoDb);
    }

    public static void s3Connect() {
        String s3Endpoint = System.getenv("S3_ENDPOINT");

        EndpointConfiguration endpoint = new EndpointConfiguration(s3Endpoint, "us-west-rack1");
        AWSCredentials credentials = new BasicAWSCredentials(accessKey, secretKey);

        s3Client = AmazonS3ClientBuilder.standard()
                .withCredentials(new ProfileCredentialsProvider())
                .withEndpointConfiguration(endpoint)
                .withPathStyleAccessEnabled(true)
                .withCredentials(new AWSStaticCredentialsProvider(credentials))
                .build();
    }

    @GetMapping("/api/images")
    public String getImage() throws IOException {
        Date date = download("lesson145", "thumbnail.png");

        long start = System.currentTimeMillis();
        MongoCollection<Document> collection = database.getCollection("images");
        collection.insertOne(new Document().append("lastModified", formatDate(date)));

        long end = System.currentTimeMillis();
        mongoRequestDuration.record(end - start, TimeUnit.MILLISECONDS);

        return "Saved!";
    }

    private static Date download(String bucketName, String key) throws IOException {
        long start = System.currentTimeMillis();

        S3Object object = s3Client.getObject(new GetObjectRequest(bucketName, key));

        IOUtils.toByteArray(object.getObjectContent());
        object.close();

        ObjectMetadata objectMetadata = object.getObjectMetadata();
        Date date = objectMetadata.getLastModified();
        if (object != null) {
            object.close();
        }
        long end = System.currentTimeMillis();
        s3RequestDuration.record(end - start, TimeUnit.MILLISECONDS);

        return date;
    }

    private static String formatDate(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX");
        sdf.setTimeZone(TimeZone.getTimeZone("UTC"));
        return sdf.format(date);
    }
}
