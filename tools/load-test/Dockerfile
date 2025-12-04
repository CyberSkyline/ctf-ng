FROM grafana/k6:latest-with-browser
WORKDIR /app
COPY . .
ENTRYPOINT ["k6", "run"]
CMD ["--out", "json=/app/output/test_result.json", "index.ts"]