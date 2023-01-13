package com.antonputra.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.mongo.MongoAutoConfiguration;

@SpringBootApplication
@EnableAutoConfiguration(exclude = { MongoAutoConfiguration.class })
public class DemoApplication {

	public static void main(String[] args) {
		System.setProperty("management.endpoints.web.exposure.include", "prometheus");

		ImagesController.s3Connect();
		ImagesController.mongodbConnect();
		SpringApplication.run(DemoApplication.class, args);
	}
}
