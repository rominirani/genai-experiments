package main

import (
	"fmt"
	"log"
	"net/http"
	"rominirani/l200/app/handlers"

	"github.com/gorilla/mux"
)

func main() {
	r := mux.NewRouter()

	// Static files
	r.PathPrefix("/static/").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))

	// Index route
	r.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("Got a request")
		http.ServeFile(w, r, "./static/index.html")
	})

	// Chat endpoint
	r.HandleFunc("/chat", handlers.ChatHandler).Methods("POST")

	// ... (Add more routes if needed)

	port := 8080
	log.Printf("Listening on port %d", port)
	err := http.ListenAndServe(":8080", r)
	if err != nil {
		log.Fatal(err)
	}
}
