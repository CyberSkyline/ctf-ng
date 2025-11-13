FROM grafana/k6:latest-with-browser
WORKDIR /app
COPY . .
ENTRYPOINT ["k6", "run"]
CMD ["index.ts"]