package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"cloud.google.com/go/cloudsqlconn"
	"cloud.google.com/go/cloudsqlconn/postgres/pgxv4"
)

// interactionData is used to pass data to the HTML template.
type interactionData struct {
	RecentTransactions []modelInteractionRow
}

// request contains a single row from the model_interactions table in the database.
// Each visit includes a timestamp.
type modelInteractionRow struct {
	Id           int
	RequestTS    time.Time
	ResponseTS   time.Time
	ResponseTime float32
	InputTokens  int
	OutputTokens int
	UserId       string
	ErrorLog     string
}

// getDB creates a connection to the database
// based on environment variables.
func getDB() (*sql.DB, func() error) {
	cleanup, err := pgxv4.RegisterDriver("cloudsql-postgres", cloudsqlconn.WithIAMAuthN())
	if err != nil {
		log.Fatalf("Error on pgxv4.RegisterDriver: %v", err)
	}

	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s sslmode=disable", os.Getenv("INSTANCE_CONNECTION_NAME"), "postgres", "rominjoonix1!", os.Getenv("DB_NAME"))
	fmt.Println(dsn)
	db, err := sql.Open("cloudsql-postgres", dsn)
	if err != nil {
		log.Fatalf("Error on sql.Open: %v", err)
	}

	/*	createVisits := `CREATE TABLE IF NOT EXISTS visits (
		    id SERIAL NOT NULL,
		    created_at timestamp NOT NULL,
		    PRIMARY KEY (id)
		  );`
			_, err = db.Exec(createVisits)
			if err != nil {
				log.Fatalf("unable to create table: %s", err)
			}
	*/
	return db, cleanup
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Printf("Listening on port %s", port)
	db, cleanup := getDB()
	defer cleanup()

	http.HandleFunc("/logrequest", func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("Got a request")
		fmt.Println(r.RequestURI)
		// Insert current visit
		_, err := db.Exec("INSERT INTO model_interactions(request_ts, response_ts,response_time, input_tokens, output_tokens, user_id, error_log) VALUES(NOW(),NOW(),10,100,200,'romin','')")
		if err != nil {
			log.Fatalf("unable to save visit: %v", err)
		}

		// Get the last 5 visits
		rows, err := db.Query("SELECT * FROM model_interactions ORDER BY request_ts DESC LIMIT 5")
		if err != nil {
			log.Fatalf("DB.Query: %v", err)
		}
		defer rows.Close()

		var visits []modelInteractionRow
		for rows.Next() {
			var rowData modelInteractionRow
			err := rows.Scan(&rowData.Id, &rowData.RequestTS, &rowData.ResponseTS, &rowData.ResponseTime, &rowData.InputTokens, &rowData.OutputTokens, &rowData.UserId, &rowData.ErrorLog)
			if err != nil {
				log.Fatalf("Rows.Scan: %v", err)
			}
			visits = append(visits, modelInteractionRow{Id: rowData.Id, RequestTS: rowData.RequestTS, ResponseTS: rowData.ResponseTS, ResponseTime: rowData.ResponseTime, InputTokens: rowData.InputTokens, OutputTokens: rowData.OutputTokens, UserId: rowData.UserId, ErrorLog: rowData.ErrorLog})
		}
		response, err := json.Marshal(interactionData{RecentTransactions: visits})
		if err != nil {
			log.Fatalf("renderIndex: failed to parse totals with json.Marshal: %v", err)
		}
		w.Write(response)
	})
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}
