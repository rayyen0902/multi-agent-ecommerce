# Go 服务多阶段构建
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server main.go

FROM alpine:3.19
RUN apk --no-cache add ca-certificates tzdata
ENV TZ=Asia/Shanghai
WORKDIR /app
COPY --from=builder /app/server .
COPY --from=builder /app/migration ./migration
EXPOSE 8080
CMD ["./server"]
