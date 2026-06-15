package config

import (
	"fmt"
	"os"
	"strconv"
)

type Config struct {
	Server   ServerConfig
	Database DatabaseConfig
	Redis    RedisConfig
	JWT      JWTConfig
	Python   PythonConfig
}

type ServerConfig struct {
	Port int
}

type DatabaseConfig struct {
	Host     string
	Port     int
	User     string
	Password string
	DBName   string
	SSLMode  string
}

type RedisConfig struct {
	Host     string
	Port     int
	Password string
	DB       int
}

type JWTConfig struct {
	Secret     string
	ExpireHour int
}

type PythonConfig struct {
	WorkerURL string
}

func (c *DatabaseConfig) DSN() string {
	return fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%d sslmode=%s",
		c.Host, c.User, c.Password, c.DBName, c.Port, c.SSLMode)
}

func Load() *Config {
	return &Config{
		Server: ServerConfig{
			Port: getEnvInt("GO_SERVER_PORT", 8080),
		},
		Database: DatabaseConfig{
			Host:     getEnv("DB_HOST", "localhost"),
			Port:     getEnvInt("DB_PORT", 5432),
			User:     getEnv("DB_USER", "ecom"),
			Password: getEnv("DB_PASSWORD", "ecom_secret_123"),
			DBName:   getEnv("DB_NAME", "ecom_order_hub"),
			SSLMode:  getEnv("DB_SSLMODE", "disable"),
		},
		Redis: RedisConfig{
			Host:     getEnv("REDIS_HOST", "localhost"),
			Port:     getEnvInt("REDIS_PORT", 6379),
			Password: getEnv("REDIS_PASSWORD", "redis_secret_123"),
			DB:       getEnvInt("REDIS_DB", 0),
		},
		JWT: JWTConfig{
			Secret:     getEnv("JWT_SECRET", "default_jwt_secret_change_me"),
			ExpireHour: getEnvInt("JWT_EXPIRE_HOUR", 24),
		},
		Python: PythonConfig{
			WorkerURL: getEnv("PYTHON_WORKER_URL", "http://localhost:8000"),
		},
	}
}

func getEnv(key, defaultVal string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return defaultVal
}

func getEnvInt(key string, defaultVal int) int {
	val := os.Getenv(key)
	if val == "" {
		return defaultVal
	}
	n, err := strconv.Atoi(val)
	if err != nil {
		return defaultVal
	}
	return n
}
