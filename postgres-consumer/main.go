package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/lib/pq"
	_ "github.com/lib/pq"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
	"github.com/knadh/koanf/parsers/yaml"
	"github.com/knadh/koanf/providers/env"
	"github.com/knadh/koanf/providers/file"
	"github.com/knadh/koanf/v2"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

var k = koanf.New(".")

type GpsEntry struct {
	Timestamp int64  `json:"timestamp"`
	Lat       string `json:"lat"`
	Lng       string `json:"lng"`
	Name      string `json:"name"`
	Uuid      string `json:"uuid"`
}

func loadConfig() {
	if err := k.Load(file.Provider("config.yaml"), yaml.Parser()); err != nil {
		fmt.Printf("error loading config: %v", err)
	}
	k.Load(env.Provider("GPS_", ".", func(s string) string {
		return strings.Replace(strings.ToLower(
			strings.TrimPrefix(s, "GPS_")), "_", ".", -1)
	}), nil)

	switch strings.ToLower(k.String("log.format")) {
	case "text":
		log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})
	case "json":
		// default
	default:
		log.Fatal().Msg("invalid log format")
	}

	switch strings.ToLower(k.String("log.level")) {
	case "debug":
		zerolog.SetGlobalLevel(zerolog.DebugLevel)
	case "info":
		zerolog.SetGlobalLevel(zerolog.InfoLevel)
	case "warn":
		zerolog.SetGlobalLevel(zerolog.WarnLevel)
	case "error":
		zerolog.SetGlobalLevel(zerolog.ErrorLevel)
	default:
		log.Fatal().Msg("invalid log level")
	}

}

func runConsumer(db *sql.DB) {
	log.Info().Msg("Starting consumer")

	sigchan := make(chan os.Signal, 1)
	signal.Notify(sigchan, syscall.SIGINT, syscall.SIGTERM)

	c, err := kafka.NewConsumer(&kafka.ConfigMap{
		"bootstrap.servers":        k.String("kafka.bootstrapServers"),
		"broker.address.family":    "v4",
		"group.id":                 k.String("kafka.group"),
		"session.timeout.ms":       6000,
		"auto.offset.reset":        "earliest",
		"enable.auto.offset.store": false,
	})

	if err != nil {
		log.Fatal().Err(err).Msg("Failed to create consumer")
	}

	log.Info().Msg("Created consumer")
	err = c.SubscribeTopics([]string{k.String("kafka.topic")}, nil)
	run := true

	for run {
		select {
		case sig := <-sigchan:
			log.Info().Msgf("Caught signal %v: terminating", sig)
			run = false
		default:
			ev := c.Poll(100)
			if ev == nil {
				continue
			}

			switch e := ev.(type) {
			case *kafka.Message:
				if e.Headers != nil {
					log.Info().Msgf("Headers: %v\n", e.Headers)
				}

				var GpsEntry GpsEntry
				json.Unmarshal(e.Value, &GpsEntry)
				log.Info().Msgf("Consuming: %v", GpsEntry.Uuid)
				log.Debug().Msgf("GpsEntry: %v", GpsEntry)

				stmt, err := db.Prepare(fmt.Sprintf("INSERT INTO %s (timestamp ,lat, lng, name, uuid) VALUES ($1, $2, $3, $4, $5)", k.String("postgres.table")))
				if err != nil {
					log.Error().Err(err).Msg("Failed to prepare statement")
				}
				time := time.Unix(GpsEntry.Timestamp, 0)
				pqts := pq.FormatTimestamp(time)
				log.Debug().Msgf("Timestamp: %s\n", pqts)
				_, err = stmt.Exec(pqts, GpsEntry.Lat, GpsEntry.Lng, GpsEntry.Name, GpsEntry.Uuid)
				if err != nil {
					log.Error().Err(err).Msg("Failed to execute statement")
					_, err = c.StoreMessage(e)
					if err != nil {
						log.Error().Err(err).Msg("Failed to store message")
					}
				}

			case kafka.Error:
				log.Error().Err(e)
				if e.Code() == kafka.ErrAllBrokersDown {
					run = false
				}
			default:
				log.Info().Msgf("Ignored %v", e)
			}
		}
	}
	log.Info().Msg("Closing consumer")
	c.Close()
}

func connectDB() *sql.DB {
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s", k.String("postgres.host"), k.String("postgres.port"), k.String("postgres.user"), k.String("postgres.password"), k.String("postgres.database"), k.String("postgres.sslmode"))
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to open DB connection")
	}
	return db
}

func main() {
	loadConfig()
	db := connectDB()
	defer db.Close()
	runConsumer(db)
}
