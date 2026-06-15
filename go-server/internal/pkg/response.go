package pkg

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// Response 统一响应结构
type Response struct {
	Code      int         `json:"code"`
	Message   string      `json:"message"`
	Data      interface{} `json:"data,omitempty"`
	Timestamp int64       `json:"timestamp"`
}

// PageData 分页数据
type PageData struct {
	List     interface{} `json:"list"`
	Total    int64       `json:"total"`
	Page     int         `json:"page"`
	PageSize int         `json:"page_size"`
}

func Success(c *gin.Context, data interface{}) {
	c.JSON(http.StatusOK, Response{
		Code:      0,
		Message:   "success",
		Data:      data,
		Timestamp: time.Now().Unix(),
	})
}

func SuccessPage(c *gin.Context, list interface{}, total int64, page, pageSize int) {
	c.JSON(http.StatusOK, Response{
		Code:    0,
		Message: "success",
		Data: PageData{
			List:     list,
			Total:    total,
			Page:     page,
			PageSize: pageSize,
		},
		Timestamp: time.Now().Unix(),
	})
}

func Fail(c *gin.Context, code int, message string) {
	c.JSON(http.StatusOK, Response{
		Code:      code,
		Message:   message,
		Timestamp: time.Now().Unix(),
	})
}

func FailWithStatus(c *gin.Context, httpStatus int, code int, message string) {
	c.JSON(httpStatus, Response{
		Code:      code,
		Message:   message,
		Timestamp: time.Now().Unix(),
	})
}
