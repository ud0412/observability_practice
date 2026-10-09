FROM maven:3.9.16-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml ./
COPY src ./src
RUN mvn -B -ntp package
FROM eclipse-temurin:21.0.10_7-jre
ARG OTEL_JAVA_VERSION=2.32.0
ADD --checksum=sha256:f787eb6c7f3d18e69a431e108a15278d25ee37f83d68b678f621e063f3988f82 https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v${OTEL_JAVA_VERSION}/opentelemetry-javaagent.jar /otel/opentelemetry-javaagent.jar
WORKDIR /app
COPY --from=build /app/target/sample-spring-boot-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
