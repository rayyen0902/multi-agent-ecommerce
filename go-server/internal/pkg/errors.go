package pkg

// 错误码定义
const (
	ErrCodeSuccess       = 0
	ErrCodeParamInvalid  = 10001
	ErrCodeUnauthorized  = 10002
	ErrCodeTokenExpired  = 10003
	ErrCodeForbidden     = 10004
	ErrCodeNotFound      = 10005
	ErrCodeServerInternal = 10006

	ErrCodeOrderNotFound  = 20001
	ErrCodeOrderStatusErr = 20002
	ErrCodeShopNotFound   = 20003
	ErrCodeProductNotFound = 20004
	ErrCodeRuleNotFound   = 20005

	ErrCodePlatformAPI    = 30001
	ErrCodePlatformAuth   = 30002
)

var errMsgMap = map[int]string{
	ErrCodeSuccess:       "success",
	ErrCodeParamInvalid:  "参数错误",
	ErrCodeUnauthorized:  "未授权",
	ErrCodeTokenExpired:  "Token已过期",
	ErrCodeForbidden:     "无权限",
	ErrCodeNotFound:      "资源不存在",
	ErrCodeServerInternal: "服务器内部错误",
	ErrCodeOrderNotFound:  "订单不存在",
	ErrCodeOrderStatusErr: "订单状态错误",
	ErrCodeShopNotFound:   "店铺不存在",
	ErrCodeProductNotFound: "商品不存在",
	ErrCodeRuleNotFound:   "规则不存在",
	ErrCodePlatformAPI:    "平台接口调用失败",
	ErrCodePlatformAuth:   "平台授权失败",
}

func GetErrMsg(code int) string {
	if msg, ok := errMsgMap[code]; ok {
		return msg
	}
	return "未知错误"
}
