FROM maven:3.8.7-amazoncorretto-19 as builder

WORKDIR /app
 
COPY pom.xml .
 
COPY src src

RUN mvn clean package

FROM amazoncorretto:19.0.1-alpine3.16

COPY --from=builder /app/target/*.jar /app/java-app.jar

ENTRYPOINT ["java","-jar","/app/java-app.jar"]
