package main

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/gin-gonic/gin/render"
)

type ginServer struct {
	*gin.Engine
}

func newGinServer() server {
	r := gin.New()

	r.GET("/api/devices", func(c *gin.Context) {
		c.Render(http.StatusOK, renderer{})
	})

	return &ginServer{r}
}

type renderer struct {
	render.JSON
}

func (r renderer) Render(w http.ResponseWriter) error {
	e := serializer.NewEncoder(w)
	e.SetEscapeHTML(false)
	return e.Encode(r.Data)
}

func (s *ginServer) serve(address string) error {

	log.Printf("Starting gin server on port %s", address)
	return s.Run(address)
}
