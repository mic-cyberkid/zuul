FROM openjdk:17-jdk-slim

WORKDIR /app
COPY . .

RUN ./gradlew :zuul-sample:installDist

EXPOSE 7001 7008
ENTRYPOINT ["./zuul-sample/build/install/zuul-sample/bin/zuul-sample"]
